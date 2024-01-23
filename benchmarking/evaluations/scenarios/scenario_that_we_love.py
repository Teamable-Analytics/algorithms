from typing import List

from api.models.enums import (
    RequirementsCriteria,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    AttributeValueEnum,
)
from api.models.student import Student
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.data.interfaces import StudentProvider
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.goals import DiversityGoal, ProjectRequirementGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal

from api.models.project import Project, ProjectRequirement
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)


class ScenarioThatWeLove(Scenario):
    def __init__(self, value_of_female: int, value_of_african: int):
        super().__init__()
        self.value_of_female = value_of_female
        self.value_of_african = value_of_african

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.RACE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_african,
                ),
            ),
            WeightGoal(project_requirement_weight=2, diversity_goal_weight=1),
        ]

    @property
    def name(self) -> str:
        return "We love Bowen <3"
