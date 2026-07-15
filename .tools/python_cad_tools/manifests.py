"""Design, build, and run manifest generation."""

from __future__ import annotations

import importlib.metadata
import platform
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .determinism import semantic_hash, sha256_file, write_json
from .geometry import bounds

DEPENDENCIES = ("build123d", "cadquery-ocp", "ifcopenshell", "trimesh", "numpy", "ezdxf", "reportlab")


def design_manifest(model) -> dict:
    elements = []
    for element in model.walk():
        elements.append(
            {
                "id": element.id,
                "name": element.name,
                "category": element.category,
                "geometry_kind": element.geometry_kind,
                "physical": element.physical,
                "bounds_mm": [round(value, 6) for value in bounds(element.geometry)],
                "placement": {
                    "translation_mm": element.placement.translation_mm,
                    "rotation_deg_xyz": element.placement.rotation_deg_xyz,
                },
                "dimensions": {
                    "length_mm": element.dimensions.length_mm,
                    "width_mm": element.dimensions.width_mm,
                    "height_mm": element.dimensions.height_mm,
                    "radius_mm": element.dimensions.radius_mm,
                    "extras": element.dimensions.extras,
                },
                "material_id": element.material.id if element.material else None,
                "color_rgb": element.color_rgb,
                "ifc_class": element.ifc_mapping.ifc_class,
                "ifc_exclusion": element.ifc_mapping.exclude_reason,
                "storey": element.storey,
                "tags": sorted(element.tags),
                "parent_id": element.parent_id,
                "source_module": element.source_module,
                "export_formats": sorted(element.export_formats),
            }
        )
    value = {
        "model_id": model.id,
        "model_name": model.name,
        "coordinate_system": model.coordinate_system,
        "metadata": model.metadata,
        "elements": elements,
    }
    value["semantic_hash"] = semantic_hash(value)
    return value


def write_manifests(
    model,
    staging: Path,
    selected_exporters: list[str],
    issues,
    git_sha: str | None,
) -> list[Path]:
    build_timestamp = datetime.now(UTC).isoformat()
    target = staging / "manifests"
    design_path = write_json(target / "design-elements.json", design_manifest(model))
    design_hash = design_manifest(model)["semantic_hash"]
    artifacts = []
    for path in sorted(staging.rglob("*")):
        if path.is_file() and path.name not in {"build-manifest.json", "run-metadata.json"}:
            relative = path.relative_to(staging).as_posix()
            artifacts.append(
                {
                    "path": relative,
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "semantic_hash": semantic_hash({"design_hash": design_hash, "output_path": relative}),
                }
            )
    semantic_inputs = {
        "design_hash": design_hash,
        "exporters": sorted(selected_exporters),
        "artifact_paths": [item["path"] for item in artifacts],
        "validation": [issue.__dict__ if hasattr(issue, "__dict__") else {
            "severity": issue.severity, "code": issue.code, "message": issue.message, "element_id": issue.element_id
        } for issue in issues],
    }
    build = {
        "tool_version": __version__,
        "git_sha": git_sha,
        "build_timestamp_utc": build_timestamp,
        "python": platform.python_version(),
        "dependencies": {name: _version(name) for name in DEPENDENCIES},
        "selected_exporters": sorted(selected_exporters),
        "artifacts": artifacts,
        "model_element_count": len(list(model.walk())),
        "validation_status": "passed" if not any(issue.severity == "error" for issue in issues) else "failed",
        "warnings": [issue.message for issue in issues if issue.severity == "warning"],
        "semantic_hash": semantic_hash(semantic_inputs),
    }
    build_path = write_json(target / "build-manifest.json", build)
    run_path = write_json(
        target / "run-metadata.json",
        {
            "timestamp_utc": build_timestamp,
            "host": platform.node(),
            "platform": platform.platform(),
        },
    )
    return [design_path, build_path, run_path]


def _version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"
