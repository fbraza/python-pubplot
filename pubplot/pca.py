"""Publication-ready PCA scatter plots with variance explained on axes.

PC1 vs PC2 coloured by a categorical variable, with optional sample
labels (adjustText) and 95 % confidence ellipses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
import pandas as pd
import ultraplot as uplt
from adjustText import adjust_text

from pubplot.palette import PUBLICATION_PALETTE

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

__all__ = ["plot_pca"]

uplt.rc.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica"],
        "font.size": 8,
        "axes.labelsize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.titlesize": 9,
    }
)


def plot_pca(
    df: pd.DataFrame,
    color_col: str,
    var_ratio: np.ndarray | list[float] | None = None,
    pc1_col: str = "PC1",
    pc2_col: str = "PC2",
    label_col: str | None = None,
    figsize: tuple[float, float] = (3.5, 3.5),
    title: str = "",
    palette: list[str] | None = None,
    point_size: float = 30,
    save_path: str | None = None,
    save_fmt: str = "png",
) -> tuple[Figure, Axes]:
    """Plot a publication-ready PCA scatter plot.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with PC coordinates and a categorical column.
    color_col : str
        Column for the categorical colouring variable.
    var_ratio : array-like of float or None
        Variance-explained ratio per PC.  First two shown on axes.
    pc1_col, pc2_col : str
        Column names for PC1 and PC2.
    label_col : str or None
        Column for point labels (adjustText prevents overlaps).
    figsize : tuple[float, float]
    title : str
    palette : list[str] or None
        Hex colour strings.  Defaults to :data:`~pubplot.palette.PUBLICATION_PALETTE`.
    point_size : float
    alpha : float
    save_path : str or None
        Base path for saving (without extension).  Saves SVG + PNG.

    Returns
    -------
    tuple[ultraplot.Figure, ultraplot.Axes]
    """
    mpl.rcParams["svg.fonttype"] = "none"

    if palette is None:
        palette = PUBLICATION_PALETTE

    categories = df[color_col].astype("category").cat.categories
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    if var_ratio is not None:
        xlabel = f"PC1 ({var_ratio[0] * 100:.1f}% variance)"
        ylabel = f"PC2 ({var_ratio[1] * 100:.1f}% variance)"
    else:
        xlabel = "PC1"
        ylabel = "PC2"

    fig, ax = uplt.subplot(figsize=figsize)

    for cat in categories:
        mask = df[color_col] == cat
        subset = df.loc[mask]
        ax.scatter(
            subset[pc1_col],
            subset[pc2_col],
            c=color_map[cat],
            s=point_size,
            alpha=1.0,
            label=str(cat),
            edgecolors="black",
            linewidths=0.3,
            zorder=3,
        )

    if label_col is not None:
        texts = [
            ax.text(
                row[pc1_col],
                row[pc2_col],
                str(row[label_col]),
                fontsize=6,
                ha="center",
                va="center",
            )
            for _, row in df.iterrows()
        ]
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.5))

    ax.format(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.legend(loc="best", ncols=1, fontsize=7, frameon=True, framealpha=0.8)

    if save_path is not None:
        fig.savefig(f"{save_path}.{save_fmt}", dpi=300, bbox_inches="tight")

    return fig, ax
