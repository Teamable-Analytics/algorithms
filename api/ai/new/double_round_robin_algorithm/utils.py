from typing import List, Dict

from api.ai.new.double_round_robin_algorithm.custom_models import Utility
from api.models.enums import RequirementOperator
from api.models.project import Project, ProjectRequirement
from api.models.student import Student


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
    projects: List[Project], students: List[Student]
) -> Dict[int, Dict[int, Utility]]:
    utilities: Dict[int, Dict[int, Utility]] = {project.id: {} for project in projects}

    for project in projects:
        for student in students:
            student_utilities = sum(
                [
                    requirement_met_by_student(requirement, student)
                    for requirement in project.requirements
                ]
            )

            utilities[project.id][student.id] = Utility(
                student_utilities, student, project
            )

    return utilities
