from typing import List

from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import WeightGoal, PreferenceGoal


class GiveThePeopleWhatTheyWant(Scenario):
    @property
    def name(self):
        return "Give the people what they want"

    @property
    def goals(self) -> List[Goal]:
        return [
            PreferenceGoal(PreferenceDirection.INCLUDE, PreferenceSubject.FRIENDS),
            PreferenceGoal(PreferenceDirection.EXCLUDE, PreferenceSubject.ENEMIES),
            WeightGoal(social_preference_weight=1),
        ]
