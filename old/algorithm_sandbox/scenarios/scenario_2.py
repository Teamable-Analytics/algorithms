from old.team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions

priorities = []

algorithm_options = AlgorithmOptions(
    diversity_weight=0,
    social_weight=1,
    preference_weight=0,
    requirement_weight=0,
    whitelist_behaviour="enforce",
    blacklist_behaviour="enforce",
)


def s2_options():
    return priorities, algorithm_options
