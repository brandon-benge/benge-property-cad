"""Shared DesignElement builder methods; keep this module below 400 lines."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.elements import DesignElement, Dimensions, IfcMapping, MaterialSpec, Placement
from python_cad_tools.geometry import box, cylinder_between, prism_between
from python_cad_tools.units import Length, to_mm

from models.shared import MATERIAL_REGISTRY, ZERO, Color, ModelState, Point3, slug
from models.shared import ifc_mapping as resolve_ifc_mapping


class ModelBuilder(ModelState):
    """Collect elements and apply the project's stable metadata contract."""

    def material(self, category: str, color: Color) -> MaterialSpec:
        key = (category, color)
        if key not in self.materials:
            rgb = "_".join(str(round(channel * 255)) for channel in color)
            info = MATERIAL_REGISTRY.get(key)
            name = info[0] if info else f"{category.title()} material"
            density = info[1] if info else None
            self.materials[key] = MaterialSpec(
                id=f"material.complex.{slug(category)}.{rgb}",
                name=name,
                category=category,
                color_rgb=color,
                density_kg_m3=density,
            )
        return self.materials[key]

    def add_shape(
        self,
        category: str,
        name: str,
        shape: Any,
        color: Color,
        dimensions: Dimensions,
        *,
        placement: Point3 = (ZERO, ZERO, ZERO),
        drawing_label: bool = False,
        properties: dict[str, Any] | None = None,
        physical: bool = True,
        parent_id: str | None = None,
        export_formats: set[str] | None = None,
        stable_id: str | None = None,
        ifc_mapping: IfcMapping | None = None,
    ) -> DesignElement:
        resolved_stable_id = stable_id or f"complex.{slug(category)}.{slug(name)}"
        values = dict(properties or {})
        if drawing_label:
            values["drawing_label"] = True
        element = DesignElement(
            id=resolved_stable_id,
            name=name,
            category=category,
            geometry=shape,
            geometry_kind="solid",
            placement=Placement((to_mm(placement[0]), to_mm(placement[1]), to_mm(placement[2]))),
            dimensions=dimensions,
            material=self.material(category, color),
            color_rgb=color,
            ifc_mapping=ifc_mapping or resolve_ifc_mapping(category, name),
            storey="Exterior Concept",
            tags={"file-template", slug(category)},
            properties=values,
            source_module="model",
            physical=physical,
            parent_id=parent_id,
            export_formats=set(export_formats or {"step", "ifc", "glb", "drawings", "quantities"}),
        )
        self.elements.append(element)
        return element

    def add_box(
        self,
        category: str,
        name: str,
        length: Length,
        depth: Length,
        height: Length,
        x: Length,
        y: Length,
        z: Length,
        color: Color,
        **kwargs: Any,
    ) -> DesignElement:
        return self.add_shape(
            category,
            name,
            box(length, depth, height, origin=(x, y, z)),
            color,
            Dimensions(to_mm(length), to_mm(depth), to_mm(height)),
            placement=(x, y, z),
            **kwargs,
        )

    def add_cylinder(
        self,
        category: str,
        name: str,
        start: Point3,
        end: Point3,
        radius: Length,
        color: Color,
        **kwargs: Any,
    ) -> DesignElement:
        length = math.dist(tuple(to_mm(value) for value in start), tuple(to_mm(value) for value in end))
        return self.add_shape(
            category,
            name,
            cylinder_between(start, end, radius),
            color,
            Dimensions(length_mm=length, radius_mm=to_mm(radius)),
            placement=start,
            **kwargs,
        )

    def add_prism(
        self,
        category: str,
        name: str,
        start: Point3,
        end: Point3,
        width: Length,
        height: Length,
        color: Color,
        **kwargs: Any,
    ) -> DesignElement:
        length = math.dist(tuple(to_mm(value) for value in start), tuple(to_mm(value) for value in end))
        return self.add_shape(
            category,
            name,
            prism_between(start, end, width, height),
            color,
            Dimensions(length, to_mm(width), to_mm(height)),
            placement=start,
            **kwargs,
        )
