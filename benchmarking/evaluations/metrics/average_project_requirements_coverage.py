from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageProjectRequirementsCoverage(TeamSetMetric):
    """
    Calculate the average project requirements coverage for each team and average the results
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        if not team_set.teams or len(team_set.teams) == 0:
            raise ValueError("Team set has no teams")

        total = 0.0
        for team in team_set.teams:
            all_requirements = team.requirements.copy()
            num_requirements = len(team.requirements)
            if num_requirements == 0:
                raise ValueError(f"Team { team.id } has no requirements")

            for student in team.students:
                all_requirements = [
                    requirement
                    for requirement in all_requirements
                    if not student.meets_requirement(requirement)
                ]

            total += (num_requirements - len(all_requirements)) / float(
                num_requirements
            )

        total /= len(team_set.teams)

        return total
