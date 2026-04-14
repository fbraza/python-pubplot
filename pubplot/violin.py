"""Publication-ready violin plots with optional jitter dots.

≤ 8 groups → one colour per group, legend shown, x-axis labels hidden.
> 8 groups → uniform fill colour, no legend, group labels on the x-axis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import ultraplot as uplt
from matplotlib.ticker import MaxNLocator, NullLocator

from pubplot.palette import PUBLICATION_PALETTE

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

__all__ = ["plot_violinplot"]

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


def plot_violinplot(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    figsize: tuple[float, float] = (3.5, 3),
    title: str = "",
    ylabel: str = "",
    palette: list[str] | None = None,
    show_points: bool = True,
    point_size: float = 0.5,
    alpha: float = 1.0,
    jitter_width: float = 0.15,
    orient: str = "v",
    groups_to_plot: list[str] | None = None,
    order: list[str] | None = None,
    uniform_color: str | None = None,
    point_color: str = "black",
    legend_loc: str = "upper left",
    legend_bbox_to_anchor: tuple[float, float] | None = None,
    save_path: str | None = None,
    save_fmt: str = "png",
) -> tuple[Figure, Axes]:
    """Plot a publication-ready violin plot with optional jitter dots.

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format DataFrame containing the data.
    group_col : str
        Column name for the categorical grouping variable.
    value_col : str
        Column name for the numeric measurement.
    figsize : tuple[float, float]
        Figure dimensions in inches.  Default ``(3.5, 3)``.
    title : str
        Plot title.
    ylabel : str
        Y-axis label (or x-axis label when ``orient='h'``).
    palette : list[str] or None
        List of hex colour strings.  If *None*, uses
        :data:`~pubplot.palette.PUBLICATION_PALETTE`.
    show_points : bool
        Whether to overlay jittered individual data points.
    point_size : float
        Size of individual data points.
    alpha : float
        Transparency for data points.
    jitter_width : float
        Horizontal spread of jittered points.
    orient : ``'v'`` | ``'h'``
        Vertical or horizontal orientation.
    groups_to_plot : list[str] or None
        Subset of groups to include, in this order (unless *order*
        overrides it).
    order : list[str] or None
        Custom ordering of groups along the categorical axis.
    uniform_color : str or None
        Fill colour used when plotting more than 8 groups.
    point_color : str
        Colour of jittered data points.
    legend_loc : str
        Legend location for ≤ 8 groups.
    legend_bbox_to_anchor : tuple[float, float] | None
        Optional legend anchor.
    save_path : str or None
        Base path for saving (without extension).
    save_fmt : ``'png'`` | ``'svg'`` | ``'both'``
        Output format.  Default ``'png'``.

    Returns
    -------
    tuple[ultraplot.Figure, ultraplot.Axes]
    """
    if palette is None:
        palette = PUBLICATION_PALETTE

    available_groups = df[group_col].dropna().unique().tolist()
    if groups_to_plot is not None:
        groups = [g for g in groups_to_plot if g in available_groups]
    else:
        groups = available_groups

    if order is not None:
        groups = [g for g in order if g in groups]

    if len(groups) == 0:
        raise ValueError(
            "No valid groups available to plot. Check `groups_to_plot` / `order`."
        )

    df = df.loc[df[group_col].isin(groups)].copy()
    df[group_col] = pd.Categorical(df[group_col], categories=groups, ordered=True)

    n_groups = len(groups)
    use_group_legend = n_groups <= 8

    if use_group_legend:
        colors = [palette[i % len(palette)] for i in range(n_groups)]
    else:
        uniform_color = uniform_color or PUBLICATION_PALETTE[0]
        colors = [uniform_color] * n_groups

    group_data = [df.loc[df[group_col] == g, value_col].dropna().values for g in groups]
    positions = np.arange(n_groups)

    fig, ax = uplt.subplot(figsize=figsize)

    vert = orient == "v"
    bodies = ax.violinplot(
        group_data,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        vert=vert,
    )

    for i, body in enumerate(bodies):
        body.set_facecolor(colors[i])
        body.set_edgecolor("black")
        body.set_linewidth(0.5)
        body.set_alpha(0.9)

    if show_points:
        rng = np.random.default_rng(42)
        for i, data in enumerate(group_data):
            jitter = rng.uniform(-jitter_width, jitter_width, size=len(data))
            if vert:
                ax.scatter(
                    positions[i] + jitter,
                    data,
                    s=point_size,
                    c=point_color,
                    alpha=alpha,
                    edgecolors="none",
                    linewidths=0,
                    zorder=6,
                )
            else:
                ax.scatter(
                    data,
                    positions[i] + jitter,
                    s=point_size,
                    c=point_color,
                    alpha=alpha,
                    edgecolors="none",
                    linewidths=0,
                    zorder=6,
                )

    if vert:
        ax.set_xticks(positions)
        if use_group_legend:
            ax.set_xticklabels([""] * n_groups)
        else:
            ax.set_xticklabels(groups, rotation=45, ha="right")
        ax.format(
            ylabel=ylabel,
            title=title,
            xlabelsize=9,
            ylabelsize=9,
            xticklabelsize=8,
            yticklabelsize=8,
            titlesize=9,
            titleweight="bold",
        )
    else:
        ax.set_yticks(positions)
        if use_group_legend:
            ax.set_yticklabels([""] * n_groups)
        else:
            ax.set_yticklabels(groups)
        ax.format(
            xlabel=ylabel,
            title=title,
            xlabelsize=9,
            ylabelsize=9,
            xticklabelsize=8,
            yticklabelsize=8,
            titlesize=9,
            titleweight="bold",
        )

    ax.grid(False)
    for side in ("left", "right", "top", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_linewidth(0.9)
        ax.spines[side].set_color("black")
    ax.tick_params(direction="out", width=0.8, length=3, color="black")

    if vert:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_minor_locator(NullLocator())
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_locator(NullLocator())

    if use_group_legend:
        if vert:
            ax.tick_params(axis="x", length=0)
        else:
            ax.tick_params(axis="y", length=0)

    if use_group_legend:
        if legend_bbox_to_anchor is None:
            legend_bbox_to_anchor = (1.02, 1.0)
        handles = [
            mpatches.Patch(facecolor=color, edgecolor="black", label=group, alpha=0.9)
            for group, color in zip(groups, colors)
        ]
        ax.legend(
            handles=handles,
            loc=legend_loc,
            bbox_to_anchor=legend_bbox_to_anchor,
            ncol=1,
            frameon=False,
            fontsize=8,
            handlelength=1.0,
            handletextpad=0.5,
            columnspacing=0.8,
        )

    if save_path is None:
        save_path = "./results/violinplot"
    if save_fmt in ("png", "both"):
        fig.savefig(f"{save_path}.png", dpi=300, bbox_inches="tight")
    if save_fmt in ("svg", "both"):
        fig.savefig(f"{save_path}.svg", dpi=300, bbox_inches="tight")

    return fig, ax
