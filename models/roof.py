"""House mass, covered-deck roof, and roof-mounted features."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from build123d import Plane, Polyline, extrude, make_face
from python_cad_tools.elements import Dimensions
from python_cad_tools.units import INCH, Length, mm, to_mm

from models.shared import CUT_MARGIN, ZERO, Point2


@dataclass(frozen=True)
class RoofPhaseResult:
    roof_back_z: Length
    roof_front_z: Length
    upper_stair_start: Point2
    upper_stair_end: Point2


def add_roof(builder: Any, cfg: Any) -> RoofPhaseResult:
    """Append the house and roof phase and return values used by later phases."""
    sliding_door_x = 3 * cfg.FOOT + 6 * INCH
    from python_cad_tools.geometry import box

    house_mass = box(cfg.HOUSE_WIDTH, cfg.HOUSE_DEPTH, cfg.HOUSE_HEIGHT, origin=(ZERO, ZERO, ZERO))
    sliding_door_opening = box(
        cfg.DOOR_WIDTH + CUT_MARGIN,
        cfg.HOUSE_DEPTH + CUT_MARGIN,
        cfg.DOOR_HEIGHT + CUT_MARGIN,
        origin=(sliding_door_x - CUT_MARGIN / 2, ZERO - CUT_MARGIN / 2, cfg.UPPER_DECK_ELEVATION - CUT_MARGIN / 2),
    )
    builder.add_shape(
        "house",
        "HouseMass",
        house_mass.cut(sliding_door_opening),
        cfg.HOUSE_COLOR,
        Dimensions(to_mm(cfg.HOUSE_WIDTH), to_mm(cfg.HOUSE_DEPTH), to_mm(cfg.HOUSE_HEIGHT)),
        drawing_label=True,
        properties={
            "complex_type": "house_mass",
            "assembly_role": "exterior_wall_with_openings",
            "opening_for": "complex.feature.sliding_door",
        },
    )

    roof_x = -cfg.ROOF_OVERHANG
    roof_front_y = -cfg.UPPER_DECK_DEPTH - cfg.ROOF_OVERHANG
    roof_back_y = cfg.ROOF_OVERHANG
    roof_w = cfg.UPPER_DECK_WIDTH + 2 * cfg.ROOF_OVERHANG
    roof_back_z = cfg.UPPER_DECK_ELEVATION + cfg.ROOF_HEIGHT_ABOVE_UPPER
    if cfg.ROOF_STYLE != "shed":
        raise ValueError(f"Unsupported ROOF_STYLE: {cfg.ROOF_STYLE!r}; expected 'shed'")
    roof_front_z = roof_back_z - cfg.ROOF_SLOPE_DROP
    builder.add_prism(
        "roof",
        "UpperDeckRoofCover",
        (roof_x, roof_back_y, roof_back_z),
        (roof_x, roof_front_y, roof_front_z),
        roof_w,
        cfg.ROOF_THICKNESS,
        (0.18, 0.20, 0.22),
    )
    if cfg.ROOF_ATTACH_TO_HOUSE:
        builder.add_box(
            "roof-framing",
            "RoofHouseLedger",
            roof_w,
            cfg.ROOF_RAFTER_WIDTH,
            cfg.ROOF_RAFTER_HEIGHT,
            roof_x,
            -cfg.ROOF_RAFTER_WIDTH / 2,
            roof_back_z - cfg.ROOF_RAFTER_HEIGHT,
            (0.92, 0.92, 0.90),
            drawing_label=True,
        )

    rafter_x = roof_x + cfg.ROOF_RAFTER_SPACING
    rafter_index = 1
    while rafter_x < roof_x + roof_w - cfg.ROOF_RAFTER_WIDTH:
        builder.add_prism(
            "roof-framing",
            f"RoofRafter_{rafter_index:02d}",
            (rafter_x, roof_back_y, roof_back_z - cfg.ROOF_THICKNESS),
            (rafter_x, roof_front_y, roof_front_z - cfg.ROOF_THICKNESS),
            cfg.ROOF_RAFTER_WIDTH,
            cfg.ROOF_RAFTER_HEIGHT,
            (0.92, 0.92, 0.90),
        )
        rafter_x += cfg.ROOF_RAFTER_SPACING
        rafter_index += 1
    builder.add_box(
        "roof-framing",
        "RoofFrontBeam",
        roof_w,
        cfg.BEAM_WIDTH,
        cfg.BEAM_HEIGHT,
        roof_x,
        roof_front_y,
        roof_front_z - cfg.ROOF_THICKNESS - cfg.BEAM_HEIGHT,
        cfg.RAILING_COLOR,
    )
    builder.add_box(
        "roof",
        "RoofFrontFascia",
        roof_w,
        cfg.ROOF_RAFTER_WIDTH,
        cfg.ROOF_FASCIA_HEIGHT,
        roof_x,
        roof_front_y,
        roof_front_z - cfg.ROOF_FASCIA_HEIGHT,
        cfg.RAILING_COLOR,
    )
    for name, x in (("RoofLeftFascia", roof_x), ("RoofRightFascia", roof_x + roof_w)):
        builder.add_prism(
            "roof",
            name,
            (x, roof_back_y, roof_back_z),
            (x, roof_front_y, roof_front_z),
            cfg.ROOF_RAFTER_WIDTH,
            cfg.ROOF_FASCIA_HEIGHT,
            cfg.RAILING_COLOR,
        )

    post = 8 * INCH
    front_post_height = roof_front_z - cfg.ROOF_THICKNESS - cfg.BEAM_HEIGHT - cfg.UPPER_DECK_ELEVATION
    front_post_count = max(2, int(cfg.ROOF_FRONT_POSTS))
    upper_stair_steps = max(
        1, math.ceil(abs(to_mm(cfg.UPPER_DECK_ELEVATION - cfg.LOWER_DECK_ELEVATION)) / to_mm(cfg.MAX_RISER))
    )
    upper_stair_start = (cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH)
    upper_stair_end = (
        cfg.UPPER_DECK_WIDTH + upper_stair_steps * cfg.TREAD_DEPTH,
        -cfg.UPPER_DECK_DEPTH - upper_stair_steps * cfg.TREAD_DEPTH,
    )
    dx = to_mm(upper_stair_end[0] - upper_stair_start[0])
    dy = to_mm(upper_stair_end[1] - upper_stair_start[1])
    run = math.hypot(dx, dy)
    px, py = -dy / run, dx / run
    offset = to_mm(cfg.STAIR_WIDTH) / 2
    upper_stair_left_top = (
        mm(to_mm(upper_stair_start[0]) - px * offset),
        mm(to_mm(upper_stair_start[1]) - py * offset),
    )
    for index in range(front_post_count):
        if index == front_post_count - 1:
            post_x, post_y = upper_stair_left_top
        else:
            ratio = index / (front_post_count - 1)
            post_x, post_y = cfg.UPPER_DECK_WIDTH * ratio, -cfg.UPPER_DECK_DEPTH
        builder.add_box(
            "roof-framing",
            f"RoofFrontPost_{index + 1}",
            post,
            post,
            front_post_height,
            post_x,
            post_y,
            cfg.UPPER_DECK_ELEVATION,
            (0.92, 0.92, 0.90),
        )
    if not cfg.ROOF_ATTACH_TO_HOUSE:
        rear_post_height = roof_back_z - cfg.ROOF_THICKNESS - cfg.UPPER_DECK_ELEVATION
        for index, post_x in enumerate((ZERO, cfg.UPPER_DECK_WIDTH - post), 1):
            builder.add_box(
                "roof-framing",
                f"RoofRearPost_{index}",
                post,
                post,
                rear_post_height,
                post_x,
                -post,
                cfg.UPPER_DECK_ELEVATION,
                (0.92, 0.92, 0.90),
            )

    fan_x = cfg.UPPER_DECK_WIDTH / 2
    fan_y = -cfg.UPPER_DECK_DEPTH / 2
    fan_z = (roof_back_z + roof_front_z) / 2 - 28 * INCH
    builder.add_cylinder(
        "feature",
        "CoveredDeckFanDownrod",
        (fan_x, fan_y, (roof_back_z + roof_front_z) / 2 - cfg.ROOF_RAFTER_HEIGHT),
        (fan_x, fan_y, fan_z),
        1.25 * INCH,
        cfg.RAILING_COLOR,
    )
    builder.add_cylinder(
        "feature",
        "CoveredDeckFanMotor",
        (fan_x, fan_y, fan_z - 3 * INCH),
        (fan_x, fan_y, fan_z + 3 * INCH),
        7 * INCH,
        cfg.RAILING_COLOR,
    )
    blade = cfg.FAN_DIAMETER / 2

    def add_fan_blade(name: str, direction_x: float, direction_y: float) -> None:
        hub_radius = 7 * INCH
        root_half_width = cfg.FAN_BLADE_WIDTH * 0.32
        tip_half_width = cfg.FAN_BLADE_WIDTH / 2
        px, py = -direction_y, direction_x
        root_x = to_mm(fan_x) + direction_x * to_mm(hub_radius)
        root_y = to_mm(fan_y) + direction_y * to_mm(hub_radius)
        tip_x = to_mm(fan_x) + direction_x * to_mm(blade)
        tip_y = to_mm(fan_y) + direction_y * to_mm(blade)
        profile = Plane.XY * Polyline(
            (root_x + px * to_mm(root_half_width), root_y + py * to_mm(root_half_width)),
            (tip_x + px * to_mm(tip_half_width), tip_y + py * to_mm(tip_half_width)),
            (tip_x - px * to_mm(tip_half_width), tip_y - py * to_mm(tip_half_width)),
            (root_x - px * to_mm(root_half_width), root_y - py * to_mm(root_half_width)),
            close=True,
        )
        shape = extrude(make_face(profile), amount=to_mm(INCH)).solid().translate((0.0, 0.0, to_mm(fan_z)))
        builder.add_shape(
            "feature",
            name,
            shape,
            cfg.SKIRTING_COLOR,
            Dimensions(to_mm(blade), to_mm(cfg.FAN_BLADE_WIDTH), to_mm(INCH)),
            placement=(fan_x, fan_y, fan_z),
            properties={"complex_type": "tapered_ceiling_fan_blade", "assembly_role": "fan_blade"},
        )

    for name, direction in (
        ("CoveredDeckFanBlade_X_Pos", (1.0, 0.0)),
        ("CoveredDeckFanBlade_X_Neg", (-1.0, 0.0)),
        ("CoveredDeckFanBlade_Y_Pos", (0.0, 1.0)),
        ("CoveredDeckFanBlade_Y_Neg", (0.0, -1.0)),
    ):
        add_fan_blade(name, *direction)
    return RoofPhaseResult(roof_back_z, roof_front_z, upper_stair_start, upper_stair_end)
