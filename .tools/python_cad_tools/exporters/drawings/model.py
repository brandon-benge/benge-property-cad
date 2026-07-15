"""Conceptual sheet-set exporter coordinating shared scenes and writers."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from .dxf import write_dxf
from .pdf import write_pdf
from .projection import project_model
from .svg import write_svg


class DrawingExporter:
    name = "drawings"

    def export(self, model, output_dir: Path) -> list[Path]:
        drawing_dir = output_dir / "drawings"
        views = (("plan", "A-101"), ("front", "A-201"), ("side", "A-202"), ("section", "A-301"))
        scenes = [project_model(model, view, sheet) for view, sheet in views]
        paths: list[Path] = []
        for scene in scenes:
            slug = scene.viewport.name.replace(" ", "_")
            paths.append(write_svg(scene, drawing_dir / "svg" / f"{model.name}_{slug}.svg"))
            paths.append(write_dxf(scene, drawing_dir / "dxf" / f"{model.name}_{slug}.dxf"))
        pdf = write_pdf(scenes, drawing_dir / "pdf" / f"{model.name}_Conceptual_Drawings.pdf")
        if len(PdfReader(pdf).pages) != len(scenes):
            raise RuntimeError("PDF validation failed: unexpected page count")
        paths.append(pdf)
        return paths
