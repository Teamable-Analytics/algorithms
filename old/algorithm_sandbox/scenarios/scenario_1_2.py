from old.team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions
from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority import (
    Priority,
)

priorities = [
    {
        "order": 1,
        "constraint": Priority.TYPE_CONCENTRATE,
        "skill_id": 2,  # GPA
        "limit_option": Priority.MAX_OF,
        "limit": 1000000,  # don't include max of
        "value": 1,  # ignored
    },
]

algorithm_options = AlgorithmOptions(
    priorities=priorities,
    concentrate_options=[
        {"id": 2},
    ],
    diversity_weight=1,
    social_weight=0,
    preference_weight=0,
    requirement_weight=0,
)


def s1_2_options():
    return priorities, algorithm_options
