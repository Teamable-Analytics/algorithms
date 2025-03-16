from typing import List

from algorithms.dataclasses.enums import DiversifyType
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Goal, Scenario
from manual_run.attributes import Attributes


class DefaultScenario(Scenario):
    @property
    def name(self) -> str:
        return "Diversify on score and concentrate on timeslot"

    @property
    def goals(self) -> List[Goal]:
        """
        This function is meant to create a list of scenerio goals to be followed for team formation.

        Returns:
            List[Goal]: A list of goals for team formation.
        """
        return [
            # Concentrate on student timeslot availability
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                Attributes.TIMESLOT_AVAILABILITY.value,
            ),
            # Diversify students on tutor preference
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.TUTOR_PREFERENCE.value,
            ),
            # Diversify students on score
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.SCORE.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]
