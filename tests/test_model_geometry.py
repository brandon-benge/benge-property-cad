"""Geometry and semantic-metadata contract tests for issue #6 changes.

Covers:
- 3' tile border ring around the pool (no longer a slab covering the pool)
- hot tub deck (lower deck) is 17.5' across
- top (upper) deck extends 20' from the house toward the pool
- stair risers line up with the back of each step (sit on the tread top)

``bounds_mm`` is ``[min_x, min_y, min_z, max_x, max_y, max_z]``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from python_cad_tools.units import FOOT, to_mm


def _element_by_id(manifest: dict, element_id: str) -> dict:
    for element in manifest["elements"]:
        if element["id"] == element_id:
            return element
    raise AssertionError(f"Element not found in design manifest: {element_id}")


def _bounds(manifest: dict, element_id: str) -> tuple[float, float, float, float, float, float]:
    element = _element_by_id(manifest, element_id)
    bounds = element["bounds_mm"]
    assert len(bounds) == 6, f"Unexpected bounds for {element_id}: {bounds}"
    return tuple(float(v) for v in bounds)  # type: ignore[return-value]


def _load_config(copied_project: Path):
    import sys

    sys.path.insert(0, str(copied_project))
    for mod in list(sys.modules):
        if mod in ("config", "model", "drawing_annotations"):
            del sys.modules[mod]
    try:
        import config as cfg

        return cfg
    finally:
        sys.path.remove(str(copied_project))


# ── Pool tile border ring ────────────────────────────────────────────────────


TILE_BORDER_IDS = {
    "complex.site.pool_tile_border_left",
    "complex.site.pool_tile_border_right",
    "complex.site.pool_tile_border_near",
    "complex.site.pool_tile_border_far",
}


def test_pool_paver_patio_removed(design_manifest: dict) -> None:
    ids = {e["id"] for e in design_manifest["elements"]}
    assert "complex.site.pool_paver_patio" not in ids
    assert ids >= TILE_BORDER_IDS


def test_pool_tile_border_ring_surrounds_pool_without_overlap(design_manifest: dict) -> None:
    pool = _bounds(design_manifest, "complex.pool.pool_water_34x12_5ft_to8ft")
    pool_min_x, pool_min_y, _, pool_max_x, pool_max_y, _ = pool

    left = _bounds(design_manifest, "complex.site.pool_tile_border_left")
    right = _bounds(design_manifest, "complex.site.pool_tile_border_right")
    near = _bounds(design_manifest, "complex.site.pool_tile_border_near")
    far = _bounds(design_manifest, "complex.site.pool_tile_border_far")

    # No border strip overlaps the pool footprint in plan (x/y).
    assert left[3] <= pool_min_x + 1e-6  # left strip max_x at pool's left edge
    assert right[0] >= pool_max_x - 1e-6  # right strip min_x at pool's right edge
    assert near[1] >= pool_max_y - 1e-6  # near strip min_y at pool's near edge
    assert far[4] <= pool_min_y + 1e-6  # far strip max_y at pool's far edge


def test_pool_tile_border_is_three_feet_wide(copied_project: Path, design_manifest: dict) -> None:
    cfg = _load_config(copied_project)
    border_mm = to_mm(cfg.PATIO_BORDER)
    assert border_mm == pytest.approx(to_mm(3 * FOOT))

    left = _bounds(design_manifest, "complex.site.pool_tile_border_left")
    # left strip x-span is the border width
    assert (left[3] - left[0]) == pytest.approx(border_mm)
    near = _bounds(design_manifest, "complex.site.pool_tile_border_near")
    # near strip y-span is the border width
    assert (near[4] - near[1]) == pytest.approx(border_mm)


def test_pool_tile_material_registered(design_manifest: dict) -> None:
    tile_elements = [e for e in design_manifest["elements"] if e["id"] in TILE_BORDER_IDS]
    assert len(tile_elements) == 4
    for element in tile_elements:
        assert element["material_id"] == "material.complex.site.199_204_209"
    # No paver-colored site element remains.
    assert not any(e["material_id"] == "material.complex.site.178_178_173" for e in design_manifest["elements"])


# ── Hot tub deck (lower deck) is 17.5' across ───────────────────────────────


def test_lower_deck_width_seventeen_and_a_half_feet(copied_project: Path) -> None:
    cfg = _load_config(copied_project)
    assert to_mm(cfg.LOWER_DECK_WIDTH) == pytest.approx(to_mm(17.5 * FOOT))


def test_hot_tub_sits_within_lower_deck(design_manifest: dict) -> None:
    hot_tub = _bounds(design_manifest, "complex.feature.hot_tub_placeholder")
    lower_skirt = _bounds(design_manifest, "complex.skirting.lower_deck_right_skirt")
    # Lower deck right edge is the right skirt's left x (min_x).
    lower_right_x = lower_skirt[0]
    # Hot tub must fit within the lower deck footprint.
    assert hot_tub[3] <= lower_right_x + 1e-6
    assert hot_tub[0] >= 0.0  # right of the upper deck
    # Hot tub is at least 1' clear from the lower deck right edge.
    assert (lower_right_x - hot_tub[3]) >= to_mm(1 * FOOT) - 1e-6


# ── Top (upper) deck extends 20' from the house toward the pool ──────────────


def test_upper_deck_depth_twenty_feet(copied_project: Path) -> None:
    cfg = _load_config(copied_project)
    assert to_mm(cfg.UPPER_DECK_DEPTH) == pytest.approx(to_mm(20 * FOOT))


def test_upper_deck_front_skirt_at_twenty_feet(copied_project: Path, design_manifest: dict) -> None:
    cfg = _load_config(copied_project)
    skirt = _bounds(design_manifest, "complex.skirting.upper_deck_front_skirt")
    # Front skirt near edge (max_y) sits at y = -UPPER_DECK_DEPTH (20' from house).
    assert skirt[4] == pytest.approx(-to_mm(cfg.UPPER_DECK_DEPTH))
    assert skirt[4] == pytest.approx(-to_mm(20 * FOOT))


# ── Stair risers line up with the back of the step ───────────────────────────


@pytest.mark.parametrize(
    "prefix, count",
    [
        ("upper_straight", 4),
        ("lower_front", 5),
    ],
)
def test_risers_sit_on_tread_top(design_manifest: dict, prefix: str, count: int) -> None:
    for index in range(1, count + 1):
        tread = _bounds(design_manifest, f"complex.stair.{prefix}_tread_{index:02d}")
        riser = _bounds(design_manifest, f"complex.stair.{prefix}_riser_{index:02d}")
        tread_top_z = tread[5]  # max_z
        riser_bottom_z = riser[2]  # min_z
        # Riser bottom must equal tread top (sits on the tread, not through it).
        assert riser_bottom_z == pytest.approx(tread_top_z), (
            f"{prefix} step {index}: riser bottom {riser_bottom_z} != tread top {tread_top_z}"
        )


@pytest.mark.parametrize(
    "prefix, count",
    [
        ("upper_straight", 4),
        ("lower_front", 5),
    ],
)
def test_riser_at_back_of_tread(design_manifest: dict, prefix: str, count: int) -> None:
    for index in range(1, count + 1):
        tread = _bounds(design_manifest, f"complex.stair.{prefix}_tread_{index:02d}")
        riser = _bounds(design_manifest, f"complex.stair.{prefix}_riser_{index:02d}")
        # The riser's back face must align with the tread's back edge.  Because
        # the stair runs along -y, the "back" (toward the upper landing) is the
        # larger y value (max_y, index 4) of each element.
        tread_back_y = tread[4]
        riser_back_y = riser[4]
        assert riser_back_y == pytest.approx(tread_back_y), (
            f"{prefix} step {index}: riser back {riser_back_y} != tread back {tread_back_y}"
        )
