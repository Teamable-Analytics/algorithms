from team_formation.app.team_generator.algorithm.consts import FRIEND, ENEMY
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


def get_satisfied_friends(student: Student):
    count = 0
    for student_id, relation in student.relationships.items():
        if relation != FRIEND:
            continue
        for teammate in student.team.students:
            if teammate.id == student_id:
                count += 1
    return count


def get_satisfied_enemies(student: Student):
    count = 0
    for student_id, relation in student.relationships.items():
        if relation != ENEMY:
            continue
        count += 1
        for teammate in student.team.students:
            if teammate.id == student_id:
                count -= 1
    return count


def is_happy_student_friend(student: Student):
    total = list(student.relationships.values()).count(FRIEND)
    return total == 0 or get_satisfied_friends(student) > 0


def is_strictly_happy_student_friend(student: Student):
    total = list(student.relationships.values()).count(FRIEND)
    return get_satisfied_friends(student) == total


def is_happy_student_enemy(student: Student):
    total = list(student.relationships.values()).count(ENEMY)
    return total == 0 or get_satisfied_enemies(student) > 0


def is_strictly_happy_student_enemy(student: Student):
    total = list(student.relationships.values()).count(ENEMY)
    return get_satisfied_enemies(student) == total


def is_strictly_happy_team_friend(team: Team):
    return all([is_strictly_happy_student_friend(s) for s in team.students])


def is_strictly_happy_team_enemy(team: Team):
    return all([is_strictly_happy_student_enemy(s) for s in team.students])


def is_happy_team_1hp_friend(team: Team):
    return any([is_happy_student_friend(s) for s in team.students])


def is_happy_team_1hp_enemy(team: Team):
    return any([is_happy_student_enemy(s) for s in team.students])


def is_happy_team_1shp_friend(team: Team):
    return any([is_strictly_happy_student_friend(s) for s in team.students])


def is_happy_team_1shp_enemy(team: Team):
    return any([is_strictly_happy_student_enemy(s) for s in team.students])


def is_happy_team_allhp_friend(team: Team):
    return all([is_happy_student_friend(s) for s in team.students])


def is_happy_team_allhp_enemy(team: Team):
    return all([is_happy_student_enemy(s) for s in team.students])


def is_happy_team_allshp_friend(team: Team):
    return all([is_strictly_happy_student_friend(s) for s in team.students])


def is_happy_team_allshp_enemy(team: Team):
    return all([is_strictly_happy_student_enemy(s) for s in team.students])


def get_friend_metrics(teams: list[Team]):
    m = len(teams)

    students = []
    for t in teams:
        students.extend(t.students)

    n = len(students)

    f = [list(s.relationships.values()).count(FRIEND) for s in students]
    fs = [get_satisfied_friends(s) for s in students]

    e = [list(s.relationships.values()).count(ENEMY) for s in students]
    es = [get_satisfied_enemies(s) for s in students]

    return {
        'S_F': sum(fs) / sum(f) * 100,
        'S_E': sum(es) / sum(e) * 100,
        'AVGS_F': sum([fs[i] / f[i] for i in range(len(students))]) * 100 / n,
        'AVGS_E': sum([es[i] / e[i] for i in range(len(students))]) * 100 / n,
        'SHP_F': sum([is_strictly_happy_student_friend(s) for s in students]) * 100 / n,
        'SHP_E': sum([is_strictly_happy_student_enemy(s) for s in students]) * 100 / n,
        'SHT_F': sum([is_strictly_happy_team_friend(t) for t in teams]) * 100 / m,
        'SHT_E': sum([is_strictly_happy_team_enemy(t) for t in teams]) * 100 / m,
        'HT_1HP_F': sum([is_happy_team_1hp_friend(t) for t in teams]) * 100 / m,
        'HT_1HP_E': sum([is_happy_team_1hp_enemy(t) for t in teams]) * 100 / m,
        'HT_1SHP_F': sum([is_happy_team_1shp_friend(t) for t in teams]) * 100 / m,
        'HT_1SHP_E': sum([is_happy_team_1shp_enemy(t) for t in teams]) * 100 / m,
        'HT_ALLHP_F': sum([is_happy_team_allhp_friend(t) for t in teams]) * 100 / m,
        'HT_ALLHP_E': sum([is_happy_team_allhp_enemy(t) for t in teams]) * 100 / m,
        'HT_ALLSHP_F': sum([is_happy_team_allshp_friend(t) for t in teams]) * 100 / m,
        'HT_ALLSHP_E': sum([is_happy_team_allshp_enemy(t) for t in teams]) * 100 / m,
    }
