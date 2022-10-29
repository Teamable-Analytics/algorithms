import copy
import matplotlib.pyplot as plt
from algorithm_sandbox.logger import Logger
from algorithm_sandbox.mock_team_generation import mock_generation
from algorithm_sandbox.student_data import fake_students
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

    for i in range(1, 10):
        num_teams = _num_teams * i
        num_students = _num_students * i
        x.append(num_teams)

        students = fake_students(n=num_students, f=num_friends, x=12, e=1)
        social_students = copy.deepcopy(students)
        priority_students = copy.deepcopy(students)
        weight_student = copy.deepcopy(students)

        logger = Logger(real=True)
        teams = mock_generation(SocialAlgorithm, AlgorithmOptions(), logger, num_teams, social_students)
        logger.end()
        logger.print_teams(teams)
        y_social.append(logger.get_time())

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
        algorithm_options = AlgorithmOptions(
            priorities=[
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
            ],
            diversify_options=[{'id': 1}],
            concentrate_options=[{'id': 0}]
        )
        teams = mock_generation(PriorityAlgorithm, algorithm_options, logger, num_teams, priority_students)
        logger.end()
        y_priority.append(logger.get_time())

    plt.plot(x, y_social)
    plt.plot(x, y_priority)
    plt.plot(x, y_weight)
    plt.xlabel("Number of students")
    plt.ylabel("Execution time (s)")
    plt.show()
