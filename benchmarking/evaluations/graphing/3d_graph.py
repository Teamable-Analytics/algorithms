from dataclasses import dataclass
import os
from os import path
from typing import List, Dict, Tuple

import numpy as np
from matplotlib import pyplot as plt


@dataclass
class Surface3D:
    points: List[Tuple[float, float, float]]
    label: str
    color: str = "blue"


def make_3d_graph(
    surfaces: List[Surface3D],
    graph_title: str,
    save_graph: bool = False,
    filename: str = None,
):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    for surface in surfaces:
        # Format data
        points = np.array(surface.points)
        x = points[:, 0]
        y = points[:, 1]
        unique_x = np.unique(x)
        unique_y = np.unique(y)
        X, Y = np.meshgrid(unique_x, unique_y)
        Z = np.zeros_like(X)
        for xi, yi, zi in points:
            Z[
                np.where(unique_y == yi)[0][0],
                np.where(unique_x == xi)[0][0],
            ] = zi

        # Plot the surface
        ax.plot_wireframe(
            X,
            Y,
            Z,
            color=surface.color,
            label=surface.label,
        )

    ax.set_title(graph_title)
    ax.set_xlabel("MAX_KEEP")
    ax.invert_xaxis()
    ax.set_ylabel("MAX_SPREAD")
    ax.set_zlabel("Score")
    ax.set_zlim(0, 1)
    plt.legend(
        loc="lower left",
        bbox_to_anchor=(1.2, 0.8),
        borderaxespad=0,
    )
    plt.subplots_adjust(right=0.64)

    if save_graph:
        file_save_location = path.abspath(filename or graph_title)
        if not path.exists(path.dirname(file_save_location)):
            os.makedirs(path.dirname(file_save_location))
        plt.savefig(file_save_location)
        plt.close()
    else:
        plt.show()
