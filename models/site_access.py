"""Paver fields and fence geometry for site access and yard closure."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.units import INCH, to_mm

from models.shared import ZERO


def add_site_access(builder: Any, cfg: Any) -> None:
    paver_width = cfg.SHED_PAVER_MAX_X - cfg.SHED_PAVER_MIN_X
    paver_depth = cfg.SHED_PAVER_END_Y - cfg.SHED_PAVER_START_Y
    builder.add_box(
        "site",
        "UnifiedShedVehicleAccessPavers",
        paver_width,
        paver_depth,
        cfg.SHED_PAVER_THICKNESS,
        cfg.SHED_PAVER_MIN_X,
        cfg.SHED_PAVER_START_Y,
        -cfg.SHED_PAVER_THICKNESS,
        cfg.PAVER_COLOR,
        drawing_label=True,
        properties={
            "label": "Unified Shed and Vehicle Access Pavers",
            "complex_type": "vehicle_access_paver_field",
            "from_element_id": "complex.shed.yard_storage_shed",
            "surface": "exterior_access_pavers",
        },
    )
    parent_id = "complex.site.shed_access_fence"
    fence_x = cfg.SHED_PAVER_MIN_X - cfg.SHED_ACCESS_FENCE_POST_SIZE
    start_y, end_y = cfg.SHED_Y, cfg.SHED_PAVER_END_Y
    depth = end_y - start_y
    properties = {
        "complex_type": "ornamental_access_fence",
        "side": "right_when_viewed_house_to_shed",
        "finish": "black_powder_coat",
        "adjacent_to": "complex.site.unified_shed_vehicle_access_pavers",
    }
    builder.add_box(
        "site",
        "ShedAccessFence",
        cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
        depth,
        cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
        fence_x,
        start_y,
        12 * INCH,
        cfg.FENCE_COLOR,
        drawing_label=True,
        properties={**properties, "assembly_role": "lower_rail"},
    )
    builder.add_box(
        "site",
        "ShedAccessFenceTopRail",
        cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
        depth,
        cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
        fence_x,
        start_y,
        cfg.SHED_ACCESS_FENCE_HEIGHT - 6 * INCH,
        cfg.FENCE_COLOR,
        parent_id=parent_id,
        properties={**properties, "assembly_role": "top_rail"},
    )
    for index in range(math.ceil(to_mm(depth) / to_mm(cfg.SHED_ACCESS_FENCE_POST_SPACING)) + 1):
        post_y = min(start_y + index * cfg.SHED_ACCESS_FENCE_POST_SPACING, end_y - cfg.SHED_ACCESS_FENCE_POST_SIZE)
        builder.add_box(
            "site",
            f"ShedAccessFencePost_{index + 1:02d}",
            cfg.SHED_ACCESS_FENCE_POST_SIZE,
            cfg.SHED_ACCESS_FENCE_POST_SIZE,
            cfg.SHED_ACCESS_FENCE_HEIGHT,
            fence_x,
            post_y,
            ZERO,
            cfg.FENCE_COLOR,
            parent_id=parent_id,
            properties={**properties, "assembly_role": "post"},
        )
    for index in range(math.floor(to_mm(depth) / to_mm(cfg.SHED_ACCESS_FENCE_PICKET_SPACING)) + 1):
        builder.add_box(
            "site",
            f"ShedAccessFencePicket_{index + 1:03d}",
            cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
            cfg.SHED_ACCESS_FENCE_RAIL_SIZE,
            cfg.SHED_ACCESS_FENCE_HEIGHT - 3 * INCH,
            fence_x,
            start_y + index * cfg.SHED_ACCESS_FENCE_PICKET_SPACING,
            ZERO,
            cfg.FENCE_COLOR,
            parent_id=parent_id,
            properties={**properties, "assembly_role": "picket"},
        )
    house_fence_properties = {
        "complex_type": "solid_privacy_fence",
        "assembly_role": "yard_closure_screen",
        "finish": "white_solid_panel",
        "opacity": "solid",
        "see_through": False,
        "adjacent_to": parent_id,
        "connects_to": "complex.house.house_mass",
        "side": "shed_access_to_house",
        "axis": "y0",
    }
    builder.add_box(
        "site",
        "ShedAccessHouseFence",
        -fence_x,
        cfg.PROPERTY_LINE_FENCE_THICKNESS,
        cfg.PROPERTY_LINE_FENCE_HEIGHT,
        fence_x,
        -cfg.PROPERTY_LINE_FENCE_THICKNESS + 2 * INCH,
        ZERO,
        cfg.PROPERTY_LINE_FENCE_COLOR,
        drawing_label=True,
        properties=house_fence_properties,
    )
    property_fence_properties = {
        "complex_type": "solid_privacy_fence",
        "assembly_role": "house_line_screen",
        "finish": "white_solid_panel",
        "opacity": "solid",
        "see_through": False,
        "adjacent_to": "complex.house.house_mass",
        "connects_to": "complex.site.property_line_solid_fence",
        "side": "house_to_property_line",
        "axis": "y0",
    }
    builder.add_box(
        "site",
        "HouseMassToPropertyLineSolidFence",
        cfg.PROPERTY_LINE_FENCE_X - cfg.HOUSE_WIDTH,
        cfg.PROPERTY_LINE_FENCE_THICKNESS,
        cfg.PROPERTY_LINE_FENCE_HEIGHT,
        cfg.HOUSE_WIDTH,
        -cfg.PROPERTY_LINE_FENCE_THICKNESS,
        ZERO,
        cfg.PROPERTY_LINE_FENCE_COLOR,
        drawing_label=True,
        properties=property_fence_properties,
    )
    builder.add_box(
        "site",
        "PropertyLineSolidFence",
        cfg.PROPERTY_LINE_FENCE_THICKNESS,
        -cfg.SHED_Y,
        cfg.PROPERTY_LINE_FENCE_HEIGHT,
        cfg.PROPERTY_LINE_FENCE_X,
        cfg.SHED_Y,
        ZERO,
        cfg.PROPERTY_LINE_FENCE_COLOR,
        drawing_label=True,
        properties={
            "complex_type": "solid_privacy_fence",
            "assembly_role": "property_line_screen",
            "finish": "white_solid_panel",
            "opacity": "solid",
            "see_through": False,
            "adjacent_to": "complex.site.unified_yard_grass",
            "connects_to": "complex.site.house_mass_to_property_line_solid_fence",
            "side": "right_property_line",
        },
    )
    rock_x = fence_x + cfg.SHED_ACCESS_FENCE_POST_SIZE
    rock_width = cfg.SHED_X - rock_x
    rock_depth = cfg.SHED_FRONT_Y - cfg.SHED_Y
    if to_mm(rock_width) > 0 and to_mm(rock_depth) > 0:
        builder.add_box(
            "site",
            "ShedFenceRockBed",
            rock_width,
            rock_depth,
            cfg.ROCK_BED_THICKNESS,
            rock_x,
            cfg.SHED_Y,
            -cfg.ROCK_BED_THICKNESS,
            cfg.ROCK_COLOR,
            drawing_label=True,
            properties={
                "complex_type": "landscape_rock_bed",
                "assembly_role": "fence_to_shed_transition",
                "from_element_id": parent_id,
                "to_element_id": "complex.shed.yard_storage_shed",
                "surface": "landscape_rock",
            },
        )
