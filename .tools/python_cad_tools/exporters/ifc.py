"""IFC4 authoring from shared elements using deterministic identifiers."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.validate

from ..determinism import write_json
from ..exceptions import ExportError
from ..geometry import tessellate
from .base import selected_elements

IFC_NAMESPACE = uuid.UUID("8ef8d46f-f692-5a1f-9966-c498829777a9")


def global_id(stable_id: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(IFC_NAMESPACE, stable_id).hex)


class IfcExporter:
    name = "ifc"

    def export(self, model, output_dir: Path) -> list[Path]:
        target = output_dir / "ifc"
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{model.name}.ifc"
        file = ifcopenshell.file(schema="IFC4")
        origin = file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        z_axis = file.createIfcDirection((0.0, 0.0, 1.0))
        x_axis = file.createIfcDirection((1.0, 0.0, 0.0))
        world = file.createIfcAxis2Placement3D(origin, z_axis, x_axis)
        context = file.create_entity(
            "IfcGeometricRepresentationContext",
            ContextIdentifier="Model",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1e-5,
            WorldCoordinateSystem=world,
        )
        units = file.createIfcUnitAssignment(
            (
                file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE"),
                file.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
                file.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
            )
        )
        project = file.create_entity(
            "IfcProject",
            GlobalId=global_id(f"{model.id}.ifc.project"),
            Name=model.name,
            RepresentationContexts=[context],
            UnitsInContext=units,
        )
        site = _spatial(file, "IfcSite", f"{model.id}.ifc.site", "Default Site", None)
        building = _spatial(file, "IfcBuilding", f"{model.id}.ifc.building", "Default Building", site.ObjectPlacement)
        storey = _spatial(file, "IfcBuildingStorey", f"{model.id}.ifc.storey", "Default Storey", building.ObjectPlacement)
        file.createIfcRelAggregates(global_id(f"{model.id}.rel.project-site"), None, None, None, project, [site])
        file.createIfcRelAggregates(global_id(f"{model.id}.rel.site-building"), None, None, None, site, [building])
        file.createIfcRelAggregates(global_id(f"{model.id}.rel.building-storey"), None, None, None, building, [storey])

        products = []
        expected_ids: list[str] = []
        for element in selected_elements(model, "ifc", physical_only=True):
            if element.ifc_mapping.ifc_class is None:
                continue
            if element.ifc_mapping.ifc_class != "IfcBuildingElementProxy":
                raise ExportError(f"Unsupported starter IFC mapping: {element.ifc_mapping.ifc_class}")
            vertices, triangles = tessellate(element.geometry, 0.5, 0.25)
            points = file.createIfcCartesianPointList3D(vertices)
            face_set = file.createIfcTriangulatedFaceSet(
                points,
                None,
                True,
                [[index + 1 for index in triangle] for triangle in triangles],
                None,
            )
            representation = file.createIfcShapeRepresentation(context, "Body", "Tessellation", [face_set])
            shape = file.createIfcProductDefinitionShape(None, None, [representation])
            product = file.create_entity(
                "IfcBuildingElementProxy",
                GlobalId=global_id(element.id),
                Name=element.name,
                ObjectType=element.category,
                ObjectPlacement=_local_placement(file, storey.ObjectPlacement),
                Representation=shape,
                PredefinedType=element.ifc_mapping.predefined_type or "NOTDEFINED",
            )
            products.append(product)
            expected_ids.append(element.id)
            _add_properties(file, product, element)
            if element.material:
                material = file.createIfcMaterial(element.material.name, element.material.category, None)
                file.createIfcRelAssociatesMaterial(
                    global_id(f"{element.id}.material"), None, None, None, [product], material
                )
                _style_item(file, face_set, element.color_rgb or element.material.color_rgb)
        file.createIfcRelContainedInSpatialStructure(
            global_id(f"{model.id}.rel.storey-elements"), None, None, None, products, storey
        )
        file.write(path)
        reloaded = ifcopenshell.open(path)
        actual_ids = sorted(
            property_value(entity, "StableId")
            for entity in reloaded.by_type("IfcBuildingElementProxy")
        )
        if actual_ids != sorted(expected_ids):
            raise ExportError(f"IFC stable IDs did not round-trip: {actual_ids}")
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(reloaded, logger, express_rules=True)
        statements = list(logger.statements)
        fatal = [item for item in statements if item.get("level") in {"error", "critical"}]
        coordinate_values = [
            coordinate
            for point_list in reloaded.by_type("IfcCartesianPointList3D")
            for coordinate in point_list.CoordList
        ]
        if coordinate_values:
            ifc_bounds = [
                min(point[index] for point in coordinate_values) for index in range(3)
            ] + [max(point[index] for point in coordinate_values) for index in range(3)]
        else:
            ifc_bounds = [0.0] * 6
        report = write_json(
            target / "validation.json",
            {
                "schema": reloaded.schema,
                "valid": not fatal,
                "fatal_count": len(fatal),
                "issue_count": len(statements),
                "issues": [_json_safe(item) for item in statements],
                "bounds_mm": [round(value, 6) for value in ifc_bounds],
                "element_global_ids": {
                    entity.Name: entity.GlobalId
                    for entity in sorted(reloaded.by_type("IfcBuildingElementProxy"), key=lambda item: item.Name)
                },
            },
        )
        if fatal:
            raise ExportError(f"IfcOpenShell validation reported {len(fatal)} fatal issue(s); see {report}")
        return [path, report]


def _spatial(file, class_name: str, stable_id: str, name: str, parent_placement):
    return file.create_entity(
        class_name,
        GlobalId=global_id(stable_id),
        Name=name,
        ObjectPlacement=_local_placement(file, parent_placement),
        CompositionType="ELEMENT",
    )


def _local_placement(file, parent):
    point = file.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis = file.createIfcAxis2Placement3D(point, None, None)
    return file.createIfcLocalPlacement(parent, axis)


def _add_properties(file, product, element) -> None:
    values: dict[str, Any] = {
        "StableId": element.id,
        "Category": element.category,
        "SourceModule": element.source_module,
        "GeometryKind": element.geometry_kind,
    }
    for name in ("length_mm", "width_mm", "height_mm", "radius_mm"):
        value = getattr(element.dimensions, name)
        if value is not None:
            values[name.removesuffix("_mm").title() + "Mm"] = value
    properties = []
    for name, value in sorted(values.items()):
        wrapped = file.createIfcReal(float(value)) if isinstance(value, (float, int)) else file.createIfcLabel(str(value))
        properties.append(file.createIfcPropertySingleValue(name, None, wrapped, None))
    pset = file.createIfcPropertySet(global_id(f"{element.id}.pset"), None, "Pset_PythonCadDesign", None, properties)
    file.createIfcRelDefinesByProperties(global_id(f"{element.id}.pset-rel"), None, None, None, [product], pset)


def _style_item(file, item, color) -> None:
    rgb = file.createIfcColourRgb(None, *[float(channel) for channel in color])
    shading = file.createIfcSurfaceStyleShading(rgb, None)
    surface = file.createIfcSurfaceStyle(None, "BOTH", [shading])
    assignment = file.createIfcPresentationStyleAssignment([surface])
    file.createIfcStyledItem(item, [assignment], None)


def property_value(product, name: str) -> str:
    for relation in product.IsDefinedBy:
        definition = relation.RelatingPropertyDefinition
        if definition.is_a("IfcPropertySet") and definition.Name == "Pset_PythonCadDesign":
            for prop in definition.HasProperties:
                if prop.Name == name:
                    return str(prop.NominalValue.wrappedValue)
    raise ExportError(f"IFC product {product.GlobalId} lacks property {name}")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
