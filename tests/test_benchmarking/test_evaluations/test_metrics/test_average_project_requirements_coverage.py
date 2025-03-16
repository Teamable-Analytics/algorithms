import unittest

from algorithms.dataclasses.enums import RequirementOperator
from algorithms.dataclasses.project import ProjectRequirement
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)


class TestAverageProjectRequirementsCoverage(unittest.TestCase):
    def setUp(self):
        self.teamset_that_all_meets_requirements = TeamSet(
            _id="0",
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
                            _id=1,
                            attributes={
                                0: [1],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.teamset_that_half_meets_requirements = TeamSet(
            _id="1",
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
                            _id=1,
                            attributes={
                                0: [0],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.teamset_that_none_meets_requirements = TeamSet(
            _id="2",
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
                                0: [0],
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
                            _id=1,
                            attributes={
                                0: [0],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.teamset_that_one_person_cover_all_requirements = TeamSet(
            _id="3",
            teams=[
                Team(
                    _id=0,
                    name="Team 0",
                    project_id=1,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=1, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=2, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=3, value=1, operator=RequirementOperator.EXACTLY
                        ),
                    ],
                    students=[
                        Student(
                            _id=0,
                            attributes={
                                0: [1],
                                1: [1],
                                2: [1],
                                3: [1],
                            },
                        ),
                        Student(
                            _id=1,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                    ],
                )
            ],
        )

        self.teamset_that_one_person_cover_half_requirements = TeamSet(
            _id="4",
            teams=[
                Team(
                    _id=0,
                    name="Team 0",
                    project_id=1,
                    requirements=[
                        ProjectRequirement(
                            attribute=0, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=1, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=2, value=1, operator=RequirementOperator.EXACTLY
                        ),
                        ProjectRequirement(
                            attribute=3, value=1, operator=RequirementOperator.EXACTLY
                        ),
                    ],
                    students=[
                        Student(
                            _id=0,
                            attributes={
                                0: [0],
                                1: [1],
                                2: [0],
                                3: [1],
                            },
                        ),
                        Student(
                            _id=1,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                0: [0],
                                1: [0],
                                2: [0],
                                3: [0],
                            },
                        ),
                    ],
                )
            ],
        )

    def test_calculate__should_return_1_when_all_teams_meet_requirements(self):
        metric = AverageProjectRequirementsCoverage()

        actual = metric.calculate(self.teamset_that_all_meets_requirements)

        self.assertEqual(1, actual)

    def test_calculate__should_return_one_half_when_half_of_the_teams_meet_requirements(
        self,
    ):
        metric = AverageProjectRequirementsCoverage()

        actual = metric.calculate(self.teamset_that_half_meets_requirements)

        self.assertEqual(0.5, actual)

    def test_calculate__should_return_0_when_none_of_the_teams_meet_requirements(self):
        metric = AverageProjectRequirementsCoverage()

        actual = metric.calculate(self.teamset_that_none_meets_requirements)

        self.assertEqual(0, actual)

    def test_calculate__should_return_1_when_one_person_cover_all_requirements(self):
        metric = AverageProjectRequirementsCoverage()

        actual = metric.calculate(self.teamset_that_one_person_cover_all_requirements)

        self.assertEqual(1, actual)

    def test_calculate__should_return_one_half_when_one_person_cover_half_requirements(
        self,
    ):
        metric = AverageProjectRequirementsCoverage()

        actual = metric.calculate(self.teamset_that_one_person_cover_half_requirements)

        self.assertEqual(0.5, actual)
