import csv
from enum import Enum
from os import path
from typing import Dict

import numpy as np

# from api.models.student import Student
from api.dataclasses.student import Student
from benchmarking.data.interfaces import StudentProvider
from manual_run.attributes import Attributes
from manual_run.map_columns import MapColumns
from manual_run.variables import Variables


class DataProvider(StudentProvider):
    def __init__(self):
        self._sid_map: Dict[int, str] = {}
        self._num_students = Variables.num_students
        self._max_project_preferences_per_student = 0

    @property
    def num_students(self) -> int:
        return self._num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return self._max_project_preferences_per_student

    def get(self, seed: int = None):
        # Note: The goal of the seed is for when we generate fake students

        students = []
        folder_path = path.join(path.dirname(__file__), "input_csv")
        csv_file_path = path.join(folder_path, Variables.input_csv_file)

        # Open the selected CSV file for reading
        with open(csv_file_path, "r") as file:
            csv_reader = csv.reader(file)
            header_row = []
            for i, row in enumerate(csv_reader):
                if i == 0:  # assuming the first row is the header, skip it
                    header_row = row
                    continue
                # student ID or an identifier such as responseId should be in the first column
                sid = row[0]
                self._sid_map[i] = sid
                sid = i  # possibly look into commenting this out

                processed_data = MapColumns.process_row(row, header_row)
                # Adjust the attributes based on the CSV file
                students.append(
                    Student(
                        _id=sid,
                        attributes={
                            Attributes.TIMESLOT_AVAILABILITY.value: [
                                processed_data["Q8"]
                            ],
                            Attributes.SCORE.value: [processed_data["z-score"]],
                            Attributes.TUTOR_PREFERENCE.value: [processed_data["Q4"]],
                            Attributes.GROUP_SIZE.value: [processed_data["Q5"]],
                        },
                    )
                )

        # Shuffle the list of students based on the seed provided
        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    def get_student(self, sid: int):
        if len(self._sid_map) == 0:
            self.get()
        return self._sid_map[sid]
