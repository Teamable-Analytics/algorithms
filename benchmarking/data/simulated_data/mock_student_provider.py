import random
from dataclasses import dataclass, field
from typing import Literal, List, Dict, Optional

import numpy as np

from api.models.enums import Relationship, AttributeValueEnum, ScenarioAttribute
from api.models.student import Student
from benchmarking.data.interfaces import (
    StudentProvider,
    AttributeRangeConfig,
    NumValuesConfig,
)
from utils.validation import is_non_negative_integer, is_unique


@dataclass
class MockStudentProviderSettings:
    number_of_students: int
    attribute_ranges: Dict[int, AttributeRangeConfig] = field(default_factory=dict)
    num_values_per_attribute: Dict[int, NumValuesConfig] = field(default_factory=dict)
    # ids of projects that can be selected as a preference by students
    project_preference_options: List[int] = field(default_factory=list)
    num_project_preferences_per_student: int = 0
    number_of_friends: int = 0
    number_of_enemies: int = 0
    friend_distribution: Literal["cluster", "random"] = "random"
    allow_probabilistic_generation: bool = False

    def __post_init__(self):
        self.validate()

    def validate(self):
        # todo: add validation for attribute_ranges vs num_values_per_attribute
        if not is_non_negative_integer(self.number_of_students):
            raise ValueError(
                f"number_of_students ({self.number_of_students}) must be a non-negative integer."
            )
        if not is_non_negative_integer(self.number_of_friends):
            raise ValueError(
                f"number_of_friends ({self.number_of_friends}) must be a non-negative integer."
            )
        if not is_non_negative_integer(self.number_of_enemies):
            raise ValueError(
                f"number_of_enemies ({self.number_of_enemies}) must be a non-negative integer."
            )
        if (
            len(self.project_preference_options)
            < self.num_project_preferences_per_student
        ):
            raise ValueError(
                f"num_project_preferences_per_student ({self.num_project_preferences_per_student}) cannot "
                "be > the number of project options."
            )
        if not is_non_negative_integer(self.num_project_preferences_per_student):
            raise ValueError(
                f"num_project_preferences_per_student ({self.num_project_preferences_per_student}) must be a "
                f"non-negative integer."
            )
        if not is_unique(self.project_preference_options):
            raise ValueError(f"project_preference_options must be unique if specified.")


class MockStudentProvider(StudentProvider):
    def __init__(self, settings: MockStudentProviderSettings):
        self.settings = settings

    def get(self, seed: int = None) -> List[Student]:
        mock_students = create_mock_students(
            self.settings.number_of_students,
            self.settings.number_of_friends,
            self.settings.number_of_enemies,
            self.settings.friend_distribution,
            self.settings.attribute_ranges,
            self.settings.num_values_per_attribute,
            self.settings.project_preference_options,
            self.settings.num_project_preferences_per_student,
            self.settings.allow_probabilistic_generation,
            seed,
        )
        # the students must be shuffled here because certain algorithms
        #   perform better/worse based on the ordering of students.
        #   i.e. if each sequential block of 5 students all selected one another as friends
        random.shuffle(mock_students)
        return mock_students

    @property
    def num_students(self) -> int:
        return self.settings.number_of_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return self.settings.num_project_preferences_per_student


