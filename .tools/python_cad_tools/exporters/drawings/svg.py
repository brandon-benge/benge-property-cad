"""SVG writer for the shared drawing scene."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from .primitives import DrawingScene

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def write_svg(scene: DrawingScene, path: Path) -> Path:
    x0, y0, x1, y1 = scene.viewport.bounds
    width = x1 - x0
    height = y1 - y0
    root = ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "viewBox": f"{x0:g} {y0:g} {width:g} {height:g}",
            "data-sheet": scene.title_block.sheet_number,
        },
    )
    ET.SubElement(root, f"{{{SVG_NS}}}title").text = scene.title_block.sheet_title
    group = ET.SubElement(root, f"{{{SVG_NS}}}g", {"transform": f"translate(0 {y0 + y1:g}) scale(1 -1)"})
    for polyline in scene.polylines:
        points = " ".join(f"{x:g},{y:g}" for x, y in polyline.points)
        ET.SubElement(
            group,
            f"{{{SVG_NS}}}{'polygon' if polyline.closed else 'polyline'}",
            {
                "points": points,
                "fill": "none",
                "stroke": "#111111",
                "stroke-width": "2",
                "vector-effect": "non-scaling-stroke",
                "data-layer": polyline.layer,
                "data-source-id": polyline.source_id or "",
            },
        )
    for line in scene.lines:
        ET.SubElement(
            group,
            f"{{{SVG_NS}}}line",
            {
                "x1": f"{line.start[0]:g}", "y1": f"{line.start[1]:g}",
                "x2": f"{line.end[0]:g}", "y2": f"{line.end[1]:g}",
                "stroke": "#111111", "data-layer": line.layer,
            },
        )
    text_group = ET.SubElement(root, f"{{{SVG_NS}}}g", {"fill": "#111111", "font-family": "sans-serif"})
    for item in scene.texts:
        ET.SubElement(
            text_group,
            f"{{{SVG_NS}}}text",
            {"x": f"{item.position[0]:g}", "y": f"{y0 + y1 - item.position[1]:g}", "font-size": f"{item.height:g}"},
        ).text = item.value
    for dimension in scene.dimensions:
        dx = dimension.end[0] - dimension.start[0]
        dy = dimension.end[1] - dimension.start[1]
        if abs(dx) >= abs(dy):
            a = (dimension.start[0], dimension.start[1] + dimension.offset)
            b = (dimension.end[0], dimension.end[1] + dimension.offset)
        else:
            a = (dimension.start[0] + dimension.offset, dimension.start[1])
            b = (dimension.end[0] + dimension.offset, dimension.end[1])
        ET.SubElement(group, f"{{{SVG_NS}}}line", {"x1": f"{a[0]:g}", "y1": f"{a[1]:g}", "x2": f"{b[0]:g}", "y2": f"{b[1]:g}", "stroke": "#333333", "data-layer": "DIMENSIONS"})
        ET.SubElement(text_group, f"{{{SVG_NS}}}text", {"x": f"{(a[0] + b[0]) / 2:g}", "y": f"{y0 + y1 - (a[1] + b[1]) / 2:g}", "font-size": "12", "text-anchor": "middle"}).text = dimension.label
    notice = ET.SubElement(root, f"{{{SVG_NS}}}text", {"x": f"{x0 + width * 0.02:g}", "y": f"{y1 - height * 0.02:g}", "font-size": f"{max(height * 0.025, 10):g}", "font-weight": "bold"})
    notice.text = scene.title_block.notice
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    ET.parse(path)
    return path
