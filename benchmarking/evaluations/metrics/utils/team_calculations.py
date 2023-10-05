from collections import defaultdict

from api.models.enums import TokenizationConstraintDirection
from api.models.team import Team
from benchmarking.evaluations.metrics.utils.student_calculations import (
    is_strictly_happy_student_friend,
    is_strictly_happy_student_enemy,
    is_happy_student_friend,
    is_happy_student_enemy,
    student_meets_requirement,
)
from api.models.tokenization_constraint import TokenizationConstraint


def team_gini_index(team: Team, attribute: int) -> float:
    students = team.students
    counter = defaultdict(int)
    for student in students:
        value = student.attributes[attribute][0]
        counter[value] += 1

    gini = 0
    for value in counter.values():
        gini += value * (value - 1)

    gini = gini / (len(students) * (len(students) - 1))
    return 1 - gini


def is_strictly_happy_team_friend(team: Team) -> bool:
    return all([is_strictly_happy_student_friend(s) for s in team.students])


def is_strictly_happy_team_enemy(team: Team) -> bool:
    return all([is_strictly_happy_student_enemy(s) for s in team.students])


def is_happy_team_1hp_friend(team: Team) -> bool:
    return any([is_happy_student_friend(s) for s in team.students])


def is_happy_team_1hp_enemy(team: Team) -> bool:
    return any([is_happy_student_enemy(s) for s in team.students])


def is_happy_team_1shp_friend(team: Team) -> bool:
    return any([is_strictly_happy_student_friend(s) for s in team.students])


def is_happy_team_1shp_enemy(team: Team) -> bool:
    return any([is_strictly_happy_student_enemy(s) for s in team.students])


def is_happy_team_allhp_friend(team: Team) -> bool:
    return all([is_happy_student_friend(s) for s in team.students])


def is_happy_team_allhp_enemy(team: Team) -> bool:
    return all([is_happy_student_enemy(s) for s in team.students])


def is_happy_team_allshp_friend(team: Team) -> bool:
    return all([is_strictly_happy_student_friend(s) for s in team.students])


def is_happy_team_allshp_enemy(team: Team) -> bool:
    return all([is_strictly_happy_student_enemy(s) for s in team.students])


def has_team_met_requirements(team: Team) -> bool:
    for requirement in team.requirements:
        is_met = False
        for student in team.students:
            is_met |= student_meets_requirement(student, requirement)
        if not is_met:
            return False
    return True


def num_satisfied_requirements(team: Team) -> int:
    num_satisfied = 0
    for requirement in team.requirements:
        is_met = False
        for student in team.students:
            is_met |= student_meets_requirement(student, requirement)
        num_satisfied += is_met
    return num_satisfied


def is_priority_satisfied(
    team: Team, attribute: int, tokenization_constraint: TokenizationConstraint
) -> bool:
    students = team.students
    counter = defaultdict(int)
    for student in students:
        value = student.attributes[attribute][0]
        counter[value] += 1

    for value in counter.values():
        if tokenization_constraint.direction == TokenizationConstraintDirection.MIN_OF:
            if value < tokenization_constraint.threshold:
                return False
        else:
            if value > tokenization_constraint.threshold:
                return False

    return True
