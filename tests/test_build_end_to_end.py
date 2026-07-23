"""Sections 12.4-12.7: Programmatic build, CLI, artifact reconciliation, determinism."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import ezdxf
import ifcopenshell
import pytest
from build123d import import_step
from pypdf import PdfReader
from python_cad_tools.build import BuildOptions, ValidationOptions, build_project, clean_project, validate_project
from python_cad_tools.determinism import semantic_hash

pytestmark = [pytest.mark.integration]

ANNOTATION_IDS = {
    "file.annotation.section.a301",
    "file.annotation.elevation.a201",
    "file.annotation.elevation.a202",
    "file.annotation.schedule.openings",
}

ANNOTATION_SUB_IDS = {
    "file.annotation.elevation.a201",
    "file.annotation.elevation.a201.label",
    "file.annotation.elevation.a201.outline",
    "file.annotation.elevation.a201.pointer",
    "file.annotation.elevation.a202",
    "file.annotation.elevation.a202.label",
    "file.annotation.elevation.a202.outline",
    "file.annotation.elevation.a202.pointer",
    "file.annotation.schedule.openings",
    "file.annotation.schedule.openings.border",
    "file.annotation.schedule.openings.header.0",
    "file.annotation.schedule.openings.header.1",
    "file.annotation.schedule.openings.header.2",
    "file.annotation.schedule.openings.header.3",
    "file.annotation.schedule.openings.row.SD-01.cell.0",
    "file.annotation.schedule.openings.row.SD-01.cell.1",
    "file.annotation.schedule.openings.row.SD-01.cell.2",
    "file.annotation.schedule.openings.row.SD-01.cell.3",
    "file.annotation.schedule.openings.row.SD-01.separator",
    "file.annotation.schedule.openings.title",
    "file.annotation.section.a301",
    "file.annotation.section.a301.arrow.end",
    "file.annotation.section.a301.arrow.start",
    "file.annotation.section.a301.label.end",
    "file.annotation.section.a301.label.start",
    "file.annotation.section.a301.line",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class TwoBuilds:
    output1: Path
    manifest1: dict
    output2: Path
    manifest2: dict


@pytest.fixture
def two_builds(copied_project: Path) -> TwoBuilds:
    build_project(BuildOptions(project_root=copied_project))
    output1 = copied_project / "generated"
    manifest1 = _load_json(output1 / "manifests" / "build-manifest.json")
    clean_project(copied_project)
    assert not (copied_project / "generated" / "step").exists()
    build_project(BuildOptions(project_root=copied_project))
    output2 = copied_project / "generated"
    manifest2 = _load_json(output2 / "manifests" / "build-manifest.json")
    return TwoBuilds(output1=output1, manifest1=manifest1, output2=output2, manifest2=manifest2)


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


def test_build_selected_formats(copied_project) -> None:
    result = build_project(BuildOptions(project_root=copied_project, formats=("step", "ifc")))
    output = result.output_root
    assert (output / "step" / "FileTemplate.step").is_file()
    assert (output / "ifc" / "FileTemplate.ifc").is_file()
    assert not (output / "glb").exists() or not list((output / "glb").rglob("*"))


def test_build_full_default_formats(built_output) -> None:
    for fmt in ("step", "ifc", "glb", "drawings", "quantities"):
        assert (built_output / fmt).exists(), f"Missing format directory: {fmt}"


# ── 12.5 CLI end-to-end ──────────────────────────────────────────────────────


def _cli(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "python_cad_tools.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_cli_build_from_root(copied_project) -> None:
    result = _cli("build", cwd=copied_project)
    assert result.returncode == 0, f"CLI build failed: stderr={result.stderr}"
    assert (copied_project / "generated" / "step" / "FileTemplate.step").is_file()


def test_cli_build_from_path_with_spaces(copied_project_with_spaces) -> None:
    result = _cli("build", cwd=copied_project_with_spaces)
    assert result.returncode == 0, f"CLI build failed in path with spaces: {result.stderr}"
    assert (copied_project_with_spaces / "generated" / "step" / "FileTemplate.step").is_file()


def test_cli_validate(copied_project) -> None:
    result = _cli("validate", cwd=copied_project)
    assert result.returncode == 0, f"CLI validate failed: {result.stderr}"
    assert '"status":"ok"' in result.stdout


def test_cli_verify(session_project) -> None:
    result = _cli("verify", cwd=session_project)
    assert result.returncode == 0, f"CLI verify failed: {result.stderr}"


def test_cli_clean(copied_project) -> None:
    _cli("build", cwd=copied_project)
    assert (copied_project / "generated" / "step" / "FileTemplate.step").is_file()
    result = _cli("clean", cwd=copied_project)
    assert result.returncode == 0, f"CLI clean failed: {result.stderr}"
    assert not (copied_project / "generated" / "step").exists()


def test_cli_repeated_format(copied_project) -> None:
    result = _cli("build", "--format", "step", "--format", "ifc", cwd=copied_project)
    assert result.returncode == 0, f"CLI repeated format failed: {result.stderr}"
    assert (copied_project / "generated" / "step" / "FileTemplate.step").is_file()
    assert not (copied_project / "generated" / "glb").exists()


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


def _ifc_entities_by_stable_id(elements) -> dict[str, Any]:
    """Map every IfcElement to its StableId property value."""
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

    # Representative mappings covering every IfcElement subclass used by the
    # model, not only IfcBuildingElementProxy.  Each entry asserts both the IFC
    # class and the accurate predefined type from the IFC4 enumeration.
    expected_mappings = {
        # IfcSlab — deck boards and structural slabs
        "complex.deck_board.upper_deck_board_01": ("IfcSlab", "FLOOR"),
        "complex.structure.hot_tub_platform": ("IfcSlab", "BASESLAB"),
        # IfcMember — rafters, plates, mullions
        "complex.roof_framing.roof_rafter_01": ("IfcMember", "RAFTER"),
        "complex.stair.upper_straight_tread_01": ("IfcMember", "PLATE"),
        "complex.feature.sliding_door_frame_left": ("IfcMember", "MULLION"),
        # IfcRailing — guardrails and balustrades
        "complex.railing.upper_straight_left_handrail": ("IfcRailing", "GUARDRAIL"),
        "complex.site.shed_access_fence": ("IfcRailing", "BALUSTRADE"),
        # IfcRoof — shed and gable roofs
        "complex.roof.upper_deck_shed_roof_cover": ("IfcRoof", "SHED_ROOF"),
        "complex.shed.shed_roof_left_slope": ("IfcRoof", "GABLE_ROOF"),
        # IfcDoor — circulation doors
        "complex.feature.sliding_door": ("IfcDoor", "DOOR"),
        "complex.shed.shed_front_double_door": ("IfcDoor", "DOOR"),
        # IfcWall — house and shed walls, fireplace masonry
        "complex.house.house_mass": ("IfcWall", "STANDARD"),
        "complex.fireplace.fireplace_masonry_body": ("IfcWall", "STANDARD"),
        # IfcBeam — deck framing beams
        "complex.deck_framing.upper_front_beam": ("IfcBeam", "BEAM"),
        # IfcColumn — support posts
        "complex.deck_framing.upper_support_post_01": ("IfcColumn", "COLUMN"),
        # IfcCovering — skirting and chimney cap
        "complex.skirting.upper_deck_front_skirt": ("IfcCovering", "SKIRTINGBOARD"),
        "complex.fireplace.fireplace_chimney_cap": ("IfcCovering", "ROOFING"),
        # IfcLightFixture — deck and stair lighting
        "complex.skirting.upper_deck_front_skirt_light_01": ("IfcLightFixture", "POINTSOURCE"),
        # IfcSanitaryTerminal — outdoor kitchen sink
        "complex.outdoor_kitchen.outdoor_kitchen_sink_basin": ("IfcSanitaryTerminal", "SINK"),
        # IfcFurniture — outdoor kitchen cabinets
        "complex.outdoor_kitchen.outdoor_kitchen_cabinet_run": ("IfcFurniture", "USERDEFINED"),
    }
    for stable_id, (ifc_class, predefined_type) in expected_mappings.items():
        entity = entities_by_id[stable_id]
        assert entity.is_a() == ifc_class, f"{stable_id}: expected {ifc_class}, got {entity.is_a()}"
        assert entity.PredefinedType == predefined_type, (
            f"{stable_id}: expected {predefined_type}, got {entity.PredefinedType}"
        )


def test_ifc_proxy_elements_use_accurate_predefined_types(built_output) -> None:
    """Every IfcBuildingElementProxy must use ELEMENT or PROVISIONFORVOID, not NOTDEFINED."""
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
    """No physical element may use NOTDEFINED as its predefined type."""
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
        assert not ezdxf.readfile(path).audit().has_errors


def test_annotation_manifest(built_output) -> None:
    ann_manifest = _load_json(built_output / "drawings" / "annotation-manifest.json")
    ann_ids = {ann["id"] for ann in ann_manifest["annotations"]}
    assert ann_ids >= ANNOTATION_IDS


# ── 12.7 Failure rollback/recovery and determinism ──────────────────────────


def test_two_clean_builds_identical(two_builds) -> None:
    assert two_builds.manifest1["design_semantic_hash"] == two_builds.manifest2["design_semantic_hash"]
    known_non_deterministic = {
        "run-metadata.json",
        "build-manifest.json",
        "FileTemplate.step",
    }
    bm1_stable_excluding_step = semantic_hash(
        [
            e
            for e in two_builds.manifest1["artifacts"]
            if not e["volatile"] and not any(e["path"].endswith(name) for name in known_non_deterministic)
        ]
    )
    bm2_stable_excluding_step = semantic_hash(
        [
            e
            for e in two_builds.manifest2["artifacts"]
            if not e["volatile"] and not any(e["path"].endswith(name) for name in known_non_deterministic)
        ]
    )
    assert bm1_stable_excluding_step == bm2_stable_excluding_step, (
        "Stable artifact hash mismatch excluding known non-deterministic files"
    )
    arts1 = {e["path"]: e for e in two_builds.manifest1["artifacts"]}
    arts2 = {e["path"]: e for e in two_builds.manifest2["artifacts"]}
    assert set(arts1) == set(arts2), "Artifact paths differ between builds"
    for path_key, entry1 in arts1.items():
        entry2 = arts2[path_key]
        if any(entry1["path"].endswith(name) for name in known_non_deterministic):
            continue
        assert entry1["sha256"] == entry2["sha256"], f"SHA-256 mismatch for {path_key} between builds"


def test_deterministic_nonvolatile_bytes(two_builds) -> None:
    volatile_names = {"run-metadata.json", "build-manifest.json", "FileTemplate.step"}
    for entry1, entry2 in zip(two_builds.manifest1["artifacts"], two_builds.manifest2["artifacts"], strict=True):
        if Path(entry1["path"]).name in volatile_names:
            continue
        path1 = two_builds.output1 / entry1["path"]
        path2 = two_builds.output2 / entry2["path"]
        bytes1 = path1.read_bytes()
        bytes2 = path2.read_bytes()
        assert bytes1 == bytes2, f"Byte mismatch for {entry1['path']} between builds"
