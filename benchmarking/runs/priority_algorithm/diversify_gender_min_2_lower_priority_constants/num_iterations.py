from typing import Dict
import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2_lower_priority_constants.interfaces import (
    DiversifyGenderMin2LowerPriorityConstants,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2NumIterations(DiversifyGenderMin2LowerPriorityConstants):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal: Run diversify gender scenario while varying the maximum number of iterations.
        The constants for the priority algorithm are also reduced compared to the original diversify_gender_min_2 runs.
        """

        # Defining our changing x-values (in the graph sense)
        num_iterations = list(range(20, 401, 20))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for iteration in num_iterations:
            print("MAX NUM ITERATIONS /", iteration)
            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2_lower_priority_constants/num_iterations/{iteration}",
                max_iterate=iteration,
            ).run(num_runs=num_trials)
            artifacts[iteration] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two Runtimes with Varied Max Iterations",
                "AverageGiniIndex": "Diversify Gender With Min of Two Average Gini Index with Varied Max Iterations",
                "PrioritySatisfaction": "Diversity Gender With Min of Two Satisfied Priorities with Varied Max Iterations",
            }
            self.generate_graphs(
                artifacts=artifacts,
                x_label="Max Number of Iterations",
                graph_names=graph_names,
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2NumIterations().start)
