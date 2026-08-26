"""Pool shell, water, planting, and equipment geometry for the property model."""

from __future__ import annotations

from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.units import Length, to_mm

from models.geometry import capsule_curve_points
from models.shared import CUT_MARGIN, ZERO, _capsule_solid

TREE_GREEN = (0.0, 0.45, 0.15)


_capsule_curve_points = capsule_curve_points


def add_pool_shell_water(
    builder: Any, cfg: Any, pool_x: Length, pool_y: Length, pool_z: Length, pool_length: Length, pool_width: Length
) -> None:
    shell_outer = _capsule_solid(pool_length, pool_width, cfg.POOL_DEEP_DEPTH, origin=(pool_x, pool_y, pool_z))
    shell_inner = _capsule_solid(
        pool_length - 2 * cfg.POOL_SHELL_THICKNESS + CUT_MARGIN,
        pool_width - 2 * cfg.POOL_SHELL_THICKNESS + CUT_MARGIN,
        cfg.POOL_DEEP_DEPTH - cfg.POOL_SHELL_THICKNESS + CUT_MARGIN,
        origin=(
            pool_x + cfg.POOL_SHELL_THICKNESS - CUT_MARGIN / 2,
            pool_y + cfg.POOL_SHELL_THICKNESS - CUT_MARGIN / 2,
            pool_z + cfg.POOL_SHELL_THICKNESS - CUT_MARGIN / 2,
        ),
    )
    shell_id = "complex.pool.main_pool_shell_sloped5ft_to8ft"
    builder.add_shape(
        "pool",
        "MainPoolShellSloped5ftTo8ft",
        shell_outer.cut(shell_inner),
        cfg.POOL_SHELL_COLOR,
        Dimensions(to_mm(pool_length), to_mm(pool_width), to_mm(cfg.POOL_DEEP_DEPTH)),
        placement=(pool_x, pool_y, pool_z),
        drawing_label=True,
        stable_id=shell_id,
        properties={
            "label": "Main Oval Pool Shell",
            "complex_type": "above_ground_oval_pool_shell",
            "assembly_role": "pool_shell",
            "center_x_mm": to_mm(cfg.POOL_CENTER_X),
            "center_y_mm": to_mm(cfg.POOL_CENTER_Y),
        },
    )
    inner_length = pool_length - 2 * cfg.POOL_SHELL_THICKNESS
    inner_width = pool_width - 2 * cfg.POOL_SHELL_THICKNESS
    inner_height = cfg.POOL_DEEP_DEPTH - cfg.POOL_COPING_THICKNESS - cfg.POOL_SHELL_THICKNESS
    inner_origin = (
        pool_x + cfg.POOL_SHELL_THICKNESS,
        pool_y + cfg.POOL_SHELL_THICKNESS,
        pool_z + cfg.POOL_SHELL_THICKNESS,
    )
    builder.add_shape(
        "pool",
        "MainPoolWaterSloped5ftTo8ft",
        _capsule_solid(inner_length, inner_width, inner_height, origin=inner_origin),
        cfg.WATER_COLOR,
        Dimensions(to_mm(inner_length), to_mm(inner_width), to_mm(inner_height)),
        placement=inner_origin,
        drawing_label=True,
        stable_id="complex.pool.main_pool_water_sloped5ft_to8ft",
        parent_id=shell_id,
        properties={
            "label": "Main Oval Pool Water",
            "complex_type": "pool_water_surface",
            "assembly_role": "water",
            "center_x_mm": to_mm(cfg.POOL_CENTER_X),
            "center_y_mm": to_mm(cfg.POOL_CENTER_Y),
        },
    )


