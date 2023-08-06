from dataclasses import dataclass, field
from typing import List

from restructure.models.project import Project
from restructure.models.student import Student


@dataclass
class Team:
    _id: int
    name: str = None
    students: List[Student] = field(default_factory=list)
    project: Project = None
