import statistics
from typing import List, Dict

from api.models.enums import AlgorithmType
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.simulation.basic_simulation_set_2 import BasicSimulationSetArtifact
from utils.validation import is_unique

InsightOutput = Dict[str, List[float]]


class Insight:
    KEY_RUNTIMES = "runtimes"

    def __init__(
        self,
        team_sets: List[TeamSet],
        metrics: List[TeamSetMetric],
        run_times: List[float] = None,
    ):
        self.team_sets = team_sets
        self.metrics = metrics
        self.run_times = run_times

        if not self.team_sets:
            raise ValueError("At least one team set must be specified for an insight.")
        if not self.metrics:
            raise ValueError("At least one metric must be specified for an insight.")
        if self.run_times and len(self.run_times) != len(self.team_sets):
            raise ValueError(
                "If you provide run times, you must provide a run time for each team set provided."
            )
        if not is_unique([m.name for m in self.metrics]):
            raise ValueError("The names of each metric specified must be unique.")

        self.insight_output: InsightOutput = {
            metric.name: [] for metric in self.metrics
        }
        self.insight_output.update({Insight.KEY_RUNTIMES: self.run_times})

    def generate(self) -> InsightOutput:
        for metric in self.metrics:
            for team_set in self.team_sets:
                self.insight_output[metric.name].append(metric.calculate(team_set))
        return self.insight_output

    @staticmethod
    def average_metric(
        insight_output_set: Dict[AlgorithmType, InsightOutput], metric_name: str
    ) -> Dict[AlgorithmType, float]:
        averages_output = {}

        for algorithm_type in insight_output_set.keys():
            metric_values = insight_output_set[algorithm_type][metric_name]
            averages_output[algorithm_type] = statistics.mean(metric_values)

        return averages_output

    @staticmethod
    def get_output_set(
        artifact: BasicSimulationSetArtifact, metrics: List[TeamSetMetric]
    ) -> Dict[AlgorithmType, InsightOutput]:
        # designed to work with BasicSimulationSet, just a shortcut/utility
        insight_output_set: Dict[AlgorithmType, InsightOutput] = {}

        for algorithm_type in artifact.keys():
            team_sets, run_times = artifact.get(algorithm_type, ([], []))
            insight = Insight(
                team_sets=team_sets, metrics=metrics, run_times=run_times
            ).generate()
            insight_output_set[algorithm_type] = insight

        return insight_output_set
