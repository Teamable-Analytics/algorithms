import os
import time
import uuid
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import List, Tuple

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.interfaces.algorithm_config import AlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.team_set import TeamSet
from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.simulation.mock_algorithm import MockAlgorithm
from benchmarking.simulation.simulation_settings import SimulationSettings
from benchmarking.simulation.utils import chunk

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

    def run(self, num_runs: int, seeds: List[int] = None) -> SimulationArtifact:
        if seeds and len(seeds) != num_runs:
            raise ValueError("Must provide a seed for each run")

        cache = None
        num_completed_runs = 0
        if self.settings.cache_key:
            cache = SimulationCache(self.settings.cache_key)
            if cache.exists():
                cached_team_sets, cached_run_times = cache.get_simulation_artifact()
                self.team_sets = cached_team_sets
                self.run_times = cached_run_times
                num_completed_runs = len(cached_team_sets)
                if len(self.team_sets) >= num_runs:
                    return self.team_sets[:num_runs], self.run_times[:num_runs]
                else:
                    num_runs -= len(cached_team_sets)

        if cache and cache.exists():
            metadata = cache.get_metadata()
            completed_run_indexes = metadata.get("used_seed_indexes") or []

            # Use as fallback
            if len(completed_run_indexes) != num_completed_runs:
                completed_run_indexes = list(range(num_completed_runs))
        else:
            completed_run_indexes = list(range(num_completed_runs))

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

        if self.settings.cache_key:
            SimulationCache.create_fragment_parent_dir(self.settings.cache_key)

        num_processes = max(1, os.cpu_count() - 2)
        # TODO: Remove this after running the simulations
        num_processes = 1
        num_runs_per_worker = chunk(num_runs, num_processes)

        # Calculate the run indexes that need to be run by each worker
        run_indexes_per_worker: List[List[int]] = []
        index = 0
        for num_runs_for_batch in num_runs_per_worker:
            batch_indexes = []
            for _ in range(num_runs_for_batch):
                # Search for indexes that have not been completed
                while index in completed_run_indexes:
                    index += 1
                batch_indexes.append(index)
                assert not seeds or index < len(seeds)
                index += 1
            run_indexes_per_worker.append(batch_indexes)

        processes: List[ApplyResult] = []

        pool = Pool(processes=num_processes)
        for fragment_id, run_indexes in enumerate(run_indexes_per_worker):
            processes.append(
                pool.apply_async(
                    run_trial_batch,
                    args=(fragment_id, run_indexes, self.settings, runner, seeds),
                )
            )

        # await completion of all processes, and store their results
        for process in processes:
            batch_team_sets, batch_run_times = process.get()
            self.team_sets.extend(batch_team_sets)
            self.run_times.extend(batch_run_times)

        if self.settings.cache_key:
            from benchmarking.caching.utils import combine

            combine(self.settings.cache_key)
        pool.close()
        return self.team_sets, self.run_times


def run_trial_batch(
    fragment: int,
    run_indexes_for_batch: List[int],
    settings: SimulationSettings,
    runner: AlgorithmRunner,
    seeds: List[int],
):
    try:
        batch_cache = None
        if settings.cache_key:
            batch_cache_key = SimulationCache.get_fragment_cache_key(
                settings.cache_key, fragment
            )
            batch_cache = SimulationCache(batch_cache_key)

        batch_team_sets = []
        batch_run_times = []

        for run_index in run_indexes_for_batch:
            if seeds:
                students = settings.student_provider.get(seeds[run_index])
            else:
                students = settings.student_provider.get()

            start_time = time.time()
            team_set = runner.generate(students)
            end_time = time.time()

            run_time = end_time - start_time

            # Give the generated team set a unique id
            team_set._id = (
                f"{uuid.uuid4()}--run_index_{run_index}--seed_{seeds[run_index]}"
                if seeds
                else f"{uuid.uuid4()}--run_index_{run_index}"
            )

            batch_team_sets.append(team_set)
            batch_run_times.append(run_time)

            # Save result to cache. Do this inside the loop so that if the program crashes, we still have the results from the previous runs.
            if batch_cache is not None:
                batch_cache.add_run(team_set, run_time)

                if seeds:
                    if batch_cache.exists():
                        metadata = batch_cache.get_metadata()
                    else:
                        metadata = {}
                    used_seed_indexes = metadata.get("used_seed_indexes") or []
                    used_seeds = metadata.get("used_seeds") or []

                    used_seed_indexes.append(run_index)
                    used_seeds.append(seeds[run_index])

                    batch_cache.update_metadata(
                        {
                            "used_seed_indexes": used_seed_indexes,
                            "used_seeds": used_seeds,
                        }
                    )

        return batch_team_sets, batch_run_times
    except Exception as e:
        print(e)
        return [], []
