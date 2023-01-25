from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions, WeightAlgorithm
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority

priorities = [
    {
        'order': 1,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 1,  # gender
        'limit_option': Priority.MIN_OF,
        'limit': 1,
        'value': 1,  # female
    }
]

algorithm_options = AlgorithmOptions(
    priorities=priorities,
    diversify_options=[{'id': 1}],
    diversity_weight=1,
)


def s1_options():
    return priorities, algorithm_options
