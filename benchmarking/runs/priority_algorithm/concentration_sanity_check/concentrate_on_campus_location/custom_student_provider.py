from typing import List

import numpy as np

from api.models.enums import ScenarioAttribute, CampusLocation
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class CampusCustomStudentProvider(StudentProvider):
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
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Kelowna.value],
                },
            ),
            Student(
                _id=2,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Kelowna.value],
                },
            ),
            Student(
                _id=3,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Kelowna.value],
                },
            ),
            Student(
                _id=4,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Kelowna.value],
                },
            ),
            Student(
                _id=5,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Vancouver.value],
                },
            ),
            Student(
                _id=6,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Vancouver.value],
                },
            ),
            Student(
                _id=7,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Vancouver.value],
                },
            ),
            Student(
                _id=8,
                attributes={
                    ScenarioAttribute.LOCATION.value: [CampusLocation.Vancouver.value],
                },
            ),
        ]

        # Add timeslot values
        rng = np.random.default_rng(seed=seed)
        order = rng.permutation(len(students))
        return [students[_] for _ in order]
