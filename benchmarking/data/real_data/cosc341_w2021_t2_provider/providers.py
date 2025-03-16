import json
from os import path
from typing import List

import numpy as np

from benchmarking.evaluations.enums import ScenarioAttribute
from api.dataclasses.student import Student, StudentSerializer
from api.dataclasses.team import TeamSerializer, TeamShell
from api.dataclasses.team_set import TeamSet
from benchmarking.data.interfaces import (
    StudentProvider,
    TeamConfigurationProvider,
    InitialTeamsProvider,
)


class COSC341W2021T2TeamConfigurationProvider(TeamConfigurationProvider):
    def get(self) -> TeamSet:
        """
        Returns the teams that were created for the W2021T2 COSC341 class
        """
        with open(
            path.join(path.dirname(__file__), "COSC341_W2021T2_data.json"), "r"
        ) as f:
            json_data = json.load(f)
            teams = [TeamSerializer().decode(team) for team in json_data["teams"]]
            return TeamSet(teams=teams)


class COSC341W2021T2InitialTeamsProvider(InitialTeamsProvider):
    def get(self) -> List[TeamShell]:
        return [
            t.to_shell() for t in COSC341W2021T2TeamConfigurationProvider().get().teams
        ]


class COSC341W2021T2StudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        """
        Returns a list of the students in COSC 341/51 in the W2021T2 semester.
        Includes their friend/enemy relationships, gender (1), timeslot availability (7), year level (6), and intended effort level (100).

        Seed shuffles student order.
        """
        with open(
            path.join(path.dirname(__file__), "COSC341_W2021T2_data.json"), "r"
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
        return 215

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


class COSC341W2021T2AnsweredSurveysStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        # As the question about what class you were in was mandatory, any student who had -1 set as their value did not answer the survey.
        return [
            student
            for student in COSC341W2021T2StudentProvider().get(seed=seed)
            if -1 not in student.attributes[ScenarioAttribute.YEAR_LEVEL.value]
        ]

    @property
    def num_students(self) -> int:
        return 175

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0
