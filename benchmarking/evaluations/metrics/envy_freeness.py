from typing import Callable, List

from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team, TeamShell
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class EnvyFreeness(TeamSetMetric):
    """
    Calculate the "envy-freeness" metric for the given attribute for each team and average the results
    ----
    Definitions:
    - Envy: Team A envies Team B if Team A's utility is less than Team B's utility
    - Envy-free: If no team envy any other team
    """

    def __init__(
        self,
        calculate_utilities: Callable[[List[Student], TeamShell], float],
        *args,
        **kwargs
    ):
        super().__init__(theoretical_range=(0, 1), *args, **kwargs)
        self.calculate_utilities = calculate_utilities

    def calculate(self, team_set: TeamSet) -> float:
        """
        If envy-free, return 1.0, else return 0.0
        ----
        Note: The return of this function should be `bool`, but we return
        `float` to calculate the average between multiple runs
        """

        for team in team_set.teams:
            for other_team in team_set.teams:
                if team.id == other_team.id:
                    continue
                if self._is_envy(other_team, team):
                    return 0.0
        return 1.0

    def _is_envy(self, team: Team, other_team: Team) -> bool:
        """
        Check if team envies other_team
        """
        team_utility = self.calculate_utilities(team.students, team.to_shell())
        other_team_utility = self.calculate_utilities(
            other_team.students, other_team.to_shell()
        )

        return team_utility < other_team_utility
