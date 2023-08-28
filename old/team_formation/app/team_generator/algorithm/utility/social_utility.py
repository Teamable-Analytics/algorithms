from typing import List

from old.team_formation.app.team_generator.algorithm.consts import LOW_WEIGHT, HIGH_WEIGHT
from old.team_formation.app.team_generator.algorithm.utility.social_network import SocialNetwork
from old.team_formation.app.team_generator.student import Student


def get_social_utility(team, students: List[Student]):
    diameter_old = SocialNetwork(team.students).get_diameter()
    diameter_new = SocialNetwork(team.students + students).get_diameter()

    norm_value = _normalize_social_utility(diameter_old - diameter_new)
    scaled_value = _scale_social_utility(norm_value)
    return scaled_value


def _normalize_social_utility(value):
    theo_min = LOW_WEIGHT - HIGH_WEIGHT
    theo_max = HIGH_WEIGHT - 2 * LOW_WEIGHT
    n = (value - theo_min) / (theo_max - theo_min)
    return n


def _scale_social_utility(value):
    return value ** (1 / 3)
