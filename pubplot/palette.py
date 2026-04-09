"""Color palettes for publication-ready scientific figures.

All palettes are colorblind-friendly.  Use ``PUBLICATION_PALETTE`` as
the default, ``OKABE_ITO`` as a fallback for accessibility-critical
contexts, and the specialised palettes for specific plot types.
"""

from __future__ import annotations

__all__ = [
    "PUBLICATION_PALETTE",
    "OKABE_ITO",
    "RIDGE_REFERENCE_COLORS",
    "CELL_COMPOSITION_PALETTE_8",
    "CELL_COMPOSITION_PALETTE_13",
    "get_cell_composition_palette",
    "build_color_map",
]

PUBLICATION_PALETTE: list[str] = [
    "#3A5BA0", "#D4753C", "#5A8F5A", "#C44E52", "#7B5EA7",
    "#E8A838", "#46878F", "#B07AA1", "#2E86C1", "#8C6D31",
    "#4E9A9A", "#D98880", "#6B8E23", "#9B59B6", "#1ABC9C",
    "#86714D", "#8EC9EB", "#6E2F84", "#F5A623", "#7BC657",
    "#708090", "#8B4513", "#C5A9D8", "#D35400", "#B8860B",
    "#E2DBA4", "#C0D0CB", "#E46571", "#90141A", "#2E5111",
    "#203161", "#40569A", "#64B024", "#BDD2CB", "#931419",
    "#C04736", "#EBA5AB", "#BEACAE", "#5C6C6B", "#F09F2E",
    "#D83746", "#DA5E28", "#DDDDDB", "#97767A", "#C24935",
]
"""Muted earthy tones — warm, distinguishable, Nature/Cell aesthetic.  Up to 45 categories."""

OKABE_ITO: list[str] = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#000000",
]
"""Okabe-Ito colorblind-safe palette.  Up to 8 categories."""

RIDGE_REFERENCE_COLORS: list[str] = [
    "#8EC9EB",  # light sky blue
    "#C5A9D8",  # soft lavender
    "#8E72A9",  # medium purple
    "#6E2F84",  # deep plum
    "#F5A623",  # orange
    "#D4C33F",  # mustard yellow
    "#86C95A",  # fresh green
    "#1C9A46",  # deep green
]
"""Reference-inspired palette for ridge plots.  Up to 8 groups."""

CELL_COMPOSITION_PALETTE_8: list[str] = [
    "#203161",  # dark navy
    "#40569A",  # mid blue
    "#64B024",  # bright green
    "#2E5111",  # deep olive green
    "#BDD2CB",  # pale sage
    "#E2DBA4",  # pale sand
    "#C04736",  # brick rust
    "#931419",  # deep crimson
]
"""Reference-inspired palette for ≤ 8 cell subtypes."""

CELL_COMPOSITION_PALETTE_13: list[str] = [
    "#5C6C6B",  # dark grey-green
    "#BDD2CB",  # pale sage
    "#DDDDDB",  # pale grey
    "#97767A",  # muted mauve-brown
    "#BEACAE",  # light taupe-mauve
    "#DA5E28",  # burnt orange
    "#F09F2E",  # warm orange
    "#EBA5AB",  # pale rose
    "#E46571",  # coral pink
    "#D83746",  # red-pink
    "#C24935",  # brick red
    "#C44E52",  # muted red
    "#90141A",  # oxblood
]
"""Reference-inspired palette for 9–13 cell subtypes."""


def get_cell_composition_palette(n_subtypes: int) -> list[str]:
    """Return the reference-inspired palette by subtype count.

    Raises ``ValueError`` if *n_subtypes* > 13.
    """
    if n_subtypes <= 8:
        return CELL_COMPOSITION_PALETTE_8[:n_subtypes]
    if n_subtypes <= 13:
        return CELL_COMPOSITION_PALETTE_13[:n_subtypes]
    raise ValueError(
        "Cell composition plot supports at most 13 subtypes. "
        "Please subset your data."
    )


def build_color_map(groups: list[str]) -> dict[str, str]:
    """Build a *group → colour* mapping using the cell-composition palettes."""
    palette = get_cell_composition_palette(len(groups))
    return {group: colour for group, colour in zip(groups, palette)}
