from typing import List

from api.models.enums import Gender, Race, AttributeValueEnum


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
