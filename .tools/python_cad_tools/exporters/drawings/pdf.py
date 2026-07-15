"""Vector PDF sheet-set writer."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen.canvas import Canvas

from .primitives import DrawingScene


def write_pdf(scenes: list[DrawingScene], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    page_size = landscape(letter)
    canvas = Canvas(str(path), pagesize=page_size, pageCompression=0, invariant=1)
    for scene in scenes:
        _draw_scene(canvas, scene, page_size)
        canvas.showPage()
    canvas.save()
    return path


def _draw_scene(canvas: Canvas, scene: DrawingScene, page_size: tuple[float, float]) -> None:
    page_width, page_height = page_size
    margin = 42
    canvas.setFillColorRGB(1, 1, 1)
    canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    canvas.setFillColorRGB(0, 0, 0)
    canvas.setStrokeColorRGB(0.2, 0.2, 0.2)
    canvas.setLineWidth(0.6)
    canvas.rect(24, 24, page_width - 48, page_height - 48, stroke=1, fill=0)
    x0, y0, x1, y1 = scene.viewport.bounds
    scale = min((page_width - 2 * margin) / (x1 - x0), (page_height - 3 * margin) / (y1 - y0))

    def point(value: tuple[float, float]) -> tuple[float, float]:
        return margin + (value[0] - x0) * scale, margin * 1.5 + (value[1] - y0) * scale

    canvas.setStrokeColorRGB(0.05, 0.05, 0.05)
    canvas.setLineWidth(1.0)
    for polyline in scene.polylines:
        path = canvas.beginPath()
        start = point(polyline.points[0])
        path.moveTo(*start)
        for source in polyline.points[1:]:
            path.lineTo(*point(source))
        if polyline.closed:
            path.close()
        canvas.drawPath(path)
    canvas.saveState()
    canvas.setStrokeColorRGB(0.1, 0.35, 0.55)
    canvas.setDash(7, 3)
    canvas.setLineWidth(0.8)
    for line in scene.lines:
        canvas.line(*point(line.start), *point(line.end))
    canvas.restoreState()
    canvas.saveState()
    canvas.setStrokeColorRGB(0.25, 0.25, 0.25)
    canvas.setFillColorRGB(0.15, 0.15, 0.15)
    canvas.setLineWidth(0.65)
    canvas.setFont("Helvetica", 7)
    for dimension in scene.dimensions:
        dx = dimension.end[0] - dimension.start[0]
        dy = dimension.end[1] - dimension.start[1]
        if abs(dx) >= abs(dy):
            start = (dimension.start[0], dimension.start[1] + dimension.offset)
            end = (dimension.end[0], dimension.end[1] + dimension.offset)
        else:
            start = (dimension.start[0] + dimension.offset, dimension.start[1])
            end = (dimension.end[0] + dimension.offset, dimension.end[1])
        start_page = point(start)
        end_page = point(end)
        canvas.line(*start_page, *end_page)
        canvas.line(start_page[0] - 3, start_page[1] - 3, start_page[0] + 3, start_page[1] + 3)
        canvas.line(end_page[0] - 3, end_page[1] - 3, end_page[0] + 3, end_page[1] + 3)
        canvas.drawCentredString(
            (start_page[0] + end_page[0]) / 2,
            (start_page[1] + end_page[1]) / 2 + 4,
            dimension.label,
        )
    canvas.restoreState()
    canvas.setFont("Helvetica", 7)
    for text in scene.texts:
        canvas.drawString(*point(text.position), text.value)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(margin, page_height - margin, scene.title_block.sheet_title)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(margin, margin * 0.72, scene.title_block.project_name)
    canvas.drawRightString(page_width - margin, page_height - margin, f"{scene.title_block.sheet_number}  Rev {scene.title_block.revision}")
    canvas.line(margin, margin * 1.05, page_width - margin, margin * 1.05)
    canvas.setFillColorRGB(0.65, 0.0, 0.0)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawCentredString(page_width / 2, margin * 0.72, scene.title_block.notice)
    canvas.setFillColorRGB(0, 0, 0)
