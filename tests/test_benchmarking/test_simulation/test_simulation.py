import json
import shutil
import unittest
from os import path
from unittest.mock import patch

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.project import Project
from api.models.team_set import TeamSet
from api.models.team_set.serializer import TeamSetSerializer
from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.simulation.basic_simulation_set import BasicSimulationSet
from benchmarking.simulation.simulation import Simulation, SimulationArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings
from tests.test_benchmarking.test_simulation._data import TestScenario


class TestSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = TestScenario()
        cls.student_provider = MockStudentProvider(
            MockStudentProviderSettings(number_of_students=10),
        )
        cls.settings = SimulationSettings(
            num_teams=2,
            scenario=cls.scenario,
            student_provider=cls.student_provider,
        )

        cls.student_provider_with_preferences = MockStudentProvider(
            MockStudentProviderSettings(
                number_of_students=10,
                project_preference_options=[1, 2],
                num_project_preferences_per_student=2,
            ),
        )
        cls.initial_teams_provider = MockInitialTeamsProvider(
            MockInitialTeamsProviderSettings(
                projects=[
                    Project(_id=1),
                    Project(_id=2),
                ]
            )
        )
        cls.complex_settings = SimulationSettings(
            scenario=cls.scenario,
            student_provider=cls.student_provider_with_preferences,
            initial_teams_provider=cls.initial_teams_provider,
        )

    def tearDown(self):
        test_cache_dir = path.abspath(
            path.join(path.dirname(__file__), "..", "..", "..", "test_simulation_cache")
        )
        if path.exists(test_cache_dir):
            shutil.rmtree(test_cache_dir)

    def mock_out_cache_location(self):
        # Mock the cache directory
        self.real_dirname = path.dirname

        def mock_dirname(path_str):
            root_dir = path.abspath(
                path.join(self.real_dirname(__file__), "..", "..", "..")
            )
            cache_dir = path.join(root_dir, "simulation_cache")
            file_name = path.abspath(path_str)
            target_dir = path.join(
                root_dir, "benchmarking", "caching", "simulation_cache.py"
            )
            # If the dirname request is from simulation_cache.py, return a directory that will cause the file to be written to the test cache directory
            if file_name == target_dir:
                return path.join(root_dir, "test_simulation_cache", "_", "_")
            return self.real_dirname(path_str)

        self.mock_dirname = mock_dirname
        self.patcher = patch("os.path.dirname", self.mock_dirname)
        self.patcher.start()

    def test_run__outputs_match_given_trials_and_schema(self):
        team_sets, run_times = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=self.settings,
        ).run(num_runs=5)

        self.assertEqual(len(team_sets), 5)
        self.assertEqual(len(run_times), 5)
        # redundant but left in as a safeguard for future logic changes
        self.assertEqual(len(team_sets), len(run_times))

        for team_set in team_sets:
            self.assertIsInstance(team_set, TeamSet)
        for run_time in run_times:
            self.assertIsInstance(run_time, float)

    def test_run__works_with_each_algorithm_type(self):
        for algorithm_type in BasicSimulationSet.DEFAULT_ALGORITHM_TYPES:
            Simulation(
                algorithm_type=algorithm_type,
                settings=self.settings,
            ).run(num_runs=1)

    def test_run__works_with_complex_settings(self):
        for algorithm_type in BasicSimulationSet.DEFAULT_ALGORITHM_TYPES:
            Simulation(
                algorithm_type=algorithm_type,
                settings=self.complex_settings,
            ).run(num_runs=1)

    def test_run__works_with_configs(self):
        # fixme: should eventually test that the custom config passed
        #  is actually used, for now just tests that it doesn't break
        Simulation(
            algorithm_type=AlgorithmType.PRIORITY,
            config=PriorityAlgorithmConfig(
                MAX_KEEP=1,
                MAX_SPREAD=1,
                MAX_TIME=1,
                MAX_ITERATE=2222,
            ),
            settings=self.settings,
        ).run(num_runs=1)

    def test_run__caches_all_runs(self):
        self.mock_out_cache_location()

        cache_key = "test_cache_key"
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=cache_key,
        )

        # Run simulation
        simulation_result: SimulationArtifact = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=5)
        simplified_simulation_result = simplify_simulation_result(simulation_result)

        # Check cache
        cache = SimulationCache(cache_key)
        cache_data = cache.get_simulation_artifact()
        self.assertTrue(cache.exists())
        self.assertEqual(simplified_simulation_result, cache_data)
        self.assertEqual(5, len(cache_data[0]))
        self.assertEqual(5, len(cache_data[1]))

        self.patcher.stop()

    def test_run__can_add_more_runs_to_simulation(self):
        self.mock_out_cache_location()

        cache_key = "test_cache_key"
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=cache_key,
        )

        # Run simulation
        simulation_result: SimulationArtifact = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=1)

        self.assertEqual(1, len(simulation_result[0]))
        self.assertEqual(1, len(simulation_result[1]))

        # Add run
        new_simulation_result = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=2)

        self.assertEqual(2, len(new_simulation_result[0]))
        self.assertEqual(2, len(new_simulation_result[1]))

        self.assertEqual(
            simplify_simulation_result(simulation_result),
            simplify_simulation_result(
                (new_simulation_result[0][:1], new_simulation_result[1][:1])
            ),
        )

        self.patcher.stop()

    def test_run__doesnt_rerun_when_cache_contains_all_runs(self):
        self.mock_out_cache_location()

        cache_key = "test_cache_key"
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=cache_key,
        )

        # Run simulation
        simulation_result: SimulationArtifact = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=2)

        self.assertEqual(2, len(simulation_result[0]))
        self.assertEqual(2, len(simulation_result[1]))

        # Run simulation again
        new_simulation_result = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=2)

        self.assertEqual(2, len(new_simulation_result[0]))
        self.assertEqual(2, len(new_simulation_result[1]))

        self.assertEqual(
            simplify_simulation_result(simulation_result),
            simplify_simulation_result(new_simulation_result),
        )

        self.patcher.stop()

    def test_run__return_only_num_runs_number_of_run_outputs(self):
        self.mock_out_cache_location()

        cache_key = "test_cache_key"
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=cache_key,
        )

        # Run simulation
        simulation_result: SimulationArtifact = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=5)

        # Run simulation again
        new_simulation_result = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=2)

        self.assertEqual(2, len(new_simulation_result[0]))
        self.assertEqual(2, len(new_simulation_result[1]))


def simplify_simulation_result(
    simulation_result: SimulationArtifact,
) -> SimulationArtifact:
    return (
        [
            TeamSetSerializer().decode(team_set)
            for team_set in json.loads(
                json.dumps(simulation_result[0], cls=TeamSetSerializer)
            )
        ],
        simulation_result[1],
    )
