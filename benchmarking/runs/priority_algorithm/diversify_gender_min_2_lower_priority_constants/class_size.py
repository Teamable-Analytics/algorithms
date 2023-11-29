import math
from typing import Dict
import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2_lower_priority_constants.interfaces import (
    DiversifyGenderMin2LowerPriorityConstants,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2ClassSize(DiversifyGenderMin2LowerPriorityConstants):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal: Run diversify gender scenario while varying the size of the class.
        The constants for the priority algorithm are also reduced compared to the original diversify_gender_min_2 runs.
        """

        # Defining our changing x-values (in the graph sense)
        class_sizes = list(range(20, 401, 20))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            number_of_teams = math.ceil(class_size / 5)

            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2_lower_priority_constants/class_size/{class_size}",
                number_of_students=class_size,
                number_of_teams=number_of_teams,
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two Runtimes with Varied Class Size",
                "AverageGiniIndex": "Diversify Gender With Min of Two Average Gini Index with Varied Class Size",
                "PrioritySatisfaction": "Diversity Gender With Min of Two Satisfied Priorities with Varied Class Size",
            }
            self.generate_graphs(
                artifacts=artifacts, x_label="Class Size", graph_names=graph_names
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2ClassSize().start)
