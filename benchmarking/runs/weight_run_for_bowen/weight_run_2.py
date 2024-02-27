from math import ceil
from typing import List

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
)
from api.models.enums import AlgorithmType, DiversifyType, ScenarioAttribute
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.runs.interfaces import Run
from benchmarking.runs.weight_run_for_bowen.bowens_data_provider import (
    Attributes,
    BowensDataProvider2,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class WeightRun(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = BowenScenario2()

        metrics = {
            "AverageCosineDifference": AverageCosineDifference(),
        }

        student_provider = BowensDataProvider2()

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=ceil(student_provider.num_students / 4),
                scenario=scenario,
                student_provider=student_provider,
                cache_key=f"priority_algorithm/weight_run_for_bowen/weight_run_2/",
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=15,
                        MAX_SPREAD=30,
                        MAX_ITERATE=30,
                        MAX_TIME=100000,
                    )
                ]
            },
        ).run(num_runs=num_trials)

        insight_output_set = Insight.get_output_set(artifact, list(metrics.values()))
        print(insight_output_set)
        cosine_differences = Insight.average_metric(
            insight_output_set, "AverageCosineDifference"
        )
        print(cosine_differences)


class BowenScenario2(Scenario):
    @property
    def name(self) -> str:
        return "Diversify on score and concentrate on timeslot"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.TUTOR_PREFERENCE.value,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.SCORE.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(WeightRun().start)
