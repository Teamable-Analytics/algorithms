from algorithm_sandbox.metrics.metric import run_algorithm
from algorithm_sandbox.scenarios.scenario_1 import s1_options
from algorithm_sandbox.scenarios.scenario_1_1 import s1_1_options
from algorithm_sandbox.student_data import fake_students
from algorithm_sandbox.visualization.visualize_metric import visualize_p_metric
from team_formation.app.team_generator.algorithm.algorithms import WeightAlgorithm
from team_formation.app.team_generator.algorithm.priority_algorithm.priority_algorithm import PriorityAlgorithm

if __name__ == '__main__':
    _num_teams = 5
    _num_students = 20
    num_friends = 4
    _num_tests = 5
    _num_req = 20
    _num_req_per_team = 3

    x = []
    y_priorities = [[] for _ in range(5)]
    y_weight = []
    metric = 'LN'

    priorities, algorithm_options = s1_options()
    initial_teams = []

    for i in range(1, 5):
        print(i)
        num_teams = _num_teams * i
        num_students = _num_students * i
        x.append(num_students)

        students = fake_students(
            number_of_students=num_students,
            number_of_females=num_students // 4,
            number_of_friends=num_friends,
            number_of_enemies=1,
            friend_distribution='cluster',
            age_range=[18, 25],
            race=[1, 2, 3, 4],
            gpa=[0, 4],
            major=[1, 2, 3, 4],
            year=[1, 2, 3, 4],
            time=[1, 2, 3, 4],
            number_of_project_req=_num_req,
        )

        for j in range(5):
            PriorityAlgorithm.MAX_ITERATE = (j+1) * 5

            avg = 0
            for t in range(_num_tests):
                metric_value, time = run_algorithm(
                    PriorityAlgorithm,
                    algorithm_options,
                    priorities,
                    num_teams,
                    students,
                    initial_teams,
                    metric
                )
                avg += time
            y_priorities[j].append(avg/_num_tests)

        w_avg = 0
        for t in range(_num_tests):
            metric_value, time = run_algorithm(
                WeightAlgorithm,
                algorithm_options,
                priorities,
                num_teams,
                students,
                initial_teams,
                metric
            )
            w_avg += time
        y_weight.append(w_avg/_num_tests)

    visualize_p_metric(x, y_priorities, y_weight, "time (s)")
