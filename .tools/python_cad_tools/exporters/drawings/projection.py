"""Orthographic shared-model projection into drawing primitives."""

from __future__ import annotations

from ...geometry import bounds
from ...units import format_feet_inches
from ..base import selected_elements
from .primitives import Dimension, DrawingScene, Line, Polyline, Text, TitleBlock, Viewport


def project_model(model, view: str, sheet_number: str, revision: str = "WORKING") -> DrawingScene:
    physical = selected_elements(model, "drawings", physical_only=True)
    rectangles = []
    for element in physical:
        x0, y0, z0, x1, y1, z1 = bounds(element.geometry)
        if view == "plan":
            rectangle = (x0, y0, x1, y1)
        elif view == "front":
            rectangle = (x0, z0, x1, z1)
        elif view == "side":
            rectangle = (y0, z0, y1, z1)
        elif view == "section":
            rectangle = (x0, z0, x1, z1)
        else:
            raise ValueError(f"Unknown drawing view: {view}")
        rectangles.append((element, rectangle))
    min_x = min(value[1][0] for value in rectangles)
    min_y = min(value[1][1] for value in rectangles)
    max_x = max(value[1][2] for value in rectangles)
    max_y = max(value[1][3] for value in rectangles)
    padding = max(max_x - min_x, max_y - min_y) * 0.12
    scene = DrawingScene(
        title_block=TitleBlock(model.name, f"Overall {view.title()}", sheet_number, revision),
        viewport=Viewport(view, (min_x - padding, min_y - padding, max_x + padding, max_y + padding), 1.0),
    )
    label_all = len(rectangles) <= 20
    for element, (x0, y0, x1, y1) in rectangles:
        scene.polylines.append(
            Polyline(((x0, y0), (x1, y0), (x1, y1), (x0, y1)), True, "VISIBLE", element.id)
        )
        if label_all or element.properties.get("drawing_label", False):
            scene.texts.append(
                Text((x0, y1 + padding * 0.12), f"{element.name} [{element.id}]", max(padding * 0.035, 3))
            )
    for element in selected_elements(model, "drawings"):
        if element.physical:
            continue
        x0, y0, z0, x1, y1, z1 = bounds(element.geometry)
        if view == "plan":
            start, end = (x0, y0), (x1, y1)
        elif view in {"front", "section"}:
            start, end = (x0, z0), (x1, z1)
        else:
            start, end = (y0, z0), (y1, z1)
        if start != end:
            scene.lines.append(Line(start, end, "REFERENCE", element.id))
    if rectangles:
        x0, y0, x1, y1 = min_x, min_y, max_x, max_y
        scene.dimensions.extend(
            [
                Dimension((x0, y0), (x1, y0), -padding * 0.35, format_feet_inches(x1 - x0), model.id),
                Dimension((x0, y0), (x0, y1), -padding * 0.35, format_feet_inches(y1 - y0), model.id),
            ]
        )
    return scene
