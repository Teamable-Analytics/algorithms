from typing import List, Dict
import json

from benchmarking.evaluations.graphing.graph_3d import Surface3D
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.cosine_similarity import (
    AverageCosineSimilarity,
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
        "y_label": "Width",
        "z_lim": (0, 1),
        "invert_xaxis": True,
        "plot_legend": True,
        "save_graph": True,
    }
