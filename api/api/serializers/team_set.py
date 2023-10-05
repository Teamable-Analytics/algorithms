from typing import Dict, Any

from api.models.team_set import TeamSet


class TeamSetSerializer:
    """
    This class represents a TeamSet as a JSON serialized object to be returned from the API
    """

    def __init__(self, team_set: TeamSet):
        pass

    @property
    def data(self) -> Dict[str, Any]:
        pass
