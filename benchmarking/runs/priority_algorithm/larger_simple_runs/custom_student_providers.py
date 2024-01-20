from enum import Enum
from typing import List

import numpy as np

from api.models.enums import (
    Gender,
    ScenarioAttribute,
    Gpa,
    Age,
    Race,
    RequirementOperator,
    Relationship,
)
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class Major(Enum):
    MATH = 1
    COMP_SCI = 2


PROGRAMMING_LANGUAGE = 10


class CustomOneHundredAndTwentyStudentWithProjectAttributesProvider(StudentProvider):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30

    def get(self, seed: int = None) -> List[Student]:
        rng = np.random.default_rng(seed=seed)

        student_template = [
            [
                Student(
                    _id=0,
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
            ],
            [
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
            ],
            [
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
            ],
        ]

        students = []
        for i in range(10):
            for pos, ideal_team in enumerate(student_template):
                project_num = i * 3 + pos

                # Shuffle team to make a random member have the project attribute
                order = np.random.default_rng(seed=seed).permutation(len(ideal_team))
                ideal_team: List[Student] = [ideal_team[_] for _ in order]

                for num, student in enumerate(ideal_team):
                    cloned_student = Student(
                        _id=(12 * i + student.id),
                        attributes={
                            **student.attributes,
                        },
                    )
                    if num % 4 == 0:
                        # Give the first member of each ideal team the attribute that satisfies the corresponding project
                        cloned_student.attributes.update(
                            {PROGRAMMING_LANGUAGE: [project_num]}
                        )

                    students.append(cloned_student)

        order = rng.permutation(len(students))
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


class Custom120SocialStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = [
            Student(
                _id=i,
                relationships={i + 1 if i % 2 == 0 else i - 1: Relationship.FRIEND},
            )
            for i in range(120)
        ]
        order = np.random.default_rng(seed=seed).permutation(120)
        real_students_of_ubc = [students[i] for i in order]
        return real_students_of_ubc

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class Custom120SocialAndProjectsStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = Custom120SocialStudentProvider().get()

        # Add project skills
        for student in students:
            if student._id % 4 == 0:
                student.attributes.update({PROGRAMMING_LANGUAGE: [student._id // 4]})

        order = np.random.default_rng(seed=seed).permutation(120)
        real_students_of_ubc = [students[i] for i in order]
        return real_students_of_ubc

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class Custom120SocialAndDiversityStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = []
        # Hi Bowen
        for i in range(120):
            students.append(
                Student(
                    _id=i,
                    relationships={
                        (i + 1 if i % 2 == 0 else i - 1): Relationship.FRIEND,
                    },
                    attributes={
                        ScenarioAttribute.GENDER.value: [
                            Gender.FEMALE.value if i < 6 else Gender.MALE.value
                        ],
                        ScenarioAttribute.AGE.value: [20 if i < 60 else 21],
                    },
                )
            )

        order = np.random.default_rng(seed=seed).permutation(120)
        return [students[i] for i in order]

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class Custom120SocialDiversityAndProjectStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        students = Custom120SocialAndDiversityStudentProvider().get()

        # Add project skills
        for student in students:
            if student._id % 4 == 0:
                student.attributes.update({PROGRAMMING_LANGUAGE: [student._id // 4]})

        order = np.random.default_rng(seed=seed).permutation(120)
        return [students[i] for i in order]

    @property
    def num_students(self) -> int:
        return 120

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
