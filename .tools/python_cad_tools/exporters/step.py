"""Exact BREP STEP assembly export and independent reload checks."""

from __future__ import annotations

import re
from pathlib import Path

from build123d import Compound, import_step
from build123d.exporters3d import _create_xde
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static
from OCP.Message import Message, Message_Gravity
from OCP.STEPCAFControl import STEPCAFControl_Controller, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_Controller, STEPControl_StepModelType

from ..determinism import write_json
from ..exceptions import ExportError
from ..geometry import combined_bounds
from .base import selected_elements


class StepExporter:
    name = "step"

    def export(self, model, output_dir: Path) -> list[Path]:
        target = output_dir / "step"
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{model.name}.step"
        elements = selected_elements(model, "step", physical_only=True)
        if not elements:
            raise ExportError("STEP export requires at least one physical solid")
        # Initialize the controllers before setting the schema. Their first initialization
        # installs defaults and would otherwise reset this value to AP214.
        STEPCAFControl_Controller.Init_s()
        STEPControl_Controller.Init_s()
        compound = Compound(children=[element.geometry for element in elements])
        _export_ap242(compound, path)
        if not path.exists() or path.stat().st_size == 0:
            raise ExportError("STEP writer produced no artifact")
        reloaded = import_step(path)
        expected = combined_bounds([element.geometry for element in elements])
        actual = combined_bounds([reloaded])
        if any(abs(left - right) > 0.01 for left, right in zip(expected, actual, strict=True)):
            raise ExportError(f"STEP reload bounds differ: expected {expected}, got {actual}")
        if not bool(reloaded.is_valid):
            raise ExportError("Reloaded STEP shape is invalid")
        schema = step_schema(path)
        if not schema.startswith("AP242_"):
            raise ExportError(f"STEP writer did not honor the AP242 requirement: {schema}")
        report = write_json(
            target / "validation.json",
            {
                "valid": True,
                "schema": schema,
                "requested_schema": "AP242",
                "schema_note": "The generated file was independently reloaded and its header reports AP242.",
                "solid_count": len(reloaded.solids()),
                "bounds_mm": [round(value, 6) for value in actual],
            },
        )
        return [path, report]


def _export_ap242(compound: Compound, path: Path) -> None:
    """Write an XDE assembly with OCP's default session so AP242 is honored."""
    if not Interface_Static.SetCVal_s("write.step.schema", "AP242DIS"):
        raise ExportError("OCP rejected the AP242 STEP schema setting")

    document = _create_xde(compound, auto_naming=True)
    messenger = Message.DefaultMessenger_s()
    for printer in messenger.Printers():
        printer.SetTraceLevel(Message_Gravity.Message_Fail)

    writer = STEPCAFControl_Writer()
    writer.SetColorMode(True)
    writer.SetLayerMode(True)
    writer.SetNameMode(True)
    if not writer.Transfer(document, STEPControl_StepModelType.STEPControl_AsIs):
        raise ExportError("STEP writer could not transfer the XDE assembly")
    status = writer.Write(str(path))
    if status != IFSelect_ReturnStatus.IFSelect_RetDone:
        raise ExportError(f"STEP writer failed with status {status}")


def step_schema(path: Path) -> str:
    header = path.read_text(encoding="latin-1", errors="ignore")[:16000]
    match = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", header)
    return match.group(1) if match else "unknown"
