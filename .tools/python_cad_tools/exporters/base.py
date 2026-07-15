"""Common exporter protocol and helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..elements import DesignElement, DesignModel


class Exporter(Protocol):
    name: str

    def export(self, model: DesignModel, output_dir: Path) -> list[Path]: ...


def selected_elements(model: DesignModel, format_name: str, *, physical_only: bool = False) -> list[DesignElement]:
    return [
        element
        for element in model.walk()
        if element.visible
        and format_name in element.export_formats
        and (element.physical or not physical_only)
    ]
