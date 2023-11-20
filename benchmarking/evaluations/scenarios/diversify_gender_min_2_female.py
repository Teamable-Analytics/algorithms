from typing import List

from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
)
from api.models.project import Project
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal, ProjectsGoal
from api.models.tokenization_constraint import TokenizationConstraint


class DiversifyGenderMin2Female(Scenario):
    def __init__(self, value_of_female: int, projects: List[Project] = None):
        self.value_of_female = value_of_female
        self.projects = projects

    @property
    def name(self):
        return "Diversify on gender with a minimum of 2 female"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
            ProjectsGoal(projects=self.projects),
        ]
