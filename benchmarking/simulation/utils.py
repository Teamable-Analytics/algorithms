from typing import List


def chunk(num_runs: int, num_workers: int) -> List[int]:
    """
    Returns a list where each element is the number of runs that thread should do
    """
    if num_runs < 1 or num_workers < 1:
        raise ValueError(
            f"Invalid args (num_runs={num_runs}, num_workers={num_workers}) for chunk()"
        )
    if num_runs < num_workers:
        return [1 for _ in range(num_runs)]
    return [
        num_runs // num_workers + (1 if i < num_runs % num_workers else 0)
        for i in range(num_workers)
    ]
