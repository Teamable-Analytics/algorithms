from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from schema import SchemaError

from api import api
from api.ai.algorithm_runner import AlgorithmRunner
from api.api.models import APISource, APILog
from api.api.utils.generate_teams_data_loader import GenerateTeamsDataLoader
from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.api.validators.generate_teams_validator import GenerateTeamsValidator
from api.dataclasses.team_set.serializer import TeamSetSerializer


class GenerateTeamsViewSet(viewsets.GenericViewSet):
    @action(url_path="teams", detail=False, methods=["POST"])
    def generate_teams(self, request: Request):
        try:
            request_data = dict(request.data)

            # validate data schema
            GenerateTeamsValidator(request_data).validate()
            input_data = GenerateTeamsDataLoader(request_data).load()

            # Lowercase the params
            params = {k.lower(): v for k, v in request.query_params.items()}
            # Don't log if it is a sandbox call
            if not params.get("sandbox") or params.get("sandbox").lower() != "true":
                # Log API call. Do it after validation has completed.
                APILog.log(
                    endpoint="/generate/teams",
                    data={
                        "algorithm_options": request_data.get("algorithm_options"),
                        "team_generation_options": request_data.get(
                            "team_generation_options"
                        ),
                    },
                    source=(
                        APISource.INTERNAL_DEMO
                        if request.META.get("REMOTE_ADDR") in api.INTERNAL_DEMO_DOMAINS
                        else APISource.NORMAL
                    ),
                )

            runner = AlgorithmRunner(
                algorithm_type=input_data.algorithm_type,
                team_generation_options=input_data.team_generation_options,
                algorithm_options=input_data.algorithm_options,
                algorithm_config=None,
            )
            team_set = runner.generate(input_data.students)

            serialized_team_set = TeamSetSerializer().default(team_set)
            return ResponseWithMetadata(
                data=serialized_team_set, data_label="teams", status=200
            )
        except SchemaError as e:
            return ResponseWithMetadata(error=str(e), data_label="teams", status=400)
        except Exception as e:
            return ResponseWithMetadata(error=str(e), data_label="teams", status=500)
