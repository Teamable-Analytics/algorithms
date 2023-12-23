import json
import jmespath


def num_of_each_attribute_per_team(
    file_path: str, attribute: int, attribute_value: int
):
    with open(file_path) as f:
        json_data = json.load(f)
    return [
        jmespath.search(
            f'team_sets[{i}].teams[].length(students[?attributes."{attribute}" | contains(@,`{attribute_value}`)])',
            json_data,
        )
        for i in range(len(json_data["team_sets"]))
    ]
