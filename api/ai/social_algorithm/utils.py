from typing import List

from api.ai.social_algorithm.custom_models import TeamWithCliques
from api.models.student import Student


def clique_is_valid(clique: List[Student]) -> bool:
    """
    A valid clique in this context means a clique where all members are not already in teams
    """
    for student in clique:
        if student.team is not None:
            return False
    return True


def clique_ids_to_student_list(
    students: List[Student], clique_ids: [int]
) -> List[List[Student]]:
    cliques = []
    for clique in clique_ids:
        clique_students = [student for student in students if student.id in clique]
        cliques.append(clique_students)
    return cliques


def valid_clique_list(cliques: List[List[Student]]) -> List[List[Student]]:
    valid_cliques = [clique for clique in cliques if clique_is_valid(clique)]
    return valid_cliques


def clean_clique_list(cliques: List[List[Student]]) -> List[List[Student]]:
    seen_students = []
    cleaned_cliques = []
    for clique in cliques:
        if any([student in seen_students for student in clique]):
            continue
        cleaned_cliques.append(clique)
        seen_students += clique
    return cleaned_cliques


def next_empty_team(teams: List[TeamWithCliques]) -> TeamWithCliques:
    for team in teams:
        if team.size == 0:
            return team


def has_empty_teams(teams: List[TeamWithCliques]) -> bool:
    _next_empty_team = next_empty_team(teams)
    return bool(_next_empty_team)
