from typing import List


def chunk(num_runs: int, num_threads: int) -> List[int]:
    """
    Returns a list where each element is the number of runs that thread should do
    """
    if num_runs < 1 or num_threads < 1:
        raise ValueError(
            f"Invalid args (num_runs={num_runs}, num_threads={num_threads}) for chunk()"
        )
    return [
        num_runs // num_threads + (1 if i < num_runs % num_threads else 0)
        for i in range(num_threads)
    ]
