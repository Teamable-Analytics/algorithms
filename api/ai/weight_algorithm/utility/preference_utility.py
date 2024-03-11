from api.dataclasses.student import Student
from api.dataclasses.team import Team


def get_preference_utility(
    team: Team, student: Student, max_project_preferences_per_student: int
) -> float:
    """
    Returns mapped preference value for each student.
    The value gets mapped and normalized between a range of [0,1].

    *If project_preference_len is none then the student is a perfect match*
    """
    if not max_project_preferences_per_student:
        return 0
    team_project = team.project_id
    value = max_project_preferences_per_student
    for project_id in student.project_preferences:
        if project_id == team_project:
            break
        else:
            value -= 1
    # normalize and map value to avoid scaling errors
    value = value / max_project_preferences_per_student
    scaled_value = scale_preference_utility(value)
    return scaled_value


def scale_preference_utility(value: float) -> float:
    return value ** (1 / 3)
