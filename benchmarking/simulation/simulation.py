import copy
import os
import time
from threading import Thread
from typing import List, Tuple

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.team_set import TeamSet
from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.simulation.mock_algorithm import MockAlgorithm
from benchmarking.simulation.simulation_settings import SimulationSettings
from benchmarking.simulation.utils import chunk
from utils.threads import ThreadWithReturnValue

# list of floats tracks the runtime of each run
SimulationArtifact = Tuple[List[TeamSet], List[float]]


class Simulation:
    """
    Represents running a Simulation num_runs times and returning the team sets from each of those runs.
    """

    KEY_RUNTIMES = "runtimes"

    def __init__(
        self,
        algorithm_type: AlgorithmType,
        settings: SimulationSettings,
        config: AlgorithmConfig = None,
    ):
        self.algorithm_type = algorithm_type
        self.settings = settings
        self.config = config
        self.team_sets = []
        self.run_times = []

    def run(self, num_runs: int) -> SimulationArtifact:
        custom_initial_teams = (
            self.settings.initial_teams_provider.get()
            if self.settings.initial_teams_provider
            else None
        )
        team_generation_options = MockAlgorithm.get_team_generation_options(
            num_students=self.settings.student_provider.num_students,
            num_teams=self.settings.num_teams,
            initial_teams=custom_initial_teams,
        )
        algorithm_options = MockAlgorithm.algorithm_options_from_scenario(
            algorithm_type=self.algorithm_type,
            scenario=self.settings.scenario,
            max_project_preferences=self.settings.student_provider.max_project_preferences_per_student,
        )
        runner = AlgorithmRunner(
            algorithm_type=self.algorithm_type,
            team_generation_options=team_generation_options,
            algorithm_options=algorithm_options,
            algorithm_config=self.config,
        )

        # todo: abstract into some other method that returns num runs remaining and sets self.team_sets and self.runtimes
        if self.settings.cache_key:
            cache = SimulationCache(self.settings.cache_key)
            if cache.exists():
                cached_team_sets, cached_run_times = cache.get_simulation_artifact()
                self.team_sets = cached_team_sets
                self.run_times = cached_run_times
                if len(self.team_sets) >= num_runs:
                    return self.team_sets[:num_runs], self.run_times[:num_runs]
                else:
                    num_runs -= len(cached_team_sets)

        # todo: START PARALLEL BLOCK
        """
        todo:
        get chunks
        for each thread, create an instance of simulation cache that goes to that threads fragment
        run like a beast
        """
        if self.settings.cache_key:
            SimulationCache.create_fragment_parent_dir(self.settings.cache_key)

        num_runs_per_thread = chunk(num_runs, os.cpu_count())
        threads: List[ThreadWithReturnValue] = []
        for fragment_id, batch_num_runs in enumerate(num_runs_per_thread):
            print("Starting thread", fragment_id)
            _thread = ThreadWithReturnValue(
                target=run_trial_batch, args=(fragment_id, batch_num_runs, self.settings, runner)
            )
            threads.append(_thread)
            _thread.start()

        # await completion of all threads, and store their results
        for thread in threads:
            batch_team_sets, batch_run_times = thread.join()
            self.team_sets.extend(batch_team_sets)
            self.run_times.extend(batch_run_times)

        # todo: END PARALLEL BLOCK
        # todo: clean up cache fragments

        return self.team_sets, self.run_times


def run_trial_batch(
    fragment: int, num_runs_for_batch: int, settings: SimulationSettings, runner: AlgorithmRunner
):
    batch_cache = None
    if settings.cache_key:
        batch_cache_key = SimulationCache.get_fragment_cache_key(
            settings.cache_key, fragment
        )
        batch_cache = SimulationCache(batch_cache_key)

    batch_team_sets = []
    batch_run_times = []

    # todo: some goated error handling, so one thread doesnt tank the others
    for _ in range(0, num_runs_for_batch):
        students = settings.student_provider.get()

        start_time = time.time()
        team_set = runner.generate(students)
        end_time = time.time()

        run_time = end_time - start_time

        batch_team_sets.append(team_set)
        batch_run_times.append(run_time)

        # Save result to cache. Do this inside the loop so that if the program crashes, we still have the results from the previous runs.
        if batch_cache is not None:
            batch_cache.add_run(team_set, run_time)

    return batch_team_sets, batch_run_times
