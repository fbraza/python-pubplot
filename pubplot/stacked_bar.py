"""Horizontal stacked-bar plots for cell-type composition.

Each row is a sample and each coloured segment is the proportion of a
cell subtype.  Supports up to 13 subtypes with dedicated palettes.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from pubplot.palette import build_color_map

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

__all__ = ["plot_cell_composition"]

mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
    }
)


def plot_cell_composition(
    composition_df: pd.DataFrame,
    color_map: dict[str, str] | None = None,
    figsize: tuple[float, float] = (4.3, 3.0),
    title_top: str = "Patient-Specific",
    title_bottom: str = "Cell Subtypes",
    xlabel: str = "Proportion [%]",
    bar_height: float = 0.94,
    legend_title: str | None = None,
    save_path: str | Path | None = None,
    save_fmt: str = "png",  # 'png' or 'svg'
) -> tuple[Figure, Axes]:
    """Plot publication-style cell-composition bars.

    Horizontal stacked bars, legend on the right, only the bottom
    x-axis line visible.

    Parameters
    ----------
    composition_df : pandas.DataFrame
        Rows are samples; columns are subtype percentages (summing to
        100).
    color_map : dict[str, str] or None
        Mapping from subtype to colour.  If *None*, uses the automatic
        palette (see :func:`~pubplot.palette.get_cell_composition_palette`).
    figsize : tuple[float, float]
    title_top : str
        First (normal-weight) title line.
    title_bottom : str
        Second (bold) title line.
    xlabel : str
    bar_height : float
        Height of each horizontal stacked bar.
    legend_title : str or None
    save_path : str, pathlib.Path, or None
        Base path for saving (without extension).  Saves SVG + PNG.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
    """
    groups = list(composition_df.columns)
    if color_map is None:
        color_map = build_color_map(groups)
    colors = [color_map[g] for g in groups]
    samples = list(composition_df.index)

    fig, ax = plt.subplots(figsize=figsize)

    y = np.arange(len(samples))
    left = np.zeros(len(samples))

    for group, color in zip(groups, colors):
        vals = composition_df[group].to_numpy()
        ax.barh(
            y,
            vals,
            left=left,
            height=bar_height,
            color=color,
            edgecolor="black",
            linewidth=0.7,
            label=group,
        )
        left += vals

    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel(xlabel, fontsize=8, labelpad=2)
    ax.invert_yaxis()

    for yi, sample in zip(y, samples):
        ax.text(
            -0.01,
            yi,  # type: ignore
            sample,
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="center",
            fontsize=8,
        )

    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.spines["bottom"].set_color("black")
    ax.tick_params(axis="x", length=3, width=0.8, pad=1, labelsize=7)
    ax.grid(False)

    ax.text(
        0.5,
        1.14,
        title_top,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="normal",
    )
    ax.text(
        0.5,
        1.05,
        title_bottom,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

    handles = [
        Patch(facecolor=color_map[g], edgecolor="black", linewidth=0.6, label=g)
        for g in groups
    ]
    ax.legend(
        handles=handles,
        title=legend_title,
        frameon=False,
        fontsize=8,
        title_fontsize=8,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        handlelength=0.9,
        handleheight=0.9,
        handletextpad=0.3,
        borderaxespad=0.0,
        labelspacing=0.25,
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout(pad=0.6)

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path.with_suffix(f".{save_fmt}"), dpi=300, bbox_inches="tight")

    return fig, ax
