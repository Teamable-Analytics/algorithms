from typing import Dict, Tuple

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.priority_algorithm.mutations.random_swap import RandomSwapMutation
from api.ai.priority_algorithm.mutations.random_team_size import RandomTeamSizeMutation
from api.ai.priority_algorithm.mutations.team_size_low_disruption import (
    TeamSizeLowDisruptionMutation,
)
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


class VariableTeamSizeMutationBenchmark(Run):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        class_sizes = [40, 100, 240, 500, 1000]
        team_sizes = [
            (2, 8),
            (3, 7),
            (4, 6),
        ]
        initial_team_size = 5

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

        ####
        # LESS BEEF ™
        max_keep = 15
        max_spread = 30
        max_iterate = 30
        max_time = 1_000_000
        ####

        num_teams = [2, 4, 6, 8]
        num_mutations = [1, 5, 10, 15]
        mutation_sets = {
            f"{mutation.__name__}_{num_team}_teams_{num_mutation}_mutations": [
                mutation(number_of_teams=num_team, num_mutations=num_mutation),
                RandomSwapMutation(num_mutations=max_spread - num_mutation),
            ]
            for num_mutation in num_mutations
            for num_team in num_teams
            for mutation in [RandomTeamSizeMutation, TeamSizeLowDisruptionMutation]
        }

        artifacts: Dict[
            int, Dict[Tuple[int, int], Dict[str, SimulationSetArtifact]]
        ] = {}

        for class_size in class_sizes:
            if class_size not in artifacts:
                artifacts[class_size] = {}
            for min_size, max_size in team_sizes:
                dict_key = (min_size, max_size)
                if dict_key not in artifacts[class_size]:
                    artifacts[class_size][dict_key] = {}
                for mutation_name, mutations in mutation_sets.items():
                    artifacts[class_size][dict_key][mutation_name] = SimulationSet(
                        settings=SimulationSettings(
                            scenario=scenario,
                            student_provider=RealisticMockStudentProvider(class_size),
                            cache_key=f"mutations/team_size/{mutation_name}/class_size_{class_size}/",
                            initial_teams_provider=RealisticMockInitialTeamsProvider(
                                class_size // initial_team_size
                            ),
                            min_team_size=min_size,
                            max_team_size=max_size,
                        ),
                        algorithm_set={
                            AlgorithmType.PRIORITY: [
                                PriorityAlgorithmConfig(
                                    MAX_KEEP=max_keep,
                                    MAX_SPREAD=max_spread,
                                    MAX_ITERATE=max_iterate,
                                    MAX_TIME=max_time,
                                    MUTATIONS=mutations,
                                ),
                            ]
                        },
                    ).run(num_runs=num_trials)

        if generate_graphs:
            for metric_name, metric in metrics.items():
                data = {}
                for class_size, _1 in artifacts.items():
                    if class_size not in data:
                        data[class_size] = {}
                    for team_size, _2 in _1.items():
                        if team_size not in data[class_size]:
                            data[class_size][team_size] = {}
                        for mutation_name, artifact in _2.items():
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
                            data[class_size][team_size][mutation_name] = avg_metric

                for team_size in team_sizes:
                    graph_data = [
                        GraphData(
                            x_data=class_sizes,
                            y_data=[
                                data[class_size][team_size][mutation_name]
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
                            title=f"Class Size vs. {metric_name}\n~Min Team Size {team_size[0]}, Max Team Size {team_size[1]}~",
                            data=graph_data,
                            # y_lim=GraphAxisRange(0, 1)
                            # if metric_name != Insight.KEY_RUNTIMES
                            # else None,
                            save_graph=True,
                            file_name=f"graphs/Class Size vs. {metric_name} - Team Size ({team_size[0]} {team_size[1]}).png",
                        )
                    )
                    # Hi Opey


if __name__ == "__main__":
    typer.run(VariableTeamSizeMutationBenchmark().start)
