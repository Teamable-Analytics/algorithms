from os import path

import csv

import numpy as np

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
        csv_file_path = path.join(path.dirname(__file__), 'P278_2023_Test File for Bowen_16feb24.csv')

        # Open the CSV file for reading
        with open(csv_file_path, 'r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Iterate over each row in the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue
                sid = row[0]
                zPos = int(float(row[4]))

                # Add the student to the list of students
                students.append(Student(
                    _id=int(sid),
                    attributes={
                        ATTRIBUTE_VALUE: [zPos],
                    },
                ))

        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]
