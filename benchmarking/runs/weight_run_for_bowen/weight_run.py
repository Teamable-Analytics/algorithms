from typing import List

import typer

from api.ai.interfaces.algorithm_config import WeightAlgorithmConfig
from api.models.enums import AlgorithmType, DiversifyType
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.runs.interfaces import Run
from benchmarking.runs.weight_run_for_bowen.bowens_data_provider import (
    ATTRIBUTE_VALUE,
    BowensDataProvider,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class WeightRun(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = BowenScenario()

        metrics = {
            "AverageCosineDifference": AverageCosineDifference(),
        }

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=13,
                scenario=scenario,
                student_provider=BowensDataProvider(),
                cache_key=f"weight_run_for_bowen/weight_run/",
            ),
            algorithm_set={AlgorithmType.WEIGHT: [WeightAlgorithmConfig()]},
        ).run(num_runs=num_trials)

        insight_output_set = Insight.get_output_set(artifact, list(metrics.values()))
        print(insight_output_set)
        cosine_differences = Insight.average_metric(
            insight_output_set, "AverageCosineDifference"
        )
        print(cosine_differences)


class BowenScenario(Scenario):
    @property
    def name(self) -> str:
        return "Bowen Scenario to diversify on attribute attribute value"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(DiversifyType.DIVERSIFY, ATTRIBUTE_VALUE),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(WeightRun().start)
