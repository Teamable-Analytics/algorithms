import time
from typing import List

from team_formation.app.team_generator.algorithm.algorithms import Algorithm
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team
from algorithm_sandbox.algorithm_state import AlgorithmState
from algorithm_sandbox.encoder import Encoder


class Logger:
    def __init__(self, real: bool = False):
        self.real = real
        self.algorithm_states: List[AlgorithmState] = []
        self.start_time = time.time()
        self.end_time = None

    def save_algorithm_state(self, teams: List[Team], algorithm: Algorithm):
        non_empty_teams = [team for team in teams if team.size > 0]
        self.algorithm_states.append(AlgorithmState(non_empty_teams, algorithm.stage))

    def print_teams(self, teams: List[Team], with_friends: bool = False):
        print(f'Number of teams: {len(teams)}')
        for team in teams:
            print(f'Team: {team.name} ({team.id})')
            for student in team.students:
                info = student.id
                if self.real:
                    info = Encoder.get_student_from_key(student, with_friends)
                print(f'\tStudent - {info}')

    def format_clique(self, clique: List[Student]):
        if self.real:
            return [*map(Encoder.get_student_from_key, clique)]
        return [student.id for student in clique]

    def print_clique(self, clique: List[Student]):
        print(self.format_clique(clique))

    def format_cliques(self, cliques: List[List[Student]]):
        return [self.format_clique(clique) for clique in cliques]

    def print_cliques(self, cliques: List[List[Student]]):
        print(self.format_cliques(cliques))

    def end(self):
        self.end_time = time.time()
