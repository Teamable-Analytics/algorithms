from typing import List

import numpy as np

from api.dataclasses.enums import ScenarioAttribute, Gender, Race
from api.dataclasses.student import Student
from benchmarking.data.interfaces import StudentProvider
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


class TimeslotCustomStudentProvider(StudentProvider):
    def __init__(
        self,
        class_size: int,
        ratio_of_female_students: float = 0.2,
        ratio_of_african_students: float = 0.15,
    ):
        self.class_size = class_size
        self.ratio_of_female_students = ratio_of_female_students
        self.ratio_of_african_students = ratio_of_african_students

    @property
    def num_students(self) -> int:
        return self.class_size

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None) -> List[Student]:
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=self.class_size,
                attribute_ranges={
                    ScenarioAttribute.GENDER.value: [
                        (Gender.FEMALE, self.ratio_of_female_students),
                        (Gender.MALE, 1 - self.ratio_of_female_students),
                    ],
                    ScenarioAttribute.YEAR_LEVEL.value: [
                        (0, 0.3),
                        (1, 0.25),
                        (2, 0.2),
                        (3, 0.2),
                        (4, 0.05),
                    ],
                    ScenarioAttribute.RACE.value: [
                        (Race.African, self.ratio_of_african_students),
                        (Race.European, 1 - self.ratio_of_african_students),
                    ],
                },
            )
        ).get()

        # Add timeslot values
        rng = np.random.default_rng(seed=seed)
        for student in students:
            num_time_slots = int(rng.random() * 3) + 3 # 3-5 timeslots
            timeslots = rng.choice(range(10), num_time_slots, replace=False)
            student.attributes[
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value
            ] = timeslots.tolist()

        order = rng.permutation(len(students))
        return [students[_] for _ in order]