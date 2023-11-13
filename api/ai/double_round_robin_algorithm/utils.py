from typing import List, Dict

from api.ai.double_round_robin_algorithm.custom_models import Utility
from api.models.student import Student
from api.models.team import Team


def calculate_utilities(
    teams: List[Team], students: List[Student]
) -> Dict[int, Dict[int, Utility]]:
    utilities: Dict[int, Dict[int, Utility]] = {team.project_id: {} for team in teams}

    for team in teams:
        for student in students:
            student_utilities = sum(
                [
                    student.meets_requirement(requirement)
                    for requirement in team.requirements
                ]
            )

            utilities[team.project_id][student.id] = Utility(
                student_utilities, student, team.project_id
            )

    return utilities
