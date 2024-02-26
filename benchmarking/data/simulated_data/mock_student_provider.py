import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, List, Dict, Optional

import numpy as np
from numpy.random import Generator

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
    ensure_exact_attribute_ratios: bool = True

    def __post_init__(self):
        self.validate()

    def validate(self):
        # todo: add validation for num_values_per_attribute
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
        if not is_non_negative_integer(self.num_project_preferences_per_student):
            raise ValueError(
                f"num_project_preferences_per_student ({self.num_project_preferences_per_student}) must be a "
                f"non-negative integer."
            )
        if (
            len(self.project_preference_options)
            < self.num_project_preferences_per_student
        ):
            raise ValueError(
                f"num_project_preferences_per_student ({self.num_project_preferences_per_student}) cannot "
                "be > the number of project options."
            )
        if not is_unique(self.project_preference_options):
            raise ValueError(f"project_preference_options must be unique if specified.")
        if self.ensure_exact_attribute_ratios and self.num_values_per_attribute:
            raise ValueError(
                "Cannot ensure exact attribute ratios when specifying num_values_per_attribute"
            )

        # Validate when attribute ranges are specified as a list of (value, % chance) tuples
        for attribute_id, range_config in self.attribute_ranges.items():
            if not isinstance(attribute_id, int):
                raise ValueError(
                    f"attribute_ranges keys must be integers. Found {attribute_id}"
                )
            if not is_non_negative_integer(attribute_id):
                raise ValueError(
                    f"attribute_ranges keys must be non-negative integers. Found {attribute_id}"
                )

            # TODO: this validation is not complete, we only check the first element on both levels
            # (https://github.com/Teamable-Analytics/algorithms/issues/369)
            if not range_config:
                raise ValueError(f"attribute_ranges[{attribute_id}] must not be empty.")
            if range_config[0][0] is not None and isinstance(
                range_config[0][0], (int, AttributeValueEnum)
            ):
                total_chance = sum([_[1] for _ in range_config])
                if not math.isclose(total_chance, 1):
                    raise ValueError(
                        f"attribute_ranges[{attribute_id}] must sum to 1. Found {total_chance}"
                    )

        if self.number_of_enemies >= self.number_of_students:
            raise ValueError(
                "Cannot request more enemies than there are people in the class"
            )
        if self.number_of_friends >= self.number_of_students:
            raise ValueError(
                "Cannot request more friends than there are people in the class"
            )
        if self.friend_distribution not in ["cluster", "random"]:
            raise ValueError(
                f"friend_distribution ({self.friend_distribution}) must be either 'cluster' or 'random'."
            )


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
            self.settings.ensure_exact_attribute_ratios,
            random_seed=seed,
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
    ensure_exact_attribute_ratios: bool,
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

    if ensure_exact_attribute_ratios and num_values_per_attribute:
        raise ValueError(
            "Cannot ensure exact attribute ratios when specifying num_values_per_attribute"
        )

    rng = (
        np.random.default_rng(seed=random_seed)
        if random_seed
        else np.random.default_rng()
    )

    attribute_value_maker = (
        ExactAttributeRatiosMaker(
            number_of_students=number_of_students,
            attribute_ranges=attribute_ranges,
            generator=rng,
        )
        if ensure_exact_attribute_ratios
        else ProbabilisticAttributeValuesMaker(
            attribute_ranges=attribute_ranges, generator=rng
        )
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
            # We only need to retrieve the num_values per attribute dynamically when ensure_exact_attribute_ratios == False
            if not ensure_exact_attribute_ratios:
                # assume we pick 1 value per student for this attribute if no explicit value is given
                num_value_config = num_values_per_attribute.get(attribute_id, None)
                num_values = (
                    num_values_for_attribute(num_value_config, generator=rng)
                    if num_value_config is not None
                    else 1
                )
            else:
                num_values = 1

            attributes[attribute_id] = attribute_value_maker.get(
                attribute_id, num_values
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
    possible_values: List, size=1, replace=False, weights=None, generator=None
) -> List[int]:
    """
    Uses np.random.choice() but always returns a list of int
    (np.random.choice return numpy.int64 if size=1 and ndarray otherwise)
    """
    if not possible_values or size == 0:
        return []

    _generator = generator or np.random.default_rng()

    values = _generator.choice(possible_values, size=size, replace=replace, p=weights)

    if size == 1:
        return [int(values)]
    return [int(val) for val in values]


class AttributeValueMaker(ABC):
    def __init__(
        self,
        attribute_ranges: Dict[int, AttributeRangeConfig],
        generator: Generator = None,
    ):
        self.attribute_ranges = attribute_ranges
        self.generator = generator or np.random.default_rng()

    @abstractmethod
    def get(self, range_config: AttributeRangeConfig, num_values: int = 1) -> List[int]:
        raise NotImplementedError


class ExactAttributeRatiosMaker(AttributeValueMaker):
    def __init__(
        self,
        attribute_ranges: Dict[int, AttributeRangeConfig],
        number_of_students: int,
        generator: Generator = None,
    ):
        super().__init__(attribute_ranges, generator)
        self.options: Dict[int, List[int]] = self._setup_fixed_attribute_value_pool(
            number_of_students, attribute_ranges
        )

    def _setup_fixed_attribute_value_pool(
        self, number_of_students: int, attribute_ranges: Dict[int, AttributeRangeConfig]
    ) -> Dict[int, List[int]]:
        options = {}
        for attribute_id, range_config in attribute_ranges.items():
            if isinstance(range_config[0], (int, AttributeValueEnum)):
                # config is a list either int or AttributeValueEnum
                self.generator.shuffle(range_config)
                options_for_attribute = [
                    range_config[i % len(range_config)]
                    for i in range(number_of_students)
                ]
            else:
                # config is a list of (int | AttributeValueEnum, % chance) tuples
                options_for_attribute = []
                for value, chance in range_config:
                    number_of_students_with_value = chance * number_of_students
                    if number_of_students_with_value != int(
                        number_of_students_with_value
                    ):
                        raise ValueError(
                            f"Cannot ensure exact attribute ratios when specifying num_values_per_attribute. "
                            f"Found chance of {chance} with class size of {number_of_students} for attribute {attribute_id}"
                        )

                    options_for_attribute.extend(
                        [value for _ in range(int(number_of_students_with_value))]
                    )

            options[attribute_id] = options_for_attribute
        return options

    def get(self, attribute_id: int, num_values: int = 1) -> List[int]:
        if num_values != 1:
            raise ValueError(
                "Cannot use ExactAttributeRatiosMaker when num_values != 1"
            )

        value = self.options.get(attribute_id).pop()
        if isinstance(value, AttributeValueEnum):
            return [value.value]
        return [value]


class ProbabilisticAttributeValuesMaker(AttributeValueMaker):
    def __init__(
        self,
        attribute_ranges: Dict[int, AttributeRangeConfig],
        generator: Generator = None,
    ):
        super().__init__(attribute_ranges, generator)

    def get(self, attribute_id: int, num_values: int = 1) -> List[int]:
        range_config = self.attribute_ranges.get(attribute_id)
        if not range_config:
            # todo: finish
            raise ValueError

        # config is a list either int or AttributeValueEnum
        if isinstance(range_config[0], (int, AttributeValueEnum)):
            if isinstance(range_config[0], int):
                possible_values = range_config
            else:
                # .value accounts for AttributeValueEnum in the range config
                possible_values = [enum.value for enum in range_config]
            return random_choice(
                possible_values,
                size=num_values,
                replace=False,
                generator=self.generator,
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
            generator=self.generator,
        )
