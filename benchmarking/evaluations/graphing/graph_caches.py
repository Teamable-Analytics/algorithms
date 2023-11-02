import statistics
from typing import List, Dict, Optional

from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.simulation.insight import Insight, InsightOutput
from benchmarking.simulation.simulation import SimulationArtifact


def graph_caches(
    cache_keys: List[List[str]],
    graph_names: List[str],
    line_names: List[str],
    metrics: List[TeamSetMetric],
    x_values: List[float],
    y_labels: List[str],
    x_label: str,
    num_runs: int,
    *args,
    **kwargs,
):
    # Check lengths are all compatible
    if len(cache_keys) != len(line_names):
        raise ValueError("You must have the same number of line names as lines")
    if any([len(line) != len(cache_keys[0]) for line in cache_keys]):
        raise ValueError("All lines must have the same number of points")
    if len(cache_keys[0]) != len(x_values):
        raise ValueError("The length of a line must be the as the number of y values")
    if len(metrics) != len(y_labels) or len(metrics) != len(graph_names):
        raise ValueError("You need a y-label and title for each metric being graphed")

    line_caches: Dict[str, List[SimulationCache]] = {
        line_names[i]: [SimulationCache(key) for key in cache_keys[i]]
        for i in range(len(line_names))
    }
    # Check that all caches exist
    for line in line_names:
        if any(not cache.exists() for cache in line_caches[line]):
            raise ValueError("All caches must exist")

    simulation_outputs: Dict[str, List[SimulationArtifact]] = {
        line: [cache.get_simulation_artifact() for cache in line_caches[line]]
        for line in line_names
    }
    # Check that each simulation has at least num_runs
    for i, line in enumerate(line_names):
        for j in range(len(simulation_outputs[line])):
            if len(simulation_outputs[line][j][0]) < num_runs:
                raise ValueError(
                    f"Cache {cache_keys[i][j]} does not have {num_runs} run{'s' if num_runs != 1 else ''}"
                )

    # Get an Insight for each simulation output. Limit outputs to only use the first num_run results
    insights: Dict[str, List[Insight]] = {
        line: [
            Insight(output[0][:num_runs], metrics)
            for output in simulation_outputs[line]
        ]
        for line in line_names
    }

    # A list of insight outputs for each line. Each InsightOutput contributes one point (y-value) to each graph
    insight_outputs: Dict[str, List[InsightOutput]] = {
        line: [insight.generate() for insight in insights[line]] for line in line_names
    }

    for metric, y_label, graph_name in zip(metrics, y_labels, graph_names):
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
                title=graph_name,
                data=list(graph_data.values()),
                x_label=x_label,
                y_label=y_label,
                *args,
                **kwargs,
            )
        )
