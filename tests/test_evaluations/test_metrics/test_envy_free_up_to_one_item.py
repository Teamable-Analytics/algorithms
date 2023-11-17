import unittest

from api.models.enums import RequirementOperator
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class TestEnvyFreeUpToOneItem(unittest.TestCase):
    def setUp(self):
        # Team 2 envies Team 1, but if Team 1 removes student 0, then Team 2 is no longer envious
        self.ef1_teamset = TeamSet(
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
            name="EF1 Teamset",
        )

        # Team 2 envies Team 1, but removing either student 0 or 1 from Team 1 cannot make Team 2 non-envious
        self.no_ef1_teamset = TeamSet(
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
                                0: [1],
                            },
                        ),
                    ],
                ),
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
            name="EF1 Teamset",
        )

    def test_calculate__should_return_1_when_ef1(self):
        pass
