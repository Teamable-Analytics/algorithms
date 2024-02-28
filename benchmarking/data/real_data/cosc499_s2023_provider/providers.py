import json
from os import path
from typing import List

import numpy as np

from api.models.student import Student, StudentSerializer
from api.models.team import TeamSerializer, TeamShell
from api.models.team_set import TeamSet
from benchmarking.data.interfaces import (
    StudentProvider,
    TeamConfigurationProvider,
    InitialTeamsProvider,
)


class COSC499S2023InitialTeamConfigurationProvider(TeamConfigurationProvider):
    def get(self) -> TeamSet:
        """
        Returns the teams that were created for the S2023 COSC499 class
        """
        with open(
            path.join(path.dirname(__file__), "COSC499_S2023_data.json"), "r"
        ) as f:
            json_data = json.load(f)
            teams = [TeamSerializer().decode(team) for team in json_data["teams"]]
        return TeamSet(teams=teams)


class COSC499S2023InitialTeamsProvider(InitialTeamsProvider):
    def get(self) -> List[TeamShell]:
        return [
            t.to_shell()
            for t in COSC499S2023InitialTeamConfigurationProvider().get().teams
        ]


class COSC499S2023StudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        """
        Returns a list of the students in COSC 499 in the S2023 semester.
        Includes their friend/enemy relationships, gender (1), timeslot availability (7), year level (6), and intended effort level (100).

        Seed shuffles student order.
        """
        with open(
            path.join(path.dirname(__file__), "COSC499_S2023_data.json"), "r"
        ) as f:
            json_data = json.load(f)
            students: List[Student] = [
                StudentSerializer().decode(student) for student in json_data["students"]
            ]

            """
            Unnecessarily complicated to shuffle since shuffle() requires
            a MutableSequence, which it doesn't seem like it recognizes
            a regular List[Student] as MutableSequence.
            """
            order = np.random.default_rng(seed=seed).permutation(len(students))
            return [students[i] for i in order]

    @property
    def num_students(self) -> int:
        return 41

    @property
    def max_project_preferences_per_student(self) -> int:
        return 3
