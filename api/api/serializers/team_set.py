from typing import Dict, Any

from api.models.team_set import TeamSet


class TeamSetSerializer:
    """
    This class represents a TeamSet as a JSON serialized object to be returned from the API
    """

    def __init__(self, team_set: TeamSet):
        self.team_set = team_set

    @property
    def data(self) -> Dict[str, Any]:
        return {
            "num_teams": self.team_set.num_teams,
            "teams": [team.todict() for team in self.team_set.teams],
        }
