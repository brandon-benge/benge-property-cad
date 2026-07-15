"""Build context passed to project model builders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class BuildContext:
    project_dir: Path
    output_dir: Path
    config: Any
    git_sha: str | None = None
