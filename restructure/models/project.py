from dataclasses import dataclass, field
from typing import List

from restructure.models.attribute import AttributeValue
from restructure.models.enums import RequirementType


@dataclass
class ProjectRequirement:
    attribute: int  # todo: Attribute?
    operator: RequirementType
    value: int


@dataclass
class Project:
    _id: int
    name: str = None
    num_teams: int = 1
    requirements: List[ProjectRequirement] = field(default_factory=list)
