from api.ai.algorithm_runner import AlgorithmRunner
from api.models.team_set import TeamSet
from api.api.utils.generate_teams_data_loader import GenerateTeamsInputData


def generate_teams(input_data: GenerateTeamsInputData) -> TeamSet:
    algorithm = AlgorithmRunner(
        algorithm_type=input_data.algorithm_type,
        team_generation_options=input_data.team_generation_options,
        algorithm_options=input_data.algorithm_options,
        algorithm_config=None,
    )

    return algorithm.generate(input_data.students)
