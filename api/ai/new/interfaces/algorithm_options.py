from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Union, Dict, Any

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

    @staticmethod
    @abstractmethod
    def parse_json(json: Dict[str, Any]):
        raise NotImplementedError("parse_json is not implemented.")


@dataclass
class RandomAlgorithmOptions(AlgorithmOptions):
    def validate(self):
        super().validate()

    @staticmethod
    def parse_json(_: Dict[str, Any]) -> "RandomAlgorithmOptions":
        return RandomAlgorithmOptions()


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

    @staticmethod
    def parse_json(json: Dict[str, Any]) -> "WeightAlgorithmOptions":
        requirement_weight = json.get("requirement_weight", 0)
        social_weight = json.get("social_weight", 0)
        diversity_weight = json.get("diversity_weight", 0)
        preference_weight = json.get("preference_weight", 0)
        friend_behaviour = RelationshipBehaviour(
            json.get("friend_behaviour", "enforce")
        )
        enemy_behaviour = RelationshipBehaviour(json.get("enemy_behaviour", "enforce"))
        attributes_to_diversify = json.get("attributes_to_diversify", [])
        attributes_to_concentrate = json.get("attributes_to_concentrate", [])
        max_project_preferences = json.get("max_project_preferences")

        return WeightAlgorithmOptions(
            requirement_weight=requirement_weight,
            social_weight=social_weight,
            diversity_weight=diversity_weight,
            preference_weight=preference_weight,
            friend_behaviour=friend_behaviour,
            enemy_behaviour=enemy_behaviour,
            attributes_to_diversify=attributes_to_diversify,
            attributes_to_concentrate=attributes_to_concentrate,
            max_project_preferences=max_project_preferences,
        )


@dataclass
class PriorityAlgorithmOptions(WeightAlgorithmOptions):
    priorities: List[Priority] = field(default_factory=list)

    def validate(self):
        super().validate()

    @staticmethod
    def parse_json(json: Dict[str, Any]) -> "PriorityAlgorithmOptions":
        priorities = json.get("priorities", [])
        requirement_weight = json.get("requirement_weight", 0)
        social_weight = json.get("social_weight", 0)
        diversity_weight = json.get("diversity_weight", 0)
        preference_weight = json.get("preference_weight", 0)
        friend_behaviour = RelationshipBehaviour(
            json.get("friend_behaviour", "enforce")
        )
        enemy_behaviour = RelationshipBehaviour(json.get("enemy_behaviour", "enforce"))
        attributes_to_diversify = json.get("attributes_to_diversify", [])
        attributes_to_concentrate = json.get("attributes_to_concentrate", [])
        max_project_preferences = json.get("max_project_preferences")

        return PriorityAlgorithmOptions(
            priorities=priorities,
            requirement_weight=requirement_weight,
            social_weight=social_weight,
            diversity_weight=diversity_weight,
            preference_weight=preference_weight,
            friend_behaviour=friend_behaviour,
            enemy_behaviour=enemy_behaviour,
            attributes_to_diversify=attributes_to_diversify,
            attributes_to_concentrate=attributes_to_concentrate,
            max_project_preferences=max_project_preferences,
        )


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

    @staticmethod
    def parse_json(_: Dict[str, Any]):
        raise AttributeError(
            "MultipleRoundRobinAlgorithmOptions does not support parsing from json."
        )


AnyAlgorithmOptions = Union[
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
]
