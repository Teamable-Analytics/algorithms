from typing import List

from algorithms.dataclasses.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.interfaces import (
    Scenario,
    Goal,
)
from benchmarking.evaluations.goals import WeightGoal, PreferenceGoal


class IncludeSocialFriends(Scenario):
    def __init__(self, max_num_friends: int, max_num_enemies: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies

    @property
    def name(self):
        return "Create teams that group social friends together"

    @property
    def goals(self) -> List[Goal]:
        return [
            PreferenceGoal(
                PreferenceDirection.INCLUDE,
                PreferenceSubject.FRIENDS,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
            WeightGoal(social_preference_weight=1),
        ]
