from api.models.enums import Relationship, RequirementOperator
from api.models.project import ProjectRequirement
from api.models.student import Student


def num_friends_satisfied(student: Student) -> int:
    count = 0
    for relation_student_id, relation in student.relationships.items():
        if relation != Relationship.FRIEND:
            continue
        if relation_student_id in [t.id for t in student.team.students if t.id != student.id]:
            count += 1
    return count


def num_enemies_satisfied(student: Student) -> int:
    count = 0
    for relation_student_id, relation in student.relationships.items():
        if relation != Relationship.ENEMY:
            continue
        if relation_student_id not in [t.id for t in student.team.students if t.id != student.id]:
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


def student_meets_requirement(student: Student, requirement: ProjectRequirement):
    is_met = False
    for value in student.attributes[requirement.attribute]:
        if requirement.operator == RequirementOperator.LESS_THAN:
            is_met |= value < requirement.value
        elif requirement.operator == RequirementOperator.MORE_THAN:
            is_met |= value > requirement.value
        else:
            is_met |= value == requirement.value
    return is_met
