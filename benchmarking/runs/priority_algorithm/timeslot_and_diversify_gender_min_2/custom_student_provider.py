import itertools
import random
import uuid
from typing import List

from api.models.enums import ScenarioAttribute, Gender, Race
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CustomStudentProvider(StudentProvider):
    def __init__(self, num_students: int = 120):
        self._num_students = num_students


    @property
    def num_students(self) -> int:
        return self._num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None) -> List[Student]:
        template_students = [
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.YEAR_LEVEL.value: [3],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                },
            ),
            Student(
                _id=9,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=10,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                },
            ),
            Student(
                _id=11,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                },
            ),
            Student(
                _id=12,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                },
            ),
        ]

        student_cycler = itertools.cycle(template_students)
        students = []
        team_cnt = 0
        for i in range(self.num_students):
            student = next(student_cycler)
            if i % 8 == 0:
                team_cnt += 1
            timeslot_list = [j for j in range(team_cnt, team_cnt + 3)]
            students.append(
                Student(
                    _id=i,
                    attributes={
                        **student.attributes,
                        ScenarioAttribute.TIMESLOT_AVAILABILITY.value: timeslot_list,
                        ScenarioAttribute.YEAR_LEVEL.value: [3],
                        ScenarioAttribute.RACE.value: [Race.Other.value],
                    },
                )
            )
        random.shuffle(students)

        return students
