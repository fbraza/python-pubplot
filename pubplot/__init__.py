"""pypubplot — Publication-ready scientific figures.

Colour palettes, plot functions, and export conventions for biology and
medicine.
"""

from __future__ import annotations

from pubplot.palette import (
    CELL_COMPOSITION_PALETTE_13,
    CELL_COMPOSITION_PALETTE_8,
    OKABE_ITO,
    PUBLICATION_PALETTE,
    RIDGE_REFERENCE_COLORS,
    build_color_map,
    get_cell_composition_palette,
)
from pubplot.pca import plot_pca
from pubplot.ridge import plot_ridge
from pubplot.stacked_bar import plot_cell_composition
from pubplot.umap import plot_embedding_categorical, plot_embedding_continuous
from pubplot.violin import plot_violinplot

__all__ = [
    # Palettes
    "PUBLICATION_PALETTE",
    "OKABE_ITO",
    "RIDGE_REFERENCE_COLORS",
    "CELL_COMPOSITION_PALETTE_8",
    "CELL_COMPOSITION_PALETTE_13",
    "get_cell_composition_palette",
    "build_color_map",
    # Plots
    "plot_ridge",
    "plot_cell_composition",
    "plot_violinplot",
    "plot_pca",
    "plot_embedding_categorical",
    "plot_embedding_continuous",
]
