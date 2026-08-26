"""Grass, pool rock beds, and related landscape surface geometry."""

from __future__ import annotations

from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import bounds, box
from python_cad_tools.units import Length, mm, to_mm

from models.geometry import capsule_curve_points
from models.pool import TREE_GREEN
from models.shared import CUT_MARGIN, ZERO, _capsule_solid


def add_grass_regions(
    builder: Any,
    cfg: Any,
    pool_x: Length,
    pool_y: Length,
    pool_length: Length,
    pool_width: Length,
    lower_stair_end_y: Length,
) -> list[Any]:
    tile_border = ZERO
    pool_right = pool_x + pool_length + tile_border
    overlap = cfg.POOL_COPING_WIDTH / 2
    regions: list[Any] = [
        _capsule_solid(
            pool_length + 2 * overlap + CUT_MARGIN,
            pool_width + 2 * overlap + CUT_MARGIN,
            cfg.GRASS_THICKNESS + CUT_MARGIN,
            origin=(
                pool_x - overlap - CUT_MARGIN / 2,
                pool_y - overlap - CUT_MARGIN / 2,
                -cfg.GRASS_THICKNESS - CUT_MARGIN / 2,
            ),
        ).cut(
            _capsule_solid(
                pool_length + CUT_MARGIN,
                pool_width + CUT_MARGIN,
                cfg.GRASS_THICKNESS + CUT_MARGIN,
                origin=(pool_x - CUT_MARGIN / 2, pool_y - CUT_MARGIN / 2, -cfg.GRASS_THICKNESS - CUT_MARGIN / 2),
            )
        )
    ]
    far_y = pool_y + pool_width + tile_border
    depth = lower_stair_end_y - far_y
    if to_mm(depth) > 0:
        regions.append(box(pool_right, depth, cfg.GRASS_THICKNESS, origin=(ZERO, far_y, -cfg.GRASS_THICKNESS)))
    south_far_y, south_start_y = pool_y - tile_border, cfg.SHED_Y
    south_depth = south_far_y - south_start_y
    connector_end_y = south_far_y
    connector_start_y = connector_end_y - cfg.VEHICLE_CONNECTOR_CLEAR_WIDTH
    connector_end_x = pool_x
    if to_mm(south_depth) > 0:
        regions.append(
            box(
                cfg.POOL_SOUTH_GRASS_MAX_X - connector_end_x,
                south_depth,
                cfg.GRASS_THICKNESS,
                origin=(connector_end_x, south_start_y, -cfg.GRASS_THICKNESS),
            )
        )
        for start_y, region_depth in (
            (south_start_y, connector_start_y - south_start_y),
            (connector_start_y, cfg.VEHICLE_CONNECTOR_CLEAR_WIDTH),
            (connector_end_y, south_far_y - connector_end_y),
        ):
            if to_mm(region_depth) > 0:
                regions.append(
                    box(
                        connector_end_x, region_depth, cfg.GRASS_THICKNESS, origin=(ZERO, start_y, -cfg.GRASS_THICKNESS)
                    )
                )
    right_depth = ZERO - south_far_y
    if to_mm(right_depth) > 0:
        regions.append(
            box(
                cfg.POOL_SOUTH_GRASS_MAX_X - pool_right,
                right_depth,
                cfg.GRASS_THICKNESS,
                origin=(pool_right, south_far_y, -cfg.GRASS_THICKNESS),
            )
        )
    return regions


def add_unified_grass(
    builder: Any, cfg: Any, regions: list[Any], pool_x: Length, pool_y: Length, pool_length: Length, pool_width: Length
) -> None:
    tile_border = ZERO
    regions.append(
        box(pool_x, pool_width, cfg.GRASS_THICKNESS, origin=(ZERO, pool_y - tile_border, -cfg.GRASS_THICKNESS))
    )
    overlap = cfg.POOL_COPING_WIDTH / 2
    regions.append(
        box(overlap, pool_width, cfg.GRASS_THICKNESS, origin=(pool_x - overlap, pool_y, -cfg.GRASS_THICKNESS))
    )
    regions.append(
        box(overlap, pool_width, cfg.GRASS_THICKNESS, origin=(pool_x + pool_length, pool_y, -cfg.GRASS_THICKNESS))
    )
    builder.add_shape(
        "site",
        "UnifiedYardGrass",
        regions[0].fuse(*regions[1:]),
        cfg.GRASS_COLOR,
        Dimensions(
            to_mm(cfg.POOL_SOUTH_GRASS_MAX_X),
            to_mm(-cfg.SHED_Y),
            to_mm(cfg.GRASS_THICKNESS),
            extras={"region_count": len(regions)},
        ),
        drawing_label=True,
        properties={
            "label": "Unified Yard Grass",
            "complex_type": "turf_assembly",
            "assembly_role": "yard_grass_with_hardscape_exclusions",
        },
    )


