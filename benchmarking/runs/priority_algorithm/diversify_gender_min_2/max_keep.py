from typing import Dict
import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2.interfaces import (
    DiversifyGenderMin2PriorityAlgorithm,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2MaxKeep(DiversifyGenderMin2PriorityAlgorithm):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal: Run diversify gender scenario while varying the maximum keep argument for the priority algorithm.
        """

        # Defining our changing x-values (in the graph sense)
        max_keep = list(range(1, 10))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for keep in max_keep:
            print("MAX KEEP /", keep)
            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2/max_keep/{keep}",
                max_keep=keep,
            ).run(num_runs=num_trials)
            artifacts[keep] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two Runtimes with Varied Max Keep",
                "AverageGiniIndex": "Diversify Gender With Min of Two Average Gini Index with Varied Max Keep",
                "PrioritySatisfaction": "Diversity Gender With Min of Two Satisfied Priorities with Varied Max Keep",
            }
            self.generate_graphs(
                artifacts=artifacts,
                x_label="Number of Children to Keep",
                graph_names=graph_names,
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2MaxKeep().start)
