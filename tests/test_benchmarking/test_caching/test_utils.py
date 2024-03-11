import unittest
from os import path
from typing import List

from api.dataclasses.team_set import TeamSet
from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.caching.utils import combine
from tests.test_benchmarking.test_caching._data import (
    mock_simulation_result,
    mock_runtimes,
    mock_simulation_result_2,
    mock_runtimes_2,
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_cache_key = "test/cache/key"
        self.cache = SimulationCache(self.test_cache_key)

    def tearDown(self):
        self.cache.clear()

    def test_combine__result_has_combined_length(self):
        create_fragments(self.test_cache_key, 4)
        combine(self.test_cache_key)
        self.assertTrue(self.cache.exists())
        result_team_sets, result_runtimes = self.cache.get_simulation_artifact()
        self.assertEqual(len(mock_simulation_result) * 4, len(result_team_sets))
        self.assertEqual(len(mock_runtimes) * 4, len(result_runtimes))

    def test_combine__result_has_correct_data(self):
        mock_simulation_results = [
            mock_simulation_result,
            mock_simulation_result_2,
        ]
        mock_runtimes_list = [
            mock_runtimes,
            mock_runtimes_2,
        ]
        create_fragments(
            self.test_cache_key, 2, mock_simulation_results, mock_runtimes_list
        )

        # Get fragment metadata
        frag_1 = SimulationCache(
            SimulationCache.get_fragment_cache_key(self.test_cache_key, 0)
        )
        frag_2 = SimulationCache(
            SimulationCache.get_fragment_cache_key(self.test_cache_key, 1)
        )

        metadata_1 = frag_1.get_metadata()
        metadata_2 = frag_2.get_metadata()

        combine(self.test_cache_key)

        result_team_sets, result_runtimes = self.cache.get_simulation_artifact()
        result_metadata = self.cache.get_metadata()

        expected = [*mock_simulation_result, *mock_simulation_result_2]
        self.assertListEqual(expected, result_team_sets)
        expected = [*mock_runtimes, *mock_runtimes_2]
        self.assertListEqual(expected, result_runtimes)

        self.assertEqual(
            max(metadata_1["timestamp"], metadata_2["timestamp"]),
            result_metadata["timestamp"],
        )

        self.assertEqual(
            1,
            len(
                {
                    metadata_1["commit_hash"],
                    metadata_2["commit_hash"],
                    result_metadata["commit_hash"],
                }
            ),
        )

    def test_combine__removes_fragments(self):
        create_fragments(self.test_cache_key, 3)
        combine(self.test_cache_key)
        self.assertFalse(
            path.exists(
                path.abspath(
                    path.join(
                        path.dirname(__file__),
                        "..",
                        "..",
                        "..",
                        "simulation_cache",
                        self.test_cache_key,
                    )
                )
            )
        )


def create_fragments(
    cache_key: str,
    num_fragments: int,
    simulation_results: List[List[TeamSet]] = None,
    runtimes: List[List[float]] = None,
):
    if not simulation_results:
        simulation_results = [mock_simulation_result for _ in range(num_fragments)]
    if not runtimes:
        runtimes = [mock_runtimes for _ in range(num_fragments)]
    for i in range(num_fragments):
        fragment_key = SimulationCache.get_fragment_cache_key(cache_key, i)
        cache = SimulationCache(fragment_key)
        if cache.exists():
            raise ValueError("Cannot create mock fragments because they already exist")
        cache.save(
            simulation_results[i],
            runtimes[i],
        )
