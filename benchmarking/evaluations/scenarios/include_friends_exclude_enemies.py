from typing import List

from algorithms.dataclasses.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import WeightGoal, PreferenceGoal


class IncludeFriendsExcludeEnemies(Scenario):
    @property
    def name(self):
        return "Include friends, exclude enemies"

    @property
    def goals(self) -> List[Goal]:
        return [
            PreferenceGoal(PreferenceDirection.INCLUDE, PreferenceSubject.FRIENDS),
            PreferenceGoal(PreferenceDirection.EXCLUDE, PreferenceSubject.ENEMIES),
            WeightGoal(social_preference_weight=1),
        ]
