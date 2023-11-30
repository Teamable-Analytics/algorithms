from typing import Dict
import typer
from benchmarking.runs.priority_algorithm.diversify_gender_min_2_lower_priority_constants.interfaces import (
    DiversifyGenderMin2LowerPriorityConstants,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact


class DiversifyGenderMin2MaxTime(DiversifyGenderMin2LowerPriorityConstants):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal:  Goal: Run diversify gender scenario while varying the maximum time argument for the priority algorithm.
        The constants for the priority algorithm are also reduced compared to the original diversify_gender_min_2 runs.
        """

        # Defining our changing x-values (in the graph sense)
        times = list(range(2, 31, 2))

        artifacts: Dict[int, SimulationSetArtifact] = {}

        for time in times:
            print("TIME /", time)
            simulation_set_artifact = self.simulation_set(
                cache_key=f"priority_algorithm/diversify_gender_min_2_lower_priority_constants/max_time/{time}_seconds",
                max_time=time,
            ).run(num_runs=num_trials)
            artifacts[time] = simulation_set_artifact

        if generate_graphs:
            graph_names = {
                Insight.KEY_RUNTIMES: "Diversify Gender With Min of Two \n Runtimes with Varied Max Time",
                "AverageGiniIndex": "Diversify Gender With Min of Two \n Average Gini Index with Varied Max Time",
                "PrioritySatisfaction": "Diversity Gender With Min of Two \n Satisfied Priorities with Varied Max Time",
            }
            self.generate_graphs(
                artifacts=artifacts,
                x_label="Maximum Time",
                graph_names=graph_names,
            )


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2MaxTime().start)
