import itertools
from typing import List

from api.models.enums import ScenarioAttribute, Gender
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CustomTwelveHundredStudentProvider(StudentProvider):
    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None) -> List[Student]:
        template_students = [
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
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
        for i in range(120):
            student = next(student_cycler)
            if i % 4 == 0:
                team_cnt += 1
            timeslot_list = [j for j in range(team_cnt, team_cnt + 3)]
            students.append(
                Student(
                    _id=student.id * 100 + i,
                    attributes={
                        **student.attributes,
                        ScenarioAttribute.TIMESLOT_AVAILABILITY.value: timeslot_list,
                    },
                )
            )

        return students
