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
    fragments = []
    for f in os.listdir(cache_location):
        match = re.match(r"(fragment_\d+)\.json", f)
        if match:
            fragments.append(match.group(1))

    fragment_data: List[Dict[str, any]] = []

    for fragment in fragments:
        cache = SimulationCache(cache_key + "/" + fragment)
        if not cache.exists():
            continue
        metadata = cache.get_metadata()
        team_sets, runtimes = cache.get_simulation_artifact()

        # Check that expected keys exist
        if (
            not metadata
            or not metadata.get("commit_hash")
            or not metadata.get("timestamp")
            or not team_sets
            or not runtimes
        ):
            print(
                f"[WARNING]: Cache fragment missing critical data, skipping {fragment}",
                file=sys.stderr,
            )
            continue

        # Commit hashes must match
        if (
            len(fragment_data) > 0
            and metadata["commit_hash"] != fragment_data[0]["metadata"]["commit_hash"]
        ):
            print(
                "[WARNING]: Commit hashes of fragments should be the same",
                file=sys.stderr,
            )

        fragment_data.append(
            {
                "metadata": metadata,
                "team_sets": team_sets,
                "runtimes": runtimes,
            }
        )

    # Sort by timestamp so that the newest fragment has metadata priority
    sorted_fragment_data = sorted(
        fragment_data, key=lambda x: x["metadata"]["timestamp"]
    )

    result_cache: Dict[str, any] = {
        "metadata": {},
        "team_sets": [],
        "runtimes": [],
    }
    for fragment in sorted_fragment_data:
        result_cache["metadata"].update(fragment["metadata"])
        result_cache["team_sets"].extend(fragment["team_sets"])
        result_cache["runtimes"].extend(fragment["runtimes"])

    # Write out resulting combined cache to cache_key
    full_cache = SimulationCache(cache_key)
    full_cache.clear()
    full_cache.save(**result_cache)

    # Remove fragments
    shutil.rmtree(cache_location)
