from abc import ABC, abstractmethod
from typing import Any, Dict


class Validator(ABC):

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @abstractmethod
    def validate(self):
        raise NotImplementedError

    @abstractmethod
    def _validate_schema(self):
        raise NotImplementedError
