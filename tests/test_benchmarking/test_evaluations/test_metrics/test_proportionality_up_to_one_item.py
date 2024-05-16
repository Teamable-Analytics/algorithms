import unittest

from api.dataclasses.enums import RequirementOperator
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.metrics.proportionality_up_to_one_item import (
    ProportionalityUpToOneItem,
)


class TestProportionalityUpToOneItem(unittest.TestCase):
    def setUp(self):
        self.additive_utility_function = lambda students, team: sum(
            [
                sum(
                    [
                        requirement.met_by_student(student)
                        for requirement in team.requirements
                    ]
                )
                for student in students
            ]
        )

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

        # Team 0 has more students that satisfy than the requirements than Team 1
        self.prop1_teamset = TeamSet(
            _id=1,
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

        # Even when remove 1 student from Team 0, it is still not proportional
        self.not_prop1_teamset = TeamSet(
            _id=2,
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
                        Student(
                            _id=2,
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
                            _id=3,
                            attributes={
                                0: [2],
                            },
                        ),
                        Student(
                            _id=4,
                            attributes={
                                0: [2],
                            },
                        ),
                        Student(
                            _id=5,
                            attributes={
                                0: [2],
                            },
                        ),
                    ],
                ),
            ],
        )

    def test_calculate__should_return_1_when_prop(self):
        metric = ProportionalityUpToOneItem(self.additive_utility_function)
        self.assertEqual(1, metric.calculate(self.prop_teamset))

    def test_calculate__should_return_1_when_prop1(self):
        metric = ProportionalityUpToOneItem(self.additive_utility_function)
        self.assertEqual(1, metric.calculate(self.prop1_teamset))

    def test_calculate__should_return_0_when_not_prop1(self):
        metric = ProportionalityUpToOneItem(self.additive_utility_function)
        self.assertEqual(0, metric.calculate(self.not_prop1_teamset))

    def test_is_proportional__should_return_true_when_all_teams_are_proportional(self):
        metric = ProportionalityUpToOneItem(self.additive_utility_function)
        all_students = [
            student for team in self.prop_teamset.teams for student in team.students
        ]
        self.assertTrue(metric._is_proportional(self.prop_teamset, all_students))

    def test_is_team_proportional__should_return_true_when_team_is_proportional(self):
        metric = ProportionalityUpToOneItem(self.additive_utility_function)
        all_students = [
            student for team in self.prop_teamset.teams for student in team.students
        ]
        self.assertTrue(
            metric._is_team_proportional(
                self.prop_teamset.teams[0], all_students, self.prop_teamset.num_teams
            )
        )
