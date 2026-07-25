"""Sections 12.4, 12.6: Programmatic build and final artifact reconciliation.

All tests share a single module-scoped full-format build (~85 s setup).
With pytest-xdist --dist loadscope, this file runs on one worker in parallel
with other build test files.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import ifcopenshell
import pytest
from build123d import import_step
from conftest import _cli
from ezdxf.filemanagement import readfile
from pypdf import PdfReader
from python_cad_tools.build import BuildOptions, BuildResult, ValidationOptions, build_project, validate_project

pytestmark = [pytest.mark.integration]

ANNOTATION_IDS = {
    "file.annotation.section.a301",
    "file.annotation.elevation.a201",
    "file.annotation.elevation.a202",
    "file.annotation.schedule.openings",
}


# ── Module-scoped full build (one build for all artifact tests) ──────────────


@pytest.fixture(scope="module")
def build_result(repo_root: Path, tmp_path_factory: pytest.TempPathFactory) -> BuildResult:
    """Full-format build, created once for this module."""
    dest = tmp_path_factory.mktemp("artifacts_build")
    from conftest import _copy_project

    _copy_project(repo_root, dest)
    return build_project(BuildOptions(project_root=dest))


@pytest.fixture(scope="module")
def built_output(build_result: BuildResult) -> Path:
    return build_result.output_root


@pytest.fixture(scope="module")
def build_manifest(built_output: Path) -> dict:
    return json.loads((built_output / "manifests" / "build-manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def design_manifest(built_output: Path) -> dict:
    return json.loads((built_output / "manifests" / "design-manifest.json").read_text(encoding="utf-8"))


# ── Helpers ──────────────────────────────────────────────────────────────────


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ifc_entities_by_stable_id(elements) -> dict[str, Any]:
    entities_by_id: dict[str, Any] = {}
    for entity in elements:
        for rel_def in entity.IsDefinedBy:
            if rel_def.is_a("IfcRelDefinesByProperties"):
                for prop in rel_def.RelatingPropertyDefinition.HasProperties:
                    if prop.Name == "StableId":
                        entities_by_id[str(prop.NominalValue.wrappedValue)] = entity
    return entities_by_id


def _ifc_stable_ids(elements) -> set[str]:
    ids: set[str] = set()
    for entity in elements:
        for rel_def in entity.IsDefinedBy:
            if rel_def.is_a("IfcRelDefinesByProperties"):
                for prop in rel_def.RelatingPropertyDefinition.HasProperties:
                    if prop.Name == "StableId":
                        ids.add(str(prop.NominalValue.wrappedValue))
    return ids


# ── 12.4 Programmatic end-to-end build ───────────────────────────────────────


def test_validate_project_no_output(copied_project) -> None:
    options = ValidationOptions(project_root=copied_project)
    report = validate_project(options)
    assert report.ok, f"Validation failed: {report.issues}"
    gen = copied_project / "generated"
    assert not gen.exists() or not list(gen.rglob("*"))


def test_build_project_returns_build_result(build_result) -> None:
    assert isinstance(build_result.design_semantic_hash, str) and len(build_result.design_semantic_hash) == 64
    bm = _load_json(build_result.output_root / "manifests" / "build-manifest.json")
    assert bm["validation"]["status"] == "passed"


def test_build_result_paths_point_to_final_output(build_manifest, built_output) -> None:
    for entry in build_manifest["artifacts"]:
        path = built_output / entry["path"]
        assert path.is_file(), f"Artifact not found: {path}"
        assert str(path).startswith(str(built_output))


def test_build_annotations_complete_before_return(built_output) -> None:
    ann_manifest = built_output / "drawings" / "annotation-manifest.json"
    assert ann_manifest.is_file(), f"Missing annotation manifest at {ann_manifest}"
    annotations = _load_json(ann_manifest)
    assert annotations["provider_id"] == "file.template.annotations"
    ann_ids = {ann["id"] for ann in annotations["annotations"]}
    assert ann_ids >= ANNOTATION_IDS


def test_build_full_default_formats(built_output) -> None:
    for fmt in ("step", "ifc", "glb", "drawings", "quantities"):
        assert (built_output / fmt).exists(), f"Missing format directory: {fmt}"


def test_cli_verify(built_output) -> None:
    """CLI verify uses the module build's project root."""
    result = _cli("verify", cwd=built_output.parent)
    assert result.returncode == 0, f"CLI verify failed: {result.stderr}"


# ── 12.6 Final artifact reconciliation ──────────────────────────────────────


