from dataclasses import dataclass, field
from typing import List

from models.enums import RequirementOperator


@dataclass
class ProjectRequirement:
    attribute: int
    operator: RequirementOperator
    value: int


@dataclass
class Project:
    _id: int
    name: str = None
    # if multiple teams can work on this project. specified here
    number_of_teams: int = 1
    requirements: List[ProjectRequirement] = field(default_factory=list)

    @property
    def id(self) -> int:
        return self._id
