from abc import ABC, abstractmethod
from typing import Any, Dict


class DataClassDecoder(ABC):
    @abstractmethod
    def decode(self, json_dict: Dict[str, Any]) -> Any:
        raise NotImplementedError
