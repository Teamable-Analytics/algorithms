from typing import Callable

from api.models.student import Student
from api.models.team_set import TeamSet


def show_team_set(team_set: TeamSet, highlight_students_by: Callable):
    print(team_set.id)
    for team in team_set.teams:
        print("\t" + str(team.id))
        print(
            "\t\t"
            + str(
                [
                    f"{s.id}{'*' if highlight_students_by(s) else ''}"
                    for s in team.students
                ]
            )
        )


def highlight_with_attribute_value(
    student: Student, attribute_id: int, value: int
) -> bool:
    return value in student.attributes.get(attribute_id, [])
