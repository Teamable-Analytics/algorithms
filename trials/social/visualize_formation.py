from sandbox_tools.encoder import DATA_FILE_PATH
from sandbox_tools.logger import Logger
from sandbox_tools.mock_team_generation import mock_generation
from sandbox_tools.visualization.visualize_teams import visualize_teams_network
from sandbox_tools.visualization.visualize_logs import VisualizeLogs
from team_generator.algorithm import AlgorithmOptions
from team_generator.algorithm import SocialAlgorithm

if __name__ == '__main__':
    logger = Logger()
    teams = mock_generation(SocialAlgorithm, AlgorithmOptions(), logger, 55, DATA_FILE_PATH)
    logger.end()
    visualize_logs = VisualizeLogs(logger)
    logger.end()
    visualize_teams_network(visualize_logs)
