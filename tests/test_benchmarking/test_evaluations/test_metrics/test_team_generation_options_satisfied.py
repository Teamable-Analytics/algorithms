import unittest

from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.metrics.team_generation_options_satisfied import TeamGenerationOptionsSatisfied


class TestTeamGenerationOptionsSatisfied(unittest.TestCase):
    def setUp(self):
        self.satisfied_teamset = TeamSet(
            _id=0,
            teams=[
                Team(
                    _id=0,
                    students=[Student(
                        _id=i,
                    ) for i in range(5)]
                )
            ],
        )

        self.missing_student_in_team_teamset = TeamSet(
            _id=1,
            teams=[Team(_id=1, students=[Student(_id=5)])
        ])

        self.have_extra_student_in_team_teamset = TeamSet(
            _id=2,
            teams=[Team(
                _id=2,
                students=[Student(_id=i) for i in range(6, 26)]
            )]
        )

        self.options = TeamGenerationOptions(
            max_team_size=5,
            min_team_size=2,
            total_teams=1,
            initial_teams=[],
        )

    def test_calculate__should_return_1_when_all_teams_are_satisfied(self):
        metric = TeamGenerationOptionsSatisfied(self.options)
        self.assertEqual(metric.calculate(self.satisfied_teamset), 1.0)

    def test_calculate__should_return_0_when_no_teams_are_satisfied_because_of_missing_student(self):
        metric = TeamGenerationOptionsSatisfied(self.options)
        self.assertEqual(metric.calculate(self.missing_student_in_team_teamset), 0.0)

    def test_calculate__should_return_0_when_no_teams_are_satisfied_because_of_extra_student(self):
        metric = TeamGenerationOptionsSatisfied(self.options)
        self.assertEqual(metric.calculate(self.have_extra_student_in_team_teamset), 0.0)
