from typing import List, Dict

from api.ai.double_round_robin_algorithm.custom_models import Utility
from api.models.enums import RequirementOperator
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team import Team


def requirement_met_by_student(requirement: ProjectRequirement, student: Student):
    is_met = False
    for attr in student.attributes[requirement.attribute]:
        if requirement.operator == RequirementOperator.LESS_THAN:
            is_met |= attr < requirement.value
        elif requirement.operator == RequirementOperator.MORE_THAN:
            is_met |= attr > requirement.value
        else:  # default case is 'exactly'
            is_met |= attr == requirement.value
    return 1 if is_met else -1


def calculate_utilities(
    teams: List[Team], students: List[Student]
) -> Dict[int, Dict[int, Utility]]:
    utilities: Dict[int, Dict[int, Utility]] = {team.project_id: {} for team in teams}

    for team in teams:
        for student in students:
            student_utilities = sum(
                [
                    requirement_met_by_student(requirement, student)
                    for requirement in team.requirements
                ]
            )

            utilities[team.project_id][student.id] = Utility(
                student_utilities, student, team.project_id
            )

    return utilities
