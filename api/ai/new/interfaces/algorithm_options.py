from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Union

from schema import Schema, SchemaError

from api.ai.new.priority_algorithm.priority.interfaces import Priority
from api.models.enums import RelationshipBehaviour
from api.models.project import Project


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
    max_project_preferences: int
    requirement_weight: int = 0
    social_weight: int = 0
    diversity_weight: int = 0
    preference_weight: int = 0
    friend_behaviour: RelationshipBehaviour = RelationshipBehaviour.ENFORCE
    enemy_behaviour: RelationshipBehaviour = RelationshipBehaviour.ENFORCE
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
class MultipleRoundRobinAlgorithmOptions(AlgorithmOptions):
    projects: List[Project]

    def validate(self):
        super().validate()
        Schema([Project]).validate(self.projects)
        if len(self.projects) == 0:
            raise SchemaError("Project list cannot be empty.")


AnyAlgorithmOptions = Union[
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
]
