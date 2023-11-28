from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    RandomAlgorithmConfig,
    WeightAlgorithmConfig,
)
from api.ai.priority_algorithm.mutations import (
    mutate_local_max,
    mutate_random_swap,
    mutate_local_max_random,
    mutate_local_max_double_random,
    mutate_robinhood,
    mutate_robinhood_holistic,
)
from api.models.enums import ScenarioAttribute, Gender, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from benchmarking.evaluations.metrics.maximum_gini_index import MaximumGiniIndex
from benchmarking.evaluations.metrics.minimum_gini_index import MinimumGiniIndex
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.diversify_gender_min_2.interfaces import DiversifyGenderMin2PriorityAlgorithm
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class DiversifyGenderMin2MaxTime(DiversifyGenderMin2PriorityAlgorithm):
    def start(self, num_trials: int = 4, generate_graphs: bool = True):
        """
        Goal:  Goal: Run diversify gender scenario while varying the maximum time argument for the priority algorithm.
        """

        # Defining our changing x-values (in the graph sense)
        times = list(range(2, 5, 2))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for time in times:
            print("TIME /", time)
            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2/max_time/{time}_seconds",
                max_time=time
            ).run(num_runs=num_trials)
            artifacts[time] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two Runtimes with Varied Max Time",
                "AverageGiniIndex": "Diversify Gender With Min of Two Average Gini Index with Varied Max Time",
                "PrioritySatisfaction": "Diversity Gender With Min of Two Satisfied Priorities with Varied Max Time",
            }
            self.generate_graphs(
                artifacts=artifacts,
                x_label="Maximum Time",
                graph_names=graph_names,
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2MaxTime().start)
