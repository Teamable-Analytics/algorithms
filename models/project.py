from dataclasses import dataclass

from models.enums import RequirementType


@dataclass
class ProjectRequirement:
    attribute: int
    operator: RequirementType
    value: int
