from dataclasses import dataclass
from typing import Optional, List

from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange


@dataclass
class LineGraphMetadata:
    title: str
    data: List[GraphData]
    x_label: str
    y_label: str
    description: Optional[str] = None
    x_lim: Optional[GraphAxisRange] = None
    y_lim: Optional[GraphAxisRange] = None
    num_minor_ticks: Optional[int] = None
    save_graph: bool = False
    file_name: Optional[str] = None
