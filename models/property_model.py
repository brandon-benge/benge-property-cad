"""Compose the property model; keep this orchestration module below 400 lines."""

from __future__ import annotations

from python_cad_tools.context import BuildContext
from python_cad_tools.elements import DesignModel, Dimensions
from python_cad_tools.geometry import box
from python_cad_tools.units import FOOT, INCH, to_mm

import config as cfg
from models.builder import ModelBuilder
from models.decks import add_decks
from models.features import add_features
from models.landscape import add_landscape
from models.lighting import add_skirt_lights, add_stair_lights
from models.play_accessories import add_play_accessories
from models.play_structure import add_play_structure
from models.pool import add_pool_equipment, add_pool_shell_water
from models.roof import add_roof
from models.shared import CUT_MARGIN, ZERO
from models.shed import add_shed
from models.site_access import add_site_access
from models.site_surfaces import add_grass_regions, add_pool_rock_bed, add_unified_grass
from models.spa import add_spa
from models.stairs import add_final_rails, add_lower_stairs, add_upper_stairs


def build_model(context: BuildContext) -> DesignModel:
    builder = ModelBuilder()

    add_decks(builder, cfg)
    roof = add_roof(builder, cfg)
    roof_back_z = roof.roof_back_z
    roof_front_z = roof.roof_front_z
    sliding_door_x = 3 * cfg.FOOT + 6 * INCH
    sliding_door_y = -1.5 * INCH

    lower_x = ZERO
    # Main above-ground oval pool centered at x=7.5yd, y=-12yd and set to a
    # standard above-ground wall height so it stays shorter than the deck.
    pool_length = cfg.POOL_LENGTH
    pool_width = cfg.POOL_WIDTH
    pool_x = cfg.POOL_CENTER_X - pool_length / 2
    pool_y = cfg.POOL_CENTER_Y - pool_width / 2
    pool_z = cfg.LOWER_DECK_ELEVATION - cfg.POOL_DEEP_DEPTH
    # Keep the hot tub fully inside the lower deck footprint, inset 1ft from
    # the deck's outer X edge and 1ft from the Y-axis edge.
    hot_tub_x = lower_x + cfg.LOWER_DECK_WIDTH - cfg.HOT_TUB_WIDTH - cfg.FOOT
    hot_tub_y = -(cfg.HOT_TUB_DEPTH + cfg.FOOT)

    upper_stair_start = roof.upper_stair_start
    upper_stair_end = roof.upper_stair_end

    add_features(builder, cfg, roof_back_z, roof_front_z, sliding_door_x, sliding_door_y)

    add_spa(builder, cfg, hot_tub_x, hot_tub_y)

    skirt_thickness = 2 * INCH
    upper_skirt_height = cfg.UPPER_DECK_ELEVATION - cfg.DECK_THICKNESS
    lower_skirt_height = cfg.LOWER_DECK_ELEVATION - cfg.DECK_THICKNESS
    upper_right_skirt_bottom = cfg.DECK_SKIRT_MIN_CLEARANCE_ABOVE_GRADE
    # The upper right skirt connects the upper deck edge to the lower deck.
    # Create it as a simple box covering the upper deck depth.
    upper_right_skirt = box(
        skirt_thickness,
        cfg.UPPER_DECK_DEPTH,
        upper_skirt_height - upper_right_skirt_bottom,
        origin=(cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH, upper_right_skirt_bottom),
    )
    builder.add_box(
        "skirting",
        "UpperDeckFrontSkirt",
        cfg.UPPER_DECK_WIDTH,
        skirt_thickness,
        upper_skirt_height,
        ZERO,
        -cfg.UPPER_DECK_DEPTH - skirt_thickness,
        ZERO,
        cfg.SKIRTING_COLOR,
    )
    upper_mid_beam_y = -cfg.UPPER_DECK_DEPTH / 2 - cfg.BEAM_WIDTH / 2
    upper_access_panel_max_y = upper_mid_beam_y - cfg.BEAM_FEATURE_CLEARANCE
    upper_access_panel_y = upper_access_panel_max_y - cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_WIDTH
    upper_access_panel_opening = box(
        skirt_thickness + CUT_MARGIN,
        cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_WIDTH + CUT_MARGIN,
        cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_HEIGHT + CUT_MARGIN,
        origin=(
            -skirt_thickness - CUT_MARGIN / 2,
            upper_access_panel_y - CUT_MARGIN / 2,
            cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_SILL - CUT_MARGIN / 2,
        ),
    )
    upper_left_skirt = box(
        skirt_thickness,
        cfg.UPPER_DECK_DEPTH,
        upper_skirt_height,
        origin=(-skirt_thickness, -cfg.UPPER_DECK_DEPTH, ZERO),
    )
    builder.add_shape(
        "skirting",
        "UpperDeckLeftSkirt",
        upper_left_skirt.cut(upper_access_panel_opening),
        cfg.SKIRTING_COLOR,
        Dimensions(to_mm(skirt_thickness), to_mm(cfg.UPPER_DECK_DEPTH), to_mm(upper_skirt_height)),
        placement=(-skirt_thickness, -cfg.UPPER_DECK_DEPTH, ZERO),
        properties={
            "complex_type": "deck_skirt_with_access_opening",
            "assembly_role": "deck_enclosure",
            "opening_for": "complex.skirting.upper_deck_left_skirt_access_panel",
            "wall_opening": True,
        },
    )
    builder.add_shape(
        "skirting",
        "UpperDeckRightSkirt",
        upper_right_skirt,
        cfg.SKIRTING_COLOR,
        Dimensions(
            to_mm(skirt_thickness),
            to_mm(cfg.UPPER_DECK_DEPTH),
            to_mm(upper_skirt_height - upper_right_skirt_bottom),
        ),
        placement=(cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH, upper_right_skirt_bottom),
        properties={
            "complex_type": "profiled_deck_skirt",
            "assembly_role": "deck_enclosure",
            "adjacent_to": "complex.deck_board.lower_*, complex.stair.lower_front_*",
            "minimum_clearance_above_grade_mm": to_mm(cfg.DECK_SKIRT_MIN_CLEARANCE_ABOVE_GRADE),
        },
    )
    builder.add_box(
        "skirting",
        "LowerDeckRightSkirt",
        skirt_thickness,
        cfg.LOWER_DECK_DEPTH,
        lower_skirt_height,
        lower_x + cfg.LOWER_DECK_WIDTH,
        -cfg.LOWER_DECK_DEPTH,
        ZERO,
        cfg.SKIRTING_COLOR,
    )
    builder.add_box(
        "skirting",
        "LowerDeckLeftSkirt",
        skirt_thickness,
        cfg.LOWER_DECK_DEPTH - cfg.UPPER_DECK_DEPTH,
        lower_skirt_height,
        -skirt_thickness,
        -cfg.UPPER_DECK_DEPTH,
        ZERO,
        cfg.SKIRTING_COLOR,
        properties={
            "complex_type": "profiled_deck_skirt",
            "assembly_role": "deck_enclosure",
            "adjacent_to": "complex.railing.lower_left_rail",
        },
    )
    # Access panel on the yard side of UpperMidBeam, aligned with its skirt opening.
    access_panel_color = (0.30, 0.25, 0.20)
    builder.add_box(
        "skirting",
        "UpperDeckLeftSkirtAccessPanel",
        INCH,
        cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_WIDTH,
        cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_HEIGHT,
        -skirt_thickness - INCH,
        upper_access_panel_y,
        cfg.UPPER_LEFT_SKIRT_ACCESS_PANEL_SILL,
        access_panel_color,
        properties={
            "complex_type": "deck_skirt_access_panel",
            "assembly_role": "service_access",
            "opening_in": "complex.skirting.upper_deck_left_skirt",
            "clear_of": "complex.deck_framing.upper_mid_beam",
            "minimum_clearance_mm": to_mm(cfg.BEAM_FEATURE_CLEARANCE),
        },
    )
    # Access panel on LowerDeckRightSkirt — starts 6in from y=0, 6ft wide
    # Box spans y=-6ft-6in to y=-6in (top edge 6in from house wall)
    builder.add_box(
        "skirting",
        "LowerDeckRightSkirtAccessPanel",
        INCH,
        6 * FOOT,
        2 * FOOT,
        lower_x + cfg.LOWER_DECK_WIDTH + skirt_thickness,
        -6 * FOOT - 6 * INCH,
        ZERO + 6 * INCH,
        access_panel_color,
    )

    add_skirt_lights(builder, skirt_thickness, lower_x, cfg)

    # Upper stairs run diagonally from the far right corner of the upper deck
    # (catty corner from the door) down to the lower deck at a 90-degree angle.
    # The stairs descend at an angle, not aligned to X or Y axis.
    # Use the roof phase endpoints so posts, stairs, and rails share one datum.
    add_stair_lights(
        builder,
        "UpperStraight",
        upper_stair_start,
        upper_stair_end,
        cfg.UPPER_DECK_ELEVATION,
        cfg.LOWER_DECK_ELEVATION,
        axis="y",
    )
    upper_stair_left_top, upper_stair_right_top = add_upper_stairs(builder, upper_stair_start, upper_stair_end, cfg)

    # Lower deck stairs positioned at the far left of the lower deck, 4' wide.
    # They descend from the lower deck to the ground.
    lower_stair_width = 4 * cfg.FOOT
    lower_stair_start = (lower_x + lower_stair_width / 2, -cfg.LOWER_DECK_DEPTH)
    lower_stair_end = (lower_stair_start[0], -cfg.LOWER_DECK_DEPTH - 6 * cfg.FOOT)
    add_lower_stairs(builder, lower_stair_start, lower_stair_end, lower_stair_width, cfg)
    add_stair_lights(
        builder, "LowerFront", lower_stair_start, lower_stair_end, cfg.LOWER_DECK_ELEVATION, ZERO, lower_stair_width
    )

    add_pool_shell_water(builder, cfg, pool_x, pool_y, pool_z, pool_length, pool_width)

    grass_regions = add_grass_regions(builder, cfg, pool_x, pool_y, pool_length, pool_width, -cfg.UPPER_DECK_DEPTH)

    add_site_access(builder, cfg)

    add_unified_grass(builder, cfg, grass_regions, pool_x, pool_y, pool_length, pool_width)

    rock_bed_width = add_pool_rock_bed(builder, cfg, pool_x, pool_y, pool_length, pool_width)

    add_pool_equipment(builder, cfg, pool_x, pool_y, pool_length, rock_bed_width)

    # East-yard swing set on the positive-X side of the grass yard.
    # The nearest edge of the structure sits 15ft south of the pool's south edge.
    swing_set_x = cfg.PROPERTY_LINE_FENCE_X - cfg.SWING_SET_LENGTH - cfg.SWING_SET_EAST_CLEARANCE
    swing_set_north_y = pool_y - cfg.SWING_SET_NEAR_EDGE_OFFSET
    swing_set_south_y = swing_set_north_y - cfg.SWING_SET_DEPTH
    swing_set_platform_y = swing_set_north_y - cfg.SWING_SET_PLATFORM_DEPTH
    beam_y, platform_top_z, swing_set_id = add_play_structure(
        builder, cfg, swing_set_x, swing_set_north_y, swing_set_south_y, swing_set_platform_y
    )
    add_play_accessories(builder, cfg, swing_set_x, swing_set_platform_y, beam_y, platform_top_z, swing_set_id)
    shed_rock_bed_x, shed_rock_bed_width = add_shed(builder, cfg, cfg.SHED_X, cfg.SHED_Y)
    add_landscape(builder, cfg, cfg.SHED_X, cfg.SHED_Y, cfg.SHED_DEPTH, shed_rock_bed_x, shed_rock_bed_width)
    add_final_rails(
        builder,
        upper_stair_left_top,
        upper_stair_right_top,
        upper_stair_start,
        lower_x,
        lower_stair_width,
        pool_x,
        pool_x + pool_length,
        cfg,
    )
    return DesignModel(
        id="file.template",
        name=cfg.PROJECT_NAME,
        artifact_stem="FileTemplate",
        elements=builder.elements,
        metadata={
            "project": "File Template CAD",
            "source_authority": "https://github.com/brandon-benge/benge-property-cad",
            "source_commit": context.source_revision or "unknown",
        },
    )
