from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.priority_algorithm.mutations.greedy_local_max import GreedyLocalMaxMutation
from api.dataclasses.enums import ScenarioAttribute, Gender, Race, AlgorithmType
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


class GreedyLocalMaxBenchmarking(Run):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        class_sizes = [40, 100, 240, 500, 1000]
        portion_of_teams = [0.25, 0.5, 0.75, 1.00]
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
        max_spread = 30
        max_iterate = 30
        max_time = 1_000_000
        artifacts: Dict[int, Dict[str, SimulationSetArtifact]] = {}

        for class_size in class_sizes:
            if class_size not in artifacts:
                artifacts[class_size] = {}
            for ratio in portion_of_teams:
                name = f"mutate_greedy_local_max_{ratio}"
                num_teams = class_size // team_size
                artifacts[class_size][name] = SimulationSet(
                    settings=SimulationSettings(
                        scenario=scenario,
                        student_provider=RealisticMockStudentProvider(class_size),
                        cache_key=f"mutations/greedy_local_max_benchmarking/{name}/class_size_{class_size}/",
                        initial_teams_provider=RealisticMockInitialTeamsProvider(
                            num_teams
                        ),
                    ),
                    algorithm_set={
                        AlgorithmType.PRIORITY: [
                            PriorityAlgorithmConfig(
                                MAX_KEEP=max_keep,
                                MAX_SPREAD=max_spread,
                                MAX_ITERATE=max_iterate,
                                MAX_TIME=max_time,
                                MUTATIONS=[
                                    GreedyLocalMaxMutation(
                                        number_of_teams=round(num_teams * ratio),
                                        num_mutations=max_spread,
                                    )
                                ],
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

                graph_data = []
                for ratio in portion_of_teams:
                    name = f"mutate_greedy_local_max_{ratio}"
                    graph_data.append(
                        GraphData(
                            x_data=class_sizes,
                            y_data=[
                                data[class_size][name] for class_size in class_sizes
                            ],
                            name=name,
                        )
                    )

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
    typer.run(GreedyLocalMaxBenchmarking().start)
