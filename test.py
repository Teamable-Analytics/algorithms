import pickle
import time
from math import floor

from algorithm_sandbox.encoder import DATA_FILE_PATH
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.mock_team_generation import mock_generation
from team_formation.app.team_generator.algorithm.social_algorithm.social_algorithm import SocialAlgorithm

if __name__ == '__main__':
    logger = Logger(real=True)
    teams = mock_generation(SocialAlgorithm, logger, 55, DATA_FILE_PATH)
    logger.end()
    logger.print_teams(teams, with_relationships=True, only_unmet=True)

    timestamp = floor(time.time())
    with open(f'algorithm_sandbox/logs/log_{timestamp}.pkl', 'wb') as f:
        pickle.dump(logger, f)
    a = 1
