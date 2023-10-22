from json import JSONEncoder, JSONDecoder

from api.models.team import Team


class TeamSerializer(JSONEncoder, JSONDecoder):
    def default(self, team: Team):
        return None

