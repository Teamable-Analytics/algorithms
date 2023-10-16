from typing import List, Tuple, Dict

from api.models.enums import RequirementOperator, ScenarioAttribute
from api.models.project import Project, ProjectRequirement
from api.models.student import Student


def calculate_value(student: Student, requirements: List[ProjectRequirement]) -> int:
    return sum(
        [
            1 if student.meets_requirement(requirement) else -1
            for requirement in requirements
        ]
    )


def get_additive_utilities(
    students: List[Student], projects: List[Project]
) -> Dict[Tuple[int, int], int]:
    utilities: Dict[Tuple[int, int], int] = {}

    for project in projects:
        project_requirements = set(project.requirements)
        for student in students:
            student_utilities = 0
            student_attributes = student.attributes
            for attribute_id, attribute_values in student_attributes.items():
                if attribute_id in project_requirements:
                    student_utilities += sum(
                        [
                            1
                            for attribute_value in attribute_values
                            if attribute_value > 0
                        ]
                    )
                else:
                    student_utilities -= 1

            utilities[(project.id, student.id)] = student_utilities

    return utilities


def requirement_met_by_student(
    requirement: ProjectRequirement, student: Student
) -> bool:
    is_met = False
    for value in student.attributes.get(requirement.attribute):
        if requirement.operator == RequirementOperator.LESS_THAN:
            is_met |= value < requirement.value
        elif requirement.operator == RequirementOperator.MORE_THAN:
            is_met |= value > requirement.value
        else:  # default case is 'exactly'
            is_met |= value == requirement.value
    return is_met
