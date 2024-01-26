import json
from typing import List, Dict

from api.models.enums import (
    ScenarioAttribute,
    Relationship,
    Gpa,
    RequirementOperator,
)
from api.models.project import Project, ProjectRequirement
from api.models.student import Student, StudentSerializer
from api.models.team import Team, TeamSerializer

if __name__ == "__main__":
    output = {
        "students": [],
        "teams": [],
    }

    # See attributes.json for description of each attribute
    projects: Dict[int, Project] = {
        175: Project(
            _id=175,
            name="Gamified Coding Practice Platform -  Learnification Technologies",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=324,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=327,
                ),
            ],
        ),
        174: Project(
            _id=174,
            name="Peer Review Application - Learnification Technologies",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=324,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=327,
                ),
            ],
        ),
        172: Project(
            _id=172,
            name="Automating Database Question Generation and Marking",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=323,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=304,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=327,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=328,
                ),
            ],
        ),
        177: Project(
            _id=177,
            name="Manpower/scheduling Board - Horizon Electric",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=304,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=325,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=326,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=332,
                ),
            ],
        ),
        173: Project(
            _id=173,
            name="Apple Database and Image Analysis",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=305,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=304,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=325,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=332,
                ),
            ],
        ),
        178: Project(
            _id=178,
            name="Love for Vernon Community Calendar",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=323,
                ),
            ],
        ),
        176: Project(
            _id=176,
            name="Rental Marketplace Tool - RentalHut Inc.",
            requirements=[
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=307,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=2,
                    attribute=304,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=327,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=328,
                ),
                ProjectRequirement(
                    operator=RequirementOperator.MORE_THAN,
                    value=1,
                    attribute=325,
                ),
            ],
        ),
    }

    with open("gen_group_set-20240125_110626.json", "r") as f:
        json_dict = json.load(f)

        for key, data in json_dict["gen_group_set"].items():
            members = data.get("members") or []
            name = data.get("name") or ""

            for i, project in projects.items():
                if project.name in name:
                    project_id = i
                    break

            # Create team
            team = Team(
                _id=int(key),
                name=name,
                project_id=project_id or -1,
                requirements=projects[project_id].requirements,
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

                relationships = {}
                for sid in student_response.get("300") or []:
                    if sid != -1:
                        relationships[sid] = Relationship.FRIEND
                for sid in student_response.get("331") or []:
                    if sid != -1:
                        relationships[sid] = Relationship.ENEMY

                timeslot_availability: List[int] = student_response.get("301") or []

                gpa = student_response.get("292") or []
                gpa_mapping = {
                    5: Gpa.A.value,
                    4: Gpa.B.value,
                    3: Gpa.C.value,
                    2: Gpa.D.value,
                    1: Gpa.F.value,
                }
                gpa = [_ for _ in map(lambda x: gpa_mapping[x], gpa) if _ != -1]

                project_preferences = [
                    _ for _ in student_response.get("333") or [] if _ != -1
                ]

                # Other attributes to include
                # See attributes.json for what each attribute is.
                # And see the "attribute_info" key in gen_group_set-20240125_110626.json
                # for the values + descriptions of each possible answer.
                other_attributes: List[Dict[str, int]] = [
                    293,
                    294,
                    295,
                    297,
                    298,
                    304,
                    305,
                    306,
                    307,
                    308,
                    310,
                    311,
                    312,
                    313,
                    314,
                    315,
                    316,
                    317,
                    318,
                    319,
                    321,
                    323,
                    324,
                    325,
                    326,
                    327,
                    328,
                    329,
                    332,
                ]
                students_other_attributes = {}
                for a in other_attributes:
                    val = student_response.get(str(a))
                    if not val or val == [-1]:
                        val = []
                    students_other_attributes[a] = val

                # Create student
                student = Student(
                    _id=int(member),
                    attributes={
                        ScenarioAttribute.GPA.value: gpa,
                        ScenarioAttribute.TIMESLOT_AVAILABILITY.value: timeslot_availability,
                        **students_other_attributes,
                    },
                    relationships=relationships,
                    project_preferences=project_preferences,
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
    with open("COSC499_S2023_data.json", "w+") as f:
        json.dump(json_output, f, indent=2)
