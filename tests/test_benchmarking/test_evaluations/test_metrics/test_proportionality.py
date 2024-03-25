import unittest

from api.dataclasses.enums import RequirementOperator
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.metrics.proportionality import Proportionality


class TestProportionality(unittest.TestCase):
    def setUp(self):
        # This teamset is proportional because each team has 2 students that meet the requirements,
        # so the utility of each team is the same, and proportional to the class utility
        self.prop_teamset = TeamSet(
            _id=0,
            teams=[
                Team(
                    _id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0,
                            value=1,
                            operator=RequirementOperator.EXACTLY,
                        ),
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
                                0: [1],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=1,
                    requirements=[
                        ProjectRequirement(
                            attribute=0,
                            value=1,
                            operator=RequirementOperator.EXACTLY,
                        ),
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
                                0: [1],
                            },
                        ),
                    ],
                ),
            ],
        )

        # This teamset is not proportional because Team 0 has 2 students that meet the requirements while Team 1 has
        # only 1 student that meets the requirements, therefore the utility of Team 1 is not proportional to the class
        # utility
        self.non_prop_teamset = TeamSet(
            _id=0,
            teams=[
                Team(
                    _id=0,
                    requirements=[
                        ProjectRequirement(
                            attribute=0,
                            value=1,
                            operator=RequirementOperator.EXACTLY,
                        ),
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
                                0: [1],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=1,
                    requirements=[
                        ProjectRequirement(
                            attribute=0,
                            value=1,
                            operator=RequirementOperator.EXACTLY,
                        ),
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

    def test_calculate__should_return_1_when_there_is_only_one_team(self):
        # Because the team is always proportional to itself
        single_team_teamset = TeamSet(_id=0, teams=[Team(_id=0)])
        metric = Proportionality(self.additive_utility_function)
        self.assertEqual(metric.calculate(single_team_teamset), 1.0)

    def test_calculate__should_return_1_if_all_teams_are_proportional(self):
        metric = Proportionality(self.additive_utility_function)
        self.assertEqual(metric.calculate(self.prop_teamset), 1.0)

    def test_calculate__should_return_0_if_any_team_is_not_proportional(self):
        metric = Proportionality(self.additive_utility_function)
        self.assertEqual(metric.calculate(self.non_prop_teamset), 0.0)
