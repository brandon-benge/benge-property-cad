"""Project-owned starter design source; this builds the shared model exactly once."""

from __future__ import annotations

from python_cad_tools.context import BuildContext
from python_cad_tools.elements import (
    DesignElement,
    DesignModel,
    Dimensions,
    IfcMapping,
    MaterialSpec,
    Placement,
    ValidationIssue,
)
from python_cad_tools.geometry import bounds, box, reference_line
from python_cad_tools.units import INCH, to_mm

import config as cfg


def build_model(context: BuildContext) -> DesignModel:
    base_material = MaterialSpec("material.starter.base", "Starter Base Material", "example", cfg.BASE_COLOR)
    primary_material = MaterialSpec("material.starter.primary", "Starter Primary Material", "example", cfg.PRIMARY_COLOR)
    block_x = (cfg.BASE_LENGTH - cfg.BLOCK_LENGTH) / 2
    block_y = (cfg.BASE_WIDTH - cfg.BLOCK_WIDTH) / 2
    block_z = cfg.BASE_THICKNESS
    axis_x_z = cfg.BASE_THICKNESS + cfg.BLOCK_HEIGHT + 6 * INCH
    axis_y_z = cfg.BASE_THICKNESS + cfg.BLOCK_HEIGHT + 10 * INCH
    zero = 0 * cfg.MM
    elements = [
        DesignElement(
            id="starter.base_plate", name="Base Plate", category="physical-example",
            geometry=box(cfg.BASE_LENGTH, cfg.BASE_WIDTH, cfg.BASE_THICKNESS, origin=(zero, zero, zero)),
            geometry_kind="solid", dimensions=Dimensions(to_mm(cfg.BASE_LENGTH), to_mm(cfg.BASE_WIDTH), to_mm(cfg.BASE_THICKNESS)),
            material=base_material, color_rgb=cfg.BASE_COLOR,
            ifc_mapping=IfcMapping("IfcBuildingElementProxy", "NOTDEFINED"), storey="Default Storey",
            tags={"starter", "physical"}, properties={"quantity_provenance": "exact_geometry"},
        ),
        DesignElement(
            id="starter.primary_block", name="Primary Block", category="physical-example",
            geometry=box(cfg.BLOCK_LENGTH, cfg.BLOCK_WIDTH, cfg.BLOCK_HEIGHT, origin=(block_x, block_y, block_z)),
            geometry_kind="solid", placement=Placement((to_mm(block_x), to_mm(block_y), to_mm(block_z))),
            dimensions=Dimensions(to_mm(cfg.BLOCK_LENGTH), to_mm(cfg.BLOCK_WIDTH), to_mm(cfg.BLOCK_HEIGHT)),
            material=primary_material, color_rgb=cfg.PRIMARY_COLOR,
            ifc_mapping=IfcMapping("IfcBuildingElementProxy", "NOTDEFINED"), storey="Default Storey",
            tags={"starter", "physical"}, properties={"quantity_provenance": "exact_geometry"},
        ),
        DesignElement(
            id="reference.axis_x", name="X Reference Axis", category="reference-axis",
            geometry=reference_line((zero, cfg.BASE_WIDTH / 2, axis_x_z), (cfg.BASE_LENGTH, cfg.BASE_WIDTH / 2, axis_x_z)),
            geometry_kind="reference", placement=Placement((0.0, to_mm(cfg.BASE_WIDTH / 2), to_mm(axis_x_z))),
            dimensions=Dimensions(length_mm=to_mm(cfg.BASE_LENGTH), radius_mm=to_mm(0.75 * INCH)),
            color_rgb=cfg.ACCENT_COLOR, ifc_mapping=IfcMapping(None, exclude_reason="non-physical reference geometry"),
            tags={"starter", "reference", "axis-x"}, export_formats={"drawings"}, physical=False,
        ),
        DesignElement(
            id="reference.axis_y", name="Y Reference Axis", category="reference-axis",
            geometry=reference_line((cfg.BASE_LENGTH / 2, zero, axis_y_z), (cfg.BASE_LENGTH / 2, cfg.BASE_WIDTH, axis_y_z)),
            geometry_kind="reference", placement=Placement((to_mm(cfg.BASE_LENGTH / 2), 0.0, to_mm(axis_y_z))),
            dimensions=Dimensions(length_mm=to_mm(cfg.BASE_WIDTH), radius_mm=to_mm(0.75 * INCH)),
            color_rgb=cfg.ACCENT_COLOR, ifc_mapping=IfcMapping(None, exclude_reason="non-physical reference geometry"),
            tags={"starter", "reference", "axis-y"}, export_formats={"drawings"}, physical=False,
        ),
    ]
    return DesignModel(
        id="starter.project_model", name=cfg.PROJECT_NAME, elements=elements,
        metadata={"fixture": "legacy starter migration", "authoritative_source": "model.py"}, validators=[_validate_starter],
    )


def _validate_starter(model: DesignModel) -> list[ValidationIssue]:
    base = model.get("starter.base_plate")
    block = model.get("starter.primary_block")
    base_bounds = bounds(base.geometry)
    block_bounds = bounds(block.geometry)
    checks = {
        "block-centered-x": abs(block_bounds[0] - (to_mm(cfg.BASE_LENGTH) - to_mm(cfg.BLOCK_LENGTH)) / 2) <= 1e-6,
        "block-centered-y": abs(block_bounds[1] - (to_mm(cfg.BASE_WIDTH) - to_mm(cfg.BLOCK_WIDTH)) / 2) <= 1e-6,
        "block-rests-on-base": abs(block_bounds[2] - base_bounds[5]) <= 1e-6,
        "base-color": base.color_rgb == cfg.BASE_COLOR,
        "block-color": block.color_rgb == cfg.PRIMARY_COLOR,
        "reference-not-physical": all(not model.get(stable_id).physical for stable_id in ("reference.axis_x", "reference.axis_y")),
    }
    return [
        ValidationIssue("error", f"starter-{code}", f"Starter migration invariant failed: {code}")
        for code, passed in checks.items() if not passed
    ]