def add_pool_rock_bed(
    builder: Any, cfg: Any, pool_x: Length, pool_y: Length, pool_length: Length, pool_width: Length
) -> Length:
    width, height = 4 * cfg.FOOT, 1 * cfg.FOOT
    outer_length, outer_width = pool_length + 2 * width, pool_width + 2 * width
    outer = _capsule_solid(outer_length, outer_width, height, origin=(pool_x - width, pool_y - width, ZERO))
    inner = _capsule_solid(
        pool_length + CUT_MARGIN,
        pool_width + CUT_MARGIN,
        height + CUT_MARGIN,
        origin=(pool_x - CUT_MARGIN / 2, pool_y - CUT_MARGIN / 2, -CUT_MARGIN / 2),
    )
    cutter = box(
        outer_length + 2 * CUT_MARGIN,
        outer_width + CUT_MARGIN,
        height + 2 * CUT_MARGIN,
        origin=(pool_x - width - CUT_MARGIN, pool_y + pool_width / 2, -CUT_MARGIN),
    )
    rock = outer.cut(inner).cut(cutter)
    pieces = rock.solids()
    properties = {
        "label": "Pool South Rock Bed",
        "complex_type": "landscape_rock_bed",
        "assembly_role": "pool_surround",
        "elevation_mm": to_mm(height),
        "width_mm": to_mm(width),
        "adjacent_to": "complex.pool.main_pool_shell_sloped5ft_to8ft",
    }
    if len(pieces) <= 1:
        builder.add_shape(
            "rock-bed",
            "PoolSouthRockBed",
            rock,
            cfg.ROCK_COLOR,
            Dimensions(to_mm(outer_length), to_mm(outer_width / 2), to_mm(height)),
            placement=(pool_x - width, pool_y - width, ZERO),
            drawing_label=True,
            stable_id="complex.rock_bed.pool_south_rock_bed",
            properties=properties,
        )
    else:
        for index, solid in enumerate(sorted(pieces, key=lambda item: bounds(item)[1]), 1):
            item_bounds = bounds(solid)
            builder.add_shape(
                "rock-bed",
                f"PoolSouthRockBed_{index:02d}",
                solid,
                cfg.ROCK_COLOR,
                Dimensions(
                    item_bounds[3] - item_bounds[0], item_bounds[4] - item_bounds[1], item_bounds[5] - item_bounds[2]
                ),
                placement=(mm(item_bounds[0]), mm(item_bounds[1]), mm(item_bounds[2])),
                properties=properties,
            )
    center_x, center_y = pool_x + pool_length / 2, pool_y + pool_width / 2
    for index, (x, y) in enumerate(
        capsule_curve_points(
            center_x,
            center_y,
            pool_length,
            pool_width,
            2 * cfg.FOOT,
            cfg.SKIP_LAUREL_SPACING,
            cfg.SKIP_LAUREL_START_OFFSET,
        ),
        1,
    ):
        builder.add_box(
            "site",
            f"PoolSouthRockBedSkipLaurel_{index:02d}",
            cfg.SKIP_LAUREL_WIDTH,
            cfg.SKIP_LAUREL_DEPTH,
            cfg.SKIP_LAUREL_HEIGHT,
            x - cfg.SKIP_LAUREL_WIDTH / 2,
            y - cfg.SKIP_LAUREL_DEPTH / 2,
            ZERO,
            TREE_GREEN,
            parent_id="complex.rock_bed.pool_south_rock_bed",
            properties={
                "complex_type": "skip_laurel_shrub",
                "assembly_role": "landscape_planting",
                "label": f"Skip Laurel {index:02d}",
                "spacing_mm": to_mm(cfg.SKIP_LAUREL_SPACING),
            },
        )
    return width
