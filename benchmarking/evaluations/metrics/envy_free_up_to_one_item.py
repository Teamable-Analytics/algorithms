import copy

from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class EnvyFreenessUpToOneItem(TeamSetMetric):
    """
    Calculate the "envy-freeness up to one item" metric for the given attribute for each team and average the results

    ----

    Definitions:

    - Envy: Team A envies Team B if Team A's utility is less than Team B's utility
    - Envy-free up to one item (ef1): Team B ef1 Team A if Team B envies Team A and if Team A removes one student, Team B no longer envies Team A
    """

    def __init__(self, *args, **kwargs):
        super().__init__(theoretical_range=(0, 1), *args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        """
        If envy-free up to one item, return 1.0, else return 0.0

        ----

        Note: The return of this function should be `bool`, but we return
        `float` to calculate the average between multiple runs
        """
        for team in team_set.teams:
            for other_team in team_set.teams:
                if team == other_team:
                    continue

                if not self._is_envy(other_team, team):
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
        Calculate **additive** utility of all students in the team

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
