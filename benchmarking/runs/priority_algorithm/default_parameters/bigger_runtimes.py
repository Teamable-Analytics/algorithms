from typing import List

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import (
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    Gender,
    Gpa,
    AlgorithmType,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.goals import DiversityGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_strictly_happy_team_friend,
    is_happy_team_1hp_friend,
)
from benchmarking.evaluations.scenarios.include_social_friends import (
    IncludeSocialFriends,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class Runtimes(Run):
    def start(self, num_trials: int = 100, generate_graphs: bool = False):
        class_sizes = [1000]
        team_size = 4

        scenarios = {
            "diversity": OneDiversityScenario(value_of_female=Gender.FEMALE.value),
            "social": IncludeSocialFriends(max_num_friends=3, max_num_enemies=0),
        }

        for class_size in class_sizes:
            print(f"Class size: {class_size}")
            student_provider = MockStudentProvider(
                settings=MockStudentProviderSettings(
                    number_of_students=class_size,
                    friend_distribution="cluster",
                    number_of_friends=3,
                    attribute_ranges={
                        ScenarioAttribute.GENDER.value: [
                            (Gender.FEMALE, 0.5),
                            (Gender.MALE, 0.5),
                        ],
                        ScenarioAttribute.GPA.value: [
                            (Gpa.A, 0.5),
                            (Gpa.B, 0.5),
                        ],
                    },
                )
            )

            for scenario_name, scenario in scenarios.items():
                artifact = SimulationSet(
                    settings=SimulationSettings(
                        num_teams=class_size // team_size,
                        scenario=scenario,
                        student_provider=student_provider,
                        cache_key=f"priority_algorithm/default_parameters/bigger_{scenario_name}/class_size_{class_size}",
                    ),
                    algorithm_set={
                        AlgorithmType.PRIORITY: [
                            PriorityAlgorithmConfig(
                                MAX_KEEP=30,
                                MAX_SPREAD=100,
                                MAX_ITERATE=500,
                                MAX_TIME=1000000,
                                name=f"config_250-100-30",
                            )
                            if "social" in scenario_name
                            else PriorityAlgorithmConfig(
                                MAX_KEEP=15,
                                MAX_SPREAD=30,
                                MAX_ITERATE=60,
                                MAX_TIME=1000000,
                                name=f"config_30-30-15",
                            ),
                        ],
                    },
                ).run(num_runs=num_trials)

                metrics = {
                    "PrioritySatisfaction": PrioritySatisfaction(
                        goals_to_priorities(scenario.goals),
                        False,
                    ),
                    "AverageSocialSatisfaction": AverageSocialSatisfaction(
                        metric_function=is_happy_team_1hp_friend,
                    ),
                }
                insight_output = Insight.get_output_set(
                    artifact, list(metrics.values())
                )
                print(scenario_name + ":")
                print(
                    f"Runtime: {Insight.average_metric(insight_output, Insight.KEY_RUNTIMES)}"
                )
                for name in metrics.keys():
                    print(f"{name}: {Insight.average_metric(insight_output, name)}")


class OneDiversityScenario(Scenario):
    def __init__(self, value_of_female: int):
        self.value_of_female = value_of_female

    @property
    def name(self) -> str:
        return "Scenario with one diversity goal"

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
        ]


if __name__ == "__main__":
    typer.run(Runtimes().start)
