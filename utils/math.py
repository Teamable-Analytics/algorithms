from typing import Tuple


def change_range(
    value: float, original_range: Tuple[float, float], new_range=Tuple[float, float]
) -> float:
    old_min, old_max = original_range
    new_min, new_max = new_range

    return new_min + (((value - old_min) / (old_max - old_min)) * (new_max - new_min))
