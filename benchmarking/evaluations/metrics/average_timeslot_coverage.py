from typing import List

from benchmarking.evaluations.enums import ScenarioAttribute
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageTimeslotCoverage(TeamSetMetric):
    """
    Calculate the average mutual timeslots between students in a team and average over all teams.
    """

    def __init__(
        self,
        available_timeslots: List[int] = None,
        timeslot_attribute_id: int = ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.available_timeslots = available_timeslots
        self.timeslot_attribute_value = timeslot_attribute_id

    def calculate(self, team_set: TeamSet) -> float:
        if len(team_set.teams) == 0:
            raise ValueError("Team set must have at least one team")
        if self.available_timeslots is None:
            raise ValueError("Available timeslots must be set")

        for student in [
            student for team in team_set.teams for student in team.students
        ]:
            if student.attributes.get(self.timeslot_attribute_value) is None:
                raise ValueError(
                    f"Student {student.id} does not have the timeslot attribute"
                )
            if any(
                [
                    attr not in self.available_timeslots
                    for attr in student.attributes.get(self.timeslot_attribute_value)
                ]
            ):
                raise ValueError(f"Student {student.id} has an invalid timeslot")

        timeslot_coverage = 0.0
        for team in team_set.teams:
            num_mutual_timeslots = 0
            for timeslot in self.available_timeslots:
                if all(
                    timeslot in student.attributes.get(self.timeslot_attribute_value)
                    for student in team.students
                ):
                    num_mutual_timeslots += 1
            timeslot_coverage += num_mutual_timeslots / float(
                len(self.available_timeslots)
            )
        return timeslot_coverage / float(len(team_set.teams))
