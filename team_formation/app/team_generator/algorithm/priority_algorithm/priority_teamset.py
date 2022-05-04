import copy
from math import floor
from typing import List, Dict
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority
from team_formation.app.team_generator.algorithm.priority_algorithm.scoring import get_priority_satisfaction_array, \
    get_multipliers
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


class PriorityTeam:
    team: Team = None  # just a reference to the team so team requirements can be found easily without duplicating them
    student_ids: List[int]

    def __init__(self, team: Team, student_ids: List[int]):
        self.team = team
        self.student_ids = student_ids


class PriorityTeamSet:
    priority_teams: List[PriorityTeam] = []

    def __init__(self, priority_teams: List[PriorityTeam]):
        self.priority_teams = priority_teams
        self.score = None  # not calculated yet

    def clone(self):
        # TODO: keep an eye on this copying properly
        cloned_priority_teams = copy.deepcopy(self.priority_teams)
        return PriorityTeamSet(priority_teams=cloned_priority_teams)

    def calculate_score(self, priorities: List[Priority], student_dict: Dict[int, Student]) -> float:
        if self.score:
            return self.score

        priority_satisfaction_array = get_priority_satisfaction_array(self.priority_teams, priorities, student_dict)
        multipliers = get_multipliers(priorities)
        score = sum(
            [satisfaction * multiplier for satisfaction, multiplier in zip(priority_satisfaction_array, multipliers)]
        )
        self.score = score
        return self.score

    # def get_teams(self, student_dict: Dict[int, Student]) -> List[Team]:
