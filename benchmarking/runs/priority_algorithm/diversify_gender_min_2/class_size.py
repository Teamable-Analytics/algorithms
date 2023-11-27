import math
from typing import Dict

import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2.interfaces import (
    PriorityAlgorithmParameters,
)
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2ClassSize(PriorityAlgorithmParameters):
    def start(self, num_trials: int = 4, generate_graphs: bool = True):
        """
        Goal: Run diversify gender scenario while varying the size of the class
        """

        # Defining our changing x-values (in the graph sense)
        class_sizes = list(range(50, 101, 50))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for class_size in class_sizes:
            print("CLASS SIZE /", class_size)
            number_of_teams = math.ceil(class_size / 5)

            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2/class_size/{class_size}",
                number_of_students=class_size,
                number_of_teams=number_of_teams,
            ).run(num_runs=num_trials)
            artifacts[class_size] = simulation_set_artifact

        if generate_graphs:
            self.generate_graphs(artifacts=artifacts, x_label="Class Size")


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2ClassSize().start)
