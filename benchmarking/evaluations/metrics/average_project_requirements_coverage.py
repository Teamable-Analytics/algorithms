from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageProjectRequirementsCoverage(TeamSetMetric):
    """
    Calculate the average project requirements coverage for each team and average the results

    Coverage in this case means 'for each requirement, does someone on the team meet it?'.
    This is analogous to RequirementsCriteria.SOMEONE, and this metric will treat all requirements in this way
    """

    def __init__(self, *args, **kwargs):
        super().__init__(theoretical_range=(0, 1), *args, **kwargs)

    def calculate(self, team_set: TeamSet) -> float:
        if not team_set.teams or len(team_set.teams) == 0:
            raise ValueError("Team set has no teams")

        total = 0.0
        for team in team_set.teams:
            to_be_satisfied_requirements = team.requirements.copy()
            num_requirements = len(team.requirements)
            if num_requirements == 0:
                raise ValueError(f"Team { team.id } has no requirements")

            for student in team.students:
                to_be_satisfied_requirements = [
                    requirement
                    for requirement in to_be_satisfied_requirements
                    if not requirement.met_by_student(student)
                ]

            total += (num_requirements - len(to_be_satisfied_requirements)) / float(
                num_requirements
            )

        total /= len(team_set.teams)

        return total
