"""DXF writer with explicit conceptual layers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ezdxf

from .primitives import DrawingScene

LAYERS: dict[str, dict[str, Any]] = {
    "VISIBLE": {"color": 7, "lineweight": 35},
    "HIDDEN": {"color": 8, "lineweight": 18, "linetype": "DASHED"},
    "TEXT": {"color": 2, "lineweight": 18},
    "DIMENSIONS": {"color": 3, "lineweight": 18},
    "REFERENCE": {"color": 4, "lineweight": 18, "linetype": "CENTER"},
    "NOTICE": {"color": 1, "lineweight": 35},
}


def write_dxf(scene: DrawingScene, path: Path) -> Path:
    document = ezdxf.new("R2018", setup=True)
    document.units = ezdxf.units.MM
    for name, attributes in LAYERS.items():
        if name not in document.layers:
            document.layers.add(name, **attributes)
    modelspace = document.modelspace()
    for polyline in scene.polylines:
        modelspace.add_lwpolyline(polyline.points, close=polyline.closed, dxfattribs={"layer": polyline.layer})
    for line in scene.lines:
        modelspace.add_line(line.start, line.end, dxfattribs={"layer": line.layer})
    for text in scene.texts:
        modelspace.add_text(text.value, height=text.height, dxfattribs={"layer": text.layer}).set_placement(text.position)
    for dimension in scene.dimensions:
        modelspace.add_aligned_dim(
            dimension.start,
            dimension.end,
            distance=dimension.offset,
            text=dimension.label,
            override={"dimtxt": 12},
            dxfattribs={"layer": "DIMENSIONS"},
        ).render()
    x0, y0, x1, y1 = scene.viewport.bounds
    modelspace.add_text(scene.title_block.notice, height=max((y1 - y0) * 0.025, 10), dxfattribs={"layer": "NOTICE"}).set_placement((x0, y0))
    path.parent.mkdir(parents=True, exist_ok=True)
    document.saveas(path)
    reloaded = ezdxf.readfile(path)
    auditor = reloaded.audit()
    if auditor.has_errors:
        raise RuntimeError(f"DXF audit failed with {len(auditor.errors)} error(s)")
    return path
