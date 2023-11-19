from typing import List

from api.models.enums import Relationship
from api.models.student import Student


def create_neutral(_id: int):
    return Student(_id=_id)


def create_friend(_id: int, friend_ids: List[int]):
    return Student(
        _id=_id, relationships={_: Relationship.FRIEND for _ in friend_ids if _ != _id}
    )


def create_enemy(_id: int, enemy_ids: List[int]):
    return Student(
        _id=_id, relationships={_: Relationship.ENEMY for _ in enemy_ids if _ != _id}
    )


def create_social_students(
    num_friends=None,
    num_enemies=None,
    num_neutrals=None,
    num_fans=None,
    num_haters=None,
    num_outcasts=None,
) -> List[Student]:
    students = []

    if num_friends:
        start_id = len(students) + 1
        friend_ids = list(range(start_id, start_id + num_friends))
        students.extend([create_friend(_, friend_ids) for _ in friend_ids])

    if num_enemies:
        start_id = len(students) + 1
        enemy_ids = list(range(start_id, start_id + num_enemies))
        students.extend([create_enemy(_, enemy_ids) for _ in enemy_ids])

    if num_neutrals:
        start_id = len(students) + 1
        neutral_ids = list(range(start_id, start_id + num_neutrals))
        students.extend([create_neutral(_) for _ in neutral_ids])

    if num_fans:
        start_id = len(students) + 1
        fan_ids = list(range(start_id, start_id + num_fans))
        existing_student_ids = [_.id for _ in students]
        students.extend([create_friend(_, existing_student_ids) for _ in fan_ids])

    if num_haters:
        start_id = len(students) + 1
        hater_ids = list(range(start_id, start_id + num_haters))
        existing_student_ids = [_.id for _ in students]
        students.extend([create_enemy(_, existing_student_ids) for _ in hater_ids])

    if num_outcasts:
        start_id = len(students) + 1
        outcast_ids = list(range(start_id, start_id + num_outcasts))
        existing_student_ids = [_.id for _ in students]
        outcasts = [create_enemy(_, existing_student_ids) for _ in outcast_ids]
        for existing_student in students:
            existing_student.relationships.update(
                {_: Relationship.ENEMY for _ in outcast_ids}
            )
        students.extend(outcasts)

    return students
