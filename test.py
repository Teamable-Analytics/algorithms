from test_social.encoder import DATA_FILE_PATH
from test_social.logger import Logger
from test_social.mock_team_generation import mock_generation

if __name__ == '__main__':
    logger = Logger(real=True)
    teams = mock_generation(logger, 5, DATA_FILE_PATH)
    logger.print_teams(teams, with_friends=True)
    a = 1