def test_artifact_manifest_schema_ids(build_manifest, design_manifest) -> None:
    assert "build-manifest" in build_manifest.get("schema_id", "")
    assert "design-manifest" in design_manifest.get("schema_id", "")


def test_artifact_integrity(built_output, build_manifest) -> None:
    for entry in build_manifest["artifacts"]:
        path = built_output / entry["path"]
        if not path.is_file():
            if path.name == ".gitkeep":
                continue
            raise AssertionError(f"Missing artifact: {path}")
        actual_size = path.stat().st_size
        assert actual_size == entry["size"], f"Size mismatch for {entry['path']}: {actual_size} != {entry['size']}"
        actual_sha = _sha256(path)
        assert actual_sha == entry["sha256"], f"SHA-256 mismatch for {entry['path']}"


def test_artifact_stable_artifact_set_hash(build_manifest) -> None:
    assert isinstance(build_manifest.get("stable_artifact_set_hash"), str)
    assert len(build_manifest["stable_artifact_set_hash"]) == 64


def test_step_reload(built_output) -> None:
    step_path = built_output / "step" / "FileTemplate.step"
    validation = _load_json(built_output / "step" / "validation.json")
    assert validation["valid"] is True
    solids = import_step(step_path).solids()
    design = _load_json(built_output / "manifests" / "design-manifest.json")
    physical_ids = {e["id"] for e in design["elements"] if e["physical"]}
    assert len(solids) == len(physical_ids)


def test_ifc_parse_and_reconcile(built_output) -> None:
    ifc = ifcopenshell.open(built_output / "ifc" / "FileTemplate.ifc")
    ifc_validation = _load_json(built_output / "ifc" / "validation.json")
    assert ifc_validation["valid"] is True
    elements = ifc.by_type("IfcElement")
    assert len(elements) > 0
    design = _load_json(built_output / "manifests" / "design-manifest.json")
    physical_ids = {e["id"] for e in design["elements"] if e["physical"]}
    ifc_ids = _ifc_stable_ids(elements)
    assert ifc_ids == physical_ids, (
        f"IFC IDs differ: {len(physical_ids - ifc_ids)} missing, {len(ifc_ids - physical_ids)} extra"
    )

    entities_by_id = _ifc_entities_by_stable_id(elements)

    # Manual-reference snapshot. Agents must not auto-update this dict.
    # Only a human updates it when the model's semantic IFC mapping intent changes.
    expected_mappings = {
        "complex.deck_board.upper_deck_board_01": ("IfcSlab", "FLOOR"),
        "complex.structure.hot_tub_platform": ("IfcSlab", "BASESLAB"),
        "complex.roof_framing.roof_rafter_01": ("IfcMember", "RAFTER"),
        "complex.stair.upper_straight_tread_01": ("IfcMember", "PLATE"),
        "complex.feature.sliding_door_frame_left": ("IfcMember", "MULLION"),
        "complex.railing.upper_straight_left_handrail": ("IfcRailing", "GUARDRAIL"),
        "complex.site.shed_access_fence": ("IfcRailing", "BALUSTRADE"),
        "complex.site.property_line_solid_fence": ("IfcRailing", "BALUSTRADE"),
        "complex.roof.upper_deck_roof_cover": ("IfcRoof", "SHED_ROOF"),
        "complex.shed.shed_roof_left_slope": ("IfcRoof", "GABLE_ROOF"),
        "complex.feature.sliding_door": ("IfcDoor", "DOOR"),
        "complex.shed.shed_front_double_door": ("IfcDoor", "DOOR"),
        "complex.house.house_mass": ("IfcWall", "STANDARD"),
        "complex.fireplace.fireplace_masonry_body": ("IfcWall", "STANDARD"),
        "complex.deck_framing.upper_front_beam": ("IfcBeam", "BEAM"),
        "complex.deck_framing.upper_support_post_01": ("IfcColumn", "COLUMN"),
        "complex.skirting.upper_deck_front_skirt": ("IfcCovering", "SKIRTINGBOARD"),
        "complex.fireplace.fireplace_chimney_cap": ("IfcCovering", "ROOFING"),
        "complex.skirting.upper_deck_front_skirt_light_01": ("IfcLightFixture", "POINTSOURCE"),
        "complex.outdoor_kitchen.outdoor_kitchen_sink_basin": ("IfcSanitaryTerminal", "SINK"),
        "complex.outdoor_kitchen.outdoor_kitchen_cabinet_run": ("IfcFurniture", "USERDEFINED"),
    }
    for stable_id, (ifc_class, predefined_type) in expected_mappings.items():
        entity = entities_by_id[stable_id]
        assert entity.is_a() == ifc_class, f"{stable_id}: expected {ifc_class}, got {entity.is_a()}"
        assert entity.PredefinedType == predefined_type, (
            f"{stable_id}: expected {predefined_type}, got {entity.PredefinedType}"
        )


