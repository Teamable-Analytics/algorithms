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
        number_of_females: int,
        number_of_friends: int,
        number_of_enemies: int,
        friend_distribution,
        age_range,
        gpa,
        race,
        major,
        year,
        time,
) -> [Student]:
    students = []
    n = number_of_students
    f = number_of_friends
    e = number_of_enemies

    genders = [1] * number_of_females + [2] * (n - number_of_females)

    for i in range(n):
        relationships = {}
        for j in range(f):
            if friend_distribution == 'cluster':
                friend_id = (i // f * f + j) % n
            else:
                friend_id = random.randrange(0, n)
            if friend_id == i:
                continue
            relationships[friend_id] = FRIEND
        for j in range(e):
            enemy_id = random.randrange(0, n)
            relationships[enemy_id] = ENEMY
        students.append(
            Student(
                i,
                relationships=relationships,
                skills={
                    0: [random.randrange(age_range[0], age_range[1])],
                    1: [genders[i]],
                    2: [random.randrange(gpa[0], gpa[1])],
                    3: [race[random.randrange(0, len(race))]],
                    4: [major[random.randrange(0, len(major))]],
                    5: [year[random.randrange(0, len(year))]],
                    6: [time[random.randrange(0, len(time))]],
                    10: [random.randint(0, 2) // 2],
                    11: [random.randint(0, 2) // 2],
                    12: [random.randint(0, 2) // 2],
                },
            )
        )
    return students
