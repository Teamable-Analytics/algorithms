import copy
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.metrics.friend_metrics import get_friend_metrics
from algorithm_sandbox.metrics.priority_metrics import get_priority_metrics
from algorithm_sandbox.metrics.project_metric import get_project_metrics
from algorithm_sandbox.mock_team_generation import mock_generation
from algorithm_sandbox.scenarios.scenario_1 import s1_options
from algorithm_sandbox.scenarios.scenario_1_1 import s1_1_options
from algorithm_sandbox.scenarios.scenario_1_2 import s1_2_options
from algorithm_sandbox.scenarios.scenario_1_3 import s1_3_options
from algorithm_sandbox.scenarios.scenario_2 import s2_options
from algorithm_sandbox.scenarios.scenario_3 import s3_options
from algorithm_sandbox.student_data import fake_students
from algorithm_sandbox.visualization.visualize_friend_metrics import visualize_friend_metrics
from algorithm_sandbox.visualization.visualize_priority_metrics import visualize_priority_metrics
from algorithm_sandbox.visualization.visualize_metric import visualize_metric
from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions, WeightAlgorithm, RandomAlgorithm
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority
from team_formation.app.team_generator.algorithm.priority_algorithm.priority_algorithm import PriorityAlgorithm
from team_formation.app.team_generator.algorithm.social_algorithm.social_algorithm import SocialAlgorithm

if __name__ == '__main__':
    _num_teams = 5
    _num_students = 20
    num_friends = 4
    _num_tests = 10
    _num_req = 20
    _num_req_per_team = 3

    x = []
    y_social = []
    y_priority = []
    y_weight = []
    y_random = []
    metric = 'S_T'

    # priorities, algorithm_options = s1_1_options()
    initial_teams = []

    for i in range(1, 10):
        print(i)
        num_teams = _num_teams * i
        num_students = _num_students * i
        x.append(num_students)

        priorities, algorithm_options, initial_teams = s3_options(num_teams, _num_req, _num_req_per_team)

        y_social_avg = 0
        y_priority_avg = 0
        y_weight_avg = 0
        y_random_avg = 0

        for t in range(_num_tests):
            students = fake_students(
                number_of_students=num_students,
                number_of_females=num_students // 2,
                number_of_friends=num_friends,
                number_of_enemies=1,
                friend_distribution='random',
                age_range=[18, 25],
                race=[1, 2, 3, 4],
                gpa=[0, 4],
                major=[1, 2, 3, 4],
                year=[1, 2, 3, 4],
                time=[1, 2, 3, 4],
                number_of_project_req=_num_req,
            )


            social_students = copy.deepcopy(students)
            priority_students = copy.deepcopy(students)
            weight_student = copy.deepcopy(students)
            random_students = copy.deepcopy(students)

            social_teams = copy.deepcopy(initial_teams)
            priority_teams = copy.deepcopy(initial_teams)
            weight_teams = copy.deepcopy(initial_teams)
            random_teams = copy.deepcopy(initial_teams)

            # SocialAlgorithm
            logger = Logger(real=True)
            social_algorithm_options = copy.deepcopy(algorithm_options)

            teams = mock_generation(
                SocialAlgorithm,
                social_algorithm_options,
                logger,
                num_teams,
                social_students,
                social_teams,
            )
            logger.end()
            y_social_avg += get_project_metrics(teams)[metric]
            # y_social_avg += get_friend_metrics(teams)[metric]
            # y_social_avg += get_priority_metrics(teams, priorities)[metric]

            # WeightAlgorithm
            logger = Logger(real=True)
            weight_algorithm_options = copy.deepcopy(algorithm_options)

            teams = mock_generation(
                WeightAlgorithm,
                weight_algorithm_options,
                logger,
                num_teams,
                weight_student,
                weight_teams,
            )
            logger.end()
            y_weight_avg += get_project_metrics(teams)[metric]
            # y_weight_avg += get_friend_metrics(teams)[metric]
            # y_weight_avg += get_priority_metrics(teams, priorities)[metric]

            # PriorityAlgorithm
            logger = Logger(real=True)
            priority_algorithm_options = copy.deepcopy(algorithm_options)

            teams = mock_generation(
                PriorityAlgorithm,
                priority_algorithm_options,
                logger,
                num_teams,
                priority_students,
                priority_teams,
            )
            logger.end()
            y_priority_avg += get_project_metrics(teams)[metric]
            # y_priority_avg += get_friend_metrics(teams)[metric]
            # y_priority_avg += get_priority_metrics(teams, priorities)[metric]

            # Random Algorithm
            logger = Logger(real=True)
            random_algorithm_options = copy.deepcopy(algorithm_options)

            teams = mock_generation(
                RandomAlgorithm,
                random_algorithm_options,
                logger,
                num_teams,
                random_students,
                random_teams,
            )
            logger.end()
            # y_random_avg += 0
            y_random_avg += get_project_metrics(teams)[metric]
            # y_random_avg += get_friend_metrics(teams)[metric]
            # y_random_avg += get_priority_metrics(teams, priorities)[metric]

        y_social.append(y_social_avg / _num_tests)
        y_weight.append(y_weight_avg / _num_tests)
        y_priority.append(y_priority_avg / _num_tests)
        y_random.append(y_random_avg / _num_tests)

    visualize_metric(x, y_weight, y_social, y_priority, y_random, metric)
    # visualize_priority_metrics(x, priority_metrics)
    # visualize_time(x, y_social, y_priority, y_weight)
    # visualize_friend_metrics(x, friend_metrics)
