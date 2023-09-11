from typing import List

from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import WeightGoal, PreferenceGoal


class IncludeSocialFriends(Scenario):
    @property
    def name(self):
        return "Create teams that group social friends together"

    @property
    def goals(self) -> List[Goal]:
        return [
            PreferenceGoal(PreferenceDirection.INCLUDE, PreferenceSubject.FRIENDS),
            WeightGoal(social_preference_weight=1),
        ]
