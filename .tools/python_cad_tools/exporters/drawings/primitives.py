"""Format-neutral conceptual drawing primitives."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Line:
    start: tuple[float, float]
    end: tuple[float, float]
    layer: str = "VISIBLE"
    source_id: str | None = None


@dataclass(frozen=True, slots=True)
class Polyline:
    points: tuple[tuple[float, float], ...]
    closed: bool = False
    layer: str = "VISIBLE"
    source_id: str | None = None


@dataclass(frozen=True, slots=True)
class Arc:
    center: tuple[float, float]
    radius: float
    start_deg: float
    end_deg: float
    layer: str = "VISIBLE"


@dataclass(frozen=True, slots=True)
class Text:
    position: tuple[float, float]
    value: str
    height: float = 3.0
    layer: str = "TEXT"


@dataclass(frozen=True, slots=True)
class Dimension:
    start: tuple[float, float]
    end: tuple[float, float]
    offset: float
    label: str
    source_id: str | None = None


@dataclass(frozen=True, slots=True)
class Leader:
    points: tuple[tuple[float, float], ...]
    label: str


@dataclass(frozen=True, slots=True)
class Hatch:
    boundary: tuple[tuple[float, float], ...]
    pattern: str = "ANSI31"


@dataclass(frozen=True, slots=True)
class Viewport:
    name: str
    bounds: tuple[float, float, float, float]
    scale: float


@dataclass(frozen=True, slots=True)
class TitleBlock:
    project_name: str
    sheet_title: str
    sheet_number: str
    revision: str
    notice: str = "Conceptual — not for construction or permitting"


@dataclass(slots=True)
class DrawingScene:
    title_block: TitleBlock
    viewport: Viewport
    lines: list[Line] = field(default_factory=list)
    polylines: list[Polyline] = field(default_factory=list)
    arcs: list[Arc] = field(default_factory=list)
    texts: list[Text] = field(default_factory=list)
    dimensions: list[Dimension] = field(default_factory=list)
    leaders: list[Leader] = field(default_factory=list)
    hatches: list[Hatch] = field(default_factory=list)
