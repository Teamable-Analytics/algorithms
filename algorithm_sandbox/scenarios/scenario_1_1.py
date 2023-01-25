from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions, WeightAlgorithm
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority

priorities = [
    {
        'order': 1,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 0,  # age
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # ignored
    },
    {
        'order': 2,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 1,  # gender
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # female
    },
    {
        'order': 3,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 2,  # GPA
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # ignored
    },
    {
        'order': 4,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 3,  # Race
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # ignored
    },
    {
        'order': 5,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 4,  # major
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # ignored
    },
    {
        'order': 6,
        'constraint': Priority.TYPE_DIVERSIFY,
        'skill_id': 5,  # Year level
        'limit_option': Priority.MIN_OF,
        'limit': 1,  # don't include min of
        'value': 1,  # ignored
    },
]

algorithm_options = AlgorithmOptions(
    priorities=priorities,
    diversify_options=[
        {'id': 0},
        {'id': 1},
        {'id': 2},
        {'id': 3},
        {'id': 4},
        {'id': 5},
    ],
    diversity_weight=1,
)


def s1_1_options():
    return priorities, algorithm_options

