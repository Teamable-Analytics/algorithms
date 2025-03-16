from enum import Enum
from typing import List


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
    LOCATION = 8


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
    D = 4
    F = 5


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


class YearLevel(AttributeValueEnum):
    First = 1
    Second = 2
    Third = 3
    Fourth = 4
    Graduate = 5
