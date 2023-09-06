from dataclasses import dataclass, field
from typing import List

from models.project import ProjectRequirement
from models.student import Student


@dataclass
class Team:
    _id: str
    name: str = None
    project_id: int = None
    students: List[Student] = field(default_factory=list)
    requirements: List[ProjectRequirement] = field(default_factory=list)

    @property
    def id(self) -> int:
        return self._id
