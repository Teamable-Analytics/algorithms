from rest_framework import viewsets
from rest_framework.decorators import action

from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.api.validators.evaluate_team_set_validator import EvaluateTeamSetValidator


class EvaluateTeamSetViewSet(viewsets.GenericViewSet):
    @action(url_path="teams", detail=False, methods=["POST"])
    def evaluate_team_set(self, request):
        try:
            request_data = dict(request.data)

            EvaluateTeamSetValidator(request_data).validate()


            return ResponseWithMetadata(data=request_data, status=200)
        except Exception as e:
            return ResponseWithMetadata(error=str(e), status=500)