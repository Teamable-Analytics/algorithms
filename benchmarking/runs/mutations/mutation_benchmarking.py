from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.priority_algorithm.mutations import (
    mutate_local_max,
    mutate_random_swap,
    mutate_local_max_random,
)
from api.ai.priority_algorithm.mutations.greedy_random_local_max import (
    greedy_local_max_mutation,
)
from api.ai.priority_algorithm.mutations.random_slice import mutate_random_slice
from api.dataclasses.enums import ScenarioAttribute, Gender, Race, AlgorithmType
from benchmarking.data.simulated_data.realistic_class.providers import (
    get_realistic_projects,
    RealisticMockInitialTeamsProvider,
    RealisticMockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.satisfy_project_requirements_and_diversify_female_min_of_2_and_diversify_african_min_of_2 import (
    SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class MutationBenchmarking(Run):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        # class_sizes = [50, 100, 250, 500]
        class_sizes = [50, 100]

        scenario = (
            SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2()
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            "AverageCosineDifferenceGender": AverageCosineDifference(
                attribute_filter=[ScenarioAttribute.GENDER.value],
                name="AverageCosineDifferenceGender",
            ),
            "AverageCosineDifferenceRace": AverageCosineDifference(
                attribute_filter=[ScenarioAttribute.RACE.value],
                name="AverageCosineDifferenceRace",
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups={
                    ScenarioAttribute.GENDER.value: [_.value for _ in Gender.values()],
                    ScenarioAttribute.MAJOR.value: [_.value for _ in Race.values()],
                }
            ),
        }

        initial_teams_provider = RealisticMockInitialTeamsProvider()
        max_keep = 15
        max_spread = 30
        max_iterate = 30
        max_time = 1_000_000

        mutation_sets = {
            "mutate_random": [(mutate_random_swap, max_spread)],
            "mutate_local_max": [
                (mutate_local_max, 1),
                (mutate_random_swap, max_spread - 1),
            ],
            "mutate_local_max_random": [
                (mutate_local_max_random, 5),
                (mutate_random_swap, max_spread - 5),
            ],
            "mutate_random_slice": [(mutate_random_slice, max_spread)],
            "mutate_half_random_slice": [
                (mutate_random_slice, max_spread / 2),
                (mutate_random_swap, max_spread / 2),
            ],
            "mutate_greedy_local_max": [(greedy_local_max_mutation, max_spread)],
            "mutate_greedy_local_max_with_random_swap": [
                (greedy_local_max_mutation, max_spread / 2),
                (mutate_random_swap, max_spread / 2),
            ],
            "mutate_greedy_local_max_with_random_slice": [
                (greedy_local_max_mutation, max_spread / 2),
                (mutate_random_slice, max_spread / 2),
            ],
        }

        artifacts: Dict[int, Dict[str, SimulationSetArtifact]] = {}

        for class_size in class_sizes:
            if class_size not in artifacts:
                artifacts[class_size] = {}
            for mutation_name, mutation_set in mutation_sets.items():
                artifacts[class_size][mutation_name] = SimulationSet(
                    settings=SimulationSettings(
                        scenario=scenario,
                        student_provider=RealisticMockStudentProvider(class_size),
                        cache_key=f"mutations/mutation_benchmarking/{mutation_name}/class_size_{class_size}/",
                        initial_teams_provider=initial_teams_provider,
                    ),
                    algorithm_set={
                        AlgorithmType.PRIORITY: [
                            PriorityAlgorithmConfig(
                                MAX_KEEP=max_keep,
                                MAX_SPREAD=max_spread,
                                MAX_ITERATE=max_iterate,
                                MAX_TIME=max_time,
                                MUTATIONS=mutation_set,
                            ),
                        ]
                    },
                ).run(num_runs=num_trials)

        if generate_graphs:
            for metric_name, metric in metrics.items():
                data = {}
                for class_size, _ in artifacts.items():
                    if class_size not in data:
                        data[class_size] = {}
                    for mutation_name, artifact in _.items():
                        insight_output_set = Insight.get_output_set(
                            artifact=artifact,
                            metrics=[metric],
                        )
                        avg_metric = list(
                            Insight.average_metric(
                                insight_output_set=insight_output_set,
                                metric_name=metric.name,
                            ).values()
                        )[0]
                        data[class_size][mutation_name] = avg_metric

                graph_data = [
                    GraphData(
                        x_data=class_sizes,
                        y_data=[
                            data[class_size][mutation_name]
                            for class_size in class_sizes
                        ],
                        name=mutation_name,
                    )
                    for mutation_name in mutation_sets.keys()
                ]

                line_graph(
                    LineGraphMetadata(
                        x_label="Class size",
                        y_label="Score",
                        title="Simulate including friends",
                        data=graph_data,
                    )
                )


if __name__ == "__main__":
    typer.run(MutationBenchmarking().start)
