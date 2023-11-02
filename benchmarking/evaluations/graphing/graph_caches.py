import statistics
from typing import List, Dict

from benchmarking.caching.simulation_cache import SimulationCache
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.simulation.insight import Insight, InsightOutput
from benchmarking.simulation.simulation import SimulationArtifact


def graph_caches(
    cache_keys: List[List[str]],
    metrics: List[TeamSetMetric],
    graph_titles: List[str],
    y_labels: List[str],
    line_names: List[str],
    x_values: List[float],
    x_label: str,
    num_runs: int,
    **kwargs,
):
    """
    Generates graphs given a 2D array of cache keys where each inner array is for one line in a graph (i.e. for one algorithm).
    Each element of one of the inner arrays would vary only by the number of students in the TeamSet (or by whatever you want on the x-axis).

    Also supplied is a list of metrics, each of which will produce a graph. Along with each metric should be a graph title and a y-axis label.

    Lastly, supply a list of x-values with length equal to that of the length of one of the inner arrays in cache_keys as well as a label to describe the x-values.

    You can also pass any argument that LineGraphMetadata also takes as a kwarg.
    """

    # Check lengths are all compatible
    if len(cache_keys) != len(line_names):
        raise ValueError("You must have the same number of line names as lines")
    if any([len(line) != len(cache_keys[0]) for line in cache_keys]):
        raise ValueError("All lines must have the same number of points")
    if len(cache_keys[0]) != len(x_values):
        raise ValueError("The length of a line must be the as the number of y values")
    if len(metrics) != len(y_labels) or len(metrics) != len(graph_titles):
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

    for metric, y_label, graph_name in zip(metrics, y_labels, graph_titles):
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
                **kwargs,
            )
        )
