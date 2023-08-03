import copy

from algorithm_sandbox.logger import Logger
from algorithm_sandbox.metrics.friend_metrics import get_friend_metrics
from algorithm_sandbox.metrics.priority_metrics import get_priority_metrics
from algorithm_sandbox.metrics.project_metric import get_project_metrics
from algorithm_sandbox.mock_team_generation import mock_generation


def get_metric(metric, teams, priorities):
    fm = get_friend_metrics(teams)
    pm = get_priority_metrics(teams, priorities)
    prm = get_project_metrics(teams)

    if metric in fm:
        return fm[metric]

    if metric in pm:
        return pm[metric]

    return prm[metric]


def run_algorithm(
        algorithm,
        algorithm_options,
        priorities,
        num_teams,
        students,
        teams,
        metric,
):
    logger = Logger(real=True)
    random_algorithm_options = copy.deepcopy(algorithm_options)
    random_students = copy.deepcopy(students)
    random_teams = copy.deepcopy(teams)

    final_teams = mock_generation(
        algorithm,
        random_algorithm_options,
        logger,
        num_teams,
        random_students,
        random_teams,
    )
    logger.end()

    metric_value = get_metric(metric, final_teams, priorities)

    return metric_value, logger.get_time()
