from typing import List
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
    if isinstance(metric, AverageCosineSimilarity):
        return "Cosine Similarity"
    if isinstance(metric, AverageCosineDifference):
        return "Cosine Difference"
    if isinstance(metric, AverageProjectRequirementsCoverage):
        return "Project Coverage"
    if isinstance(metric, AverageSocialSatisfaction):
        return "Social Satisfaction"


def save_points(surfaces: List[Surface3D], path: str):
    points = {s.label: s.points for s in surfaces}

    with open(f"{path}.json", "w+") as f:
        json.dump(points, f)
