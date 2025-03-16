from dataclasses import dataclass
from typing import Dict, Any, List

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.ai.interfaces.algorithm_options import AlgorithmOptions
from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.dataclasses.enums import AlgorithmType
from algorithms.dataclasses.student import Student, StudentSerializer
from algorithms.dataclasses.team import TeamSerializer


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
        return [StudentSerializer().decode(student) for student in students]

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
                TeamSerializer().decode(team).to_shell()
                for team in team_generation_options.get("initial_teams")
            ],
            max_team_size=team_generation_options.get("max_team_size"),
            min_team_size=team_generation_options.get("min_team_size"),
        )
