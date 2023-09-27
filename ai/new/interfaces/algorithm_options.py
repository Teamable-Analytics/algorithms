from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from models.enums import Relationship, RelationshipBehaviour


class AlgorithmOptions(ABC):
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self):
        pass


@dataclass
class RandomAlgorithmOptions(AlgorithmOptions):
    def validate(self):
        super().validate()


@dataclass
class WeightAlgorithmOptions(AlgorithmOptions):
    requirement_weight: int
    social_weight: int
    diversity_weight: int
    preference_weight: int
    max_project_preferences: int
    friend_behaviour: RelationshipBehaviour
    enemy_behaviour: RelationshipBehaviour
    diversify_options: List[dict] = field(default_factory=list)
    concentrate_options: List[dict] = field(default_factory=list)

    def validate(self):
        super().validate()


@dataclass
class PriorityAlgorithmOptions(WeightAlgorithmOptions):
    priorities: List[dict] = field(default_factory=list)

    def validate(self):
        super().validate()


@dataclass
class SocialAlgorithmOptions(WeightAlgorithmOptions):
    def validate(self):
        super().validate()
