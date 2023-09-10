from typing import List

from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import WeightGoal


class DiversifySocialFriends(Scenario):
    @property
    def name(self):
        return "Diversify on social with a minimum of 2 friends"

    @property
    def goals(self) -> List[Goal]:
        return [
            WeightGoal(social_preference_weight=1),
        ]
