from typing import List

from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet

mock_simulation_result: List[TeamSet] = [
    TeamSet(
        _id=0,
        name="TeamSet0",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=1),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=2),
                    Student(_id=3),
                ],
            ),
        ],
    ),
    TeamSet(
        _id=1,
        name="TeamSet1",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=2),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=1),
                    Student(_id=3),
                ],
            ),
        ],
    ),
]

mock_simulation_result_2: List[TeamSet] = [
    TeamSet(
        _id=0,
        name="TeamSet0",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=3),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=1),
                    Student(_id=2),
                ],
            ),
        ],
    ),
    TeamSet(
        _id=1,
        name="TeamSet1",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=2),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=1),
                    Student(_id=3),
                ],
            ),
        ],
    ),
]

mock_runtimes: List[float] = [
    1.8,
    2.0,
]

mock_runtimes_2: List[float] = [
    1.7,
    2120.6,
]
