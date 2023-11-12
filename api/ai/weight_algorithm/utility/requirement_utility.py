from api.models.student import Student
from api.models.team import Team


def get_requirement_utility(team: Team, student: Student) -> float:
    """Return the number of requirements met as a scaled normal value

    Gets the number of requirement met, then with the total requirements
    it calculates the normal. The normal value is scaled and returned.

    *If a team has no requirements then the student is a perfect match*
    """
    total_requirements = len(team.requirements)
    if total_requirements <= 0:
        return 1
    total_met_requirements = team.num_requirements_met_by_student(student)
    normal = total_met_requirements / total_requirements
    return _scale_requirement_utility(normal)


def _scale_requirement_utility(value):
    return value ** (1 / 3)
