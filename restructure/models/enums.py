from enum import Enum
from typing import List


class Relationship(Enum):
    FRIEND = -1
    DEFAULT = 0
    ENEMY = 1.1


class RequirementType(Enum):
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


class TokenizationConstraintDirection(Enum):
    MIN_OF = "min_of"
    MAX_OF = "max_of"


class ScenarioAttribute(Enum):
    """
    Attributes that are used in scenarios.
    For the sake of benchmarking and testing, these are the only attributes a Student can have.
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


class Gpa(AttributeValueEnum):
    A = 1
    B = 2
    C = 3


class Age(AttributeValueEnum):
    _18 = 1
    _19 = 1
    _20 = 1
    _21 = 1
