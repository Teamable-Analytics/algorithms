import re
from typing import Dict, Tuple, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.dataclasses.enums import (
    AlgorithmType,
    DiversifyType,
    TokenizationConstraintDirection,
)
from benchmarking.evaluations.enums import (
    ScenarioAttribute,
    Gender,
    Age,
)
from api.dataclasses.tokenization_constraint import TokenizationConstraint
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.evaluations.goals import (
    DiversityGoal,
    ProjectRequirementGoal,
    WeightGoal,
)
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.custom_projects import (
    get_custom_projects,
)
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.custom_student_providers import (
    CustomOneHundredAndTwentyStudentWithProjectAttributesProvider,
    Major,
)
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.run_utils import (
    plot_and_save_points_dict,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class CombinedProjectsAndDiversityRun(Run):
    def start(self, num_trials: int = 30, generate_graphs: bool = True):
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
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups={
                    ScenarioAttribute.GENDER.value: [_.value for _ in Gender.values()],
                    ScenarioAttribute.AGE.value: [_.value for _ in Age.values()],
                    ScenarioAttribute.MAJOR.value: [_.value for _ in Major.values()],
                }
            ),
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
                    cache_key=f"priority_algorithm/internal_parameter_exploration/class_size_120/combined_run/",
                    initial_teams_provider=initial_teams_provider,
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=1_000_000,
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

                plot_and_save_points_dict(
                    points_dict,
                    max_iterations_range,
                    metric,
                    "Project & Diversify Scenario",
                    "project_and_diversity",
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
            ProjectRequirementGoal(),
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
