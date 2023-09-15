from dataclasses import dataclass

from models.enums import RequirementOperator


@dataclass
class ProjectRequirement:
    attribute: int
    operator: RequirementOperator
    value: int
