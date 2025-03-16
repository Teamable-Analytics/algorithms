from collections import defaultdict

from algorithms.dataclasses.enums import TokenizationConstraintDirection
from algorithms.dataclasses.team import Team
from benchmarking.evaluations.metrics.utils.student_calculations import (
    is_strictly_happy_student_friend,
    is_strictly_happy_student_enemy,
    is_happy_student_friend,
    is_happy_student_enemy,
    has_friend_and_no_enemies,
)
from algorithms.dataclasses.tokenization_constraint import TokenizationConstraint


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


def is_happy_team_all_have_friend_no_enemy(team: Team) -> bool:
    return all([has_friend_and_no_enemies(s) for s in team.students])


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
