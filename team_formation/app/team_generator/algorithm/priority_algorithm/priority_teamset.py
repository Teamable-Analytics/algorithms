import copy
from math import floor
from typing import List
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority
from team_formation.app.team_generator.team import Team


class PriorityTeamSet:
    teams: List[Team] = []
    priorities: List[Priority] = []
    NUM_BUCKETS: int = 25

    def __init__(self, teams: List[Team], priorities: List[Priority]):
        self.teams = teams
        self.priorities = priorities
        self.score = self.calculate_score()

    def __lt__(self, other: 'PriorityTeamSet'):
        return self.score < other.score

    def __gt__(self, other: 'PriorityTeamSet'):
        return self.score > other.score

    def __lte__(self, other):
        return not self.__gt__(other)

    def __gte__(self, other):
        return not self.__lt__(other)

    def clone(self):
        # TODO: keep an eye on this copying properly
        cloned_teams = [team.clone() for team in self.teams]
        return PriorityTeamSet(teams=cloned_teams, priorities=self.priorities)

    def get_priority_satisfaction_array(self) -> List[int]:
        return [self.get_priority_satisfaction(priority) for priority in self.priorities]

    def get_priority_satisfaction(self, priority: Priority) -> int:
        satisfaction_ratio = self.satisfaction_ratio(priority)
        if satisfaction_ratio == 0:
            return 0
        if satisfaction_ratio == 1:
            return self.NUM_BUCKETS - 1

        return min(
            floor(satisfaction_ratio * self.NUM_BUCKETS),
            self.NUM_BUCKETS - 1
        )

    def satisfaction_ratio(self, priority: Priority) -> float:
        # returns value in [0, 1] IMPORTANT that it does this, satisfaction value relies on it
        count = 0
        for team in self.teams:
            count += priority.satisfied_by(team)
        return count / len(self.teams)

    def calculate_score(self) -> float:
        priority_satisfaction_array = self.get_priority_satisfaction_array()
        multipliers = get_multipliers(self.priorities, self.NUM_BUCKETS)

        return sum(
            [satisfaction * multiplier for satisfaction, multiplier in zip(priority_satisfaction_array, multipliers)]
        )


def get_multipliers(priorities: List[Priority], num_buckets: int) -> List[int]:
    # with 2 buckets and [C1, C2, C3], returns [4, 2, 1]
    multipliers = [num_buckets ** (n - 1)
                   for n in range(1, len(priorities) + 1)]
    return multipliers[::-1]


def compare_arrays(first, second):
    counter = 0
    while counter < len(first) and counter < len(second):
        comparison = first[counter] - second[counter]
        if comparison != 0:
            return comparison
        counter += 1
    return 0
