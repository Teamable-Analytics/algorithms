from typing import List

from algorithms.ai.weight_algorithm.utility.social_network import SocialNetwork
from algorithms.dataclasses.enums import Weight
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team


def get_social_utility(team: Team, students: List[Student]) -> float:
    diameter_old = SocialNetwork(team.students).get_diameter()
    diameter_new = SocialNetwork(team.students + students).get_diameter()

    norm_value = _normalize_social_utility(diameter_old - diameter_new)
    scaled_value = _scale_social_utility(norm_value)
    return scaled_value


def _normalize_social_utility(value: float) -> float:
    theo_min = Weight.LOW_WEIGHT.value - Weight.HIGH_WEIGHT.value
    theo_max = Weight.HIGH_WEIGHT.value - 2 * Weight.LOW_WEIGHT.value
    n = (value - theo_min) / (theo_max - theo_min)
    return n


def _scale_social_utility(value):
    return value ** (1 / 3)
