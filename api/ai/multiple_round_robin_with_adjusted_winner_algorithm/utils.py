from typing import Callable

from api.models.student import Student
from api.models.team import TeamShell, Team


def is_ordered_envy_freeness_up_to_one_item(
    team_i: Team, team_j: Team, utility_function: Callable[[Student, TeamShell], float]
) -> bool:
    """
    True if value of team_i is less than value of team_j and if we remove 1 student from team_j, the value of team_i is
    greater than the value of team_j. False otherwise
    """

    team_j_value_with_requirements_i = sum(
        utility_function(student, team_i.to_shell()) for student in team_j.students
    )
    team_i_value = sum(
        utility_function(student, team_i.to_shell()) for student in team_i.students
    )
    if team_i_value >= team_j_value_with_requirements_i:
        return True

    for student_j in team_j.students:
        student_j_value_to_team_i = utility_function(student_j, team_i.to_shell())
        team_j_without_one_student_value_to_team_i = (
            team_j_value_with_requirements_i - student_j_value_to_team_i
        )
        if team_i_value >= team_j_without_one_student_value_to_team_i:
            return True
        team_j_value_with_requirements_i += student_j_value_to_team_i

    return False
