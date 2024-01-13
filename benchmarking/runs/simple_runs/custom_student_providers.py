from enum import Enum
from typing import List

import numpy as np

from api.models.enums import Gender, ScenarioAttribute, Gpa, Age, Race
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class Major(Enum):
    MATH = 1
    COMP_SCI = 2


class CustomTwelveStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = [
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=9,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=10,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=11,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=12,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
        ]

        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    @property
    def num_students(self) -> int:
        return 12

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class CustomFifteenStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = [
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=9,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=10,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=11,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=12,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=13,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=14,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=15,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
        ]

        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    @property
    def num_students(self) -> int:
        return 15

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
