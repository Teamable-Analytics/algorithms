from random import shuffle
from typing import List

from api.models.enums import Gender, ScenarioAttribute, Gpa, Age
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CustomStudentProvider(StudentProvider):
    """
    This is a custom provider meant for use in a single run.

    Creates a list of 100 students the following attributes in a specific way to guarantee a max score:
        - 20% female, rest male
        - 20% A students, rest B students
        - 20% age 20, rest 21

    Using the following metric, a score of 0.8057142857142858
    ```
    PrioritySatisfaction(
            goals_to_priorities(
                CustomScenario(
                    value_of_female=Gender.FEMALE.value,
                    value_of_gpa=Gpa.A.value,
                    value_of_age=Age._21.value,
                ).goals
            ),
            False,
        )
    ```
    """

    def get(self, seed: int = None) -> List[Student]:
        students = []

        for team_num in range(20):
            for member_num in range(5):
                student_num = team_num * 5 + member_num
                student = Student(
                    _id=student_num,
                    attributes={
                        ScenarioAttribute.GENDER.value: [
                            (
                                Gender.FEMALE.value
                                if member_num < 2
                                else Gender.MALE.value
                            )
                        ],
                        ScenarioAttribute.GPA.value: [
                            (Gpa.A.value if team_num < 5 else Gpa.B.value)
                        ],
                        ScenarioAttribute.AGE.value: [
                            (Age._20.value if team_num % 5 == 0 else Age._21.value)
                        ],
                    },
                )

                students.append(student)

        # Shuffle students
        shuffle(students)
        return students

    @property
    def num_students(self) -> int:
        return 100

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
