"""Remaining landscape accents, trees, and planting details."""

from __future__ import annotations

import math
from typing import Any

from build123d import Cone, Sphere
from python_cad_tools.elements import Dimensions
from python_cad_tools.units import FOOT, INCH, Length, to_mm

from models.shared import ZERO

TREE_GREEN = (0.0, 0.45, 0.15)
TREE_BROWN = (0.40, 0.25, 0.10)


def add_landscape(
    builder: Any,
    cfg: Any,
    shed_x: Length,
    shed_y: Length,
    shed_depth: Length,
    rock_bed_x: Length,
    rock_bed_width: Length,
) -> None:
    for rock_index in range(12):
        radius = (2.5 + (rock_index % 4) * 0.45) * INCH
        rock_x = rock_bed_x + rock_bed_width * ((rock_index % 3) + 1) / 4
        rock_y = shed_y + shed_depth * ((rock_index // 3) + 1) / 5
        shape = Sphere(to_mm(radius)).solid().translate((to_mm(rock_x), to_mm(rock_y), -to_mm(radius) * 0.25))
        builder.add_shape(
            "site",
            f"ShedRockAccent_{rock_index + 1:02d}",
            shape,
            cfg.ROCK_COLOR,
            Dimensions(to_mm(2 * radius), to_mm(2 * radius), to_mm(2 * radius)),
            placement=(rock_x - radius, rock_y - radius, -radius),
            parent_id="complex.site.shed_grass_rock_bed",
            properties={"complex_type": "landscape_accent_stone", "assembly_role": "rock_bed_surface_detail"},
        )
    trunk_height, trunk_radius = cfg.TREE_TRUNK_HEIGHT, cfg.TREE_TRUNK_RADIUS
    for tree_number, tree_y, lower_depth in (
        (7, -54 * FOOT, 6 * FOOT),
        (8, -58 * FOOT, 6 * FOOT),
        (9, -62 * FOOT, 6 * FOOT),
        (10, -66 * FOOT, 6 * FOOT),
    ):
        builder.add_cylinder(
            "site",
            f"Tree_{tree_number:02d}Trunk",
            (ZERO, tree_y, ZERO),
            (ZERO, tree_y, trunk_height),
            trunk_radius,
            TREE_BROWN,
        )
        scale = lower_depth / (6 * FOOT)
        variation = 1.0 + ((tree_number * 17) % 5 - 2) * 0.025
        layers = (
            (3 * FOOT * scale, 3.25 * FOOT * variation, ZERO),
            (2.35 * FOOT * scale, 3.25 * FOOT * variation, 2.25 * FOOT),
            (1.65 * FOOT * scale, 3.5 * FOOT * variation, 4.5 * FOOT),
        )
        for layer, (radius, height, offset) in enumerate(layers):
            shape = (
                Cone(to_mm(radius), to_mm(2 * INCH), to_mm(height))
                .solid()
                .translate((0, to_mm(tree_y), to_mm(trunk_height + offset)))
            )
            builder.add_shape(
                "site",
                f"Tree_{tree_number:02d}Foliage_{layer + 1}",
                shape,
                TREE_GREEN,
                Dimensions(to_mm(2 * radius), to_mm(2 * radius), to_mm(height)),
                placement=(-radius, tree_y - radius, trunk_height + offset),
                drawing_label=tree_number == 1 and layer == 2,
                properties={"complex_type": "evergreen_foliage_crown", "assembly_role": "foliage", "conceptual": False},
            )
    count = (
        int(
            math.floor(
                to_mm(cfg.RIGHT_TREE_LINE_START_Y - cfg.RIGHT_TREE_LINE_END_Y) / to_mm(cfg.RIGHT_TREE_LINE_SPACING)
            )
        )
        + 1
    )
    for index in range(count):
        tree_y, number = cfg.RIGHT_TREE_LINE_START_Y - index * cfg.RIGHT_TREE_LINE_SPACING, index + 1
        props = {
            "complex_type": "evergreen_tree",
            "label": f"Right Yard Evergreen Tree {number:02d}",
            "landscape_role": "positive_x_yard_tree_line",
            "layout_axis": "y",
            "center_x_mm": to_mm(cfg.RIGHT_TREE_LINE_X),
            "center_y_mm": to_mm(tree_y),
            "spacing_mm": to_mm(cfg.RIGHT_TREE_LINE_SPACING),
            "conceptual": False,
        }
        builder.add_cylinder(
            "site",
            f"RightBoundaryTree_{number:02d}Trunk",
            (cfg.RIGHT_TREE_LINE_X, tree_y, ZERO),
            (cfg.RIGHT_TREE_LINE_X, tree_y, trunk_height),
            trunk_radius,
            TREE_BROWN,
            properties={**props, "assembly_role": "trunk"},
        )
        variation = 1.0 + ((number * 13) % 5 - 2) * 0.025
        for layer, (radius, height, offset) in enumerate(
            (
                (3 * FOOT, 3.25 * FOOT * variation, ZERO),
                (2.35 * FOOT, 3.25 * FOOT * variation, 2.25 * FOOT),
                (1.65 * FOOT, 3.5 * FOOT * variation, 4.5 * FOOT),
            )
        ):
            shape = (
                Cone(to_mm(radius), to_mm(2 * INCH), to_mm(height))
                .solid()
                .translate((to_mm(cfg.RIGHT_TREE_LINE_X), to_mm(tree_y), to_mm(trunk_height + offset)))
            )
            builder.add_shape(
                "site",
                f"RightBoundaryTree_{number:02d}Foliage_{layer + 1}",
                shape,
                TREE_GREEN,
                Dimensions(to_mm(2 * radius), to_mm(2 * radius), to_mm(height)),
                placement=(cfg.RIGHT_TREE_LINE_X - radius, tree_y - radius, trunk_height + offset),
                drawing_label=number == 1 and layer == 2,
                properties={**props, "assembly_role": "foliage", "foliage_tier": layer + 1},
            )
        if number == 1:
            builder.add_box(
                "site",
                "RightBoundaryTree_01CardinalBranchTip",
                INCH,
                INCH,
                INCH,
                cfg.RIGHT_TREE_LINE_X - 0.5 * INCH,
                tree_y + 3 * FOOT - INCH,
                trunk_height + 2 * FOOT,
                TREE_GREEN,
                parent_id="complex.site.right_boundary_tree_01_foliage_1",
                properties={
                    **props,
                    "complex_type": "evergreen_branch_tip",
                    "assembly_role": "cardinal_foliage_extent",
                },
            )
