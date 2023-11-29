from typing import Dict
import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2.interfaces import (
    DiversifyGenderMin2PriorityAlgorithm,
)
from benchmarking.runs.priority_algorithm.diversify_gender_min_2_lower_priority_constants.interfaces import \
    DiversifyGenderMin2LowerPriorityConstants
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2MaxKeep(DiversifyGenderMin2LowerPriorityConstants):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        """
        Goal: Run diversify gender scenario while varying the maximum spread argument for the priority algorithm.
        The constants for the priority algorithm are also reduced compared to the original diversify_gender_min_2 runs.
        """

        # Defining our changing x-values (in the graph sense)
        max_spread = list(range(1, 11))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for spread in max_spread:
            print("MAX SPREAD /", spread)
            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2_lower_constants/max_spread/{spread}",
                max_spread=spread,
            ).run(num_runs=num_trials)
            artifacts[spread] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two Runtimes with Varied Max Spread",
                "AverageGiniIndex": "Diversify Gender With Min of Two Average Gini Index with Varied Max Spread",
                "PrioritySatisfaction": "Diversity Gender With Min of Two Satisfied Priorities with Varied Max Spread",
            }
            self.generate_graphs(
                artifacts=artifacts,
                x_label="Maximum Spread",
                graph_names=graph_names,
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2MaxKeep().start)
