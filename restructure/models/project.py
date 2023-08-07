from dataclasses import dataclass

from restructure.models.enums import RequirementType


@dataclass
class ProjectRequirement:
    attribute: int
    operator: RequirementType
    value: int
