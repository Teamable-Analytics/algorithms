import csv
from enum import Enum
from os import path
from typing import Dict

import numpy as np

from api.models.enums import ScenarioAttribute
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider

ATTRIBUTE_VALUE = 0


class BowensDataProvider(StudentProvider):
    @property
    def num_students(self) -> int:
        return 26

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None):
        students = []

        # Define the path to your CSV file
        csv_file_path = path.join(
            path.dirname(__file__), "P278_2023_Test File for Bowen_16feb24.csv"
        )

        # Open the CSV file for reading
        with open(csv_file_path, "r") as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Iterate over each row in the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue
                sid = row[0]
                zPos = int(float(row[4]))

                # Add the student to the list of students
                students.append(
                    Student(
                        _id=int(sid),
                        attributes={
                            ATTRIBUTE_VALUE: [zPos],
                        },
                    )
                )

        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]


class Attributes(Enum):
    SCORE = 0
    TUTOR_PREFERENCE = 1
    GROUP_SIZE = 2


class BowensDataProvider2(StudentProvider):
    def __init__(self):
        self._sid_map: Dict[int, str] = {}

    @property
    def num_students(self) -> int:
        return 146

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0

    def get(self, seed: int = None):
        students = []

        # Define the path to your CSV file
        csv_file_path = path.join(path.dirname(__file__), "BIOC202W2 deidentified.csv")

        # Open the CSV file for reading
        with open(csv_file_path, "r") as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            count = 0
            # Iterate over each row in the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue
                sid = row[0]
                self._sid_map[i] = sid
                sid = i

                if row[1] == "In-person before or after class":
                    timeslot = 1
                elif row[1] == "In-person nights or weekends":
                    timeslot = 2
                elif row[1] == "On zoom":
                    timeslot = 3
                else:
                    raise ValueError(f"Invalid timeslot: {row[1]}")

                tutor_preference = row[17]
                if (
                    tutor_preference
                    == "I am looking for a classmate to tutor me in BIOC 202"
                ):
                    tutor_preference = 1
                elif (
                    tutor_preference
                    == "I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee"
                ):
                    tutor_preference = 2
                elif (
                    tutor_preference
                    == "I am interested in being a peer tutor in BIOC 202"
                ):
                    tutor_preference = 3
                else:
                    raise ValueError(f"Invalid tutor preference: {tutor_preference}")

                group_size = row[18]
                if group_size == "1":
                    group_size = 1
                elif group_size == "2 to 3":
                    group_size = 2
                elif group_size == "3+":
                    group_size = 3
                else:
                    group_size = -1

                score = float(row[20])
                score = 1 if score >= 0 else 0

                count += 1
                
                # Add the student to the list of students
                students.append(
                    Student(
                        _id=sid,
                        attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [timeslot],
                            Attributes.SCORE.value: [score],
                            Attributes.TUTOR_PREFERENCE.value: [tutor_preference],
                            Attributes.GROUP_SIZE.value: [group_size],
                        },
                    )
                )

        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    def get_student(self, sid: int):
        if len(self._sid_map) == 0:
            self.get()
        return self._sid_map[sid]

if __name__ == "__main__":
    print("test")
    provider = BowensDataProvider2()
    students = provider.get()
    print(students)
