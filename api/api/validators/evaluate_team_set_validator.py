from typing import Dict, Any

from schema import Schema, Optional, Or, SchemaError

from api.api.validators.interface import Validator
from api.models.enums import RequirementOperator, Relationship
from api.api.utils.relationship import get_relationship_str
from utils.validation import is_unique


class EvaluateTeamSetValidator(Validator):
    def validate(self):
        self._validate_schema()
        self.validate_team_set()
        self.validate_metrics()

    def _validate_schema(self):
        Schema(
            {
                "team_set": dict,
                "metrics": dict,
            }
        ).validate(self.data)

    def validate_team_set(self):
        team_set = self.data.get("team_set", {})

        if "id" in team_set and team_set["id"] is not None:
            Schema(str).validate(team_set["id"])
            # Check if team_set[id] is a number
            try:
                Schema(int).validate(int(team_set["id"]))
            except ValueError:
                raise ValueError("team_set[id] must be a number")

        if "name" in team_set and team_set["name"] is not None:
            Schema(str).validate(team_set["name"])

        Schema(list).validate(team_set["teams"])

        Schema(
            [
                {
                    "id": int,
                    Optional("name"): str,
                    Optional("project_id"): int,
                    Optional("requirements"): [
                        {
                            "attribute": int,
                            "operator": Or(*[op.value for op in RequirementOperator]),
                            "value": int,
                        }
                    ],
                    Optional("is_locked"): bool,
                    "students": [
                        {
                            "id": int,
                            "attributes": Or({str: [int]}, {}),
                            Optional("name"): str,
                            Optional("relationships"): Or(
                                {
                                    str: Or(
                                        *(
                                            [
                                                get_relationship_str(relationship)
                                                for relationship in Relationship
                                            ]
                                            + [float, int]
                                        )
                                    )
                                },
                                {},
                            ),
                            Optional("project_preferences"): [int],
                        }
                    ],
                }
            ]
        ).validate(team_set["teams"])

        # No teams should have the same id
        team_ids = [team["id"] for team in team_set["teams"]]
        if len(team_ids) != len(set(team_ids)):
            raise ValueError("team_set[teams] contains teams with the same id")

        # There should not be any duplicate students
        student_ids = [
            student["id"] for team in team_set["teams"] for student in team["students"]
        ]
        if not is_unique(student_ids):
            raise ValueError("team_set[teams] contains duplicate students")

    def validate_metrics(self):
        no_params_metrics = ["project_coverage", "social_satisfaction"]

        metrics: Dict[str, Dict[str, Any]] = self.data["metrics"]
        for metric, params in metrics.items():
            # TODO: After deadline, make a get metric method like in AlgorithmRunner
            # (https://github.com/Teamable-Analytics/algorithms/issues/369)
            if metric == "avg_cosine_difference":
                self._validate_avg_cosine_metric(params)
            elif metric == "avg_cosine_similarity":
                self._validate_avg_cosine_metric(params)
            elif metric == "avg_solo_status":
                self._validate_solo_status_metric(params)
            elif metric == "common_time_availability":
                self._validate_common_time_availability_metric(params)
            elif metric in no_params_metrics:
                continue
            else:
                raise ValueError(f"Unknown metric {metric}")

    def _validate_avg_cosine_metric(self, avg_cosine_metric_params: Dict[str, Any]):
        if len(avg_cosine_metric_params) == 0:
            return

        # If the avg_cosine_difference_metric_params is not empty, it must contain "attribute_filter"
        if "attribute_filter" not in avg_cosine_metric_params:
            raise ValueError(
                "attribute_filter is missing in avg_cosine_difference_metric_params"
            )

        attribute_filter = avg_cosine_metric_params["attribute_filter"]
        Schema([int]).validate(attribute_filter)

        # Check if numbers in attribute_filter are unique
        if len(attribute_filter) != len(set(attribute_filter)):
            raise ValueError("attribute_filter contains duplicate attributes")

        # Check if attributes exist in the team_set
        team_set = self.data["team_set"]
        all_attributes = set(
            [
                attribute
                for team in team_set["teams"]
                for student in team["students"]
                for attribute in student["attributes"]
            ]
        )

        for attribute in attribute_filter:
            if attribute not in all_attributes:
                raise ValueError(
                    f"attribute_filter contains non-existent attribute {attribute}"
                )

    def _validate_solo_status_metric(self, solo_status_metric_params: Dict[str, Any]):
        if "minority_groups_map" not in solo_status_metric_params:
            raise SchemaError(
                "minority_groups_map is missing in solo status metric params"
            )

        minority_groups_map = solo_status_metric_params["minority_groups_map"]

        if len(minority_groups_map) == 0:
            raise SchemaError("minority_groups_map is empty")

        Schema({int: [int]}).validate(minority_groups_map)

    def _validate_common_time_availability_metric(
        self, common_time_availability_metric_params: Dict[str, Any]
    ):
        if "timeslot_attribute_id" not in common_time_availability_metric_params:
            raise SchemaError(
                "timeslot_attribute_id is missing in common time availability metric params"
            )

        if "available_timeslots" not in common_time_availability_metric_params:
            raise SchemaError(
                "available_timeslots is missing in common time availability metric params"
            )

        available_timeslots = common_time_availability_metric_params[
            "available_timeslots"
        ]
        timeslot_attribute_id = common_time_availability_metric_params[
            "timeslot_attribute_id"
        ]

        Schema([int]).validate(available_timeslots)
        Schema(int).validate(timeslot_attribute_id)

        if not is_unique(available_timeslots):
            raise ValueError("available_timeslots contains duplicate timeslots")

        # all students' timeslots
        all_students_timeslots = set()
        for _team in self.data["team_set"]["teams"]:
            for _student in _team["students"]:
                if timeslot_attribute_id in _student["attributes"]:
                    raise ValueError(
                        f"timeslot_attribute_id {timeslot_attribute_id} is missing in student {_student['id']}"
                    )
                all_students_timeslots.update(
                    _student["attributes"][timeslot_attribute_id]
                )

        # Check if all students' timeslots are in available_timeslots
        if not all_students_timeslots.issubset(available_timeslots):
            raise ValueError("Not all students' timeslots are in available_timeslots")
