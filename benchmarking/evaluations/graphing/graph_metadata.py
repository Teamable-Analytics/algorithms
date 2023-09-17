from dataclasses import dataclass
from typing import List


@dataclass
class GraphAxisRange:
    start: float
    end: float


@dataclass
class GraphData:
    x_data: List[float]
    y_data: List[float]
    name: str
