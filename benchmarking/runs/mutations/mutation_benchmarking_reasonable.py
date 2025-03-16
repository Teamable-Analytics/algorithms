from typing import Dict

import typer

from algorithms.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from algorithms.ai.priority_algorithm.mutations.greedy_local_max import GreedyLocalMaxMutation
from algorithms.ai.priority_algorithm.mutations.local_max import LocalMaxMutation
from algorithms.ai.priority_algorithm.mutations.local_max_random import LocalMaxRandomMutation
from algorithms.ai.priority_algorithm.mutations.random_slice import RandomSliceMutation
from algorithms.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from algorithms.ai.priority_algorithm.mutations.robinhood import RobinhoodMutation
from algorithms.ai.priority_algorithm.mutations.robinhood_holistic import (
    RobinhoodHolisticMutation,
)
from algorithms.dataclasses.enums import AlgorithmType
from benchmarking.evaluations.enums import ScenarioAttribute, Gender, Race
from benchmarking.data.simulated_data.realistic_class.providers import (
    RealisticMockInitialTeamsProvider,
    RealisticMockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
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
    def start(
        self,
        num_trials: int = 100,
        generate_graphs: bool = False,
        run_with_robinhood: bool = False,
    ):
        class_sizes = [40, 100, 240, 500, 1000]
        team_size = 5

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
                minority_groups_map={
                    ScenarioAttribute.GENDER.value: [Gender.FEMALE.value],
                    ScenarioAttribute.RACE.value: [Race.African.value],
                },
            ),
            Insight.KEY_RUNTIMES: "runtime",
        }

        max_keep = 15
        # In this run, max_spread must be divisible by two so the mutation configs below sum to max_spread
        max_spread = 30
        max_iterate = 30
        max_time = 1_000_000

        mutation_sets = {
            "mutate_random": [RandomSwapMutation(num_mutations=max_spread)],
            "mutate_local_max": [
                LocalMaxMutation(num_mutations=1),
                RandomSwapMutation(num_mutations=max_spread - 1),
            ],
            "mutate_local_max_random": [
                LocalMaxRandomMutation(num_mutations=5),
                RandomSwapMutation(num_mutations=max_spread - 5),
            ],
            "mutate_random_slice": [RandomSliceMutation(num_mutations=max_spread)],
            "mutate_half_random_slice": [
                RandomSliceMutation(num_mutations=max_spread // 2),
                RandomSwapMutation(num_mutations=max_spread // 2),
            ],
            "mutate_greedy_local_max_n_2": [
                GreedyLocalMaxMutation(number_of_teams=2, num_mutations=max_spread)
            ],
            "mutate_greedy_local_max_n_4": [
                GreedyLocalMaxMutation(number_of_teams=4, num_mutations=max_spread)
            ],
            "mutate_greedy_local_max_n_8": [
                GreedyLocalMaxMutation(number_of_teams=8, num_mutations=max_spread)
            ],
            "mutate_greedy_local_max_with_random_swap": [
                GreedyLocalMaxMutation(num_mutations=max_spread // 2),
                RandomSwapMutation(num_mutations=max_spread // 2),
            ],
            "mutate_greedy_local_max_with_random_slice_n_2": [
                GreedyLocalMaxMutation(num_mutations=max_spread // 2),
                RandomSliceMutation(num_mutations=max_spread // 2),
            ],
            "mutate_greedy_local_max_with_random_slice_n_4": [
                GreedyLocalMaxMutation(
                    number_of_teams=4, num_mutations=max_spread // 2
                ),
                RandomSliceMutation(num_mutations=max_spread // 2),
            ],
            "mutate_greedy_local_max_with_random_slice_n_8": [
                GreedyLocalMaxMutation(
                    number_of_teams=8, num_mutations=max_spread // 2
                ),
                RandomSliceMutation(num_mutations=max_spread // 2),
            ],
        }
        if run_with_robinhood:
            mutation_sets.update(
                {
                    "mutate_robinhood": [RobinhoodMutation(max_spread)],
                    "mutate_robinhood_half_random_swap": [
                        RobinhoodMutation(num_mutations=max_spread // 2),
                        RandomSwapMutation(num_mutations=max_spread // 2),
                    ],
                    "mutate_robinhood_holistic": [
                        RobinhoodHolisticMutation(max_spread)
                    ],
                    "mutate_robinhood_holistic_half_random_swap": [
                        RobinhoodHolisticMutation(num_mutations=max_spread // 2),
                        RandomSwapMutation(num_mutations=max_spread // 2),
                    ],
                }
            )

        artifacts: Dict[int, Dict[str, SimulationSetArtifact]] = {}

        for class_size in class_sizes:
            if class_size not in artifacts:
                artifacts[class_size] = {}
            for mutation_name, mutation_set in mutation_sets.items():
                artifacts[class_size][mutation_name] = SimulationSet(
                    settings=SimulationSettings(
                        scenario=scenario,
                        student_provider=RealisticMockStudentProvider(class_size),
                        cache_key=f"mutations/mutation_benchmarking_reasonable/{mutation_name}/class_size_{class_size}/",
                        initial_teams_provider=RealisticMockInitialTeamsProvider(
                            class_size // team_size
                        ),
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
                            metrics=[
                                metric
                                if metric != "runtime"
                                else AverageProjectRequirementsCoverage()
                            ],
                        )
                        avg_metric = list(
                            Insight.average_metric(
                                insight_output_set=insight_output_set,
                                metric_name=metric_name
                                if metric_name == Insight.KEY_RUNTIMES
                                else metric.name,
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
                        y_label=metric_name,
                        title=f"Class Size vs. {metric_name}",
                        data=graph_data,
                        y_lim=GraphAxisRange(0, 1),
                    )
                )


if __name__ == "__main__":
    typer.run(MutationBenchmarking().start)
