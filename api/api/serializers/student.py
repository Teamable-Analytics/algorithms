from typing import Dict, Any

from models.student import Student


class StudentSerializer:
    """
    This class represents a Student as a JSON serialized object to be returned from the API
    """

    def __init__(self, student: Student):
        pass

    @property
    def data(self) -> Dict[str, Any]:
        pass
