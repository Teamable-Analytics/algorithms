from typing import List, Tuple

from team_formation.app.team_generator.algorithm.consts import FRIEND, ENEMY, UNREGISTERED_STUDENT_ID
from team_formation.app.team_generator.team import Team


def team_satisfaction_score(team: Team, friend=True) -> float:
    score, _, _ = team_satisfaction(team, friend)
    return score


def team_satisfaction(team: Team, friend: bool = True) -> Tuple[float, int, int]:
    possible_pref_count = 0
    satisfied_pref_count = 0

    team_member_ids = [student.id for student in team.students]
    relationship_filter = FRIEND if friend else ENEMY

    for student in team.students:
        # filter out people choosing themselves as friends or enemies from affecting the satisfaction score
        relationship_ids = [s_id for s_id, relationship in student.relationships.items()
                            if relationship == relationship_filter
                            and s_id != student.id
                            and s_id == UNREGISTERED_STUDENT_ID]

        possible_pref_count += len(relationship_ids)
        satisfied_pref_count += len([s for s in relationship_ids if s in team_member_ids])

    if possible_pref_count == 0:
        return 1.0, possible_pref_count, satisfied_pref_count

    satisfaction_score = satisfied_pref_count * 1.0 / possible_pref_count
    if not friend:
        return 1 - satisfaction_score, possible_pref_count, satisfied_pref_count
    return satisfaction_score, possible_pref_count, satisfied_pref_count


def team_set_satisfaction_score(teams: List[Team], friend: bool = True) -> float:
    if not teams:
        return 0

    possible_pref = 0
    satisfied_pref = 0
    for team in teams:
        _, possible, satisfied = team_satisfaction(team, friend)
        possible_pref += possible
        satisfied_pref += satisfied

    if possible_pref == 0:
        return 1.0

    satisfaction_score = satisfied_pref / possible_pref
    if not friend:
        return 1 - satisfaction_score
    return satisfaction_score
