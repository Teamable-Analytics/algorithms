from os import path
from typing import List

import numpy as np

from api.models.student import Student, StudentSerializer
from api.models.team import Team, TeamSerializer
from benchmarking.data.interfaces import (
    StudentProvider,
    InitialTeamsProvider,
)
import json


class COSC341W2021T2InitialTeamsProvider(InitialTeamsProvider):
    def get(self) -> List[Team]:
        """
        Returns the teams that were created for the W2021T2 COSC341 class
        """
        with open(
            path.join(path.dirname(__file__), "COSC341_W2021T2_data.json"), "r"
        ) as f:
            json_data = json.load(f)
            return [TeamSerializer().decode(team) for team in json_data["teams"]]


class COSC341W2021T2StudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        """
        Returns a list of the students in COSC 341/51 in the W2021T2 semester.
        Includes their friend/enemy relationships, gender, timeslot availability, year level, and intended effort level.

        Seed shuffles student order.
        """
        with open(
            path.join(path.dirname(__file__), "COSC341_W2021T2_data.json"), "r"
        ) as f:
            json_data = json.load(f)
            students: List[Student] = [
                StudentSerializer().decode(student) for student in json_data["students"]
            ]
            if seed:
                """
                Unnecessarily complicated to shuffle since shuffle() requires
                a MutableSequence, which it doesn't seem like it recognizes
                a regular List[Student] as MutableSequence.
                """
                order = np.random.default_rng(seed=seed).permutation(len(students))
                return [students[i] for i in order]
            else:
                return students

    @property
    def num_students(self) -> int:
        return 215

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
