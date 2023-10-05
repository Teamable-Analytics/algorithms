from typing import Dict, Any

from api.models.team import Team


class TeamSerializer:
    """
    This class represents a Team as a JSON serialized object to be returned from the API
    """

    def __init__(self, team: Team):
        pass

    @property
    def data(self) -> Dict[str, Any]:
        pass
