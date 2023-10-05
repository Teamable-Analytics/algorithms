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


@dataclass
class MockStudentProviderSettings:
    number_of_students: int
    attribute_ranges: Dict[int, AttributeRangeConfig] = field(default_factory=dict)
    num_values_per_attribute: Dict[int, NumValuesConfig] = field(default_factory=dict)
    number_of_friends: int = 0
    number_of_enemies: int = 0
    friend_distribution: Literal["cluster", "random"] = "random"


class MockStudentProvider(StudentProvider):
    def __init__(self, settings: MockStudentProviderSettings):
        self.settings = settings

    def get(self) -> List[Student]:
        mock_students = create_mock_students(
            self.settings.number_of_students,
            self.settings.number_of_friends,
            self.settings.number_of_enemies,
            self.settings.friend_distribution,
            self.settings.attribute_ranges,
            self.settings.num_values_per_attribute,
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
        num_values_config: NumValuesConfig = self.settings.num_values_per_attribute.get(
            ScenarioAttribute.PROJECT_PREFERENCES.value,
            None,
        )

        if isinstance(num_values_config, int):
            return num_values_config

        if isinstance(num_values_config, tuple):
            return num_values_config[1]

        return 0


def create_mock_students(
    number_of_students: int,
    number_of_friends: int,
    number_of_enemies: int,
    friend_distribution: Literal["cluster", "random"],
    attribute_ranges: Dict[int, AttributeRangeConfig],
    num_values_per_attribute: Dict[int, NumValuesConfig],
) -> List[Student]:
    students = []
    n = number_of_students
    f = number_of_friends
    e = number_of_enemies

    for i in range(n):
        relationships = {}
        for j in range(f):
            # todo: (document) this doesn't guarantee the friend/enemy count, just sets the max
            if friend_distribution == "cluster":
                friend_id = (i // f * f + j) % n
            else:
                friend_id = random.randrange(0, n)
            if friend_id == i:
                continue
            relationships[friend_id] = Relationship.FRIEND
        for j in range(e):
            enemy_id = random.randrange(0, n)
            relationships[enemy_id] = Relationship.ENEMY

        attributes = {}
        for attribute_id, attribute_range_config in attribute_ranges.items():
            num_value_config = num_values_per_attribute.get(attribute_id, None)
            num_values = (
                num_values_for_attribute(num_value_config) if num_value_config else None
            )
            attributes[attribute_id] = attribute_values_from_range(
                attribute_range_config, num_values
            )

        students.append(
            Student(
                i,
                relationships=relationships,
                attributes=attributes,
            )
        )
    return students


def num_values_for_attribute(num_values_config: NumValuesConfig) -> int:
    if isinstance(num_values_config, int):
        return num_values_config

    min_choices, max_choices = num_values_config
    return random.randrange(min_choices, max_choices)


def random_choice(
    possible_values: List, size=None, replace=False, weights=None
) -> List[int]:
    """
    Uses np.random.choice() but always returns a list of int
    (np.random.choice return numpy.int64 if size=1 and ndarray otherwise)
    """
    size = size or 1
    values = np.random.choice(possible_values, size=size, replace=replace, p=weights)
    if size == 1:
        return [int(values)]
    return [int(val) for val in values]


def attribute_values_from_range(
    range_config: AttributeRangeConfig, num_values: Optional[int] = 1
) -> List[int]:
    if isinstance(range_config[0], (int, AttributeValueEnum)):
        if isinstance(range_config[0], int):
            possible_values = range_config
        else:
            # .value accounts for AttributeValueEnum in the range config
            possible_values = [enum.value for enum in range_config]
        return random_choice(possible_values, size=num_values, replace=False)

    # config is a list of (value, % chance) tuples
    if isinstance(range_config[0][0], int):
        possible_values = [_[0] for _ in range_config]
    else:
        possible_values = [_[0].value for _ in range_config]

    weights = [_[1] for _ in range_config]
    return random_choice(
        possible_values, weights=weights, size=num_values, replace=False
    )
