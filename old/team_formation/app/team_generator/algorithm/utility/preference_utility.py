def get_preference_utility(team, student, project_preference_len):
    """
    Returns mapped preference value for each student.
    The value gets mapped and normalized between a range of [0,1].

    *If project_preference_len is none then the student is a perfect match*

    Parameters
    ----------
    team: Team
        Team object
    student: Student
        Student object
    project_preference_len: int
        Max preference length

    Returns
    -------
    float:
        preference utility
    """
    if not project_preference_len:
        return 0
    preferences = student.project_preferences
    team_project = team.project_id
    value = project_preference_len
    for pref_value in preferences.values():
        if pref_value == team_project:
            break
        else:
            value -= 1
    # normalize and map value to avoid scaling errors
    value = value / project_preference_len
    scaled_value = scale_preference_utility(value)
    return scaled_value


def scale_preference_utility(value):
    return value ** (1 / 3)
