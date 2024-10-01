import csv
from os import path

import numpy as np

from api.dataclasses.student import Student
from benchmarking.data.interfaces import StudentProvider
from manual_run.attributes import Attributes
from manual_run.map_columns import process_row
from manual_run.variables import Variables


class DataProvider(StudentProvider):
    @property
    def num_students(self) -> int:
        return Variables.num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0  # this should always return 0

    def get(self, seed: int = None):
        """Note: The goal of the seed within this function is for when we generate fake students"""

        students = []
        folder_path = path.dirname(__file__)
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

                processed_data = process_row(row, header_row)
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
