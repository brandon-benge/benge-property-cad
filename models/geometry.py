"""Reusable property-model geometry helpers; keep this module below 400 lines."""

from __future__ import annotations

import math

from python_cad_tools.units import Length, mm, to_mm

from models.shared import Point2


def capsule_curve_points(
    center_x: Length,
    center_y: Length,
    length: Length,
    width: Length,
    offset_from_edge: Length,
    spacing: Length,
    start_offset: Length,
) -> list[Point2]:
    """Generate planting points along the south half of a capsule curve."""
    cx, cy = to_mm(center_x), to_mm(center_y)
    radius = to_mm(width) / 2 + to_mm(offset_from_edge)
    west = cx - (to_mm(length) - to_mm(width)) / 2
    east = cx + (to_mm(length) - to_mm(width)) / 2
    points: list[Point2] = []
    distance = to_mm(start_offset)
    arc_length = math.pi / 2 * radius
    while distance < arc_length:
        angle = math.pi + distance / radius
        points.append((mm(west + radius * math.cos(angle)), mm(cy + radius * math.sin(angle))))
        distance += to_mm(spacing)
    straight = east - west
    distance_in_straight = distance - arc_length
    while distance_in_straight < straight:
        points.append((mm(west + distance_in_straight), mm(cy - radius)))
        distance_in_straight += to_mm(spacing)
    distance_in_east = distance_in_straight - straight
    while distance_in_east < arc_length:
        angle = 3 * math.pi / 2 + distance_in_east / radius
        points.append((mm(east + radius * math.cos(angle)), mm(cy + radius * math.sin(angle))))
        distance_in_east += to_mm(spacing)
    return points
