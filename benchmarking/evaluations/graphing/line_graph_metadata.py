from dataclasses import dataclass
from typing import Optional

from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange


@dataclass
class LineGraphMetadata:
    title: str
    legend: str
    data: list[GraphData]
    description: Optional[str]
    x_label: Optional[str]
    y_label: Optional[str]
    x_lim: Optional[GraphAxisRange]
    y_lim: Optional[GraphAxisRange]
