import copy

from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class EnvyFreenessUpToOne(TeamSetMetric):
    """
    Calculate the envy-free up to one metric for the given attribute for each team and average the results

    A allocation is envy-free up to one if no agent envies another agent by more than one unit of the given attribute
    Meaning if A is envying B, then A will no longer envy B if we remove one unit of the given attribute from  B
    """

    def __init__(self, *args, **kwargs):
        super().__init__(name="EF1", *args, **kwargs)

    def calculate(self, team_set: TeamSet) -> int:
        """
        If envy-free up to one, return 1, else return 0
        """
        for team in team_set.teams:
            for other_team in team_set.teams:
                if team == other_team:
                    continue

                if not self._is_envy(team, other_team):
                    continue

                envy_up_to_one = False
                for student_idx, student in enumerate(team.students):
                    team_copy = copy.deepcopy(team)
                    team_copy.students.pop(student_idx)
                    if not self._is_envy(team, other_team):
                        envy_up_to_one = True
                        break
                if not envy_up_to_one:
                    return 0
        return 1

    def _is_envy(self, team: Team, other_team: Team) -> bool:
        """
        Check if team envies other_team
        """
        team_utility = self._calculate_team_utility(team)
        other_team_utility = self._calculate_team_utility(other_team)
        if team_utility < other_team_utility:
            return True
        return False

    def _calculate_team_utility(self, team: Team) -> int:
        """
        Calculate additive utility of all students in the team

        Utility of a student is calculated as the sum of the student's satisfied attributes to the requirements
        """
        team_utility = 0
        for student in team.students:
            team_utility += sum(
                [
                    student.meets_requirement(requirement)
                    for requirement in team.requirements
                ]
            )
        return team_utility
