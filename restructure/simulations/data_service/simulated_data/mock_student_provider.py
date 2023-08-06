import random
from typing import Literal, Tuple, List, Dict, Union

from restructure.models.enums import ScenarioAttribute
from restructure.models.student import Student
from restructure.simulations.data_service.interfaces import (
    MockStudentProviderSettings,
    StudentProvider,
)


class MockStudentProvider(StudentProvider):
    def __init__(self, settings: MockStudentProviderSettings):
        pass

    def get(self) -> List[Student]:
        pass

    @property
    def max_project_preferences_per_student(self) -> int:
        return 1


def fake_students(
    number_of_students: int,
    number_of_friends: int,
    number_of_enemies: int,
    friend_distribution: Literal["cluster", "random"],
    attribute_ranges: Dict[int, Union[List[int], List[Tuple[int, float]]]],
    number_of_project_req,  # todo: need a way to handle this case
) -> []:
    """
    Handling project requirements being met and whatnot
    I need a way to give students the correct attributes to match project

    """
    pass


def test():
    fake_students(
        number_of_students=100,
        number_of_friends=3,
        number_of_enemies=5,
        friend_distribution="clui",
        attribute_ranges={
            ScenarioAttribute.GENDER: [(1, 0.3), (2, 0.5)],
            ScenarioAttribute.AGE: list(range(18, 25)),
        },
    )


# def fake_students_old(
#     number_of_students: int,
#     number_of_females: int,
#     number_of_friends: int,
#     number_of_enemies: int,
#     friend_distribution: Literal["cluster", "random"],
#     age_range: Tuple[int, int],
#     gpa,
#     race,
#     major,
#     year,
#     time,
#     number_of_project_req,
# ) -> [Student]:
#     students = []
#     n = number_of_students
#     f = number_of_friends
#     e = number_of_enemies
#
#     genders = [1] * number_of_females + [2] * (n - number_of_females)
#
#     for i in range(n):
#         relationships = {}
#         for j in range(f):
#             if friend_distribution == "cluster":
#                 friend_id = (i // f * f + j) % n
#             else:
#                 friend_id = random.randrange(0, n)
#             if friend_id == i:
#                 continue
#             relationships[friend_id] = FRIEND
#         for j in range(e):
#             enemy_id = random.randrange(0, n)
#             relationships[enemy_id] = ENEMY
#
#         skills = {
#             0: [random.randrange(age_range[0], age_range[1])],
#             1: [genders[i]],
#             2: [random.randrange(gpa[0], gpa[1])],
#             3: [race[random.randrange(0, len(race))]],
#             4: [major[random.randrange(0, len(major))]],
#             5: [year[random.randrange(0, len(year))]],
#             6: [time[random.randrange(0, len(time))]],
#         }
#
#         for j in range(number_of_project_req):
#             skills[j + 10] = [random.randint(0, 2) // 2]
#
#         students.append(
#             Student(
#                 i,
#                 relationships=relationships,
#                 skills=skills,
#             )
#         )
#     return students
