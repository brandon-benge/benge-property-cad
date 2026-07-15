"""Reusable build123d geometry adapters using explicit millimetre inputs."""

from __future__ import annotations

from math import sqrt
from typing import Any

from build123d import Align, Box, Edge, Face, Location, Plane, Solid, Vector, Wire

from .units import Length, to_mm


def box(
    length: Length,
    width: Length,
    height: Length,
    *,
    origin: tuple[Length, Length, Length] | None = None,
) -> Solid:
    shape = Box(
        to_mm(length),
        to_mm(width),
        to_mm(height),
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    solid = shape.solid()
    if solid is None:
        raise RuntimeError("build123d Box did not produce a solid")
    if origin is not None:
        solid = solid.moved(Location(tuple(to_mm(value) for value in origin)))
    return solid


def reference_line(
    start: tuple[Length, Length, Length],
    end: tuple[Length, Length, Length],
) -> Edge:
    return Edge.make_line(
        tuple(to_mm(value) for value in start),
        tuple(to_mm(value) for value in end),
    )


def cylinder_between(
    start: tuple[Length, Length, Length],
    end: tuple[Length, Length, Length],
    radius: Length,
) -> Solid:
    start_mm = tuple(to_mm(value) for value in start)
    end_mm = tuple(to_mm(value) for value in end)
    direction = tuple(end_mm[index] - start_mm[index] for index in range(3))
    height = sqrt(sum(value * value for value in direction))
    if height <= 0:
        raise ValueError("Cylinder endpoints must be distinct")
    return Solid.make_cylinder(to_mm(radius), height, Plane(origin=start_mm, z_dir=direction))


def prism_between(
    start: tuple[Length, Length, Length],
    end: tuple[Length, Length, Length],
    width: Length,
    height: Length,
) -> Solid:
    start_mm = tuple(to_mm(value) for value in start)
    end_mm = tuple(to_mm(value) for value in end)
    direction = tuple(end_mm[index] - start_mm[index] for index in range(3))
    length = sqrt(sum(value * value for value in direction))
    if length <= 0:
        raise ValueError("Prism endpoints must be distinct")
    x_dir = tuple(value / length for value in direction)
    horizontal = sqrt(x_dir[0] ** 2 + x_dir[1] ** 2)
    if horizontal <= 1e-12:
        z_dir = (1.0, 0.0, 0.0)
    else:
        z_dir = (-x_dir[0] * x_dir[2] / horizontal, -x_dir[1] * x_dir[2] / horizontal, horizontal)
    return Solid.make_box(length, to_mm(width), to_mm(height), Plane(origin=start_mm, x_dir=x_dir, z_dir=z_dir))


def sloped_pool(
    length: Length,
    width: Length,
    shallow_depth: Length,
    deep_depth: Length,
    *,
    origin: tuple[Length, Length, Length],
) -> Solid:
    length_mm = to_mm(length)
    width_mm = to_mm(width)
    shallow_mm = to_mm(shallow_depth)
    deep_mm = to_mm(deep_depth)
    origin_mm = tuple(to_mm(value) for value in origin)
    profile = Wire.make_polygon(
        [
            origin_mm,
            (origin_mm[0] + length_mm, origin_mm[1], origin_mm[2]),
            (origin_mm[0] + length_mm, origin_mm[1], origin_mm[2] - deep_mm),
            (origin_mm[0], origin_mm[1], origin_mm[2] - shallow_mm),
        ],
        close=True,
    )
    return Solid.extrude(Face(profile), Vector(0, width_mm, 0))


def bounds(shape: Any) -> tuple[float, float, float, float, float, float]:
    box_value = shape.bounding_box()
    return (
        float(box_value.min.X),
        float(box_value.min.Y),
        float(box_value.min.Z),
        float(box_value.max.X),
        float(box_value.max.Y),
        float(box_value.max.Z),
    )


def combined_bounds(shapes: list[Any]) -> tuple[float, float, float, float, float, float]:
    values = [bounds(shape) for shape in shapes]
    if not values:
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return (
        min(value[0] for value in values),
        min(value[1] for value in values),
        min(value[2] for value in values),
        max(value[3] for value in values),
        max(value[4] for value in values),
        max(value[5] for value in values),
    )


def tessellate(shape: Any, linear_deflection: float, angular_deflection: float) -> tuple[list[list[float]], list[list[int]]]:
    vertices, triangles = shape.tessellate(linear_deflection, angular_deflection)
    points = [[float(vertex.X), float(vertex.Y), float(vertex.Z)] for vertex in vertices]
    faces = [[int(index) for index in triangle] for triangle in triangles]
    return points, faces


def is_valid_solid(shape: Any) -> bool:
    return isinstance(shape, Solid) and bool(shape.is_valid) and float(shape.volume) > 0


def diagonal(bounds_value: tuple[float, float, float, float, float, float]) -> float:
    return sqrt(sum((bounds_value[index + 3] - bounds_value[index]) ** 2 for index in range(3)))
