import json
from typing import List, Dict

from algorithms.models.enums import ScenarioAttribute, Gender, YearLevel, Gpa, Relationship
from algorithms.models.student import Student
from benchmarking.data.real_data.cosc499_s2023_provider.providers import (
    COSC499S2023StudentProvider,
)


def get_attr_values(attr_id: str, attribute_info: Dict) -> Dict[int, str]:
    questions = attribute_info[attr_id]["questions"]
    answers = questions[list(questions.keys())[0]]
    return {_[1]: _[0] for _ in answers}


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
        ScenarioAttribute.TIMESLOT_AVAILABILITY.value: {},
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
    # Swap timeslot id
    other_attributes[301] = other_attributes.pop(
        ScenarioAttribute.TIMESLOT_AVAILABILITY.value
    )
    with open("attributes.json", "r") as f:
        names = json.load(f)
        names = {_["id"]: _["name"] for _ in names}
    named_attributes = {}
    with open("gen_group_set-20240125_110626.json", "r") as f:
        data = json.load(f)
        attribute_info = data["attribute_info"]
    for a, counts in other_attributes.items():
        av = get_attr_values(str(a), attribute_info)
        named_attributes[a] = {f"{k} - {av[k]}": v for k, v in counts.items()}
    variable_names_suck = {}
    for k, v in named_attributes.items():
        variable_names_suck[f"{k} - {names[k]}"] = v

    # Validate data
    # Each attributes counts should add to 41
    for a, counts in variable_names_suck.items():
        if sum(counts.values()) != 41:
            print(f"Attribute {a} does not sum to 41: {sum(counts.values())}")

    print(json.dumps(variable_names_suck, indent=2))
