import math
import os
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
)
from api.models.enums import (
    AlgorithmType,
    DiversifyType,
    ScenarioAttribute,
    RequirementsCriteria,
)
from benchmarking.data.real_data.cosc499_s2023_provider.providers import (
    COSC499S2023StudentProvider,
    COSC499S2023InitialTeamConfigurationProvider,
    COSC499S2023InitialTeamsProvider,
)
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    ProjectRequirementGoal,
    PreferenceGoal,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.cosine_similarity import (
    AverageCosineDifference,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_all_have_friend_no_enemy,
)
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class ConcentrateTimeslotDiversifyGenderAndStudentLevel(Run):
    TEAM_SIZE = 4

    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = Scenario4(max_num_friends=3, max_num_enemies=3)

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageCosineDifference": AverageCosineDifference(),
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_happy_team_all_have_friend_no_enemy
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
        }

        student_provider = COSC499S2023StudentProvider()
        initial_teams_provider = COSC499S2023InitialTeamsProvider()
        simulation_settings = SimulationSettings(
            num_teams=math.ceil(student_provider.num_students / self.TEAM_SIZE),
            student_provider=student_provider,
            initial_teams_provider=initial_teams_provider,
            scenario=scenario,
            cache_key=f"real_data/cosc_499/499_scenario_4",
        )

        artifacts = SimulationSet(
            settings=simulation_settings,
            algorithm_set={
                AlgorithmType.WEIGHT: [
                    WeightAlgorithmConfig(),
                ],
                AlgorithmType.GROUP_MATCHER: [
                    GroupMatcherAlgorithmConfig(
                        csv_output_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../../..",
                                f"api/ai/group_matcher_algorithm/group-matcher/inpData/{175}-generated.csv",
                            )
                        ),
                        group_matcher_run_path=os.path.abspath(
                            os.path.join(
                                os.path.dirname(__file__),
                                "../../../..",
                                "api/ai/group_matcher_algorithm/group-matcher/run.py",
                            )
                        ),
                    ),
                ],
            },
        ).run(num_runs=1)

        artifacts.update(
            SimulationSet(
                settings=simulation_settings,
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=1000000,
                            MAX_KEEP=30,
                            MAX_SPREAD=100,
                            MAX_ITERATE=250,
                        ),
                    ],
                    AlgorithmType.RANDOM: [
                        RandomAlgorithmConfig(),
                    ],
                },
            ).run(num_runs=num_trials)
        )

        if generate_graphs:
            graph_data: Dict[str, Dict[str, GraphData]] = {}
            insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
                artifact=artifacts, metrics=list(metrics.values())
            )

            average_metrics: Dict[str, Dict[str, float]] = {}
            for metric_name in metrics.keys():
                average_metrics[metric_name] = Insight.average_metric(
                    insight_set, metrics[metric_name].name
                )

            for metric_name, average_metric in average_metrics.items():
                if metric_name not in graph_data:
                    graph_data[metric_name] = {}
                for algorithm_name, value in average_metric.items():
                    if algorithm_name not in graph_data[metric_name]:
                        graph_data[metric_name][algorithm_name] = GraphData(
                            x_data=[120],
                            y_data=[value],
                            name=algorithm_name,
                        )
                    else:
                        graph_data[metric_name][algorithm_name].x_data.append(120)
                        graph_data[metric_name][algorithm_name].y_data.append(value)

            for metric_name in metrics.keys():
                y_label = metrics[metric_name].name
                y_lim = GraphAxisRange(0, 1.1)
                line_graph(
                    LineGraphMetadata(
                        x_label="Class Size",
                        y_label=y_label,
                        title="COSC 341 Simplified Scenario",
                        data=list(graph_data[metric_name].values()),
                        y_lim=y_lim,
                    ),
                )


class Scenario4(Scenario):
    def __init__(self, max_num_friends: int, max_num_enemies: int):
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies

    @property
    def name(self) -> str:
        return "Prioritizes project requirements, then friends/enemies, then diversifies GPA"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED,
            ),
            PreferenceGoal(
                direction=PreferenceDirection.INCLUDE,
                subject=PreferenceSubject.FRIENDS,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
            PreferenceGoal(
                direction=PreferenceDirection.EXCLUDE,
                subject=PreferenceSubject.ENEMIES,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
            # DiversityGoal(
            #     DiversifyType.DIVERSIFY,
            #     ScenarioAttribute.GPA.value,
            #     tokenization_constraint=TokenizationConstraint(
            #         direction=TokenizationConstraintDirection.MIN_OF,
            #         threshold=2,
            #         value=Gpa.A.value,
            #     ),
            # ),
            # DiversityGoal(
            #     DiversifyType.DIVERSIFY,
            #     ScenarioAttribute.GPA.value,
            #     tokenization_constraint=TokenizationConstraint(
            #         direction=TokenizationConstraintDirection.MIN_OF,
            #         threshold=2,
            #         value=Gpa.B.value,
            #     ),
            # ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GPA.value,
            ),
            WeightGoal(social_preference_weight=2, diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(ConcentrateTimeslotDiversifyGenderAndStudentLevel().start)
