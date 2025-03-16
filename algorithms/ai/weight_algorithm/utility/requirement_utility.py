from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team


def get_requirement_utility(team: Team, student: Student) -> float:
    """
    Gets the number of requirement met, then with the total requirements
    it calculates the normal. The normal value is scaled and returned.

    *If a team has no requirements then the student is a perfect match*
    """
    num_requirements = len(team.requirements)
    if num_requirements <= 0:
        return 1

    # calculate the total satisfaction of requirements assuming we add this student to the team
    total_requirement_satisfaction = sum(
        [
            req.satisfaction_by_students(team.students + [student])
            for req in team.requirements
        ]
    )
    normal = total_requirement_satisfaction / num_requirements
    return _scale_requirement_utility(normal)


def _scale_requirement_utility(value):
    return value ** (1 / 3)
