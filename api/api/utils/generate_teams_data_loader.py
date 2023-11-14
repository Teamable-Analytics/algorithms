from typing import Dict, Any, List
from dataclasses import dataclass

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.interfaces import AlgorithmOptions
from api.ai.interfaces import TeamGenerationOptions
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.api.utils.relationship import get_relationship
from api.models.team import TeamShell


@dataclass
class GenerateTeamsInputData:
    students: List[Student]
    algorithm_type: AlgorithmType
    algorithm_options: AlgorithmOptions
    team_generation_options: TeamGenerationOptions


class GenerateTeamsDataLoader:
    def __init__(self, validated_data: Dict[str, Any]):
        self.data = validated_data

    def load(self) -> GenerateTeamsInputData:
        return GenerateTeamsInputData(
            students=self._get_students(),
            team_generation_options=self._get_team_generation_options(),
            algorithm_type=self._get_algorithm_type(),
            algorithm_options=self._get_algorithm_options(),
        )

    def _get_algorithm_type(self) -> AlgorithmType:
        algorithm_options = self.data.get("algorithm_options")
        algorithm_type = algorithm_options.get("algorithm_type")
        return AlgorithmType(algorithm_type)

    def _get_students(self) -> List[Student]:
        students = self.data.get("students")
        return [
            Student(
                _id=int(student.get("id")),
                name=student.get("name"),
                relationships={
                    int(student_id): get_relationship(relationship)
                    for student_id, relationship in student.get("relationships").items()
                },
                attributes=student.get("attributes"),
                project_preferences=student.get("project_preferences"),
            )
            for student in students
        ]

    def _get_algorithm_options(self) -> AlgorithmOptions:
        algorithm_options = {**self.data.get("algorithm_options")}
        algorithm_type = AlgorithmType(algorithm_options.pop("algorithm_type"))
        algorithm_option_class = AlgorithmRunner.get_algorithm_option_class(
            algorithm_type
        )

        return algorithm_option_class.parse_json(algorithm_options)

    def _get_team_generation_options(self) -> TeamGenerationOptions:
        team_generation_options = self.data.get("team_generation_options")

        return TeamGenerationOptions(
            total_teams=team_generation_options.get("total_teams"),
            initial_teams=[
                TeamShell(
                    _id=int(team.get("id")),
                    name=team.get("name"),
                    project_id=int(team.get("project_id")),
                    requirements=team.get("requirements", []),
                )
                for team in team_generation_options.get("initial_teams")
            ],
            max_team_size=team_generation_options.get("max_team_size"),
            min_team_size=team_generation_options.get("min_team_size"),
        )
