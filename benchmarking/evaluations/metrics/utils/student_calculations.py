from api.dataclasses.enums import Relationship, RequirementOperator
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.student import Student


def num_friends_satisfied(student: Student) -> int:
    count = 0
    for relation_student_id, relation in student.relationships.items():
        if relation != Relationship.FRIEND or relation_student_id == student.id:
            continue
        if relation_student_id in [t.id for t in student.team.students]:
            count += 1
    return count


def num_enemies_satisfied(student: Student) -> int:
    count = 0
    for relation_student_id, relation in student.relationships.items():
        if relation != Relationship.ENEMY or relation_student_id == student.id:
            continue
        if relation_student_id not in [t.id for t in student.team.students]:
            count += 1
    return count


def is_happy_student_friend(student: Student) -> bool:
    total = list(student.relationships.values()).count(Relationship.FRIEND)
    return total == 0 or num_friends_satisfied(student) > 0


def is_strictly_happy_student_friend(student: Student) -> bool:
    total = list(student.relationships.values()).count(Relationship.FRIEND)
    return num_friends_satisfied(student) == total


def is_happy_student_enemy(student: Student) -> bool:
    total = list(student.relationships.values()).count(Relationship.ENEMY)
    return total == 0 or num_enemies_satisfied(student) > 0


def is_strictly_happy_student_enemy(student: Student) -> bool:
    total = list(student.relationships.values()).count(Relationship.ENEMY)
    return num_enemies_satisfied(student) == total


def has_friend_and_no_enemies(student: Student) -> bool:
    num_friend_requests = list(student.relationships.values()).count(
        Relationship.FRIEND
    )
    friends_in_team = num_friends_satisfied(student)
    if num_friend_requests > 0 and friends_in_team == 0:
        return False
    num_enemy_requests = list(student.relationships.values()).count(Relationship.ENEMY)
    enemies_satisfied = num_enemies_satisfied(student)
    return num_enemy_requests == enemies_satisfied
