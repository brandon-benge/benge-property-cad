"""Optional, truthful FreeCADCmd compatibility adapter."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..exceptions import DependencyUnavailableError, ExportError
from .step import StepExporter


class FcstdExporter:
    name = "fcstd"

    def export(self, model, output_dir: Path) -> list[Path]:
        executable = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
        if not executable:
            raise DependencyUnavailableError(
                "FCStd was explicitly requested, but FreeCADCmd is unavailable. Install FreeCAD and ensure FreeCADCmd is on PATH."
            )
        step_paths = StepExporter().export(model, output_dir)
        step_path = step_paths[0]
        target = output_dir / "fcstd"
        target.mkdir(parents=True, exist_ok=True)
        result = target / f"{model.name}.FCStd"
        metadata = target / "element-metadata.json"
        metadata.write_text(
            json.dumps({element.id: {"name": element.name, "category": element.category} for element in model.walk()}, sort_keys=True),
            encoding="utf-8",
        )
        with tempfile.TemporaryDirectory() as temp_name:
            script = Path(temp_name) / "create_fcstd.py"
            script.write_text(_script(step_path, result, metadata), encoding="utf-8")
            completed = subprocess.run([executable, str(script)], text=True, capture_output=True, check=False)
        if completed.returncode or not result.exists():
            raise ExportError(f"FreeCADCmd FCStd creation failed: {completed.stderr or completed.stdout}")
        return [result]


def _script(step_path: Path, output_path: Path, metadata_path: Path) -> str:
    return f'''import json
import FreeCAD
import Part

doc = FreeCAD.newDocument("PythonCadCompatibility")
shape = Part.read({str(step_path)!r})
obj = doc.addObject("PartDesign::Feature", "ImportedSharedModel")
obj.Shape = shape
obj.addProperty("App::PropertyString", "SourceMetadata")
obj.SourceMetadata = json.dumps(json.load(open({str(metadata_path)!r}, encoding="utf-8")), sort_keys=True)
doc.recompute()
doc.saveAs({str(output_path)!r})
FreeCAD.closeDocument(doc.Name)
check = FreeCAD.openDocument({str(output_path)!r})
if not check.Objects or check.Objects[0].Shape.isNull():
    raise RuntimeError("FCStd reopen validation failed")
FreeCAD.closeDocument(check.Name)
'''
