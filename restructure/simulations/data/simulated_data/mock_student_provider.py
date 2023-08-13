import random
from typing import Literal, List, Dict

from restructure.models.enums import Relationship, AttributeValueEnum
from restructure.models.student import Student
from restructure.simulations.data.interfaces import (
    MockStudentProviderSettings,
    StudentProvider,
    AttributeRangeConfig,
)


class MockStudentProvider(StudentProvider):
    def __init__(self, settings: MockStudentProviderSettings):
        self.settings = settings

    def get(self) -> List[Student]:
        return create_mock_students(
            self.settings.number_of_students,
            self.settings.number_of_friends,
            self.settings.number_of_enemies,
            self.settings.friend_distribution,
            self.settings.attribute_ranges,
        )

    @property
    def num_students(self) -> int:
        return self.settings.number_of_students

    @property
    def max_project_preferences_per_student(self) -> int:
        # TODO: handle, probably have a way to define attribute ids that can have multiple
        #   values and check for what the ScenarioAttribute.ProjPref's is
        return 0


def create_mock_students(
    number_of_students: int,
    number_of_friends: int,
    number_of_enemies: int,
    friend_distribution: Literal["cluster", "random"],
    attribute_ranges: Dict[int, AttributeRangeConfig],
) -> List[Student]:
    students = []
    n = number_of_students
    f = number_of_friends
    e = number_of_enemies

    for i in range(n):
        relationships = {}
        for j in range(f):
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

        attributes = {
            attribute_id: attribute_values_from_range(attribute_range_config)
            for attribute_id, attribute_range_config in attribute_ranges.items()
        }

        students.append(
            Student(
                i,
                relationships=relationships,
                attributes=attributes,
            )
        )
    return students


def attribute_values_from_range(range_config: AttributeRangeConfig) -> List[int]:
    # .value accounts for AttributeValueEnum in the range config
    if isinstance(range_config[0], (int, AttributeValueEnum)):
        if isinstance(range_config[0], int):
            # config is a list of possible values
            return [random.choice(range_config)]
        return [random.choice(range_config).value]

    # config is a list of (value, % chance) tuples
    if isinstance(range_config[0][0], int):
        possible_values = [_[0] for _ in range_config]
    else:
        possible_values = [_[0].value for _ in range_config]

    weights = [_[1] for _ in range_config]
    return random.choices(possible_values, weights=weights, k=1)
