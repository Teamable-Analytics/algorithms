from json import JSONEncoder
from typing import Dict, Any

from api.models.interfaces import ModelDecoder
from api.models.team import TeamSerializer
from api.models.team_set import TeamSet


class TeamSetSerializer(JSONEncoder, ModelDecoder):
    def default(self, team_set: TeamSet) -> Dict[str, Any]:
        team_serializer = TeamSerializer()
        teams = [team_serializer.default(team) for team in team_set.teams]
        return {"_id": team_set._id, "name": team_set.name, "teams": teams}

    def decode(self, json_dict: Dict[str, Any]) -> TeamSet:
        team_serializer = TeamSerializer()
        teams = [team_serializer.decode(team) for team in json_dict["teams"]]
        return TeamSet(_id=json_dict["_id"], name=json_dict["name"], teams=teams)
