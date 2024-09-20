import csv
import os
from enum import Enum
from os import path
from typing import Dict, List

import numpy as np

from api.models.enums import ScenarioAttribute
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider
from benchmarking.runs.csv_weight_run_revised.attributes import Attributes


class DataProvider(StudentProvider):
    def __init__(self):
        self._sid_map: Dict[int, str] = {}
        self._num_students = 26  # input the num of students in the CSV file
        self._max_project_preferences_per_student = (
            0  # input the max num of project preferences per student
        )

    @property
    def num_students(self) -> int:
        return self._num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return self._max_project_preferences_per_student

    def get(self, seed: int = None):
        """
        This function reads the CSV file and returns a list of students

        Args:
            seed: int, seed for the random number generator

        Returns:
            List[Student]: list of students
        """
        students = []
        folder_path = path.join(path.dirname(__file__), "input_csv")
        csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the directory")

        selected_file = csv_files[0]  # adjust to choose which file to use
        csv_file_path = path.join(folder_path, selected_file)

        # Open the selected CSV file for reading
        with open(csv_file_path, "r") as file:
            csv_reader = csv.reader(file)

            for i, row in enumerate(csv_reader):
                if i == 0:  # assuming the first row is the header, skip it
                    continue
                sid = row[
                    0
                ]  # student ID or an identifier such as responseId should be in the first column
                self._sid_map[i] = sid
                sid = i

                processed_data = Attributes.process_row(row)

                # Ajdust the attributes based on the CSV file
                students.append(
                    Student(
                        _id=sid,
                        attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [
                                processed_data["time_slot"]
                            ],
                            Attributes.SCORE.value: [processed_data["score"]],
                            Attributes.TUTOR_PREFERENCE.value: [
                                processed_data["tutor_preference"]
                            ],
                            Attributes.GROUP_SIZE.value: [processed_data["group_size"]],
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
