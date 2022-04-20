import time
from typing import List, Dict, Tuple

from algorithm_sandbox.algorithm_state import AlgorithmState
from algorithm_sandbox.encoder import Encoder
from algorithm_sandbox.evaluation import TeamEvaluation
from team_formation.app.team_generator.algorithm.algorithms import Algorithm
from team_formation.app.team_generator.algorithm.consts import ENEMY, UNREGISTERED_STUDENT_ID, FRIEND
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


class Logger:
    def __init__(self, real: bool = False):
        self.real = real
        self.algorithm_states: List[AlgorithmState] = []
        self.start_time = time.time()
        self.end_time = None

    def save_algorithm_state(self, teams: List[Team], algorithm: Algorithm):
        non_empty_teams = [team for team in teams if team.size > 0]
        self.algorithm_states.append(AlgorithmState(non_empty_teams, algorithm.stage))

    def print_metrics_bar(self, evaluation_metrics: Tuple[int, int, int, int]):
        satisfied, reach, missed, possible = evaluation_metrics
        bar_length = 50

        def standardize(value) -> int:
            return round((float(value) / possible) * bar_length)
        symbol_frequencies = {
            '▓': standardize(satisfied),
            '▒‍': standardize(missed),
            '░': standardize(reach)
        }
        print_symbols(symbol_frequencies)

    def print_teams(self, teams: List[Team], with_relationships: bool = False, only_unmet: bool = False):
        team_evaluation = TeamEvaluation(teams)
        print(f'Number of teams: {len(teams)}')
        print('\t(F)\t', end='')
        self.print_metrics_bar(team_evaluation.team_set_satisfaction_metrics(True))
        print('\t(E)\t', end='')
        self.print_metrics_bar(team_evaluation.team_set_satisfaction_metrics(False))
        print(f'\tOverall Friend Satisfaction Score: {team_evaluation.team_set_satisfaction_score(friend=True)}')
        print(f'\tOverall Enemy Satisfaction Score: {team_evaluation.team_set_satisfaction_score(friend=False)}')
        for team in teams:
            friend_score = team_evaluation.team_satisfaction_score(team, friend=True)
            enemy_score = team_evaluation.team_satisfaction_score(team, friend=False)
            print(f'Team: {team.name} ({team.id})\t| Friend Score: {friend_score}\t| Enemy Score: {enemy_score}')
            for student in team.students:
                print(f'\t{self.format_student(student, with_relationships, team if only_unmet else None)}')

    def format_student(self, student: Student, with_relationships: bool = False, team: Team = None) -> str:
        if not self.real:
            return f'Student - {student.id}'
        team_member_ids = [student.id for student in team.students] if team else []
        student_name = Encoder.get_student_name(student)
        student_key = Encoder.get_student_key()

        friends = [
            Encoder.get_student_name_by_id(student_key, other_id)
            for other_id, relationship
            in student.relationships.items()
            if relationship == FRIEND and other_id != UNREGISTERED_STUDENT_ID and
               (other_id not in team_member_ids if team else True)
        ]

        enemies = [
            Encoder.get_student_name_by_id(student_key, other_id)
            for other_id, relationship
            in student.relationships.items()
            if relationship == ENEMY and other_id != UNREGISTERED_STUDENT_ID and
               (other_id in team_member_ids if team else True)
        ]

        output = f'{student_name}'
        if not with_relationships:
            return output

        if friends:
            output += f' => {"Missing" if team else ""} Friends ({", ".join(friends)})'
        if enemies:
            output += f' => {"Included" if team else ""} Enemies ({", ".join(enemies)})'
        return output

    def format_clique(self, clique: List[Student]):
        if self.real:
            return [*map(self.format_student, clique)]
        return [student.id for student in clique]

    def print_clique(self, clique: List[Student]):
        print(self.format_clique(clique))

    def format_cliques(self, cliques: List[List[Student]]):
        return [self.format_clique(clique) for clique in cliques]

    def print_cliques(self, cliques: List[List[Student]]):
        print(self.format_cliques(cliques))

    def end(self):
        self.end_time = time.time()


def print_symbols(symbol_frequencies: Dict[str, int]):
    for text, frequency in symbol_frequencies.items():
        print(text * frequency, end='')
    print()  # for the newline
