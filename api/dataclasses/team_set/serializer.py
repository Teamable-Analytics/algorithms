from json import JSONEncoder
from typing import Dict, Any

from api.dataclasses.interfaces import DataClassDecoder
from api.dataclasses.team import TeamSerializer
from api.dataclasses.team_set import TeamSet


class TeamSetSerializer(JSONEncoder, DataClassDecoder):
    def default(self, team_set: TeamSet) -> Dict[str, Any]:
        team_serializer = TeamSerializer()
        teams = [team_serializer.default(team) for team in team_set.teams]
        return {"id": team_set.id, "name": team_set.name, "teams": teams}

    def decode(self, json_dict: Dict[str, Any]) -> TeamSet:
        team_serializer = TeamSerializer()
        teams = [team_serializer.decode(team) for team in json_dict.get("teams", [])]
        return TeamSet(
            # TODO: After fixing no _id in teamset, add integer casting
            _id=json_dict.get("id", json_dict.get("_id")),
            name=json_dict.get("name"),
            teams=teams,
        )
