from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class GraphAxisRange:
    start: float
    end: float


@dataclass
class GraphData:
    x_data: List[float]
    y_data: List[float]
    name: str
    legend_subtitle: Optional[str] = None
    # See https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html for documentation
    line_style: Tuple[int, Tuple[int, ...]] = None
    marker: str = None
    line_color: str = None
