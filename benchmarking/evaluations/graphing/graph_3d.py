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


def graph_3d(
    surfaces: List[Surface3D],
    graph_title: str,
    x_label: str,
    y_label: str,
    z_label: str,
    plot_legend: bool = False,
    x_lim: Tuple[float, float] = None,
    y_lim: Tuple[float, float] = None,
    z_lim: Tuple[float, float] = None,
    invert_xaxis: bool = False,
    invert_yaxis: bool = False,
    invert_zaxis: bool = False,
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
    if invert_xaxis:
        ax.invert_xaxis()
    if invert_yaxis:
        ax.invert_yaxis()
    if invert_zaxis:
        ax.invert_zaxis()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    if x_lim:
        ax.set_xlim(*x_lim)
    if y_lim:
        ax.set_ylim(*y_lim)
    if z_lim:
        ax.set_zlim(*z_lim)
    if plot_legend:
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
