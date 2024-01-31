import os
from typing import Dict, List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    WeightAlgorithmConfig,
    GroupMatcherAlgorithmConfig,
    RandomAlgorithmConfig,
    DoubleRoundRobinAlgorithmConfig,
)
from api.models.enums import (
    AlgorithmType,
    DiversifyType,
    ScenarioAttribute,
    RequirementsCriteria,
)
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.data.real_data.cosc499_s2023_provider.providers import (
    COSC499S2023StudentProvider,
    COSC499S2023InitialTeamsProvider,
)
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    DiversityGoal,
    WeightGoal,
    ProjectRequirementGoal,
    PreferenceGoal,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import (
    AverageCosineDifference,
    AverageCosineSimilarity,
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


def additive_utility_function(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 0.0

    return sum(
        [student.meets_requirement(requirement) for requirement in team.requirements]
    ) / float(len(team.requirements))


class Cosc499Scenario4Run(Run):
    TEAM_SIZE = 4

    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = Scenario4(max_num_friends=3, max_num_enemies=3, max_num_timeslots=6)

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageCosineDifference": AverageCosineDifference(
                [ScenarioAttribute.GPA.value]
            ),
            "AverageCosineSimilarity": AverageCosineSimilarity(
                [ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
            ),
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_happy_team_all_have_friend_no_enemy
            ),
            "AverageTimeslotCoverage": AverageTimeslotCoverage(
                available_timeslots=[1, 2, 3, 4, 5, 6],
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
        }

        student_provider = COSC499S2023StudentProvider()
        initial_teams_provider = COSC499S2023InitialTeamsProvider()
        simulation_settings = SimulationSettings(
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
                # AlgorithmType.GROUP_MATCHER: [
                #     GroupMatcherAlgorithmConfig(
                #         csv_output_path=os.path.abspath(
                #             os.path.join(
                #                 os.path.dirname(__file__),
                #                 "../../../..",
                #                 f"api/ai/group_matcher_algorithm/group-matcher/inpData/{41}-generated.csv",
                #             )
                #         ),
                #         group_matcher_run_path=os.path.abspath(
                #             os.path.join(
                #                 os.path.dirname(__file__),
                #                 "../../../..",
                #                 "api/ai/group_matcher_algorithm/group-matcher/run.py",
                #             )
                #         ),
                #     ),
                # ],
                AlgorithmType.DRR: [
                    DoubleRoundRobinAlgorithmConfig(
                        utility_function=additive_utility_function
                    )
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

            # Print data as csv
            data = {
                "": list(graph_data["PrioritySatisfaction"].keys()),
            }
            for metric_name, inner_data in graph_data.items():
                data[metric_name] = []
                for algorithm_name, g_data in inner_data.items():
                    data[metric_name].extend([str(_) for _ in g_data.y_data])
            for k, v in data.items():
                print(",".join([k] + v))


class Scenario4(Scenario):
    def __init__(
        self, max_num_friends: int, max_num_enemies: int, max_num_timeslots: int
    ):
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies
        self.max_num_timeslots = max_num_timeslots

    @property
    def name(self) -> str:
        return "Prioritizes project requirements, then diversify GPA, then concentrate timeslot, then friends/enemies"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GPA.value,
            ),
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
                max_num_choices=self.max_num_timeslots,
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
            WeightGoal(
                project_requirement_weight=3,
                social_preference_weight=1,
                diversity_goal_weight=2,
            ),
        ]


if __name__ == "__main__":
    typer.run(Cosc499Scenario4Run().start)
