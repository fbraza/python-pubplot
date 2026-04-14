"""Publication-ready dimensionality-reduction scatter plots.

UMAP, tSNE, PHATE, and similar 2-D embeddings coloured by cluster /
cell type (categorical) or gene expression (continuous / feature plot).

Aesthetic principles (from the reference figures):

* Minimal L-shaped axis stubs — no full frame, no ticks, no tick numbers.
* Point size auto-scales with cell count.
* Fully opaque points (alpha=1.0) with darkened edge contours.
* Legend only — no text labels on the plot.
* Feature plots use magma with Min/Max colourbar labels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.colors as mcolors
import pandas as pd
import ultraplot as uplt

from pubplot.palette import PUBLICATION_PALETTE

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

__all__ = [
    "plot_embedding_categorical",
    "plot_embedding_continuous",
]

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


def _auto_point_size(n_cells: int) -> float:
    if n_cells > 50_000:
        return 0.20
    if n_cells > 20_000:
        return 0.5
    if n_cells > 10_000:
        return 1.0
    if n_cells > 5_000:
        return 2.0
    if n_cells > 2_000:
        return 4.0
    if n_cells > 500:
        return 16.0
    return 32


def _darken_color(hex_color: str, factor: float = 0.6) -> str:
    rgb = mcolors.to_rgb(hex_color)
    return mcolors.to_hex(tuple(c * factor for c in rgb))  # type: ignore


def _draw_axis_stubs(
    ax: Axes,
    embedding_type: str = "UMAP",
    stub_length_frac: float = 0.12,
) -> None:
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]

    pad_x = 0.03 * x_range
    pad_y = 0.03 * y_range
    origin_x = xlim[0] + pad_x
    origin_y = ylim[0] + pad_y
    stub_x = stub_length_frac * x_range
    stub_y = stub_length_frac * y_range

    ax.annotate(
        "",
        xy=(origin_x + stub_x, origin_y),
        xytext=(origin_x, origin_y),
        arrowprops=dict(arrowstyle="-", color="black", lw=1.2),
        annotation_clip=False,
    )
    ax.annotate(
        "",
        xy=(origin_x, origin_y + stub_y),
        xytext=(origin_x, origin_y),
        arrowprops=dict(arrowstyle="-", color="black", lw=1.2),
        annotation_clip=False,
    )

    ax.text(
        origin_x + stub_x / 2,
        origin_y - 0.03 * y_range,
        f"{embedding_type} 1",
        ha="center",
        va="top",
        fontsize=8,
    )
    ax.text(
        origin_x - 0.03 * x_range,
        origin_y + stub_y / 2,
        f"{embedding_type} 2",
        ha="right",
        va="center",
        fontsize=8,
        rotation=90,
    )


def plot_embedding_categorical(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    embedding_type: str = "UMAP",
    figsize: tuple[float, float] = (4, 3.5),
    title: str = "",
    palette: list[str] | None = None,
    point_size: float | None = None,
    show_legend: bool = True,
    save_path: str | None = None,
    save_fmt: str = "png",
) -> tuple[Figure, Axes]:
    """Plot a categorical-coloured embedding (UMAP, tSNE, PHATE, …).

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with embedding coordinates and a categorical column.
    x_col, y_col : str
        Coordinate columns (e.g. ``"UMAP1"``, ``"UMAP2"``).
    color_col : str
        Categorical column for colouring.
    embedding_type : str
        Label prefix for axis stubs (``"UMAP"``, ``"tSNE"``, …).
    figsize : tuple[float, float]
    title : str
    palette : list[str] or None
        Defaults to :data:`~pubplot.palette.PUBLICATION_PALETTE`.
    point_size : float or None
        Auto-computed from cell count if *None*.
    show_legend : bool
    save_path : str or None
        Base path for saving (without extension).
    save_fmt : ``'png'`` | ``'svg'``
        Output format.  Default ``'png'``.

    Returns
    -------
    tuple[ultraplot.Figure, ultraplot.Axes]
    """
    mpl.rcParams["svg.fonttype"] = "none"

    if palette is None:
        palette = PUBLICATION_PALETTE

    n_cells = len(df)
    if point_size is None:
        point_size = _auto_point_size(n_cells)

    categories = df[color_col].astype("category").cat.categories
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    fig, ax = uplt.subplot(figsize=figsize)

    df_shuffled = df.sample(frac=1, random_state=42)

    for cat in categories:
        mask = df_shuffled[color_col] == cat
        if not mask.any():
            continue
        fill_color = color_map[cat]
        edge_color = _darken_color(fill_color, 0.4)
        ax.scatter(
            df_shuffled.loc[mask, x_col],
            df_shuffled.loc[mask, y_col],
            c=fill_color,
            s=point_size,
            alpha=1.0,
            edgecolors=edge_color,
            linewidths=0.4 if point_size >= 15 else 0.2,
            label=str(cat),
            zorder=2,
            rasterized=True,
        )

    ax.format(title=title, titlesize=9, titleweight="bold")
    _draw_axis_stubs(ax, embedding_type=embedding_type)

    if show_legend:
        ax.legend(
            loc="right",
            ncols=1,
            fontsize=6,
            markersize=5,
            frameon=False,
            handletextpad=0.4,
            columnspacing=1.0,
        )

    if save_path is not None:
        fig.savefig(f"{save_path}.{save_fmt}", dpi=300, bbox_inches="tight")

    return fig, ax


def plot_embedding_continuous(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    value_col: str,
    embedding_type: str = "UMAP",
    figsize: tuple[float, float] = (3.5, 3.5),
    title: str = "",
    cmap: str = "magma",
    point_size: float | None = None,
    cbar_label: str = "norm. Expression",
    save_path: str | None = None,
    save_fmt: str = "png",
) -> tuple[Figure, Axes]:
    """Plot a continuous-coloured embedding (feature / gene-expression plot).

    Points sorted so high values plot on top.  Gene name shown in
    *italics* as the title.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with embedding coordinates and a continuous column.
    x_col, y_col : str
        Coordinate columns.
    value_col : str
        Continuous column for colouring.
    embedding_type : str
    figsize : tuple[float, float]
    title : str
        If empty, uses *value_col* in italics.
    cmap : str
        Default ``"magma"``.
    point_size : float or None
        Auto-computed if *None*.
    cbar_label : str
    save_path : str or None
        Base path for saving (without extension).  Saves SVG + PNG.

    Returns
    -------
    tuple[ultraplot.Figure, ultraplot.Axes]
    """
    mpl.rcParams["svg.fonttype"] = "none"

    n_cells = len(df)
    if point_size is None:
        point_size = _auto_point_size(n_cells)

    df_sorted = df.sort_values(value_col, ascending=True)

    fig, ax = uplt.subplot(figsize=figsize)

    scatter = ax.scatter(
        df_sorted[x_col],
        df_sorted[y_col],
        c=df_sorted[value_col],
        cmap=cmap,
        s=point_size,
        alpha=1.0,
        edgecolors="none",
        rasterized=True,
        zorder=2,
    )

    display_title = title if title else f"$\\it{{{value_col}}}$"
    ax.format(title=display_title, titlesize=9, titleweight="normal")

    _draw_axis_stubs(ax, embedding_type=embedding_type)

    cbar = fig.colorbar(scatter, loc="top", width=0.08, length=0.5)
    cbar.set_label(cbar_label, fontsize=7)
    cbar.set_ticks([df_sorted[value_col].min(), df_sorted[value_col].max()])  # type: ignore
    cbar.set_ticklabels(["Min", "Max"])
    cbar.ax.tick_params(labelsize=7)

    if save_path is not None:
        fig.savefig(f"{save_path}.{save_fmt}", dpi=300, bbox_inches="tight")

    return fig, ax