def test_ifc_proxy_elements_use_accurate_predefined_types(built_output) -> None:
    ifc = ifcopenshell.open(built_output / "ifc" / "FileTemplate.ifc")
    elements = ifc.by_type("IfcBuildingElementProxy")
    assert len(elements) > 0
    entities_by_id = _ifc_entities_by_stable_id(elements)
    valid_proxy_types = {"ELEMENT", "PROVISIONFORVOID"}
    for stable_id, entity in entities_by_id.items():
        predefined_type = entity.PredefinedType
        assert predefined_type in valid_proxy_types, (
            f"{stable_id}: IfcBuildingElementProxy must use one of {valid_proxy_types}, got {predefined_type!r}"
        )


def test_ifc_no_notdefined_predefined_types(built_output) -> None:
    ifc = ifcopenshell.open(built_output / "ifc" / "FileTemplate.ifc")
    elements = ifc.by_type("IfcElement")
    entities_by_id = _ifc_entities_by_stable_id(elements)
    for stable_id, entity in entities_by_id.items():
        predefined_type = entity.PredefinedType
        assert predefined_type != "NOTDEFINED", f"{stable_id}: predefined type must not be NOTDEFINED"


def test_glb_manifest(built_output) -> None:
    glb = _load_json(built_output / "glb" / "manifest.json")
    design = _load_json(built_output / "manifests" / "design-manifest.json")
    physical_ids = {e["id"] for e in design["elements"] if e["physical"]}
    assert set(glb["elements"]) == physical_ids
    step_validation = _load_json(built_output / "step" / "validation.json")
    assert glb["bounds_cad_mm"] == step_validation["bounds_mm"]


def test_quantities_inventory(built_output) -> None:
    qty = _load_json(built_output / "quantities" / "quantities.json")
    design = _load_json(built_output / "manifests" / "design-manifest.json")
    physical_ids = {e["id"] for e in design["elements"] if e["physical"]}
    qty_ids = {row["element_id"] for row in qty["records"]}
    assert qty_ids == physical_ids
    assert all(row["volume_mm3"] > 0 for row in qty["records"])
    assert (built_output / "quantities" / "quantities.csv").is_file()
    assert (built_output / "quantities" / "materials.csv").is_file()
    assert (built_output / "quantities" / "summary.md").is_file()
    with (built_output / "quantities" / "quantities.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(physical_ids)
    assert "element_id" in rows[0] and "volume_mm3" in rows[0]


def test_drawings_inventory(built_output) -> None:
    svg_paths = sorted((built_output / "drawings" / "svg").glob("*.svg"))
    dxf_paths = sorted((built_output / "drawings" / "dxf").glob("*.dxf"))
    assert len(svg_paths) == len(dxf_paths) == 4
    for svg, dxf in zip(svg_paths, dxf_paths, strict=True):
        assert svg.stem == dxf.stem
    pdf_path = built_output / "drawings" / "pdf" / "FileTemplate_Conceptual_Drawings.pdf"
    assert pdf_path.is_file()
    pdf = PdfReader(pdf_path)
    assert len(pdf.pages) == 4
    assert all("Conceptual" in (page.extract_text() or "") for page in pdf.pages)


def test_plan_svg_content(built_output) -> None:
    plan = ET.parse(built_output / "drawings" / "svg" / "FileTemplate_plan.svg").getroot()
    plan_source_ids = {element.attrib.get("data-source-id") for element in plan.iter()}
    assert {
        "complex.house.house_mass",
        "complex.pool.main_pool_water_sloped5ft_to8ft",
        "complex.feature.hot_tub_placeholder",
    } <= plan_source_ids
    assert "Conceptual" in "".join(plan.itertext())


def test_dxf_audit(built_output) -> None:
    for path in sorted((built_output / "drawings" / "dxf").glob("*.dxf")):
        assert not readfile(path).audit().has_errors


def test_annotation_manifest(built_output) -> None:
    ann_manifest = built_output / "drawings" / "annotation-manifest.json"
    assert ann_manifest.is_file()
    annotations = _load_json(ann_manifest)
    ann_ids = {ann["id"] for ann in annotations["annotations"]}
    assert ann_ids >= ANNOTATION_IDS
