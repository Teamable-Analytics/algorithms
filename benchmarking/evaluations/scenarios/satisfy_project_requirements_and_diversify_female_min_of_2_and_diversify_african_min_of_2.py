from typing import List

from api.dataclasses.enums import (
    RequirementsCriteria,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection, Gender, Race,
)
from api.dataclasses.tokenization_constraint import TokenizationConstraint
from benchmarking.evaluations.goals import (
    DiversityGoal,
    ProjectRequirementGoal,
    WeightGoal,
)
from benchmarking.evaluations.interfaces import Scenario, Goal


class SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2(
    Scenario
):
    def __init__(
            self,
            value_of_female: int = Gender.FEMALE.value,
            value_of_african: int = Race.African.value,
    ):
        super().__init__()
        self.value_of_female = value_of_female
        self.value_of_african = value_of_african

    @property
    def name(self) -> str:
        return "Satisfy Project Requirements and Diversify Female Min Of 2 And Diversify African Min Of 2"

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
