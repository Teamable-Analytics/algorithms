from typing import List, Dict

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

    # Get project req distribution
    other_attributes: Dict[int, Dict[int, int]] = {
        293: {},
        294: {},
        295: {},
        297: {},
        298: {},
        304: {},
        305: {},
        306: {},
        307: {},
        308: {},
        310: {},
        311: {},
        312: {},
        313: {},
        314: {},
        315: {},
        316: {},
        317: {},
        318: {},
        319: {},
        321: {},
        323: {},
        324: {},
        325: {},
        326: {},
        327: {},
        328: {},
        329: {},
        332: {},
    }
    for s in students:
        for attribute_type in other_attributes.keys():
            student_attribute = s.attributes.get(attribute_type) or []
            for attr_val in student_attribute:
                if attr_val not in other_attributes[attribute_type]:
                    other_attributes[attribute_type][attr_val] = 0
                other_attributes[attribute_type][attr_val] += 1
    print(other_attributes)
