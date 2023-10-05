from enum import Enum
from typing import List


class Relationship(Enum):
    FRIEND = -1
    DEFAULT = 0
    ENEMY = 1.1


class RelationshipBehaviour(Enum):
    ENFORCE = "enforce"
    INVERT = "invert"
    IGNORE = "ignore"


class RequirementOperator(Enum):
    EXACTLY = "exactly"
    LESS_THAN = "less than"
    MORE_THAN = "more than"


class DiversifyType(Enum):
    DIVERSIFY = "diversify"
    CONCENTRATE = "concentrate"


class Weight(Enum):
    HIGH_WEIGHT = 10
    LOW_WEIGHT = 1


class AlgorithmType(Enum):
    RANDOM = "random"
    WEIGHT = "weight"
    SOCIAL = "social"
    PRIORITY = "priority"
    PRIORITY_NEW = "priority_new"


class TokenizationConstraintDirection(Enum):
    MIN_OF = "min_of"
    MAX_OF = "max_of"


class ScenarioAttribute(Enum):
    """
    Attributes that are used in scenarios.
    This set of attribute ids are named so that we can refer to them semantically.
    Any attribute given to a student with an id that is not one of these can semantically mean anything,
        please document this in your run if doing so.
    """

    GENDER = 1
    GPA = 2
    AGE = 3
    RACE = 4
    MAJOR = 5
    YEAR_LEVEL = 6
    TIMESLOT_AVAILABILITY = 7
    PROJECT_PREFERENCES = 8


class AttributeValueEnum(Enum):
    @classmethod
    def values(cls, integers_only=False) -> List["AttributeValueEnum"]:
        if integers_only:
            return [_.value for _ in cls]
        return [_ for _ in cls]


class Gender(AttributeValueEnum):
    MALE = 1
    FEMALE = 2
    NON_BINARY = 3
    OTHER = 4
    NA = 5


class Gpa(AttributeValueEnum):
    A = 1
    B = 2
    C = 3


class Age(AttributeValueEnum):
    _18 = 18
    _19 = 19
    _20 = 20
    _21 = 21


class Race(AttributeValueEnum):
    African = 1
    European = 2
    East_Asian = 3
    South_Asian = 4
    South_East_Asian = 5
    First_Nations_or_Indigenous = 6
    Hispanic_or_Latin_American = 7
    Middle_Eastern = 8
    Other = 9
