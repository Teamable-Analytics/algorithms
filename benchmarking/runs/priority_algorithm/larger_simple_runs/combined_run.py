import re
from os import path
from typing import Dict, Tuple, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.models.enums import (
    AlgorithmType,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    RequirementsCriteria,
    Gender,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.evaluations.goals import (
    DiversityGoal,
    ProjectRequirementGoal,
    WeightGoal,
)
from benchmarking.evaluations.graphing.graph_3d import graph_3d, Surface3D
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_projects import (
    get_custom_projects,
)
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    CustomOneHundredAndTwentyStudentWithProjectAttributesProvider,
    Major,
)
from benchmarking.runs.priority_algorithm.larger_simple_runs.run_utils import (
    get_pretty_metric_name,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class CombinedProjectsAndDiversityRun(Run):
    def start(self, num_trials: int = 30, generate_graphs: bool = False):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [1] + list(range(5, 31, 5))

        scenario = DiversityAndProjectsScenario(
            value_of_female=Gender.FEMALE.value,
            value_of_math=Major.MATH.value,
            value_of_21=21,
        )
        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageCosineDifference": AverageCosineDifference(),
            "AverageProjectRequirementCoverage": AverageProjectRequirementsCoverage(),
        }

        initial_teams_provider = MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=get_custom_projects(),
            )
        )

        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {start_type: {} for start_type in start_types}
        for start_type in start_types:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=CustomOneHundredAndTwentyStudentWithProjectAttributesProvider(),
                    cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/combined_run/",
                    initial_teams_provider=initial_teams_provider,
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=10000000,
                            START_TYPE=start_type,
                            name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}-{start_type.value}_start",
                        )
                        for max_keep in max_keep_range
                        for max_spread in max_spread_range
                        for max_iterations in max_iterations_range
                    ]
                },
            ).run(num_runs=num_trials)

            for name, simulation_artifact in artifact.items():
                match = re.search(
                    r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)",
                    name,
                )
                if match:
                    max_keep = int(match.group(1))
                    max_spread = int(match.group(2))
                    max_iterations = int(match.group(3))
                    artifacts_dict[start_type][
                        (max_keep, max_spread, max_iterations)
                    ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                points_dict = {}
                for start_type, artifacts in artifacts_dict.items():
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
                        points[point_location] = value
                    points_dict[start_type] = points

                for max_iterations in max_iterations_range:
                    surfaces: List[Surface3D] = []
                    for start_type, points in points_dict.items():
                        surfaces.append(
                            Surface3D(
                                points=[
                                    (keep, spread, score)
                                    for (
                                        keep,
                                        spread,
                                        iterations,
                                    ), score in points.items()
                                    if iterations == max_iterations
                                ],
                                label=f"{start_type.value} start".title(),
                                color="blue" if start_type.value == "weight" else "red",
                            )
                        )
                    save_loc = path.abspath(
                        path.join(
                            path.dirname(__file__),
                            "graphs",
                            "project_and_diversity",
                            f"{get_pretty_metric_name(metric)} - {max_iterations} Iterations",
                        )
                    )
                    graph_3d(
                        surfaces,
                        graph_title=f"Priority Algorithm Parameters vs {get_pretty_metric_name(metric)}\n~Project & Diversify Scenario, {max_iterations} iterations, 120 students~",
                        x_label="Max Keep",
                        y_label="Max Spread",
                        z_label=get_pretty_metric_name(metric),
                        z_lim=(0, 1),
                        invert_xaxis=True,
                        plot_legend=True,
                        save_graph=True,
                        filename=save_loc,
                    )


class DiversityAndProjectsScenario(Scenario):
    def __init__(self, value_of_female, value_of_math, value_of_21):
        self.value_of_female = value_of_female
        self.value_of_math = value_of_math
        self.value_of_21 = value_of_21

    @property
    def name(self):
        return "Diversify constraints with project constrains"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.MAJOR.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_math,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_21,
                ),
            ),
            WeightGoal(
                project_requirement_weight=2,
                diversity_goal_weight=1,
            ),
        ]


if __name__ == "__main__":
    typer.run(CombinedProjectsAndDiversityRun().start)
