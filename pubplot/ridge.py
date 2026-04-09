"""Publication-ready ridge plots.

Stacked kernel-density curves for comparing one continuous feature
(gene expression, score, QC metric) across multiple groups.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator, NullLocator
from scipy.stats import gaussian_kde

from pubplot.palette import RIDGE_REFERENCE_COLORS

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

__all__ = ["plot_ridge"]

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


def _feature_fontsize(feature_name: str) -> float:
    n = len(feature_name)
    if n <= 8:
        return 18
    if n <= 14:
        return 15
    if n <= 22:
        return 12
    return 10


def _major_tick_step(xlim: tuple[float, float]) -> float:
    span = xlim[1] - xlim[0]
    if span <= 4:
        return 1
    if span <= 8:
        return 2
    if span <= 20:
        return 5
    return 10


def plot_ridge(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    feature_name: str,
    groups_to_plot: list[str] | None = None,
    colors: list[str] | None = None,
    figsize: tuple[float, float] = (4.2, 4.8),
    xlim: tuple[float, float] | None = None,
    bw_method: float | str = 0.25,
    fill_alpha: float = 1.0,
    baseline_lw: float = 1.8,
    frame_lw: float = 2.0,
    feature_loc: tuple[float, float] = (0.5, 1.02),
    group_label_fontsize: float = 15,
    save_path: str | Path | None = None,
    save_fmt: str = "png",
) -> tuple[Figure, Axes]:
    """Plot a publication-style ridge plot.

    Stacked kernel-density curves on separate baselines, group labels
    inside the panel, feature name centred above the frame.

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format table.
    group_col : str
        Column for the grouping variable.
    value_col : str
        Column for the continuous feature.
    feature_name : str
        Name displayed above the plot.
    groups_to_plot : list[str] or None
        Groups to include and their order.  All groups if *None*.
    colors : list[str] or None
        Fill / baseline colours.  Defaults to
        :data:`~pubplot.palette.RIDGE_REFERENCE_COLORS`.
    figsize : tuple[float, float]
    xlim : tuple[float, float] or None
        X-axis limits.  Auto-computed if *None*.
    bw_method : float or str
        KDE bandwidth.  Default ``0.25``.
    fill_alpha : float
    baseline_lw : float
    frame_lw : float
    feature_loc : tuple[float, float]
        Feature label position in axes coords.
    group_label_fontsize : float
    save_path : str, pathlib.Path, or None
        Base path for saving (without extension).  Saves SVG + PNG.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
    """
    groups = groups_to_plot or df[group_col].dropna().unique().tolist()
    data_by_group = [
        df.loc[df[group_col] == g, value_col].dropna().to_numpy() for g in groups
    ]

    keep = [(g, arr) for g, arr in zip(groups, data_by_group) if len(arr) > 1]
    if not keep:
        raise ValueError("No groups with enough values to draw densities.")
    groups, data_by_group = zip(*keep)  # type: ignore[assignment]
    groups = list(groups)
    data_by_group = list(data_by_group)

    if colors is None:
        colors = RIDGE_REFERENCE_COLORS[: len(groups)]
    if len(colors) < len(groups):
        colors = [colors[i % len(colors)] for i in range(len(groups))]

    all_values = np.concatenate(data_by_group)
    if xlim is None:
        x_min = min(0, float(np.floor(all_values.min() * 10) / 10))
        x_max = float(np.ceil(all_values.max() * 10) / 10)
        xlim = (x_min, x_max)

    x_grid = np.linspace(xlim[0], xlim[1], 400)
    y_positions = np.arange(len(groups))[::-1]
    rng = np.random.default_rng(42)

    fig, ax = plt.subplots(figsize=figsize)

    max_height = 0.0
    for y0, group, values, color in zip(y_positions, groups, data_by_group, colors):
        if np.std(values) < 1e-10:
            values = values + rng.normal(0, 1e-6, size=len(values))
        kde = gaussian_kde(values, bw_method=bw_method)
        density = kde(x_grid)
        density = density / density.max() * 0.82
        max_height = max(max_height, density.max())

        ax.fill_between(
            x_grid, y0, y0 + density, color=color, alpha=fill_alpha, linewidth=0
        )
        ax.plot(x_grid, y0 + density, color=color, linewidth=1.4)
        ax.hlines(y0, xlim[0], xlim[1], color=color, linewidth=baseline_lw)

        ax.text(
            xlim[1] - 0.01 * (xlim[1] - xlim[0]),
            y0 + density.max() * 0.38,
            group,
            ha="right",
            va="center",
            fontsize=group_label_fontsize,
            color="#1F1B20",
        )

    ax.text(
        feature_loc[0],
        feature_loc[1],
        feature_name,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=_feature_fontsize(feature_name),
        fontweight="bold",
        clip_on=False,
    )

    ax.set_xlim(xlim)
    ax.set_ylim(-0.05, y_positions.max() + max_height + 0.12)
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.set_xlabel("")

    ax.xaxis.set_major_locator(MultipleLocator(_major_tick_step(xlim)))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.tick_params(axis="x", width=1.6, length=10, labelsize=28, pad=12)
    ax.tick_params(axis="y", length=0)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(frame_lw)
        spine.set_color("black")

    ax.grid(False)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    fig.tight_layout(pad=0.6)

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if save_fmt in ("png", "both"):
            fig.savefig(save_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
        if save_fmt in ("svg", "both"):
            fig.savefig(save_path.with_suffix(".svg"), dpi=300, bbox_inches="tight")

    return fig, ax
