from typing import List

from api.models.enums import RequirementOperator
from api.models.project import Project, ProjectRequirement
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.custom_student_providers import (
    PROGRAMMING_LANGUAGE,
)


def get_custom_projects() -> List[Project]:
    all_projects = []
    for i in range(30):
        all_projects.append(
            Project(
                _id=i,
                name=f"Project {i}",
                requirements=[
                    ProjectRequirement(
                        attribute=PROGRAMMING_LANGUAGE,
                        operator=RequirementOperator.EXACTLY,
                        value=i,
                        # bueno
                    ),
                ],
            )
        )
    return all_projects
