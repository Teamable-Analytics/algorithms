from typing import Callable

from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell, Team


def is_ordered_envy_freeness_up_to_one_item(
    team_i: Team, team_j: Team, utility_function: Callable[[Student, TeamShell], float]
) -> bool:
    """
    Check if team i is envy-free up to one item to team j.


    ------

    Team i envy-freeness up to one item to team j if either:
        - Team i does not envy team j
        - Team i envies team j, but removing one student from team j makes team i not envy team j
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
