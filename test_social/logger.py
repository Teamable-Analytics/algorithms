from typing import List

from algorithm.algorithms import Algorithm
from algorithm.consts import FRIEND
from student import Student
from team import Team
from test_social.algorithm_state import AlgorithmState
from test_social.mock_team_generation import KEY_FILE_PATH, load_json_data


class Logger:
    def __init__(self, real: bool = False):
        self.real = real
        self.algorithm_states: List[AlgorithmState] = []

    def save_algorithm_state(self, teams: List[Team], algorithm: Algorithm):
        non_empty_teams = [team for team in teams if team.size > 0]
        self.algorithm_states.append(AlgorithmState(non_empty_teams, algorithm.stage))

    def print_teams(self, teams: List[Team], with_friends: bool = False):
        print(f'Number of teams: {len(teams)}')
        for team in teams:
            print(f'Team: {team.id}')
            for student in team.students:
                info = student.id
                if self.real:
                    info = get_student_from_key(student, with_friends)
                print(f'\tStudent - {info}')

    def format_clique(self, clique: List[Student]):
        if self.real:
            return [*map(get_student_from_key, clique)]
        return [student.id for student in clique]

    def print_clique(self, clique: List[Student]):
        print(self.format_clique(clique))

    def format_cliques(self, cliques: List[List[Student]]):
        if self.real:
            return [*map(Logger.print_clique, cliques)]
        return [self.format_clique(clique) for clique in cliques]

    def print_cliques(self, cliques: List[List[Student]]):
        print(self.format_cliques(cliques))


def get_student_from_key(student_anon: Student, with_friends: bool = False):
    student_key = load_json_data(KEY_FILE_PATH)
    student_name = get_real_student_name(student_key, student_anon.id)
    if not with_friends:
        return student_name

    friends = [get_real_student_name(student_key, other_id)
               for other_id, relationship
               in student_anon.relationships.items()
               if relationship == FRIEND]
    return f'{student_name} => Friends ({", ".join(friends)})'


def get_real_student_name(student_key: dict, student_anon_id: int) -> str:
    for real_id, student_info in student_key.items():
        if student_info['anon_student_id'] == student_anon_id:
            return student_info['real_name']
    return f'Unknown Student ({student_anon_id})'
