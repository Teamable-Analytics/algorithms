import copy
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.metrics.friend_metrics import get_friend_metrics
from algorithm_sandbox.metrics.priority_metrics import get_priority_metrics
from algorithm_sandbox.mock_team_generation import mock_generation
from algorithm_sandbox.scenarios.scenario_1 import s1_options
from algorithm_sandbox.scenarios.scenario_1_1 import s1_1_options
from algorithm_sandbox.scenarios.scenario_1_3 import s1_3_options
from algorithm_sandbox.student_data import fake_students
from algorithm_sandbox.visualization.visualize_friend_metrics import visualize_friend_metrics
from algorithm_sandbox.visualization.visualize_priority_metrics import visualize_priority_metrics
from algorithm_sandbox.visualization.visualize_metric import visualize_metric
from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions, WeightAlgorithm
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority
from team_formation.app.team_generator.algorithm.priority_algorithm.priority_algorithm import PriorityAlgorithm
from team_formation.app.team_generator.algorithm.social_algorithm.social_algorithm import SocialAlgorithm

if __name__ == '__main__':
    _num_teams = 5
    _num_students = 15
    num_friends = 3

    x = []
    y_social = []
    y_priority = []
    y_weight = []
    metric = 'AVG_GINI'
    priorities, algorithm_options = s1_3_options()

    for i in range(1, 10):
        num_teams = _num_teams * i
        num_students = _num_students * i
        x.append(num_teams)

        students = fake_students(
            number_of_students=num_students,
            number_of_females=10,
            number_of_friends=num_friends,
            number_of_enemies=1,
            age_range=[18, 25],
            race=[1, 2, 3, 4],
            gpa=[0, 100],
            major=[1, 2, 3, 4],
            year=[1, 2, 3, 4],
            time=[1, 2, 3, 4]
        )
        social_students = copy.deepcopy(students)
        priority_students = copy.deepcopy(students)
        weight_student = copy.deepcopy(students)

        # SocialAlgorithm
        logger = Logger(real=True)
        teams = mock_generation(SocialAlgorithm, AlgorithmOptions(), logger, num_teams, social_students)
        logger.end()
        # logger.print_teams(teams)
        # y_social.append(logger.get_time())
        # y_social.append(get_friend_metrics(teams)[metric])
        y_social.append(get_priority_metrics(teams, priorities)[metric])


        # WeightAlgorithm
        logger = Logger(real=True)
        teams = mock_generation(
            WeightAlgorithm,
            AlgorithmOptions(
                requirement_weight=1,
                diversity_weight=1,
                social_weight=1,
                preference_weight=1,
            ),
            logger,
            num_teams,
            weight_student
        )
        logger.end()
        # y_weight.append(logger.get_time())
        # y_weight.append(get_friend_metrics(teams)[metric])
        y_weight.append(get_priority_metrics(teams, priorities)[metric])

        # PriorityAlgorithm
        logger = Logger(real=True)

        teams = mock_generation(
            PriorityAlgorithm,
            algorithm_options,
            logger,
            num_teams,
            priority_students
        )
        logger.end()

        # priority_metrics = get_priority_metrics(teams, priorities)
        # y_priority.append(logger.get_time())
        # y_priority.append(get_friend_metrics(teams)[metric])
        y_priority.append(get_priority_metrics(teams, priorities)[metric])

    visualize_metric(x, y_weight, y_social, y_priority, metric)
    # visualize_priority_metrics(x, priority_metrics)
    # visualize_time(x, y_social, y_priority, y_weight)
    # visualize_friend_metrics(x, friend_metrics)
