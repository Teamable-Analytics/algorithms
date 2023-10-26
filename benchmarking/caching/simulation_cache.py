import json
import os
from datetime import datetime
from os import path
from typing import List, Dict, Any, TYPE_CHECKING

import git

from api.models.team_set import TeamSet
from api.models.team_set.serializer import TeamSetSerializer

if TYPE_CHECKING:
    from benchmarking.simulation.simulation import SimulationArtifact


class SimulationCache:
    """
    This class is used to cache the results of a simulation, which is a List[TeamSet] and List[float], where each element of the list is a different run and it's runtime.
    All TeamSets should have been generated by the same algorithm (with the same settings).
    It uses the cache_key to generate a file with the results of the simulation.
    """

    def __init__(self, cache_key: str) -> None:
        self.cache_key: str = cache_key
        self._data: Dict[str, Any] = {}
        """
        Dict in the form of:
        {
            "metadata": Dict[str, Any],  # Contains at least "timestamp" and "commit_hash"
            "team_sets": List[TeamSet],
            "runtimes": List[float],
        }
        """

    def exists(self) -> bool:
        """
        Checks if the cache_key is in the cache.
        """
        return path.exists(self._get_file())

    def get_simulation_artifact(self) -> "SimulationArtifact":
        """
        Gets the simulation results from the cache.
        """
        self._load_data()

        return self._data["team_sets"], self._data["runtimes"]

    def get_metadata(self) -> Dict[str, Any]:
        """
        Gets the metadata associated with the simulation results from the cache.
        """
        self._load_data()

        return self._data["metadata"]

    def save(
        self,
        team_sets: List[TeamSet],
        runtimes: List[float],
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Puts the simulation results into the cache.
        Overwrites any existing cache with the same cache_key.
        """

        if len(team_sets) != len(runtimes):
            raise ValueError(
                "The number of team_sets and runtimes must be the same. "
                f"Got {len(team_sets)} team_sets and {len(runtimes)} runtimes."
            )

        # Get metadata
        metadata = metadata or {}
        # Epoch time, num seconds since 1970, no timezone (utc)
        metadata["timestamp"] = datetime.utcnow().timestamp()
        # Get latest commit hash. This is so that we can track which commit generated the cache and go back to the code that generated it if needed. Would then be accessible at https://github.com/Teamable-Analytics/algorithms/commit/<commit_hash>
        metadata["commit_hash"] = git.Repo(
            search_parent_directories=True
        ).head.object.hexsha

        # Get stripped down version of TeamSets
        stripped_team_sets = [
            TeamSetSerializer().default(team_set) for team_set in team_sets
        ]

        # Make dict that will be stored
        cached_data = {
            "metadata": metadata,
            "team_sets": stripped_team_sets,
            "runtimes": runtimes,
        }

        # Write to json file
        with open(self._get_file(), "w+") as file:
            json.dump(cached_data, file)

        # Invalidate the in memory cache now that the data has changed
        self._data = {}

    def clear(self) -> None:
        """
        Clears the cache.
        """
        if self.exists():
            os.remove(self._get_file())
        self._data = {}

    def _get_file(self) -> str:
        """
        Gets the file associated with the cache_key.
        """

        # Get cache directory
        current_dir = path.dirname(__file__)
        cache_dir = path.abspath(path.join(current_dir, "..", "..", "run_cache"))

        # Create cache directory if it doesn't exist
        if not path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Get file
        return path.join(cache_dir, self.cache_key + ".json")

    def _load_data(self) -> None:
        if not self._data:
            if not self.exists():
                raise FileNotFoundError("Cache doesn't exist")

            # Load json data
            with open(self._get_file(), "r") as f:
                json_data = json.load(f)
            if not json_data:
                raise ValueError(
                    f'No json could be loaded from the "{self.cache_key}" cache'
                )

            # Init data to be the loaded json
            self._data = json_data

            # Convert json team sets to actual TeamSets
            self._data["team_sets"] = [
                TeamSetSerializer().decode(team_set)
                for team_set in json_data["team_sets"]
            ]

            self._data: Dict[str, Any] = json_data
