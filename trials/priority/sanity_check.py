from sandbox_tools.encoder import DATA_FILE_PATH
from sandbox_tools.logger import Logger
from sandbox_tools.mock_team_generation import mock_generation
from team_generator.algorithm import AlgorithmOptions
from team_generator.algorithm import Priority
from team_generator.algorithm.priority_algorithm.priority_algorithm import PriorityAlgorithm

if __name__ == '__main__':
    logger = Logger(real=True)
    algorithm_options = AlgorithmOptions(
        priorities=[
            {
                'order': 1,
                'constraint': Priority.TYPE_CONCENTRATE,
                'skill_id': 73,  # timeslot availability
                'limit_option': Priority.MAX_OF,
                'limit': 2,
                'value': 3,  # some timeslot
            },
            {
                'order': 2,
                'constraint': Priority.TYPE_DIVERSIFY,
                'skill_id': 81,  # gender
                'limit_option': Priority.MIN_OF,
                'limit': 2,
                'value': 2,  # female
            }
        ],
        diversify_options=[{'id': 81}],
        concentrate_options=[{'id': 73}]
    )
    teams = mock_generation(PriorityAlgorithm, algorithm_options, logger, 56, DATA_FILE_PATH)
    logger.end()
    logger.print_teams(teams, with_relationships=True, only_unmet=True)
