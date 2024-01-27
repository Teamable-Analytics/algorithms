import json
from typing import List

from api.models.enums import Gender, ScenarioAttribute, Relationship, YearLevel
from api.models.student import Student, StudentSerializer
from api.models.team import Team, TeamSerializer

if __name__ == "__main__":
    output = {
        "students": [],
        "teams": [],
    }

    with open("gen_group_set-20220331_141058.json", "r") as f:
        json_dict = json.load(f)

        for key, data in json_dict["gen_group_set"].items():
            members = data.get("members") or []
            name = data.get("name") or ""

            # Create team
            team = Team(
                _id=int(key),
                name=name,
            )

            for member in members:
                student_info = json_dict["student_info"].get(str(member))
                if not student_info:
                    print(key, name)
                else:
                    role = student_info.get("role")
                    if not role or role != "Student":
                        print(key, name, member)

                student_response = json_dict["student_responses"].get(str(member)) or {}

                student_gender = student_response.get("81") or [Gender.NA.value]

                relationships = {}
                for _ in student_response.get("74") or []:
                    relationships[_] = Relationship.FRIEND
                for _ in student_response.get("75") or []:
                    relationships[_] = Relationship.ENEMY

                timeslot_availability: List[int] = student_response.get("73") or []
                if timeslot_availability == [-1]:
                    timeslot_availability = []

                # A student will have one of the following values: 1: 341, 2: 541, -1: no answer to survey
                x = student_response.get("72") or [-1]
                year_level = [
                    (
                        YearLevel.Third.value
                        if _ == 1
                        else YearLevel.Graduate.value
                        if _ == 2
                        else _
                    )
                    for _ in x
                ]

                # effort level [1-4]
                # 1 - I expect to participate minimally because this class is a requirement and I just need to pass
                # 2 - I expect to participate when it's convenient for me because I have other classes and work that are more important than this class
                # 3 - I expect to participate as much as needed because I want to get a good grade in this class
                # 4 - I expect to participate actively and learn as much as I can because the topic of this class is a potential future career direction for me
                effort_level = student_response.get("82") or [1]

                # Create student
                student = Student(
                    _id=int(member),
                    attributes={
                        ScenarioAttribute.GENDER.value: student_gender,
                        ScenarioAttribute.TIMESLOT_AVAILABILITY.value: timeslot_availability,
                        ScenarioAttribute.YEAR_LEVEL.value: year_level,
                        100: effort_level,
                    },
                    relationships=relationships,
                )

                # Add student to team
                team.add_student(student)

                # Add student to students list
                output["students"].append(student)

            # Add team to output
            output["teams"].append(team)

    # Check that student list is unique
    ids = [student.id for student in output["students"]]
    if len(set(ids)) != len(ids):
        print("Duplicate student ids found")

    # Format output to json
    json_output = {
        "teams": json.loads(json.dumps(output["teams"], cls=TeamSerializer)),
        "students": json.loads(
            json.dumps(output["students"], cls=StudentSerializer),
        ),
    }

    # Write json
    with open("COSC341_W2021T2_data.json", "w+") as f:
        json.dump(json_output, f)
