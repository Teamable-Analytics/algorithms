import csv
import os
from os import path
from typing import Dict, List

import numpy as np

from api.models.enums import ScenarioAttribute
from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider
from benchmarking.runs.csv_weight_run_revised.attributes import Attributes


class DataProvider(StudentProvider):
    def __init__(self, file_name: str):
        self.file_name = file_name
        self._sid_map: Dict[int, str] = {}
        self._num_students = 26  # input the num of students in the CSV file
        self._max_project_preferences_per_student = 0  # input the max num of project preferences per student

    @property
    def num_students(self) -> int:
        return self._num_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return self._max_project_preferences_per_student

    def get_csv_data(self, seed: int = None) -> List[Student]:
        students = []
        folder_path = path.join(path.dirname(__file__), "input_csv")

        # List all CSV files in the directory
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        if not csv_files:
            raise FileNotFoundError("No CSV files found in the directory")

        # User selects a file so that they can choose which file to use
        selected_file = input(f"Select a file from {csv_files}: ")
        csv_file_path = path.join(folder_path, selected_file)

        # Open the selected CSV file for reading
        with open(csv_file_path, "r") as file:
            csv_reader = csv.reader(file)

            # Iterate over each row in the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:  # assuming the first row is the header, skip it
                    continue

                sid = row[0]  # student ID should be in the first column
                self._sid_map[i] = sid

                # Use the Attributes class to process the row
                processed_data = Attributes.process_row(row)

                # Add the student to the list of students
                students.append(
                    Student(
                        _id=sid,
                        attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [processed_data["timeslot"]],
                            Attributes.SCORE.value: [processed_data["score"]],
                            Attributes.TUTOR_PREFERENCE.value: [processed_data["tutor_preference"]],
                            Attributes.GROUP_SIZE.value: [processed_data["group_size"]],
                        },
                    )
                )

        # Shuffle the list of students based on the seed provided
        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    def get_student(self, sid: int):
        if len(self._sid_map) == 0:
            self.get_csv_data()
        return self._sid_map.get(sid, "Student ID not found.")
    
if __name__ == "__main__":
    print("Running data_provider_revised...")
    provider = DataProvider()
    students = provider.get_csv_data()
    print(students)
