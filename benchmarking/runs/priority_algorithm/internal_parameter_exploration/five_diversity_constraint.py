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
    Gender,
    ScenarioAttribute,
    Gpa,
    Race,
    Age,
)
from api.dataclasses.tokenization_constraint import TokenizationConstraint
from benchmarking.data.interfaces import StudentProvider
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.custom_student_providers import (
    CustomOneHundredAndTwentyStudentProvider,
    Major,
)
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.run_utils import (
    plot_and_save_points_dict,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class FiveDiversityConstraint(Run):
    def start(self, num_trials: int = 30, generate_graphs: bool = True):
        class_sizes = [120]
        num_teams = 30
        student_providers: Dict[int, StudentProvider] = {
            120: CustomOneHundredAndTwentyStudentProvider(),
        }

        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [1, 5, 10, 20, 30]

        scenario = FiveDiversityConstraintScenario(
            value_of_female=Gender.FEMALE.value,
            value_of_a=Gpa.A.value,
            value_of_21=21,
            value_of_math=Major.MATH.value,
            value_of_european=Race.European.value,
        )
        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageCosineDifference": AverageCosineDifference(),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups={
                    ScenarioAttribute.GENDER.value: [_.value for _ in Gender.values()],
                    ScenarioAttribute.GPA.value: [_.value for _ in Gpa.values()],
                    ScenarioAttribute.AGE.value: [_.value for _ in Age.values()],
                    ScenarioAttribute.MAJOR.value: [_.value for _ in Major.values()],
                    ScenarioAttribute.RACE.value: [_.value for _ in Race.values()],
                }
            ),
        }
        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {
            class_size: {start_type: {} for start_type in start_types}
            for class_size in class_sizes
        }
        for class_size in class_sizes:
            for start_type in start_types:
                artifact: SimulationSetArtifact = SimulationSet(
                    settings=SimulationSettings(
                        num_teams=num_teams,
                        scenario=scenario,
                        student_provider=student_providers[class_size],
                        cache_key=f"priority_algorithm/internal_parameter_exploration/class_size_{class_size}/five_diversity_constraint/25_buckets",
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
                        artifacts_dict[class_size][start_type][
                            (max_keep, max_spread, max_iterations)
                        ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                for class_size in class_sizes:
                    points_dict = {}
                    for start_type, artifacts in artifacts_dict[class_size].items():
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
                        "Five Diversity Constraint",
                        "diversity",
                    )


class FiveDiversityConstraintScenario(Scenario):
    def __init__(
        self,
        value_of_female: int,
        value_of_a: int,
        value_of_21: int,
        value_of_math: int,
        value_of_european: int,
    ):
        self.value_of_female = value_of_female
        self.value_of_a = value_of_a
        self.value_of_21 = value_of_21
        self.value_of_math = value_of_math
        self.value_of_european = value_of_european

    @property
    def name(self):
        return "Diversify on gender with a minimum of 2 female"

    @property
    def goals(self) -> List[Goal]:
        return [
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
                ScenarioAttribute.GPA.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_a,
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
                ScenarioAttribute.RACE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_european,
                ),
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(FiveDiversityConstraint().start)
