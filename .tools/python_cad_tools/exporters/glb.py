"""Headless OCP tessellation and glTF 2.0 binary scene export."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np
import trimesh

from ..determinism import write_json
from ..exceptions import ExportError
from ..geometry import combined_bounds, tessellate
from .base import selected_elements


class GlbExporter:
    name = "glb"

    def __init__(self, linear_deflection: float = 0.5, angular_deflection: float = 0.25) -> None:
        self.linear_deflection = linear_deflection
        self.angular_deflection = angular_deflection

    def export(self, model, output_dir: Path) -> list[Path]:
        target = output_dir / "glb"
        target.mkdir(parents=True, exist_ok=True)
        scene = trimesh.Scene(base_frame="model")
        expected_ids: list[str] = []
        triangle_counts: dict[str, int] = {}
        for element in selected_elements(model, "glb", physical_only=True):
            vertices, faces = tessellate(element.geometry, self.linear_deflection, self.angular_deflection)
            # CAD Z-up (x,y,z) -> glTF Y-up (x,z,-y), a right-handed rotation.
            converted = np.asarray([[x, z, -y] for x, y, z in vertices], dtype=np.float64)
            material = trimesh.visual.material.PBRMaterial(
                name=element.material.name if element.material else element.id,
                baseColorFactor=[
                    int(round(channel * 255)) for channel in (element.color_rgb or (0.7, 0.7, 0.7))
                ]
                + [255],
                metallicFactor=0.0,
                roughnessFactor=0.8,
            )
            mesh = trimesh.Trimesh(vertices=converted, faces=np.asarray(faces), process=False, validate=True)
            mesh.visual = trimesh.visual.TextureVisuals(material=material)
            extras = {
                "stable_id": element.id,
                "category": element.category,
                "source_module": element.source_module,
                "geometry_kind": element.geometry_kind,
                "units": "millimetres",
            }
            scene.add_geometry(mesh, geom_name=element.id, node_name=element.id, metadata=extras)
            expected_ids.append(element.id)
            triangle_counts[element.id] = len(faces)
        path = target / f"{model.name}.glb"
        path.write_bytes(trimesh.exchange.gltf.export_glb(scene, include_normals=True))
        document = glb_json(path)
        found_ids = sorted(
            node.get("extras", {}).get("stable_id")
            for node in document.get("nodes", [])
            if node.get("extras", {}).get("stable_id")
        )
        if found_ids != sorted(expected_ids):
            raise ExportError(f"GLB node extras missing stable IDs: {found_ids}")
        loaded = trimesh.load(path, force="scene", process=False)
        if not isinstance(loaded, trimesh.Scene) or len(loaded.geometry) != len(expected_ids):
            raise ExportError("Independent GLB reload did not preserve element geometry count")
        manifest = write_json(
            target / "manifest.json",
            {
                "coordinate_transform": "CAD (x,y,z) to glTF (x,z,-y), right-handed",
                "elements": sorted(expected_ids),
                "triangle_counts": triangle_counts,
                "bounds_cad_mm": [
                    round(value, 6)
                    for value in combined_bounds(
                        [element.geometry for element in selected_elements(model, "glb", physical_only=True)]
                    )
                ],
                "bounds_y_up_mm": np.asarray(loaded.bounds).round(6).tolist(),
                "file_size": path.stat().st_size,
            },
        )
        return [path, manifest]


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise ExportError("Invalid GLB magic")
    _, version, _ = struct.unpack_from("<4sII", data, 0)
    if version != 2:
        raise ExportError(f"Expected glTF 2.0, got {version}")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise ExportError("First GLB chunk is not JSON")
    return json.loads(data[20 : 20 + chunk_length].decode("utf-8").rstrip(" \t\r\n\0"))
