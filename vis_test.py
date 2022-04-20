from algorithm_sandbox.encoder import DATA_FILE_PATH
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.mock_team_generation import mock_generation
from algorithm_sandbox.visualization.visualize_teams import visualize_teams_network
from algorithm_sandbox.visualization.visualize_logs import VisualizeLogs

if __name__ == '__main__':
    logger = Logger()
    teams = mock_generation(logger, 56, DATA_FILE_PATH)
    logger.end()
    visualize_logs = VisualizeLogs(logger)
    logger.end()
    visualize_teams_network(visualize_logs)
