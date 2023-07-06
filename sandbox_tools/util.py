from typing import List

from team_generator.team import Team


def teams_are_different(teams_1: List[Team], teams_2: List[Team]) -> bool:
    if len(teams_1) != len(teams_2):
        return True
    for t1, t2 in zip(teams_1, teams_2):
        if len(t1.students) != len(t2.students):
            return True
        t2_student_ids = [s.id for s in t2.students]
        for student in t1.students:
            if student.id not in t2_student_ids:
                return True
    return False
