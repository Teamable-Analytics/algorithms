from enum import Enum
from typing import List

from api.models.project import Project
from api.models.project import ProjectRequirement
import random
import itertools

import numpy as np

from api.models.enums import (
    Gender,
    ScenarioAttribute,
    Gpa,
    Age,
    Race,
    RequirementOperator,
)
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class Major(Enum):
    MATH = 1
    COMP_SCI = 2


class CustomOneHundredAndTwentyStudentWithProjectAttributesProvider(StudentProvider):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30

    def get(self, seed: int = None) -> List[Student]:
        student_template = [
            Student(
                _id=12,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=9,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
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
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=11,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
        ]

        students = []
        gpas = [Gpa.A.value, Gpa.B.value, Gpa.C.value]
        for i in range(1, 11):
            for pos, student in enumerate(student_template):
                cloned_student = Student(
                    _id=(12 * i + student.id),
                    attributes={
                        **student.attributes,
                        ScenarioAttribute.GPA.value: [
                            gpas[pos // 4] if pos % 4 == 0 else Gpa.D.value
                        ],
                    },
                )
                students.append(cloned_student)

        all_projects = [
            Project(
                _id=-1,
                name="Project 1",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.A.value,
                    ),
                ],
            ),
            Project(
                _id=-2,
                name="Project 2",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.B.value,
                    ),
                ],
            ),
            Project(
                _id=-3,
                name="Project 3",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.C.value,
                    )
                ],
            ),
        ]
        random.shuffle(all_projects)
        projects = []
        for idx, proj in enumerate(itertools.cycle(all_projects)):
            projects.append(
                Project(
                    _id=idx,
                    name=f"{proj.name} - {idx}",
                    requirements=proj.requirements,
                )
            )

            if len(projects) == self.NUMBER_OF_TEAMS:
                break

        order = np.random.default_rng(seed=seed).permutation(len(students))
        the_real_student_list = [students[i] for i in order]
        return the_real_student_list

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class CustomOneHundredAndTwentyStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        student_template = [
            Student(
                _id=12,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.B.value],
                    ScenarioAttribute.AGE.value: [20],
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
            Student(
                _id=9,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
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
                    ScenarioAttribute.MAJOR.value: [Major.MATH.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Student(
                _id=11,
                attributes={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.GPA.value: [Gpa.A.value],
                    ScenarioAttribute.AGE.value: [21],
                    ScenarioAttribute.MAJOR.value: [Major.COMP_SCI.value],
                    ScenarioAttribute.RACE.value: [Race.European.value],
                },
            ),
        ]

        students = [
            Student(_id=(12 * i + student.id), attributes=student.attributes)
            for student in student_template
            for i in range(1, 11)
        ]

        order = np.random.default_rng(seed=seed).permutation(len(students))
        the_real_student_list = [students[i] for i in order]
        return the_real_student_list

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
