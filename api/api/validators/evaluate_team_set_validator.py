from schema import Schema, Optional, Or

from api.api.validators.interface import Validator
from api.models.enums import RequirementOperator, Relationship
from utils.relationship import get_relationship_str


class EvaluateTeamSetValidator(Validator):
    def validate(self):
        self._validate_schema()
        self.validate_team_set()
        self.validate_metrics()

    def _validate_schema(self):
        Schema(
            {
                "team_set": dict,
                "metrics": [dict],
            }
        ).validate(self.data)

    def validate_team_set(self):
        team_set = self.data["team_set"]

        if "id" in team_set:
            Schema(str).validate(team_set["id"])
            # Check if team_set[id] is a number
            try:
                Schema(int).validate(int(team_set["id"]))
            except ValueError:
                raise ValueError("team_set[id] must be a number")

            Schema(str).validate(team_set["name"])

        Schema(Optional(str)).validate(team_set["name"])

        Schema(list).validate(team_set["teams"])

        Schema([{
            "id": int,
            Optional("name"): str,
            Optional("project_id"): int,
            Optional("requirements"): [
                {
                    "attribute": int,
                    "operator": Or(
                        *[op.value for op in RequirementOperator]
                    ),
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
                                *[
                                    get_relationship_str(relationship)
                                    for relationship in Relationship
                                ]
                            )
                        },
                        {},
                    ),
                    Optional("project_preferences"): [int],
                }
            ],
        }]).validate(team_set["teams"])

        # No teams should have the same id
        team_ids = [team.id for team in team_set["teams"]]
        if len(team_ids) != len(set(team_ids)):
            raise ValueError("team_set[teams] contains teams with the same id")

        # There should not be any duplicate students
        student_ids = [student.id for team in team_set["teams"] for student in team.students]
        if len(student_ids) != len(set(student_ids)):
            raise ValueError("team_set[teams] contains duplicate students")

    def validate_metrics(self):
        # TODO: Validate 5 metrics that in the paper after merging solo status and update for cosine differences
        pass
