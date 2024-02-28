from typing import Dict

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType, ScenarioAttribute
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.concentrate_campus import (
    ConcentrateCampusLocation,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.concentration_sanity_check.concentrate_on_campus_location.custom_student_provider import (
    CampusCustomStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import InsightOutput, Insight
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SanityCheckConcentrateOnCampusLocation(Run):
    def start(self, num_trials: int = 30, generate_graphs: bool = True):
        scenario = ConcentrateCampusLocation()

        simulation_settings = SimulationSettings(
            num_teams=2,
            student_provider=CampusCustomStudentProvider(),
            scenario=scenario,
            cache_key=f"sanity_check/campus_concentration",
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        artifact = SimulationSet(
            settings=simulation_settings,
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        name="PriorityAlgorithm",
                    ),
                ],
            },
        ).run(num_runs=num_trials)

        insight_set: Dict[str, InsightOutput] = Insight.get_output_set(
            artifact=artifact, metrics=list(metrics.values())
        )

        average_metrics: Dict[str, Dict[str, float]] = {}
        for metric_name in metrics.keys():
            average_metrics[metric_name] = Insight.average_metric(
                insight_set, metrics[metric_name].name
            )

        print(average_metrics)

        all_teamsets = artifact.get("AlgorithmType.PRIORITY-PriorityAlgorithm")[0]
        for idx, teamset in enumerate(all_teamsets):
            print(f"Teamset {idx + 1}")
            for team in teamset.teams:
                print(
                    f"Team { team.id }: "
                    + str(
                        [
                            student.attributes.get(ScenarioAttribute.LOCATION.value)
                            for student in team.students
                        ]
                    )
                )


if __name__ == "__main__":
    typer.run(SanityCheckConcentrateOnCampusLocation().start)
