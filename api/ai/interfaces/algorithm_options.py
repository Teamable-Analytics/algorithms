from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Callable

from schema import Schema, SchemaError, Const, Or, Optional as SchemaOptional, And

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.priority_algorithm.priority.priority import (
    TokenizationPriority,
    get_priority_from_type,
)
from api.dataclasses.enums import (
    RelationshipBehaviour,
    DiversifyType,
    TokenizationConstraintDirection,
    AlgorithmType,
    PriorityType,
)
from api.dataclasses.project import Project
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell


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

    @staticmethod
    @abstractmethod
    def get_schema() -> Schema:
        raise NotImplementedError("get_schema is not implemented.")


@dataclass
class RandomAlgorithmOptions(AlgorithmOptions):
    def validate(self):
        super().validate()

    @staticmethod
    def parse_json(_: Dict[str, Any]) -> "RandomAlgorithmOptions":
        return RandomAlgorithmOptions()

    @staticmethod
    def get_schema() -> Schema:
        return Schema({"algorithm_type": Const(AlgorithmType.RANDOM.value)})


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

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "algorithm_type": Const(AlgorithmType.WEIGHT.value),
                "max_project_preferences": int,
                SchemaOptional("requirement_weight"): int,
                SchemaOptional("social_weight"): int,
                SchemaOptional("diversity_weight"): int,
                SchemaOptional("preference_weight"): int,
                SchemaOptional("friend_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("enemy_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("attributes_to_diversify"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
                SchemaOptional("attributes_to_concentrate"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
            }
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
            priorities=[
                TokenizationPriority(
                    attribute_id=p.get("attribute_id"),
                    strategy=DiversifyType(p.get("strategy")),
                    direction=TokenizationConstraintDirection(p.get("direction")),
                    threshold=p.get("threshold"),
                    value=p.get("value"),
                )
                for p in priorities
            ],
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

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "algorithm_type": Const(AlgorithmType.PRIORITY.value),
                "max_project_preferences": int,
                "priorities": [
                    And(
                        dict,
                        lambda _data: PriorityAlgorithmOptions.validate_priority(_data),
                    )
                ],
                SchemaOptional("requirement_weight"): int,
                SchemaOptional("social_weight"): int,
                SchemaOptional("diversity_weight"): int,
                SchemaOptional("preference_weight"): int,
                SchemaOptional("friend_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("enemy_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("attributes_to_diversify"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
                SchemaOptional("attributes_to_concentrate"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
            }
        )

    @staticmethod
    def validate_priority(priority_data: Dict):
        if "priority_type" not in priority_data:
            raise SchemaError("Priority type not specified.")
        priority_type = priority_data.pop("priority_type")
        Schema(Or(*[pri.value for pri in PriorityType])).validate(priority_type)

        priority_cls = get_priority_from_type(PriorityType(priority_type))
        if priority_cls is None:
            raise SchemaError("Priority type not supported.")

        priority_cls.get_schema().validate(priority_data)
        return True


@dataclass
class SocialAlgorithmOptions(WeightAlgorithmOptions):
    def validate(self):
        super().validate()

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "algorithm_type": Const(AlgorithmType.SOCIAL.value),
                "max_project_preferences": int,
                SchemaOptional("requirement_weight"): int,
                SchemaOptional("social_weight"): int,
                SchemaOptional("diversity_weight"): int,
                SchemaOptional("preference_weight"): int,
                SchemaOptional("friend_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("enemy_behaviour"): Or(
                    *[behaviour.value for behaviour in RelationshipBehaviour]
                ),
                SchemaOptional("attributes_to_diversify"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
                SchemaOptional("attributes_to_concentrate"): And(
                    list,
                    lambda _data: all(isinstance(i, int) for i in _data),
                ),
            }
        )


AnyAlgorithmOptions = Union[
    RandomAlgorithmOptions,
    WeightAlgorithmOptions,
    SocialAlgorithmOptions,
    PriorityAlgorithmOptions,
]
