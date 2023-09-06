from models.enums import Relationship, RequirementType
from models.project import ProjectRequirement
from models.student import Student


def num_friends_satisfied(student: Student) -> int:
    count = 0
    for student_id, relation in student.relationships.items():
        if relation != Relationship.FRIEND:
            continue
        for teammate in student.team.students:
            if teammate.id != student_id:
                count += 1
    return count


def num_enemies_satisfied(student: Student) -> int:
    count = 0
    for student_id, relation in student.relationships.items():
        if relation != Relationship.ENEMY:
            continue
        count += 1
        for teammate in student.team.students:
            if teammate.id != student_id:
                count -= 1
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
        if requirement.operator == RequirementType.LESS_THAN:
            is_met |= value < requirement.value
        elif requirement.operator == RequirementType.MORE_THAN:
            is_met |= value > requirement.value
        else:
            is_met |= value == requirement.value
    return is_met
