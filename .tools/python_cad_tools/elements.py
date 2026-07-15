"""Typed intermediate model shared by every exporter."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Literal

Color = tuple[float, float, float]
GeometryKind = Literal["solid", "shell", "wire", "edge", "reference"]


@dataclass(frozen=True, slots=True)
class MaterialSpec:
    id: str
    name: str
    category: str
    color_rgb: Color
    density_kg_m3: float | None = None
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Placement:
    translation_mm: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_deg_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(frozen=True, slots=True)
class Dimensions:
    length_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    radius_mm: float | None = None
    extras: dict[str, float] = field(default_factory=dict)

    def values(self) -> tuple[float, ...]:
        primary = (self.length_mm, self.width_mm, self.height_mm, self.radius_mm)
        return tuple(value for value in primary if value is not None) + tuple(
            self.extras[key] for key in sorted(self.extras)
        )


@dataclass(frozen=True, slots=True)
class IfcMapping:
    ifc_class: str | None
    predefined_type: str | None = None
    exclude_reason: str | None = None


@dataclass(slots=True)
class DesignElement:
    id: str
    name: str
    category: str
    geometry: Any
    geometry_kind: GeometryKind
    placement: Placement = field(default_factory=Placement)
    dimensions: Dimensions = field(default_factory=Dimensions)
    material: MaterialSpec | None = None
    color_rgb: Color | None = None
    ifc_mapping: IfcMapping = field(default_factory=lambda: IfcMapping(None, exclude_reason="not mapped"))
    storey: str | None = None
    tags: set[str] = field(default_factory=set)
    properties: dict[str, Any] = field(default_factory=dict)
    children: list[DesignElement] = field(default_factory=list)
    visible: bool = True
    export_formats: set[str] = field(default_factory=lambda: {"step", "ifc", "glb", "drawings", "quantities"})
    source_module: str = "model"
    physical: bool = True
    parent_id: str | None = None

    def walk(self) -> Iterator[DesignElement]:
        yield self
        for child in sorted(self.children, key=lambda item: item.id):
            yield from child.walk()


@dataclass(slots=True)
class DesignModel:
    id: str
    name: str
    elements: list[DesignElement]
    coordinate_system: str = "right-handed; X right, Y depth/away, Z up; millimetres"
    metadata: dict[str, Any] = field(default_factory=dict)
    validators: list[Any] = field(default_factory=list)

    def walk(self) -> Iterator[DesignElement]:
        for element in sorted(self.elements, key=lambda item: item.id):
            yield from element.walk()

    def get(self, stable_id: str) -> DesignElement:
        for element in self.walk():
            if element.id == stable_id:
                return element
        raise KeyError(stable_id)


@dataclass(frozen=True, slots=True)
class QuantityRecord:
    element_id: str
    category: str
    material_id: str | None
    count: int
    area_mm2: float | None
    volume_mm3: float | None
    mass_kg: float | None
    provenance: str


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    element_id: str | None = None
