import json
import unittest

from api.ai.new.interfaces.algorithm_options import RarestFirstAlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.new.rarest_first_algorithm.rarest_first_algorithm import (
    RarestFirstAlgorithm,
)
from api.models.enums import ScenarioAttribute, RequirementOperator
from api.models.project import ProjectRequirement
from api.models.team import TeamShell
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


class TestRarestFirstAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.algorithm_options = RarestFirstAlgorithmOptions()
        cls.team_generation_options = TeamGenerationOptions(
            max_team_size=5,
            min_team_size=4,
            total_teams=1,
            initial_teams=[
                TeamShell(
                    _id=1,
                    requirements=[
                        ProjectRequirement(
                            attribute=ScenarioAttribute.AGE.value,
                            value=30,
                            operator=RequirementOperator.LESS_THAN,
                        ),
                        ProjectRequirement(
                            attribute=ScenarioAttribute.GPA.value,
                            value=80,
                            operator=RequirementOperator.MORE_THAN,
                        ),
                    ],
                )
            ],
        )

    def test_algorithm__returns_teams_with_enough_coverage(self):
        # The odd of having all 100 students in the provider with age >= 30 and gpa <= 80 is very low
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=100,
                attribute_ranges={
                    ScenarioAttribute.AGE.value: list(range(20, 40)),
                    ScenarioAttribute.GPA.value: list(range(60, 100)),
                },
            )
        )

        algo = RarestFirstAlgorithm(
            algorithm_options=self.algorithm_options,
            team_generation_options=self.team_generation_options,
        )

        result = algo.generate(students.get())

        # Only comparing 2 attributes, so at most there are 2 students, each satisfying one attribute
        self.assertEqual(len(result.teams), 1)
        self.assertGreater(len(result.teams[0].students), 0)
        self.assertLessEqual(len(result.teams[0].students), 2)

        requirement_1 = result.teams[0].requirements[0]
        requirement_2 = result.teams[0].requirements[1]
        student_1 = result.teams[0].students[0]
        student_2 = (
            result.teams[0].students[1] if len(result.teams[0].students) == 2 else None
        )
        if len(result.teams[0].students) == 2:
            self.assertTrue(
                student_1.meets_requirement(requirement_1)
                or student_2.meets_requirement(requirement_1)
            )
            self.assertTrue(
                student_1.meets_requirement(requirement_2)
                or student_2.meets_requirement(requirement_2)
            )
        elif len(result.teams[0].students) == 1:
            self.assertTrue(
                student_1.meets_requirement(requirement_1)
                and student_1.meets_requirement(requirement_2)
            )
        else:
            self.fail(
                "Unexpected number of students in team: "
                + str(len(result.teams[0].students))
            )
