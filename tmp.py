import copy
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.metrics.friend_metrics import get_friend_metrics
from algorithm_sandbox.metrics.priority_metrics import get_priority_metrics
from algorithm_sandbox.mock_team_generation import mock_generation
from algorithm_sandbox.student_data import fake_students
from algorithm_sandbox.visualization.visualize_friend_metrics import visualize_friend_metrics
from algorithm_sandbox.visualization.visualize_priority_metrics import visualize_priority_metrics
from algorithm_sandbox.visualization.visualize_time import visualize_time
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
    friend_metrics = []
    priority_metrics = []

    for i in range(1, 2):
        num_teams = _num_teams * i
        num_students = _num_students * i
        x.append(num_teams)

        students = fake_students(
            number_of_students=num_students,
            number_of_friends=num_friends,
            number_of_enemies=1,
            age_range=[18, 25],
            age_distribution='uniform',
            gender_options={
                'male': num_students - 10,
                'female': 10,
            },
        )
        social_students = copy.deepcopy(students)
        priority_students = copy.deepcopy(students)
        weight_student = copy.deepcopy(students)

        logger = Logger(real=True)
        teams = mock_generation(SocialAlgorithm, AlgorithmOptions(), logger, num_teams, social_students)
        logger.end()
        # logger.print_teams(teams)
        y_social.append(logger.get_time())

        friend_metrics.append(get_friend_metrics(teams))

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
        y_weight.append(logger.get_time())

        logger = Logger(real=True)
        priorities = [
                {
                    'order': 1,
                    'constraint': Priority.TYPE_CONCENTRATE,
                    'skill_id': 0,  # timeslot availability
                    'limit_option': Priority.MAX_OF,
                    'limit': 2,
                    'value': 3,  # some timeslot
                },
                {
                    'order': 2,
                    'constraint': Priority.TYPE_DIVERSIFY,
                    'skill_id': 1,  # gender
                    'limit_option': Priority.MIN_OF,
                    'limit': 2,
                    'value': 2,  # female
                }
            ]
        algorithm_options = AlgorithmOptions(
            priorities=priorities,
            diversify_options=[{'id': 1}],
            concentrate_options=[{'id': 0}]
        )
        teams = mock_generation(PriorityAlgorithm, algorithm_options, logger, num_teams, priority_students)
        logger.end()
        y_priority.append(logger.get_time())
        priority_metrics.append(get_priority_metrics(teams, priorities))

    visualize_priority_metrics(x, priority_metrics)
    # visualize_time(x, y_social, y_priority, y_weight)
    # visualize_friend_metrics(x, friend_metrics)
