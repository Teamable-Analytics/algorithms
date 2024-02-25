from typing import Dict, Any

from rest_framework import viewsets
from rest_framework.decorators import action
from schema import SchemaError

from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.api.validators.evaluate_team_set_validator import EvaluateTeamSetValidator
from api.models.team_set.serializer import TeamSetSerializer
from benchmarking.evaluations.interfaces import TeamSetMetric
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.average_timeslot_coverage import (
    AverageTimeslotCoverage,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_allhp_friend,
)


class EvaluateTeamSetViewSet(viewsets.GenericViewSet):
    data_label = "metric_evaluations"

    @action(url_path="team_set", detail=False, methods=["POST"])
    def evaluate_team_set(self, request):
        try:
            request_data: Dict[str, Dict[str, Any]] = dict(request.data)

            EvaluateTeamSetValidator(request_data).validate()

            team_set_json = request_data["team_set"]
            team_set = TeamSetSerializer().decode(team_set_json)
            metrics = request_data["metrics"]

            return_metrics: Dict[str, float] = {
                metric_name: None for metric_name in metrics.keys()
            }
            for metric_name, metric_params in metrics.items():
                metric = _get_metric(metric_name, metric_params)
                try:
                    return_metrics[metric_name] = metric.calculate(team_set)
                except ValueError:
                    # If the metric cannot be calculated, skip it
                    continue
                except Exception as e:
                    return ResponseWithMetadata(
                        error=str(e), data_label=self.data_label, status=500
                    )

            return ResponseWithMetadata(
                data=return_metrics, data_label=self.data_label, status=200
            )
        except KeyError as e:
            return ResponseWithMetadata(
                error=f"Missing key: {e}", data_label=self.data_label, status=400
            )
        except ValueError as e:
            return ResponseWithMetadata(
                error=str(e), data_label=self.data_label, status=400
            )
        except SchemaError as e:
            return ResponseWithMetadata(
                error=str(e), data_label=self.data_label, status=400
            )
        except Exception as e:
            return ResponseWithMetadata(
                error=str(e), data_label=self.data_label, status=500
            )


# TODO: After deadline, make a get metric method like in AlgorithmRunner
# (https://github.com/Teamable-Analytics/algorithms/issues/369)
def _get_metric(metric_name: str, metric_params: Dict[str, Any]) -> TeamSetMetric:
    if metric_name == "avg_cosine_difference":
        return AverageCosineDifference(**metric_params)
    elif metric_name == "avg_cosine_similarity":
        return AverageCosineDifference(**metric_params)
    elif metric_name == "avg_solo_status":
        return AverageSoloStatus(**metric_params)
    elif metric_name == "common_time_availability":
        return AverageTimeslotCoverage(**metric_params)
    elif metric_name == "project_coverage":
        return AverageProjectRequirementsCoverage()
    elif metric_name == "social_satisfaction":
        return AverageSocialSatisfaction(metric_function=is_happy_team_allhp_friend)

    # This line should never be reached since the validator should catch this
    raise ValueError(f"Unknown metric: {metric_name}")
