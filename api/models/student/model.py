import random
from dataclasses import dataclass, field
from typing import List, Dict

import faker

from api.models.enums import Relationship, RequirementOperator, fromYearLevelToAlYearLevel, ScenarioAttribute, \
    fromNumbersToTimeSlots, fromGenderToAlGender, Gender, fromRaceToAlRace, Race
from api.models.project import ProjectRequirement


@dataclass
class Student:
    _id: int
    name: str = None
    attributes: Dict[int, List[int]] = field(default_factory=dict)
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    project_preferences: List[int] = field(default_factory=list)
    team: "Team" = None

    @property
    def id(self) -> int:
        return self._id

    def add_team(self, team: "Team"):
        if self.team:
            raise ValueError(
                f"Cannot add student ({self.id}) to team ({team.name}). Student already has a team ({self.team.name})"
            )
        self.team = team

    def meets_requirement(self, requirement: ProjectRequirement) -> bool:
        is_met = False
        # note that attributes are modelled as lists of integers
        for value in self.attributes.get(requirement.attribute, []):
            if requirement.operator == RequirementOperator.LESS_THAN:
                is_met |= value < requirement.value
            elif requirement.operator == RequirementOperator.MORE_THAN:
                is_met |= value > requirement.value
            else:  # default case is RequirementOperator.EXACTLY
                is_met |= value == requirement.value
        return is_met

    def __post_init__(self):
        if not self.name:
            self.name = faker.Faker().name()


    def to_opponent_data_format(self):
        dictionary = {
            'Email Address': faker.Faker().email(),
            'SID': self.id,
            'First name': self.name.split()[0],
            'Last name': self.name.split()[1],
            'What year are you': fromYearLevelToAlYearLevel(self.attributes[ScenarioAttribute.YEAR_LEVEL.value][0]).value,
            'Would you like to be part of a course study group?': 'Yes',
            'Do you have an existing study group of size 2-6 in mind': 'No',
            'timezone offset': '-7',  # all the same timezone
            'Would you like to attend the same discussion': 'Yes',
            'discussion section times': fromNumbersToTimeSlots(self.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]),
            '2nd Group Member Berkeley Student Email': '',
            '3rd Group Member Berkeley Student Email': '',
            '4th Group Member Berkeley Student Email': '',
            '5th Group Member Berkeley Student Email': '',
            '6th Group Member Berkeley Student Email': '',
            'Will you be on the Berkeley campus': 'Yes',    # No remote students
            'Which of these options best describes your race?': fromRaceToAlRace(Race(self.attributes[ScenarioAttribute.RACE.value][0])).value,
            'How do you self-identify?': fromGenderToAlGender(Gender(self.attributes[ScenarioAttribute.GENDER.value][0])).value
        }
        return dictionary
