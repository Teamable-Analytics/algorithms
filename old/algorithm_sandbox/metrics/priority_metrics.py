from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority import (
    Priority,
)
from old.team_formation.app.team_generator.team import Team


def is_priority_satisfied(team: Team, priority):
    students = team.students
    skill_id = priority["skill_id"]
    cnt = {}
    for student in students:
        value = student.get_skill(skill_id)[0]
        if value not in cnt:
            cnt[value] = 0
        cnt[value] += 1

    for value in cnt.values():
        if priority["limit_option"] == Priority.MIN_OF:
            if value < priority["limit"]:
                return False
        else:
            if value > priority["limit"]:
                return False
    return True


def gini_index(team: Team, priority):
    students = team.students
    skill_id = priority["skill_id"]
    cnt = {}
    for student in students:
        value = student.get_skill(skill_id)[0]
        if value not in cnt:
            cnt[value] = 0
        cnt[value] += 1

    gini = 0
    for value in cnt.values():
        gini += value * (value - 1)

    gini = gini / (len(students) * (len(students) - 1))
    return 1 - gini


def get_priority_metrics(teams: list[Team], priorities):
    metrics = {
        "EXP": 0,
        "LN": 0,
        "MAX": 0,
        "AVG_GINI": 0,
    }

    k = len(priorities)
    m = len(teams)

    for i, priority in enumerate(priorities):
        total_sat = True
        for j, team in enumerate(teams):
            sat = is_priority_satisfied(team, priority)
            if not sat:
                total_sat = False

            metrics["LN"] += sat * (k - i) / (k * (k + 1) / 2) / m
            metrics["EXP"] += sat * (2 ** (k - i - 1)) / (2**k - 1) / m
            metrics["AVG_GINI"] += gini_index(team, priority) / m / k
        if total_sat:
            metrics["MAX"] = i + 1

    return metrics
