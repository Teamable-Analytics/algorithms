from dataclasses import dataclass, field
from typing import List, Dict

from api.models.enums import Relationship, RequirementOperator
from api.models.project import ProjectRequirement


@dataclass
class Student:
    _id: int
    name: str = None
    attributes: Dict[int, List[int]] = field(default_factory=dict)
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    project_preferences: List[int] = field(default_factory=list)
    team: "Team" = None

    @property
    def id(self) -> int:
        return self._id

    def add_team(self, team: "Team"):
        if self.team:
            raise ValueError(
                f"Cannot add student ({self.id}) to team ({team.name}). Student already has a team ({self.team.name})"
            )
        self.team = team

    def meets_requirement(self, requirement: ProjectRequirement) -> bool:
        is_met = False
        # note that attributes are modelled as lists of integers
        for value in self.attributes.get(requirement.attribute, []):
            if requirement.operator == RequirementOperator.LESS_THAN:
                is_met |= value < requirement.value
            elif requirement.operator == RequirementOperator.MORE_THAN:
                is_met |= value > requirement.value
            else:  # default case is RequirementOperator.EXACTLY
                is_met |= value == requirement.value
        return is_met
