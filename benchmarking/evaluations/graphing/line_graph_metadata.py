from dataclasses import dataclass
from typing import Optional, List

from benchmarking.evaluations.graphing.graph_metadata import GraphData, GraphAxisRange


@dataclass
class LineGraphMetadata:
    title: str
    data: List[GraphData]
    x_label: str
    y_label: str
    description: Optional[str]
    x_lim: Optional[GraphAxisRange]
    y_lim: Optional[GraphAxisRange]
    save_path: Optional[str]
