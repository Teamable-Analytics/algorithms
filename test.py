from algorithm.consts import FRIEND, DEFAULT
from algorithm.social_algorithm.clique_finder import CliqueFinder
from team import Team
from test_social.logger import Logger
from test_social.mock_team_generation import mock_generation, DATA_FILE_PATH
from test_social.student_data import fake_custom_students

if __name__ == '__main__':
    logger = Logger(real=True)
    teams = mock_generation(DATA_FILE_PATH)
    logger.print_teams(teams)
