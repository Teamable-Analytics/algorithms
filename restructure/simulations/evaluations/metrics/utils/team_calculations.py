from collections import defaultdict

from restructure.models.team import Team


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
