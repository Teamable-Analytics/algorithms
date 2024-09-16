import csv
import os
from os import path
from typing import Dict, List

import numpy as np

from api.models.student import Student
from benchmarking.data.interfaces import StudentProvider


class DataProvider(StudentProvider):
    def __init__(self, file_name: str):
        self.file_name = file_name
        self._sid_map: Dict[int, str] = {}
    
    def get_csv_data(self, seed: int = None) -> List[Student]:
        """
        Get the data from the CSV file

        Args:
            seed (int, optional): Defaults to None.
            
        Returns:
            List[Student]: List of students
        """
        students = []
        
        folder_path = path.join(
            path.dirname(__file__), "input_csv"
        )

        # List all CSV files in the directory
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        if not csv_files:
            raise FileNotFoundError("No CSV files found in the directory")

        # User selects a file so that they can choose which file to use
        selected_file = input(f"Select a file from {csv_files}: ")
        csv_file_path = path.join(folder_path, selected_file)
        
        select_attributes = input("Select column numbers of the attributes to use separated by a comma: ")
        try:
            select_attributes = [int(attr.strip()) for attr in select_attributes.split(",")]
        except ValueError:
            print("Invalid column number provided. Please enter integers only.")
            return []

        if not select_attributes:
            print("No attributes selected.")
            return []

        # Open the selected CSV file for reading
        with open(csv_file_path, "r") as file:
            csv_reader = csv.reader(file)
            
            # Iterate over each row in the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:  # if the row is the header, skip it
                    continue
                
                sid = row[0]
                self._sid_map[i] = sid
                
                attributes = {}
                
                for attribute_value, col_index in enumerate(select_attributes):
                    if col_index < len(row):  # Ensure the column index is within bounds
                        value = row[col_index]
                        attributes[attribute_value] = [value]
                    else:
                        print(f"Column index {col_index} is out of range for this row.")

                # Add the student to the list of students
                students.append(
                    Student(
                        _id=int(sid),
                        attributes=attributes
                    )
                )
        
        # Shuffle the list of students based on the seed provided        
        order = np.random.default_rng(seed=seed).permutation(len(students))
        return [students[i] for i in order]

    def get_student(self, sid: int):
        if len(self._sid_map) == 0:
            self.get_csv_data()
        return self._sid_map.get(sid, "Student ID not found.")
