import os
import re
import shutil
import sys
from os import path
from typing import List, Dict, Tuple, Union

from api.models.team_set import TeamSet
from benchmarking.caching.simulation_cache import SimulationCache


SimulationArtifact = Tuple[List[TeamSet], List[float]]


def combine(cache_key: str):
    """
    Takes a cache key and checks for any fragments. Combines them into one cache
    file and uses the most recent data for the metadata. Removes fragments after
    combining.

    Example:
    cache_key="test/abc" will be in fragments
    simulation_cache
        /test
            /abc
                /fragment_0.json
                /fragment_1.json
                ...
    """

    cache_directory = path.abspath(
        path.join(path.dirname(__file__), "..", "..", "simulation_cache")
    )
    cache_location = path.normpath(path.join(cache_directory, cache_key)).replace(
        "\\", "/"
    )

    # If cache not found, return
    if not path.exists(cache_location):
        return

    # Get initial list of files where the cache should be
    fragments = [
        f for f in os.listdir(cache_location) if re.match(r"fragment_\d+\.json", f)
    ]
    # Remove .json
    fragments = [f[:-5] for f in fragments]

    info: List[Dict[str, any]] = []

    for fragment in fragments:
        cache = SimulationCache(cache_key + "/" + fragment)
        if not cache.exists():
            continue
        metadata = cache.get_metadata()
        team_sets, runtimes = cache.get_simulation_artifact()

        # Commit hashes must match
        if (
            len(info) > 0
            and metadata["commit_hash"] != info[0]["metadata"]["commit_hash"]
        ):
            print(
                "[WARNING]: Commit hashes of fragments should be the same",
                file=sys.stderr,
            )

        info.append(
            {
                "metadata": metadata,
                "team_sets": team_sets,
                "runtimes": runtimes,
            }
        )

    # Sort by timestamp so that the newest fragment has metadata priority
    sorted_info = sorted(info, key=lambda x: x["metadata"]["timestamp"])

    result_cache: Dict[str, any] = {
        "metadata": {},
        "team_sets": [],
        "runtimes": [],
    }
    for fragment_data in sorted_info:
        result_cache["metadata"].update(fragment_data["metadata"])
        result_cache["team_sets"].extend(fragment_data["team_sets"])
        result_cache["runtimes"].extend(fragment_data["runtimes"])

    # Write out resulting combined cache to cache_key
    full_cache = SimulationCache(cache_key)
    full_cache.clear()
    full_cache.save(**result_cache)

    # Remove fragments
    shutil.rmtree(cache_location)


if __name__ == "__main__":
    combine("social/varied_class_size/10_students/AlgorithmType.RANDOM-default")
