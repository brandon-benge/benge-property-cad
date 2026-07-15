"""Shared-model validation framework."""

from __future__ import annotations

from math import isfinite

from .elements import DesignElement, DesignModel, ValidationIssue
from .geometry import is_valid_solid


def validate_model(model: DesignModel) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    known = {element.id for element in model.walk()}
    for element in model.walk():
        issues.extend(_validate_element(element, seen, known))
    for validator in model.validators:
        issues.extend(validator(model))
    return sorted(issues, key=lambda issue: (issue.severity, issue.code, issue.element_id or ""))


def _validate_element(
    element: DesignElement,
    seen: set[str],
    known: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not element.id or element.id in seen:
        issues.append(ValidationIssue("error", "stable-id", "Stable IDs must be non-empty and unique", element.id or None))
    seen.add(element.id)
    values = (*element.placement.translation_mm, *element.placement.rotation_deg_xyz)
    if not all(isfinite(value) for value in values):
        issues.append(ValidationIssue("error", "placement", "Placement values must be finite", element.id))
    if element.geometry is None:
        issues.append(ValidationIssue("error", "geometry-missing", "Geometry must be present", element.id))
    if element.physical and element.geometry_kind != "solid":
        issues.append(ValidationIssue("error", "physical-kind", "Physical elements must be solids", element.id))
    if element.physical and element.geometry is not None and not is_valid_solid(element.geometry):
        issues.append(ValidationIssue("error", "solid-invalid", "Physical geometry must be a valid positive-volume solid", element.id))
    if not element.physical and element.geometry_kind == "solid":
        issues.append(ValidationIssue("warning", "reference-solid", "Non-physical reference geometry is represented as a solid", element.id))
    if any(value <= 0 or not isfinite(value) for value in element.dimensions.values()):
        issues.append(ValidationIssue("error", "dimensions", "Declared dimensions must be finite and positive", element.id))
    if element.physical and element.material is None:
        issues.append(ValidationIssue("error", "material", "Physical elements require a material", element.id))
    mapping = element.ifc_mapping
    if mapping.ifc_class is None and not mapping.exclude_reason:
        issues.append(ValidationIssue("error", "ifc-intent", "IFC mapping or exclusion reason is required", element.id))
    if element.parent_id is not None and element.parent_id not in known:
        issues.append(ValidationIssue("error", "parent", f"Unknown parent ID: {element.parent_id}", element.id))
    return issues


def fatal_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [issue for issue in issues if issue.severity == "error"]
