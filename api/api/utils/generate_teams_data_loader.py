from typing import Dict, Any, List
from dataclasses import dataclass, field

from api.ai.new.interfaces.algorithm_options import AlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.models.enums import AlgorithmType
from api.models.project import Project
from api.models.student import Student


@dataclass
class GenerateTeamsInputData:
    students: List[Student]
    algorithm_type: AlgorithmType
    algorithmOptions: AlgorithmOptions
    team_generation_options: TeamGenerationOptions
    projects: List[Project] = field(default_factory=list)


class GenerateTeamsDataLoader:
    def __init__(self, validated_data: Dict[str, Any]):
        self.data = validated_data

    def load(self) -> GenerateTeamsInputData:
        pass

    def _get_algorithm_type(self) -> AlgorithmType:
        pass

    def _get_students(self) -> List[Student]:
        pass

    def _get_projects(self) -> List[Project]:
        pass

    def _get_algorithm_options(self) -> AlgorithmOptions:
        pass

    def _get_team_generation_options(self) -> TeamGenerationOptions:
        pass
