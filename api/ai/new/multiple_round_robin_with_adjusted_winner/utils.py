from typing import List

from api.models.project import ProjectRequirement
from api.models.student.student import Student


def calculate_value(student: Student, requirements: List[ProjectRequirement]) -> int:
    return sum(
        [
            1 if student.meets_requirement(requirement) else -1
            for requirement in requirements
        ]
    )


def is_ordered_envy_freeness_up_to_one_item(
    team_i: "TeamWithValues", team_j: "TeamWithValues"
) -> bool:
    """
    True if value of team_i is less than value of team_j and if we remove 1 student from team_j, the value of team_i is greater than the value of team_j
    False otherwise
    """
    if team_i.value >= team_j.value:
        return False

    for student in team_i.students:
        student_value_to_team_i = calculate_value(student, team_i.project.requirements)
        if team_i.value - student_value_to_team_i >= team_j.value:
            return True

    return False
