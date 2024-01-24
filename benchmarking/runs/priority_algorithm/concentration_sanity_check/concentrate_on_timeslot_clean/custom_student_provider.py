from typing import List

import numpy as np

from api.models.enums import ScenarioAttribute
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CleanTimeslotCustomStudentProvider(StudentProvider):
    def __init__(self):
        self.class_size = 8

    @property
    def num_students(self) -> int:
        return self.class_size

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None) -> List[Student]:
        students = [
            Student(
                _id=1,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 4],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [5, 6, 7, 8],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [5, 7, 8],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [6, 7],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [7],
                },
            ),
        ]

        # Add timeslot values
        rng = np.random.default_rng(seed=seed)
        order = rng.permutation(len(students))
        return [students[_] for _ in order]
