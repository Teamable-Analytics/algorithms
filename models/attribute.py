from dataclasses import dataclass
from typing import List


@dataclass
class Attribute:
    _id: int
    possible_values: List[int] = None

    @property
    def id(self) -> int:
        return self._id
