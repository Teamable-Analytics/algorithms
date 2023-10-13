from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List
from schema import Schema, SchemaError

from api.ai.new.priority_algorithm.interfaces import Priority
from api.models.enums import RelationshipBehaviour


class AlgorithmOptions(ABC):
    """
    An algorithm option is semantically different from AlgorithmConfig.
    AlgorithmOptions specifies the customizable aspects of an algorithm made available for users to specify to their needs.
    """

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
    attributes_to_diversify: List[int] = field(default_factory=list)
    attributes_to_concentrate: List[int] = field(default_factory=list)

    def validate(self):
        super().validate()
        try:
            Schema(int).validate(self.requirement_weight)
            Schema(int).validate(self.social_weight)
            Schema(int).validate(self.diversity_weight)
            Schema(int).validate(self.preference_weight)
            Schema(int).validate(self.max_project_preferences)
            Schema(RelationshipBehaviour).validate(self.friend_behaviour)
            Schema(RelationshipBehaviour).validate(self.enemy_behaviour)
            Schema([int]).validate(self.attributes_to_diversify)
            Schema([int]).validate(self.attributes_to_concentrate)
        except SchemaError as error:
            raise ValueError(f"Error while validating WeightAlgorithmOptions \n{error}")


@dataclass
class PriorityAlgorithmOptions(WeightAlgorithmOptions):
    priorities: List[Priority] = field(default_factory=list)

    def validate(self):
        super().validate()


@dataclass
class SocialAlgorithmOptions(WeightAlgorithmOptions):
    def validate(self):
        super().validate()


@dataclass
class PathGaspAlgorithmOptions(AlgorithmOptions):
    def validate(self):
        super().validate()
