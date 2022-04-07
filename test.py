import pickle
import time
from math import floor

from test_social.encoder import DATA_FILE_PATH
from test_social.logger import Logger
from test_social.mock_team_generation import mock_generation

if __name__ == '__main__':
    for _ in range(10, 55, 5):
        logger = Logger(real=True)
        teams = mock_generation(logger, 55, DATA_FILE_PATH)
        logger.end()
        logger.print_teams(teams, with_friends=True)

        timestamp = floor(time.time())
        with open(f'test_social/logs/log_{timestamp}.pkl', 'wb') as f:
            pickle.dump(logger, f)
    a = 1
