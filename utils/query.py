import json
from typing import List

import jmespath


def num_of_each_attribute_per_team(
    file_path: str, attribute: int, attribute_value: any
) -> List[List]:
    """
    Used to count the number of students on each team that has a given attribute.
    The function returns a list of lists where each inner list is the count of students on each team in the team set
    that have the attribute specified in the function parameters.
    num_of_each_attribute_per_team('path', 1, 2) will count how many students have the value 2 in their attribute array
    with key 1.
    Note that this function will only work if the attribute array key is numeric.
    """
    with open(file_path) as f:
        json_data = json.load(f)
    return [
        jmespath.search(
            f'team_sets[{i}].teams[].length(students[?attributes."{attribute}" | contains(@,`{attribute_value}`)])',
            json_data,
        )
        for i in range(len(json_data["team_sets"]))
    ]
