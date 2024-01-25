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
    MRR = "multiple_round_robin_with_adjusted_winner"
    GEG = "generalized_envy_graph"
    DRR = "double_round_robin"
    GROUP_MATCHER = "group_matcher"


class TokenizationConstraintDirection(Enum):
    MIN_OF = "min_of"
    MAX_OF = "max_of"


class RequirementsCriteria(Enum):
    """
    STUDENT_ATTRIBUTES_ARE_RELEVANT: This focuses the algorithm on putting students that have skills relevant to the
    project on the team. This can result in a scenario where everyone on the team has the same skill, and some of the
    project requirements are not met.

    PROJECT_REQUIREMENTS_ARE_SATISFIED: This focuses on making sure all project requirements are met. If one student has
    all the skills required, then this priority would be satisfied.
    """

    STUDENT_ATTRIBUTES_ARE_RELEVANT = "student_attributes_are_relevant"
    PROJECT_REQUIREMENTS_ARE_SATISFIED = "project_requirements_are_satisfied"


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


class PriorityType(Enum):
    TOKENIZATION = "tokenization"
    DIVERSITY = "diversity"
    PROJECT_PREFERENCE = "project_preference"
    PROJECT_REQUIREMENT = "project_requirement"
    SOCIAL_PREFERENCE = "social_preference"


class CampusLocation(AttributeValueEnum):
    Kelowna = 1
    Vancouver = 2

class YearLevel(AttributeValueEnum):
    First = 0
    Second = 1
    Third = 2
    Fourth = 3
    Graduate = 4

# From paper: https://sigcse2023.sigcse.org/details/sigcse-ts-2023-papers/163/Inclusive-study-group-formation-at-scale
class AlRace(AttributeValueEnum):
    White = "White"
    Asian = "Asian"
    Hispanic = "Hispanic"
    Black_Or_African_American = "Black/African American"
    Indegenous = "Indegenous"
    Middle_Eastern = "Middle-Eastern"
    Multiple_Races = "Multiple races"


class AlYearLevel(AttributeValueEnum):
    Freshman = "freshman"
    Sophomore = "sophomore"
    Junior = "junior"
    Senior = "senior"
    Graduate = "graduate"


class AlGender(AttributeValueEnum):
    Female = "Female"
    Male = "Male"
    Other = "Other"


def fromGenderToAlGender(gender: Gender) -> AlGender:
    if gender == Gender.MALE:
        return AlGender.Male
    if gender == Gender.FEMALE:
        return AlGender.Female
    return AlGender.Other


def fromAlGenderToGender(alGenderNum: int or str) -> Gender:
    if alGenderNum == 0 or alGenderNum == "Male":
        return Gender.FEMALE
    if alGenderNum == 1 or alGenderNum == "Female":
        return Gender.MALE
    return Gender.OTHER


def fromRaceToAlRace(race: Race) -> AlRace:
    if race == Race.European:
        return AlRace.White
    if (
        race == Race.South_Asian
        or race == Race.East_Asian
        or race == Race.South_East_Asian
    ):
        return AlRace.Asian
    if race == Race.Hispanic_or_Latin_American:
        return AlRace.Hispanic
    if race == Race.African:
        return AlRace.Black_Or_African_American
    if race == Race.First_Nations_or_Indigenous:
        return AlRace.Indegenous
    if race == Race.Middle_Eastern:
        return AlRace.Middle_Eastern
    if race == Race.Other:
        return AlRace.Multiple_Races


def fromAlRaceToRace(alRaceNum: int or str) -> Race:
    if alRaceNum == 0 or alRaceNum == "White":
        return Race.European
    if alRaceNum == 1 or alRaceNum == "Asian":
        return Race.South_Asian
    if alRaceNum == 2 or alRaceNum == "Hispanic":
        return Race.Hispanic_or_Latin_American
    if alRaceNum == 3 or alRaceNum == "Black/African American":
        return Race.African
    if alRaceNum == 4 or alRaceNum == "Indegenous":
        return Race.First_Nations_or_Indigenous
    if alRaceNum == 5 or alRaceNum == "Middle-Eastern":
        return Race.Middle_Eastern
    if alRaceNum == 6 or alRaceNum == "Multiple races":
        return Race.Other


def fromYearLevelToAlYearLevel(yearLevel: int) -> AlYearLevel:
    if yearLevel == 0:
        return AlYearLevel.Freshman
    if yearLevel == 1:
        return AlYearLevel.Sophomore
    if yearLevel == 2:
        return AlYearLevel.Junior
    if yearLevel == 3:
        return AlYearLevel.Senior
    return AlYearLevel.Graduate


def fromAlYearLevelToYearLevel(alYearLevel: str) -> int:
    if "freshman" in alYearLevel.lower():
        return 0
    if "sophomore" in alYearLevel.lower():
        return 1
    if "junior" in alYearLevel.lower():
        return 2
    if "senior" in alYearLevel.lower():
        return 3
    return 4


def fromNumbersToTimeSlots(numbers: List[int]) -> List[str]:
    return [fromNumberToTimeslot(number) for number in numbers]


def fromNumberToTimeslot(number: int) -> str:
    return str(number)


def fromTimeslotToNumber(timeslot: str) -> int:
    return int(timeslot)


def fromTimeslotsToNumbers(timeslots: List[str]) -> List[int]:
    return [fromTimeslotToNumber(timeslot) for timeslot in timeslots]
