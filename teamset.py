import copy
import random

from team import Team


class PriorityTeamSet:
    teams = []
    priorities = []

    def __init__(self, teams: [Team], priorities: []):
        self.teams = teams
        self.priorities = priorities

    def __lt__(self, other):
        satisfaction_array = self.get_priority_satisfaction_array()
        satisfaction_array_other = other.get_priority_satisfaction_array()
        return compare_arrays(satisfaction_array, satisfaction_array_other) < 0

    def __gt__(self, other):
        satisfaction_array = self.get_priority_satisfaction_array()
        satisfaction_array_other = other.get_priority_satisfaction_array()
        return compare_arrays(satisfaction_array, satisfaction_array_other) > 0

    def __lte__(self, other):
        return not self.__gt__(other)

    def __gte__(self, other):
        return not self.__lt__(other)

    def clone(self):
        # needs to be a super deep copy
        cloned_teams = [copy.deepcopy(team) for team in self.teams]
        return PriorityTeamSet(teams=cloned_teams, priorities=self.priorities)

    def get_priority_satisfaction_array(self) -> [int]:
        return [self.get_priority_satisfaction(priority) for priority in self.priorities]

    def get_priority_satisfaction(self, priority) -> int:
        # TODO: assign a numeric score [Z] a teamset based on a single priority. We either add a "point" every time a
        #  team meets the priority or deducting every time a team violates the priority
        return round(random.random() * 10)


def compare_arrays(first, second):
    counter = 0
    while counter < len(first) and counter < len(second):
        comparison = first[counter] - second[counter]
        if comparison != 0:
            return comparison
        counter += 1
    return 0
