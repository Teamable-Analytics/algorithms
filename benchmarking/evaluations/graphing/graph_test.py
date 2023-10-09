from itertools import product
from typing import Dict, List

from matplotlib.lines import Line2D

from api.models.enums import AlgorithmType
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata

if __name__ == "__main__":
    graph1_dict: Dict[AlgorithmType, GraphData] = {
        AlgorithmType.RANDOM: GraphData(
            x_data=[1, 2, 3, 4, 5],
            y_data=[1, 3, 5, 7, 9],  # Adjusted y_data values
            name="Random",
        ),
        AlgorithmType.WEIGHT: GraphData(
            x_data=[1, 2, 3, 4, 5],
            y_data=[2, 4, 6, 8, 10],  # Adjusted y_data values
            name="Weight",
        ),
        AlgorithmType.PRIORITY_NEW: GraphData(
            x_data=[1, 2, 3, 4, 5],
            y_data=[3, 5, 7, 9, 11],  # Adjusted y_data values
            name="Priority New",
        ),
        AlgorithmType.SOCIAL: GraphData(
            x_data=[1, 2, 3, 4, 5],
            y_data=[4, 6, 8, 10, 12],  # Adjusted y_data values
            name="Social",
        ),
    }

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Run time (seconds)",
            title="Concentrate GPA Runtimes",
            data=list(graph1_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )

    line_styles: List[str] = [s for s in Line2D.lineStyles.keys() if s != "None"]
    markers: List[str] = Line2D.markers

    print(line_styles)
    print(markers)
