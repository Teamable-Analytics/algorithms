from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineSimilarity
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction


def get_pretty_metric_name(metric: TeamSetMetric) -> str:
    if isinstance(metric, PrioritySatisfaction):
        return "Priority Satisfaction"
    if isinstance(metric, AverageCosineSimilarity):
        return "Cosine Similarity"
    # if isinstance(metric, AverageCosineDifference):
    #     pass
