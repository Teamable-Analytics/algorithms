from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata

if __name__ == '__main__':
    datas = [
        GraphData(
            x_data=list(range(1, 5)),
            y_data=[x**i for x in range(1, 5)],
            name=f"x^{i}",
            error_bars=[5]*4,
        )
        for i in range(1, 4)
    ]

    line_graph(
        LineGraphMetadata(
            title='Test Graph',
            x_label='x',
            y_label='y',
            data=datas,
        )
    )
