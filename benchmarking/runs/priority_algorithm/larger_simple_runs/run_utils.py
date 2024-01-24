import json
from os import path
from typing import List, Dict, Tuple

from api.ai.interfaces.algorithm_config import PriorityAlgorithmStartType
from benchmarking.evaluations.graphing.graph_3d import Surface3D, graph_3d
from benchmarking.evaluations.interfaces import TeamSetMetric
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


def get_pretty_metric_name(metric: TeamSetMetric) -> str:
    if isinstance(metric, PrioritySatisfaction):
        return "Priority Satisfaction"
    if isinstance(metric, AverageCosineDifference):
        return "Intra-Heterogeneity"
    if isinstance(metric, AverageProjectRequirementsCoverage):
        return "Project Coverage"
    if isinstance(metric, AverageSocialSatisfaction):
        return "Social Satisfaction"
    return "Score"


def save_points(surfaces: List[Surface3D], path: str):
    points = {s.label: s.points for s in surfaces}

    with open(f"{path}.json", "w+") as f:
        json.dump(points, f)


def get_graph_params() -> Dict:
    return {
        "x_label": "K",
        "y_label": "Spread",
        "z_lim": (0, 1),
        "invert_xaxis": True,
        "plot_legend": True,
        "save_graph": True,
    }


def plot_points_dict(
    points_dict: Dict[PriorityAlgorithmStartType, Dict[Tuple[int, int, int], float]],
    max_iterations_range: List[int],
):
    for max_iterations in max_iterations_range:
        surfaces: List[Surface3D] = []
        for start_type, points in points_dict.items():
            surfaces.append(
                Surface3D(
                    points=[
                        (keep, spread, score)
                        for (
                            keep,
                            spread,
                            iterations,
                        ), score in points.items()
                        if iterations == max_iterations
                    ],
                    label=f"{start_type.value} start".title(),
                    color="blue" if start_type.value == "weight" else "red",
                    linestyle="solid" if start_type.value == "weight" else "dashed",
                )
            )
        save_loc = path.abspath(
            path.join(
                path.dirname(__file__),
                "graphs",
                "projects",
                f"{get_pretty_metric_name(metric)} - {max_iterations} Iterations",
            )
        )
        graph_3d(
            surfaces,
            graph_title=f"Priority Algorithm Parameters vs {get_pretty_metric_name(metric)}\n~3 Project Scenario, {max_iterations} iterations, 120 students~",
            z_label=get_pretty_metric_name(metric),
            **get_graph_params(),
            filename=save_loc,
        )
        save_points(surfaces, save_loc)
