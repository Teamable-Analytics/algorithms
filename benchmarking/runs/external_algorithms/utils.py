from typing import List

from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell


def calculate_student_utility(student: Student, team: TeamShell) -> float:
    """
    Calculate the utility of a student in a team
    """
    if len(team.requirements) == 0:
        return 0

    return team.num_requirements_met_by_student(student) / len(team.requirements)


def calculate_students_utilities(students: List[Student], team: TeamShell) -> float:
    """
    Calculate the utility of a list of students in a team
    """
    if len(students) == 0:
        return 0

    return sum(
        [calculate_student_utility(student, team) for student in students]
    ) / len(students)
