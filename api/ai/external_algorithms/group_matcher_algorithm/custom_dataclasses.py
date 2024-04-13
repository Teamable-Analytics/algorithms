from dataclasses import dataclass
from typing import Dict, Iterator

import faker
from pandas import DataFrame

from api.ai.external_algorithms.group_matcher_algorithm.utils import (
    fromYearLevelToAlYearLevel,
    fromNumbersToTimeSlots,
    fromGenderToAlGender,
    fromRaceToAlRace,
)
from api.dataclasses.enums import ScenarioAttribute, Gender, Race
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet


@dataclass
class GroupMatcherStudent(Student):
    def __init__(self, student: Student):
        super().__init__(
            student.id,
            student.name,
            student.attributes,
            student.relationships,
            student.project_preferences,
            student.team,
        )
        self.email = faker.Faker().email()
        if not self.name:
            self.name = faker.Faker().name()

    def get_formatted_data(self):
        return {
            "Email Address": self.email,
            "SID": self.id,
            "First name": self.name.split()[0],
            "Last name": self.name.split()[1],
            "What year are you": fromYearLevelToAlYearLevel(
                self.attributes.get(ScenarioAttribute.YEAR_LEVEL.value, [1])[0]
            ).value,
            "Would you like to be part of a course study group?": "Yes",
            "Do you have an existing study group of size 2-6 in mind": "No",
            "timezone offset": "-7",  # all the same timezone
            "Would you like to attend the same discussion": "Yes",
            "discussion section times": fromNumbersToTimeSlots(
                self.attributes.get(
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value, ["1"]
                )
            ),
            "Will you be on the Berkeley campus": "Yes",  # No remote students
            "Which of these options best describes your race?": fromRaceToAlRace(
                Race(self.attributes.get(ScenarioAttribute.RACE.value, [Race.Other])[0])
            ).value,
            "How do you self-identify?": fromGenderToAlGender(
                Gender(self.attributes[ScenarioAttribute.GENDER.value][0])
            ).value,
        }

    @staticmethod
    def transform_output_data_to_team_set(
        output_data: DataFrame,
        team_trace: Dict[int, Team],
        student_trace: Dict[int, Student],
        team_cycler: Iterator[Team],
    ) -> TeamSet:
        for _, row in output_data.iterrows():
            student_id = row["sid"]
            group_num = int(row["group_num"]) + 1
            if group_num not in team_trace.keys():
                new_team_attributes = next(team_cycler)
                new_team = Team(
                    _id=len(team_trace) + 1,
                    name=f"Team {len(team_trace) + 1}",
                    requirements=new_team_attributes.requirements,
                    project_id=new_team_attributes.project_id,
                    students=[],
                )
                team_trace[int(row["group_num"]) + 1] = new_team

            student = student_trace[student_id]
            team = team_trace[int(row["group_num"]) + 1]

            student.add_team(team)
            team.add_student(student)

        return TeamSet(
            teams=[team for team in team_trace.values() if len(team.students) > 0]
        )
