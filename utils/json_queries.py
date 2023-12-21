import json


# def num_females_in_teams():
with open(
        'simulation_cache/priority_algorithm/all_parameters/diversify_gender_min_2/AlgorithmType.PRIORITY-max_keep_10-max_spread_1-max_iterations_10_random_start.json',
        "r") as f:
    json_data = json.load(f)
print(json_data.team_sets)
