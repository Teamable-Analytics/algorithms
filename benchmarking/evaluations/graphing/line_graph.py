import os
from os import path
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata


def make_space_above(axes, top_margin=1):
    """
    Adding space on top of the graph
    """
    fig = axes.flatten()[0].figure
    s = fig.subplotpars
    w, h = fig.get_size_inches()

    figh = h - (1 - s.top) * h + top_margin
    fig.subplots_adjust(bottom=s.bottom * h / figh, top=1 - top_margin / figh)
    fig.set_figheight(figh)


def line_graph(graph_data: LineGraphMetadata):
    # Select graph theme
    plt.style.use("bmh")

    # Data security
    if graph_data.data is None:
        raise ValueError("There is no data to graph")

    # Graphing
    fig, ax = plt.subplots(figsize=(9, 7), squeeze=False)
    legends = []
    line_styles: List[Tuple[int, Tuple[int, ...]]] = [
        (0, ()),  # solid
        (0, (5, 2)),  # dashed
        (0, (1, 1)),  # densely dotted
        (0, (5, 1, 1, 1)),  # dashdotted
        (0, (5, 1, 1, 1, 1, 1)),  # dashdotdotted
        (0, (3, 1, 3, 1, 1, 1)),  # dashdash dotted
        (0, (3, 1, 3, 1, 1, 1, 1, 1)),  # dashdash dotdotted
    ]
    markers: List[str] = ["o", "v", "s", "d", "x", "P", "*"]
    curr_data: GraphData
    for i, curr_data in enumerate(graph_data.data):
        # Get line styles from input, else use default values
        line_style = (
            curr_data.line_style
            if curr_data.line_style is not None
            else line_styles[i % len(line_styles)]
        )
        marker = (
            curr_data.marker
            if curr_data.marker is not None
            else markers[i % len(markers)]
        )
        color = curr_data.line_color

        # Plot line
        plt.errorbar(
            curr_data.x_data,
            curr_data.y_data,
            linestyle=line_style,
            marker=marker,
            color=color,
            yerr=curr_data.error_bars,
            capsize=3.0,
        )

        # Add line to legend
        legends.append(
            curr_data.name
            if curr_data.legend_subtitle is None
            else curr_data.name + "\n" + curr_data.legend_subtitle
        )

    # Graph format
    # legend = plt.legend(
    #     legends, bbox_to_anchor=(1.05, 1), loc="upper left", edgecolor="none"
    # )
    # Legend should be below xlabel and spread across the graph
    # legend = plt.legend(
    #     legends,
    #     bbox_to_anchor=(0.5, -0.15),
    #     loc="upper center",
    #     edgecolor="none",
    #     ncol=5,
    #     # Make the space between columns less
    #     columnspacing=0.5,
    # )
    # Legend should be inside the graph on top right, 1 column
    legend = plt.legend(
        legends,
        loc="upper right",
        edgecolor="none",
        ncol=1,
        # Bigger legend
        fontsize=12,
    )
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor("white")

    if graph_data.title is not None:
        plt.suptitle(graph_data.title, size=20, fontweight="bold", y=0.98)

    if graph_data.description is not None:
        plt.title(graph_data.description, size=13, y=1.05, fontweight="ultralight")

    if graph_data.x_lim is not None:
        plt.xlim([graph_data.x_lim.start, graph_data.x_lim.end])

    if graph_data.y_lim is not None:
        plt.ylim([graph_data.y_lim.start, graph_data.y_lim.end])

    if graph_data.x_label is not None:
        plt.xlabel(graph_data.x_label)

    if graph_data.y_label is not None:
        plt.ylabel(graph_data.y_label)

    if graph_data.num_minor_ticks:
        ax[0][0].xaxis.set_minor_locator(
            AutoMinorLocator(graph_data.num_minor_ticks + 1)
        )
    else:
        ax[0][0].xaxis.set_minor_locator(AutoMinorLocator())

    make_space_above(ax)

    plt.tight_layout()
    if graph_data.save_graph:
        file_save_location = path.abspath(graph_data.file_name or graph_data.title)
        if not path.exists(path.dirname(file_save_location)):
            os.makedirs(path.dirname(file_save_location))
        plt.savefig(file_save_location)
    else:
        plt.show()
    plt.close()
