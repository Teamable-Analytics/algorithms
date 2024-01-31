from typing import List

from api.models.enums import ScenarioAttribute, Gender, YearLevel, Gpa, Relationship
from api.models.student import Student
from benchmarking.data.real_data.cosc499_s2023_provider.providers import (
    COSC499S2023StudentProvider,
)

if __name__ == "__main__":
    students: List[Student] = COSC499S2023StudentProvider().get()

    # Grade distribution: {A: 4, B: 16, C: 18, D: 3, F: 0}
    grade_distribution = {
        Gpa.A.value: 0,
        Gpa.B.value: 0,
        Gpa.C.value: 0,
        Gpa.D.value: 0,
        Gpa.F.value: 0,
    }
    other = 0
    for s in students:
        vals = s.attributes.get(ScenarioAttribute.GPA.value) or [-1]
        if len(vals) != 1:
            print("AAAAAA huge grade")
        if vals[0] in grade_distribution:
            grade_distribution[vals[0]] += 1
        else:
            other += 1
    print(f"Grades: {grade_distribution}, Other: {other}")

    # Get max number friends/enemies specified
    # Max friends: 3, Max enemies: 3
    max_friends = 0
    max_enemies = 0
    for s in students:
        max_friends = max(
            max_friends,
            len([_ for _, r in s.relationships.items() if r == Relationship.FRIEND]),
        )
        max_enemies = max(
            max_enemies,
            len([_ for _, r in s.relationships.items() if r == Relationship.ENEMY]),
        )
    print(f"Max friends: {max_friends}, Max enemies: {max_enemies}")
