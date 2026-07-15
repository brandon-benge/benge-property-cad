"""Exact geometry-derived quantity schedules."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..determinism import write_json
from ..elements import DesignModel, QuantityRecord
from .base import selected_elements


class QuantityExporter:
    name = "quantities"

    def export(self, model: DesignModel, output_dir: Path) -> list[Path]:
        target = output_dir / "quantities"
        target.mkdir(parents=True, exist_ok=True)
        records = records_for(model)
        json_path = write_json(target / "quantities.json", [record_to_dict(record) for record in records])
        quantities_csv = target / "quantities.csv"
        with quantities_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(record_to_dict(records[0]).keys()) if records else _fields())
            writer.writeheader()
            writer.writerows(record_to_dict(record) for record in records)

        materials = material_rows(model, records)
        materials_csv = target / "materials.csv"
        with materials_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(materials[0].keys()) if materials else _material_fields())
            writer.writeheader()
            writer.writerows(materials)

        summary = target / "summary.md"
        total_volume = sum(record.volume_mm3 or 0 for record in records)
        known_masses = [record.mass_kg for record in records if record.mass_kg is not None]
        mass_line = f"{sum(known_masses):.3f} kg" if known_masses else "not calculated (no material density)"
        summary.write_text(
            "# Quantity Summary\n\n"
            "Geometry-derived quantities from physical shared-model elements. Reference geometry is excluded.\n\n"
            f"- Physical elements: {sum(record.count for record in records)}\n"
            f"- Exact volume: {total_volume / 1_000_000_000:.6f} m³\n"
            f"- Known mass: {mass_line}\n"
            "- Waste factor: not applied\n"
            "- Cost: not calculated\n",
            encoding="utf-8",
        )
        return [json_path, quantities_csv, materials_csv, summary]


def records_for(model: DesignModel) -> list[QuantityRecord]:
    result: list[QuantityRecord] = []
    for element in selected_elements(model, "quantities", physical_only=True):
        area = float(element.geometry.area)
        volume = float(element.geometry.volume)
        density = element.material.density_kg_m3 if element.material else None
        mass = volume / 1_000_000_000 * density if density is not None else None
        result.append(
            QuantityRecord(
                element_id=element.id,
                category=element.category,
                material_id=element.material.id if element.material else None,
                count=1,
                area_mm2=area,
                volume_mm3=volume,
                mass_kg=mass,
                provenance="exact_geometry",
            )
        )
    return sorted(result, key=lambda record: record.element_id)


def record_to_dict(record: QuantityRecord) -> dict[str, Any]:
    return {
        "element_id": record.element_id,
        "category": record.category,
        "material_id": record.material_id,
        "count": record.count,
        "area_mm2": round(record.area_mm2, 6) if record.area_mm2 is not None else None,
        "volume_mm3": round(record.volume_mm3, 6) if record.volume_mm3 is not None else None,
        "mass_kg": round(record.mass_kg, 6) if record.mass_kg is not None else None,
        "provenance": record.provenance,
    }


def _fields() -> list[str]:
    return ["element_id", "category", "material_id", "count", "area_mm2", "volume_mm3", "mass_kg", "provenance"]


def _material_fields() -> list[str]:
    return ["material_id", "material_name", "category", "element_count", "volume_m3", "mass_kg", "waste_factor"]


def material_rows(model: DesignModel, records: list[QuantityRecord]) -> list[dict[str, Any]]:
    materials = {element.material.id: element.material for element in model.walk() if element.material}
    grouped: dict[str, list[QuantityRecord]] = defaultdict(list)
    for record in records:
        if record.material_id:
            grouped[record.material_id].append(record)
    rows = []
    for material_id in sorted(grouped):
        records_for_material = grouped[material_id]
        material = materials[material_id]
        rows.append(
            {
                "material_id": material_id,
                "material_name": material.name,
                "category": material.category,
                "element_count": sum(record.count for record in records_for_material),
                "volume_m3": round(sum(record.volume_mm3 or 0 for record in records_for_material) / 1_000_000_000, 9),
                "mass_kg": (
                    round(sum(record.mass_kg for record in records_for_material if record.mass_kg is not None), 6)
                    if any(record.mass_kg is not None for record in records_for_material)
                    else None
                ),
                "waste_factor": 0,
            }
        )
    return rows
