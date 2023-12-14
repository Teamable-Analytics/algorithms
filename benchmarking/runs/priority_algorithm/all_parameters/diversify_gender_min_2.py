import re
from typing import Dict, Tuple

import matplotlib
import typer
from matplotlib import pyplot as plt, cm

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import Gender, ScenarioAttribute, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import (
    DiversifyGenderMin2Female,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation import SimulationArtifact
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class DiversifyGenderMin2(Run):
    RATIO_OF_FEMALE_STUDENT = 0.4

    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        """
        Goal:
        - Need to create a run to generate all the data for max spread, max keep, and max iterations
        - Create a graph function to plot the data in 3D and generate the heat map
        - Need to rationalize bounds for each of the items in the plot (consider relationships between features)
        - We will be ignoring max time as it is just an arbitrary value we impose on the algorithm to reduce computation time
        """

        scenario = DiversifyGenderMin2Female(value_of_female=Gender.FEMALE.value)
        class_size = 120
        team_size = 5
        num_teams = class_size // team_size

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - self.RATIO_OF_FEMALE_STUDENT),
                    (Gender.FEMALE, self.RATIO_OF_FEMALE_STUDENT),
                ],
            },
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        # Ranges
        max_keep_range = [10, 500, 1000, 1500, 2000, 2500]
        max_spread_range = [1, 10, 20, 30, 40, 50]
        max_iterations_range = [10, 250, 500, 750, 1000]

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=num_teams,
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=f"priority_algorithm/all_parameters/diversify_gender_min_2/",
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=max_keep,
                        MAX_SPREAD=max_spread,
                        MAX_ITERATE=max_iterations,
                        MAX_TIME=10000000,
                        name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}",
                    )
                    for max_keep in max_keep_range
                    for max_spread in max_spread_range
                    for max_iterations in max_iterations_range
                ]
            },
        ).run(num_runs=num_trials)

        artifacts: Dict[Tuple[int, int, int], SimulationArtifact] = {}
        for name, simulation_artifact in artifact.items():
            match = re.search(
                r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)", name
            )
            if match:
                max_keep = int(match.group(1))
                max_spread = int(match.group(2))
                max_iterations = int(match.group(3))
                artifacts[(max_keep, max_spread, max_iterations)] = simulation_artifact

        if generate_graphs:
            # Process data and plot
            for metric_name, metric in metrics.items():
                # Dict with points[(x, y, z)] = avg metric value (between 0-1)
                points: Dict[Tuple[int, int, int], float] = {}
                for point_location, simulation_artifact in artifacts.items():
                    insight_set = Insight.get_output_set(
                        artifact={"arbitrary_name": simulation_artifact},
                        metrics=[metric],
                    )

                    # Returns a dict[algorithm, value]
                    value_dict = Insight.average_metric(
                        insight_output_set=insight_set, metric_name=metric_name
                    )

                    # Get first value, assumes only one algorithm being run
                    value = list(value_dict.values())[0]
                    if 0.85 <= value:
                        points[point_location] = value

                # Graph data
                fig = plt.figure()
                ax = fig.add_subplot(projection="3d")
                cmap = plt.get_cmap("Blues")
                c_norm = matplotlib.colors.Normalize(
                    vmin=min(list(points.values())), vmax=max(list(points.values()))
                )
                scalar_map = cm.ScalarMappable(norm=c_norm, cmap=cmap)

                values = list(points.values())

                ax.scatter(
                    [x for x, y, z in points.keys()],
                    [y for x, y, z in points.keys()],
                    [z for x, y, z in points.keys()],
                    c=scalar_map.to_rgba(values),
                )

                ax.set_title("Priority Algorithm Parameters vs Priorities Satisfied")
                ax.set_xlabel("Children to Keep")
                ax.set_ylabel("Spread")
                ax.set_zlabel("Number of Iterations")

                # Plot color scale
                scalar_map.set_array(values)
                fig.colorbar(scalar_map, ax=ax, pad=0.15)

                plt.show()


if __name__ == "__main__":
    typer.run(DiversifyGenderMin2().start)
