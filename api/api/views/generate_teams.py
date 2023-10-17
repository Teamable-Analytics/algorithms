from rest_framework import viewsets
from rest_framework.decorators import action

from api.api.serializers.team_set import TeamSetSerializer
from api.api.utils.generate_teams import generate_teams
from api.api.utils.generate_teams_data_loader import GenerateTeamsDataLoader
from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.api.validators.generate_teams_validator import GenerateTeamsValidator


class GenerateTeamsViewSet(viewsets.GenericViewSet):
    pass

    @action(url_path="teams", detail=False, methods=["POST"])
    def generate_teams(self, request):
        """
        Steps to do this:
        0. Permissions/access/api keys/etc
        1. Read JSON
            1.1. Parse to dict
            1.2. Throw error if invalid JSON
                1.2.1 API layer validation (i.e. cannot say you're using priority_algorithm and pass the options for the weight algorithm)
        2. Encode data from JSON to the correct Dataclasses (hopefully can import?)
            2.1. Validate dataclasses (so logical validation of values)
        3. Feed dataclasses to algorithm
            3.1. Determine which algorithm to use
        4. Run algorithm
        5. Serialize algorithm's output (TeamSet) to JSON
        6. Return JSON to a happy user :) 🚀!

        """
        request_data = dict(request.data)

        # validate data schema
        GenerateTeamsValidator(request_data).validate()
        input_data = GenerateTeamsDataLoader(request_data).load()
        team_set = generate_teams(input_data)

        serialized_team_set = TeamSetSerializer(team_set).data

        return ResponseWithMetadata(
            data_label="teams", data=serialized_team_set, status=200
        )
