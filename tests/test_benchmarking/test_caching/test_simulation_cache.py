import json
import os
import shutil
import unittest
from os import path
from typing import List

from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from api.models.team_set.serializer import TeamSetSerializer
from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.simulation.simulation import SimulationArtifact

mock_simulation_result: List[TeamSet] = [
    TeamSet(
        _id=0,
        name="TeamSet0",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=1),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=2),
                    Student(_id=3),
                ],
            ),
        ],
    ),
    TeamSet(
        _id=1,
        name="TeamSet1",
        teams=[
            Team(
                _id=0,
                name="Team0",
                students=[
                    Student(_id=0),
                    Student(_id=2),
                ],
            ),
            Team(
                _id=1,
                name="Team1",
                students=[
                    Student(_id=1),
                    Student(_id=3),
                ],
            ),
        ],
    ),
]
mock_runtimes: List[float] = [
    1.8,
    2.0,
]


class TestSimulationCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # I'm paranoid about these tests modifying the cache, so move the cache to a different location as a precaution
        # This also ensures no leftover files from running the tests
        cache_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "simulation_cache")
        )
        backup_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "cache_backup")
        )
        if path.exists(cache_dir):
            if path.exists(backup_dir):
                os.rmdir(backup_dir)
            os.rename(cache_dir, backup_dir)

    @classmethod
    def tearDownClass(cls):
        # Move the cache back to its original location
        cache_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "simulation_cache")
        )
        backup_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "cache_backup")
        )
        if path.exists(cache_dir):
            # Only contains files that were created by this test, so it's safe to delete
            shutil.rmtree(cache_dir)
        if path.exists(backup_dir):
            os.rename(backup_dir, cache_dir)

    def test_get_file__path_in_cache_dir(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Get the absolute path of the directory and the file
        cache_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "simulation_cache")
        )
        file_path = path.abspath(cache._get_file())

        # Check if the file path is a subpath of the directory
        self.assertEqual(path.commonpath([cache_dir, file_path]), cache_dir)

        cache.clear()

    def test_save__file_is_created(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Make sure file doesn't exist
        cache.clear()

        # Save
        cache.save([], [])

        # Check to make sure file exists
        self.assertTrue(path.exists(cache._get_file()))

    def test_save__file_is_overwritten(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Save
        cache.save([], [])

        # Read file contents
        with open(cache._get_file(), "r") as file:
            file_contents = file.read()

        # Save again with different contents
        cache.save(mock_simulation_result, mock_runtimes)

        # Read file contents again
        with open(cache._get_file(), "r") as file:
            new_file_contents = file.read()

        # Check to make sure file contents are different
        self.assertNotEqual(file_contents, new_file_contents)

    def test_save__is_json(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Save
        cache.save([], [])

        # Read file contents
        with open(cache._get_file(), "r") as file:
            file_contents = file.read()

        # Check to make sure file contents are valid json
        try:
            json.loads(file_contents)
        except ValueError:
            self.fail("File contents are not valid json.")

    def test_save__saves_time_and_commit_in_metadata(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Save
        cache.save([], [])

        # Read file contents
        with open(cache._get_file(), "r") as file:
            file_contents = json.load(file)

        # Check to make sure metadata is in file contents
        self.assertIn("metadata", file_contents)
        self.assertIn("timestamp", file_contents["metadata"])
        self.assertIn("commit_hash", file_contents["metadata"])

    def test_save__saves_team_sets_and_runtimes(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)

        # Save
        cache.save(mock_simulation_result, mock_runtimes)

        # Read file contents
        with open(cache._get_file(), "r") as file:
            file_contents = json.load(file)

        # Check to make sure team_sets is in file contents
        self.assertIn("team_sets", file_contents)
        self.assertEqual(len(file_contents["team_sets"]), len(mock_simulation_result))
        json_team_sets = [
            TeamSetSerializer().default(team_set) for team_set in mock_simulation_result
        ]
        self.assertEqual(json_team_sets, file_contents["team_sets"])
        self.assertIn("runtimes", file_contents)
        self.assertEqual(len(file_contents["runtimes"]), len(mock_runtimes))
        self.assertEqual(mock_runtimes, file_contents["runtimes"])

    def test_add_run__correctly_adds_run(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)
        cache.save(mock_simulation_result[:1], mock_runtimes[:1])

        self.assertEqual(1, len(cache.get_simulation_artifact()[0]))
        self.assertEqual(1, len(cache.get_simulation_artifact()[1]))

        # Add run
        cache.add_run(mock_simulation_result[0], mock_runtimes[0])

        self.assertEqual(2, len(cache.get_simulation_artifact()[0]))
        self.assertEqual(2, len(cache.get_simulation_artifact()[1]))

        # Check file contents
        with open(cache._get_file(), "r") as file:
            file_contents = json.load(file)

        self.assertEqual(2, len(file_contents["team_sets"]))
        self.assertEqual(2, len(file_contents["runtimes"]))

    def test_clear__deletes_cache_file(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)
        cache.save([], [])

        # Check to make sure file exists
        self.assertTrue(cache.exists())

        # Clear
        cache.clear()

        # Check to make sure file doesn't exist
        self.assertFalse(cache.exists())

    def test_get_simulation_artifact__returns_correct_teams(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)
        cache.save(mock_simulation_result, mock_runtimes)

        # Get teams
        artifact: SimulationArtifact = cache.get_simulation_artifact()

        # Check to make sure teams are correct
        self.assertIsInstance(artifact[0], List)
        self.assertIsInstance(artifact[0][0], TeamSet)
        self.assertEqual(mock_simulation_result, artifact[0])
        # Check to make sure runtimes are correct
        self.assertIsInstance(artifact[1], List)
        self.assertIsInstance(artifact[1][0], float)
        self.assertEqual(mock_runtimes, artifact[1])

    def test_get_metadata__returns_correct_metadata(self):
        cache_key = "test_cache_key"
        cache = SimulationCache(cache_key)
        cache.save([], [])

        # Get metadata
        metadata = cache.get_metadata()

        # Check to make sure metadata is correct
        self.assertEqual(2, len(metadata))
        self.assertIn("timestamp", metadata)
        self.assertIn("commit_hash", metadata)

        cache.clear()
        cache.save([], [], {"foo": "bar", "num": 1})

        # Get metadata
        metadata = cache.get_metadata()

        # Check to make sure metadata is correct
        self.assertEqual("bar", metadata["foo"])
        self.assertEqual(1, metadata["num"])
        self.assertIsInstance(metadata["num"], int)
        self.assertIsInstance(metadata["timestamp"], float)
