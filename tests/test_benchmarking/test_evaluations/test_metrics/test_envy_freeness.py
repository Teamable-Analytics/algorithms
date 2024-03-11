import unittest
from typing import Callable, List

from api.dataclasses.enums import RequirementOperator
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell
from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.metrics.envy_freeness import EnvyFreeness


class TestEnvyFreenessUpToOneItem(unittest.TestCase):
    def setUp(self):
        # Team_1 and Team_2 are both envy free because the members in the teams are the same
        self.ef_teamset = TeamSet(
            _id=0,
            teams=[
                Team(
                    _id=0,
                    name="Team 0",
                    project_id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        )
                    ],
                    students=[
                        Student(
                            _id=0,
                            attributes={
                                0: [1],
                            },
                        ),
                        Student(
                            _id=1,
                            attributes={
                                0: [2],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=1,
                    name="Team 1",
                    project_id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        )
                    ],
                    students=[
                        Student(
                            _id=2,
                            attributes={
                                0: [1],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                0: [2],
                            },
                        ),
                    ],
                ),
            ],
            name="Envyfree Teamset",
        )

        # Team 2 envies team 1 because team 1 has a student with attribute 1, which satisfies the requirement
        # while team 2 does not have any students that satisfy the requirement
        self.no_ef_teamset = TeamSet(
            _id=0,
            teams=[
                Team(
                    _id=0,
                    name="Team 0",
                    project_id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        )
                    ],
                    students=[
                        Student(
                            _id=0,
                            attributes={
                                0: [1],
                            },
                        ),
                        Student(
                            _id=1,
                            attributes={
                                0: [2],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=1,
                    name="Team 1",
                    project_id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        )
                    ],
                    students=[
                        Student(
                            _id=2,
                            attributes={
                                0: [2],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                0: [2],
                            },
                        ),
                    ],
                ),
            ],
            name="Envious Teamset",
        )

        self.additive_utility_function = lambda students, team: sum(
            [
                sum(
                    [
                        student.meets_requirement(requirement)
                        for requirement in team.requirements
                    ]
                )
                for student in students
            ]
        )

    def test_calculate__should_return_1_when_no_team_envy(self):
        metric = EnvyFreeness(self.additive_utility_function)
        self.assertEqual(1, metric.calculate(self.ef_teamset))

    def test_calculate__should_return_0_when_there_is_envious_team(self):
        metric = EnvyFreeness(self.additive_utility_function)
        self.assertEqual(0, metric.calculate(self.no_ef_teamset))

    def test_is_envy__should_return_true_when_utility_of_team_1_less_than_team_2(self):
        team_1 = Team(_id=0)
        team_2 = Team(_id=1)
        utility_function = lambda students, team: 0 if team._id == 0 else 1

        metric = EnvyFreeness(utility_function)
        self.assertTrue(metric._is_envy(team_1, team_2))

    def test_is_envy__should_return_false_when_utility_of_team_1_greater_than_team_2(
        self,
    ):
        team_1 = Team(_id=0)
        team_2 = Team(_id=1)
        utility_function = lambda students, team: 0 if team._id == 1 else 1

        metric = EnvyFreeness(utility_function)
        self.assertFalse(metric._is_envy(team_1, team_2))

    def test_is_envy__should_return_false_when_utility_of_team_1_equal_team_2(self):
        team_1 = Team(_id=0)
        team_2 = Team(_id=1)
        utility_function = lambda students, team: 0 if team._id == 1 else 0

        metric = EnvyFreeness(utility_function)
        self.assertFalse(metric._is_envy(team_1, team_2))
