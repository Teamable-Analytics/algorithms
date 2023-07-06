import pickle
import time
from math import floor

from sandbox_tools.encoder import DATA_FILE_PATH
from sandbox_tools.logger import Logger
from sandbox_tools.mock_team_generation import mock_generation
from team_generator.algorithm import AlgorithmOptions
from team_generator.algorithm import SocialAlgorithm

if __name__ == '__main__':
    logger = Logger(real=True)
    teams = mock_generation(SocialAlgorithm, AlgorithmOptions(), logger, 55, DATA_FILE_PATH)
    logger.end()
    logger.print_teams(teams, with_relationships=True, only_unmet=True)

    timestamp = floor(time.time())
    with open(f'algorithm_sandbox/logs/log_{timestamp}.pkl', 'wb') as f:
        pickle.dump(logger, f)
    a = 1