def create_mock_students(
    number_of_students: int,
    number_of_friends: int,
    number_of_enemies: int,
    friend_distribution: Literal["cluster", "random"],
    attribute_ranges: Dict[int, AttributeRangeConfig],
    num_values_per_attribute: Dict[int, NumValuesConfig],
    project_preference_options: List[int],
    num_project_preferences_per_student: int,
    allow_probabilistic_generation: bool = False,
    random_seed: int = None,
) -> List[Student]:
    students = []
    n = number_of_students
    f = number_of_friends
    e = number_of_enemies

    if number_of_friends + number_of_enemies >= number_of_students:
        raise ValueError(
            "Cannot request more friends/enemies than there are people in the class"
        )

    rng = (
        np.random.default_rng(seed=random_seed)
        if random_seed
        else np.random.default_rng()
    )

    probabilistic_attributes = (
        {}
        if allow_probabilistic_generation
        else (_generate_attribute_values_without_probability(attribute_ranges, n))
    )

    for i in range(n):
        relationships = {}

        # Pick friends
        if friend_distribution == "cluster":
            clique_start = i // (f + 1) * (f + 1)
            friends = [
                friend_id % n
                for friend_id in range(clique_start, clique_start + f + 1)
                if friend_id != i
            ]
        else:
            other_people = [_ for _ in range(0, n) if _ != i]
            friends = random_choice(
                possible_values=other_people,
                size=min(f, len(other_people)),
                replace=False,
                generator=rng,
            )
        for friend_id in friends:
            relationships[friend_id] = Relationship.FRIEND

        # Pick enemies
        eligible_enemies = [_ for _ in range(0, n) if _ not in [i, *friends]]
        enemies = random_choice(
            possible_values=eligible_enemies,
            size=min(e, len(eligible_enemies)),
            replace=False,
            generator=rng,
        )

        for enemy_id in enemies:
            relationships[enemy_id] = Relationship.ENEMY

        attributes = {}
        for attribute_id, attribute_range_config in attribute_ranges.items():
            num_value_config = num_values_per_attribute.get(attribute_id, None)
            num_values = (
                num_values_for_attribute(num_value_config, generator=rng)
                if num_value_config
                else None
            )
            attributes[attribute_id] = attribute_values_from_range(
                attribute_range_config,
                num_values,
                allow_probabilistic_generation,
                probabilistic_attributes.get(attribute_id, []),
                generator=rng,
            )

        project_preferences = None
        if project_preference_options and num_project_preferences_per_student:
            project_preferences = random_choice(
                project_preference_options,
                num_project_preferences_per_student,
                generator=rng,
            )

        students.append(
            Student(
                i,
                relationships=relationships,
                attributes=attributes,
                project_preferences=project_preferences or [],
            )
        )
    return students


def num_values_for_attribute(num_values_config: NumValuesConfig, generator=None) -> int:
    if isinstance(num_values_config, int):
        return num_values_config

    _generator = generator or np.random.default_rng()

    min_choices, max_choices = num_values_config
    return int(_generator.integers(low=min_choices, high=max_choices))


def random_choice(
    possible_values: List, size=None, replace=False, weights=None, generator=None
) -> List[int]:
    """
    Uses np.random.choice() but always returns a list of int
    (np.random.choice return numpy.int64 if size=1 and ndarray otherwise)
    """
    if not possible_values:
        return []

    _generator = generator or np.random.default_rng()

    size = size or 1
    values = _generator.choice(possible_values, size=size, replace=replace, p=weights)

    if size == 1:
        return [int(values)]
    return [int(val) for val in values]


def attribute_values_from_range(
    range_config: AttributeRangeConfig,
    num_values: Optional[int] = 1,
    allow_probabilistic_generation: bool = False,
    probabilistic_attribute_values: List[int] = None,
    generator=None,
) -> List[int]:
    _generator = generator or np.random.default_rng()

    if isinstance(range_config[0], (int, AttributeValueEnum)):
        if isinstance(range_config[0], int):
            possible_values = range_config
        else:
            # .value accounts for AttributeValueEnum in the range config
            possible_values = [enum.value for enum in range_config]
        return random_choice(
            possible_values, size=num_values, replace=False, generator=_generator
        )

    if not allow_probabilistic_generation:
        return (
            [probabilistic_attribute_values.pop()]
            if probabilistic_attribute_values
            else []
        )

    # config is a list of (value, % chance) tuples
    if isinstance(range_config[0][0], int):
        possible_values = [_[0] for _ in range_config]
    else:
        possible_values = [_[0].value for _ in range_config]

    weights = [_[1] for _ in range_config]
    return random_choice(
        possible_values,
        weights=weights,
        size=num_values,
        replace=False,
        generator=_generator,
    )


def _generate_attribute_values_without_probability(
    attribute_ranges: Dict[int, AttributeRangeConfig], class_size: int
):
    probabilistic_attributes = {}
    for attribute_id, attribute_range_config in attribute_ranges.items():
        if isinstance(attribute_range_config[0], (int, AttributeValueEnum)):
            continue

        # Assume if the range is probabilistic, the number of value per attribute is 0
        if (sum([_[1] for _ in attribute_range_config])) != 1:
            raise ValueError(f"Probabilistic attribute range must sum to 100$")

        probabilistic_attributes[attribute_id] = []
        for attribute_range in attribute_range_config:
            probabilistic_attributes[attribute_id].extend(
                [
                    attribute_range[0]
                    if isinstance(attribute_range[0], int)
                    else attribute_range[0].value
                    for _ in range(int(attribute_range[1] * class_size))
                ]
            )
        random.shuffle(probabilistic_attributes[attribute_id])

    return probabilistic_attributes
