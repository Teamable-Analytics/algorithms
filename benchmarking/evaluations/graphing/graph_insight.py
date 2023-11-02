import statistics
from typing import List, Dict, Optional

from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.simulation.insight import Insight, InsightOutput
from benchmarking.simulation.simulation import SimulationArtifact


class InsightGrapher:
    @classmethod
    def f(
        cls,
        cache_keys: List[List[str]],
        graph_name: str,
        line_names: List[str],
        metrics: List[TeamSetMetric],
        x_values: List[float],
        y_labels: List[str],
        x_label: str,
        save: Optional[bool] = False,
    ):
        # Check lengths are all compatible
        if len(cache_keys) != len(line_names):
            raise ValueError("You must have the same number of line names as lines")
        if any([len(line) != len(cache_keys[0]) for line in cache_keys]):
            raise ValueError("All lines must have the same number of points")
        if len(cache_keys[0]) != len(x_values):
            raise ValueError(
                "The length of a line must be the as the number of y values"
            )
        if len(metrics) != len(y_labels):
            raise ValueError("You need a y-label for each metric being graphed")

        line_caches: Dict[str, List[SimulationCache]] = {
            line_names[i]: [SimulationCache(key) for key in cache_keys[i]]
            for i in range(len(line_names))
        }
        for line in line_names:
            if any(not cache.exists() for cache in line_caches[line]):
                raise ValueError("All caches must exist")

        simulation_outputs: Dict[str, List[SimulationArtifact]] = {
            line: [cache.get_simulation_artifact() for cache in line_caches[line]]
            for line in line_names
        }

        insights: Dict[str, List[Insight]] = {
            line: [Insight(output[0], metrics) for output in simulation_outputs[line]]
            for line in line_names
        }

        # A list of insight outputs for each line. Each InsightOutput contributes one point (y-value) to each graph
        insight_outputs: Dict[str, List[InsightOutput]] = {
            line: [insight.generate() for insight in insights[line]]
            for line in line_names
        }

        for metric, y_label in zip(metrics, y_labels):
            # Each value of this dict is a list of y values for the points
            y_points: Dict[str, List[float]] = {
                line: [
                    statistics.mean(insight_output[metric.name])
                    for insight_output in insight_outputs[line]
                ]
                for line in line_names
            }

            graph_data: Dict[str, GraphData] = {
                line: GraphData(
                    x_data=x_values,
                    y_data=y_points[line],
                    name=line,
                )
                for line in line_names
            }

            line_graph(
                LineGraphMetadata(
                    title=f"{graph_name} - {metric.name}",
                    data=list(graph_data.values()),
                    x_label=x_label,
                    y_label=y_label,
                    save_graph=save,
                )
            )
