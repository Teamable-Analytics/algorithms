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
