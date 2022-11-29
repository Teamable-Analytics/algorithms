import random

from team_formation.app.team_generator.algorithm.consts import DEFAULT, FRIEND, ENEMY
from team_formation.app.team_generator.student import Student

CUSTOM_STUDENTS_1 = [
    Student(1, relationships={
        2: FRIEND,
        3: FRIEND
    }),
    Student(2, relationships={
        1: FRIEND,
        3: FRIEND
    }),
    Student(3, relationships={
        1: FRIEND,
        2: FRIEND,  # TODO: change to test behaviour when this is an ENEMY connection
        4: FRIEND,
        5: DEFAULT,
    }),
    Student(4, relationships={
        3: FRIEND,
        5: FRIEND
    }),
    Student(5, relationships={
        3: DEFAULT,
        4: FRIEND
    })
]


def fake_custom_students() -> [Student]:
    return CUSTOM_STUDENTS_1


def fake_all_friend_students(n: int) -> [Student]:
    students = []
    for i in range(n):
        student = Student(i, relationships={
            other_id: FRIEND for other_id in range(n)
        })
        student.relationships[i] = DEFAULT
        students.append(student)
    return students


def fake_all_neutral_students(n: int) -> [Student]:
    students = []
    for i in range(n):
        student = Student(i, relationships={
            other_id: DEFAULT for other_id in range(n)
        })
        students.append(student)
    return students


def fake_students(
        number_of_students: int,
        number_of_friends: int,
        number_of_enemies: int,
        age_range,
        age_distribution,
        gender_options,
) -> [Student]:
    students = []
    n = number_of_students
    f = number_of_friends
    e = number_of_enemies

    g = len(gender_options)
    if type(gender_options) == list:
        genders = [random.randrange(0, g) for _ in range(n)]
    else:
        genders = []
        for i, entity in enumerate(gender_options.items()):
            genders.extend([i for _ in range(entity[1])])

    for i in range(n):
        relationships = {}
        for j in range(f):
            friend_id = random.randrange(0, n)
            relationships[friend_id] = FRIEND
        for j in range(e):
            enemy_id = random.randrange(0, n)
            relationships[enemy_id] = ENEMY
        students.append(Student(i, relationships=relationships, skills={
            0: [random.randrange(age_range[0], age_range[1])],
            1: [genders[i]],
        }))
    return students