def add_pool_equipment(
    builder: Any, cfg: Any, pool_x: Length, pool_y: Length, pool_length: Length, rock_bed_width: Length
) -> None:
    slab_x = pool_x + pool_length + rock_bed_width
    slab_y = pool_y - rock_bed_width - cfg.POOL_EQUIPMENT_SLAB_WIDTH + 8 * cfg.FOOT
    builder.add_box(
        "pool-equipment",
        "PoolEquipmentSlab",
        cfg.POOL_EQUIPMENT_SLAB_LENGTH,
        cfg.POOL_EQUIPMENT_SLAB_WIDTH,
        cfg.POOL_EQUIPMENT_SLAB_THICKNESS,
        slab_x,
        slab_y,
        ZERO,
        (0.50, 0.50, 0.50),
        drawing_label=True,
        stable_id="complex.pool_equipment.equipment_slab",
        properties={
            "label": "Pool Equipment Slab",
            "complex_type": "pool_equipment_pad",
            "assembly_role": "foundation",
            "dimensions": "5ft x 5ft x 4in concrete pad",
            "adjacent_to": "complex.rock_bed.pool_south_rock_bed",
        },
    )
    top_z = cfg.POOL_EQUIPMENT_SLAB_THICKNESS
    pump_x, pump_y = slab_x + cfg.POOL_EQUIPMENT_SLAB_LENGTH / 4, slab_y + cfg.POOL_EQUIPMENT_SLAB_WIDTH / 4
    builder.add_cylinder(
        "pool-equipment",
        "PoolPump",
        (pump_x, pump_y, top_z),
        (pump_x, pump_y, top_z + cfg.POOL_PUMP_HEIGHT),
        cfg.POOL_PUMP_DIAMETER / 2,
        (0.15, 0.15, 0.15),
        parent_id="complex.pool_equipment.equipment_slab",
        properties={
            "complex_type": "pool_pump",
            "assembly_role": "equipment",
            "label": "Pool Pump",
            "diameter_mm": to_mm(cfg.POOL_PUMP_DIAMETER),
            "height_mm": to_mm(cfg.POOL_PUMP_HEIGHT),
        },
    )
    heater_x, heater_y = slab_x + cfg.POOL_EQUIPMENT_SLAB_LENGTH / 2, slab_y + cfg.POOL_EQUIPMENT_SLAB_WIDTH / 4
    builder.add_box(
        "pool-equipment",
        "PoolHeater",
        cfg.POOL_HEATER_LENGTH,
        cfg.POOL_HEATER_WIDTH,
        cfg.POOL_HEATER_HEIGHT,
        heater_x - cfg.POOL_HEATER_LENGTH / 2,
        heater_y - cfg.POOL_HEATER_WIDTH / 2,
        top_z,
        (0.25, 0.25, 0.25),
        parent_id="complex.pool_equipment.equipment_slab",
        properties={
            "complex_type": "pool_heater",
            "assembly_role": "equipment",
            "label": "Pool Heater",
            "dimensions_mm": f"{to_mm(cfg.POOL_HEATER_LENGTH)}x{to_mm(cfg.POOL_HEATER_WIDTH)}x{to_mm(cfg.POOL_HEATER_HEIGHT)}",
        },
    )
    filter_x, filter_y = slab_x + 3 * cfg.POOL_EQUIPMENT_SLAB_LENGTH / 4, slab_y + 3 * cfg.POOL_EQUIPMENT_SLAB_WIDTH / 4
    builder.add_cylinder(
        "pool-equipment",
        "PoolFilter",
        (filter_x, filter_y, top_z),
        (filter_x, filter_y, top_z + cfg.POOL_FILTER_HEIGHT),
        cfg.POOL_FILTER_DIAMETER / 2,
        (0.35, 0.35, 0.35),
        parent_id="complex.pool_equipment.equipment_slab",
        properties={
            "complex_type": "pool_filter",
            "assembly_role": "equipment",
            "label": "Pool Filter",
            "diameter_mm": to_mm(cfg.POOL_FILTER_DIAMETER),
            "height_mm": to_mm(cfg.POOL_FILTER_HEIGHT),
        },
    )
    plant_y = slab_y - cfg.FOOT
    plant_x = slab_x + cfg.POOL_EQUIPMENT_SLAB_LENGTH - cfg.SKIP_LAUREL_WIDTH / 2
    index = 1
    while plant_x >= pool_x + pool_length + rock_bed_width:
        builder.add_box(
            "site",
            f"PoolEquipmentSlabSouthSkipLaurel_{index:02d}",
            cfg.SKIP_LAUREL_WIDTH,
            cfg.SKIP_LAUREL_DEPTH,
            cfg.SKIP_LAUREL_HEIGHT,
            plant_x - cfg.SKIP_LAUREL_WIDTH / 2,
            plant_y - cfg.SKIP_LAUREL_DEPTH / 2,
            ZERO,
            TREE_GREEN,
            parent_id="complex.pool_equipment.equipment_slab",
            properties={
                "complex_type": "skip_laurel_shrub",
                "assembly_role": "landscape_planting",
                "label": f"Skip Laurel South {index:02d}",
                "spacing_mm": to_mm(cfg.SKIP_LAUREL_SPACING),
                "purpose": "screen_pool_equipment_from_south",
            },
        )
        plant_x -= cfg.SKIP_LAUREL_SPACING
        index += 1
