from dataclasses import dataclass


@dataclass
class GraphAxisRange:
    start: float
    end: float


@dataclass
class GraphData:
    x_data: list[float]
    y_data: list[float]
    legend: str
