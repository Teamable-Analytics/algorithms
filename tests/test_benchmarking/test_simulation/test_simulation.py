import json
import shutil
import unittest
from datetime import datetime
from os import path

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.dataclasses.enums import AlgorithmType
from api.dataclasses.project import Project
from api.dataclasses.team_set import TeamSet
from api.dataclasses.team_set.serializer import TeamSetSerializer
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

    def setUp(self):
        self.test_cache_key = f"test/{datetime.now().timestamp()}/test_cache_key"

    def tearDown(self):
        test_cache_dir = path.abspath(
            path.join(
                path.dirname(__file__), "..", "..", "..", "simulation_cache", "test"
            )
        )
        if path.exists(test_cache_dir):
            shutil.rmtree(test_cache_dir)

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
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=self.test_cache_key,
        )

        # Run simulation and sort by team
        simulation_result = Simulation(
            algorithm_type=AlgorithmType.RANDOM,
            settings=settings,
        ).run(num_runs=5)
        simulation_team_sets, simulation_runtimes = simplify_simulation_result(
            simulation_result
        )
        sorted_simulation_results = sorted(
            zip(simulation_team_sets, simulation_runtimes), key=lambda x: x[0]._id
        )

        # Check cache
        cache = SimulationCache(self.test_cache_key)
        cache_team_sets, cache_runtimes = cache.get_simulation_artifact()
        sorted_cache = sorted(
            zip(cache_team_sets, cache_runtimes), key=lambda x: x[0]._id
        )

        self.assertTrue(cache.exists())
        self.assertEqual(sorted_simulation_results, sorted_cache)
        self.assertEqual(5, len(simulation_runtimes))
        self.assertEqual(5, len(cache_runtimes))

    def test_run__can_add_more_runs_to_simulation(self):
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=self.test_cache_key,
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

    def test_run__doesnt_rerun_when_cache_contains_all_runs(self):
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=self.test_cache_key,
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
            simplify_simulation_result(
                (
                    sorted(simulation_result[0], key=lambda x: x._id),
                    sorted(simulation_result[1]),
                )
            ),
            simplify_simulation_result(
                (
                    sorted(new_simulation_result[0], key=lambda x: x._id),
                    sorted(new_simulation_result[1]),
                )
            ),
        )

    def test_run__return_only_num_runs_number_of_run_outputs(self):
        settings = SimulationSettings(
            num_teams=2,
            scenario=self.scenario,
            student_provider=self.student_provider,
            cache_key=self.test_cache_key,
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
