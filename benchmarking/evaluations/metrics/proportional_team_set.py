from typing import Callable, List

from api.models.student import Student
from api.models.team import TeamShell
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class ProportionalTeamSet(TeamSetMetric):
    """
    Calculate the proportional (PROP) metric for team set average the results

    ----

    Definition:

    - PROP: A team set is proportional if the utility of each team is at least the fair share of
    the class utility with the team's requirements.
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
        all_students = [student for team in team_set.teams for student in team.students]

        for team in team_set.teams:
            class_utility = self.calculate_utilities(all_students, team.to_shell())
            team.utility = self.calculate_utilities(team.students, team.to_shell())

            expected_team_utility = class_utility / float(team_set.num_teams)
            if team.utility < expected_team_utility:
                return 0.0

        return 1.0
