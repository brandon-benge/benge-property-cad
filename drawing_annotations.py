"""Post-process generated CAD drawing files to add drafting annotations.

This module is project-owned code that applies annotation layers — section cut
lines, elevation markers, and door/window schedules — to generated SVG and DXF
files after the standard build pipeline produces them.

The `python_cad_tools` exporter pipeline (`.tools/`, managed) does not currently
support an annotation/decorations layer. This module works around that by
editing the rendered SVG XML and DXF directly.

Integration:
    The module is imported by model.py.  On import it registers an atexit
    handler so that annotate_all() runs automatically after python build.py
    completes — no separate step required.

Standalone usage (optional):
    python drawing_annotations.py
    python drawing_annotations.py --rebuild   (also runs build.py first)
"""

from __future__ import annotations

import atexit
import math
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

PROJECT_DIR = Path(__file__).resolve().parent
GENERATED_DIR = PROJECT_DIR / "generated"

# Section cut parameters (matches projection.py values)
SECTION_CUT_X = 4000.0  # mm — cut plane through centre of house/upper deck

# ---- helpers ----------------------------------------------------------------

def _ns(tag: str) -> str:
    return f"{{{SVG_NS}}}{tag}"


def _make_point(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:g},{y:g}" for x, y in points)


def _model_to_svg_y(y0: float, y1: float, model_y: float) -> float:
    """Convert model-space Y to SVG text-space Y (outside the flipped group)."""
    return y0 + y1 - model_y


def parse_viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    vb = root.get("viewBox", "0 0 100 100")
    parts = [float(v) for v in vb.split()]
    return parts[0], parts[1], parts[2], parts[3]


def _strip_old_annotations(root: ET.Element) -> None:
    """Remove any existing annotation elements to ensure idempotency."""
    ns = SVG_NS
    # Remove annotation elements from all groups
    for group in root.findall(f"{{{ns}}}g"):
        to_remove: list[ET.Element] = []
        for child in group:
            if (child.get("data-layer") or "").startswith("ANNOTATION_"):
                to_remove.append(child)
        for child in to_remove:
            group.remove(child)

    # Also remove any top-level annotation elements
    to_remove = []
    for child in root:
        if (child.get("data-layer") or "").startswith("ANNOTATION_"):
            to_remove.append(child)
    for child in to_remove:
        root.remove(child)


# ---- section cut ------------------------------------------------------------

def add_section_cut_line(
    root: ET.Element,
    geo_group: ET.Element,
    text_group: ET.Element,
    vx: float, vy: float, vw: float, vh: float,
    y_model_min: float,
    y_model_max: float,
) -> None:
    """Add a dashed vertical section cut line and A-301 callouts on the plan."""
    y0 = vy
    y1 = vy + vh

    # Dashed cut line in the geometry group (model coordinates)
    ET.SubElement(
        geo_group,
        _ns("polyline"),
        {
            "points": _make_point([
                (SECTION_CUT_X, y_model_min),
                (SECTION_CUT_X, y_model_max),
            ]),
            "fill": "none",
            "stroke": "#E53935",
            "stroke-width": "3",
            "stroke-dasharray": "12,6",
            "vector-effect": "non-scaling-stroke",
            "data-layer": "ANNOTATION_SECTION",
        },
    )

    # Arrow heads at each end point RIGHT (viewer looks from +X toward -X)
    arrow_size = 250.0
    for tip_y in (y_model_max, y_model_min):
        ET.SubElement(
            geo_group,
            _ns("polyline"),
            {
                "points": _make_point([
                    (SECTION_CUT_X - arrow_size * 0.4, tip_y - arrow_size * 0.15),
                    (SECTION_CUT_X, tip_y),
                    (SECTION_CUT_X - arrow_size * 0.4, tip_y + arrow_size * 0.15),
                ]),
                "fill": "none",
                "stroke": "#E53935",
                "stroke-width": "3",
                "vector-effect": "non-scaling-stroke",
                "data-layer": "ANNOTATION_SECTION",
            },
        )

    # "A-301" label at top and bottom of cut
    label_y_top = y_model_max - 600.0
    label_y_bot = y_model_min + 600.0

    ET.SubElement(
        text_group,
        _ns("text"),
        {
            "x": f"{SECTION_CUT_X:g}",
            "y": f"{_model_to_svg_y(y0, y1, label_y_top):g}",
            "font-size": "28",
            "fill": "#E53935",
            "font-weight": "bold",
            "text-anchor": "middle",
            "data-layer": "ANNOTATION_SECTION_TEXT",
        },
    ).text = "A-301"

    ET.SubElement(
        text_group,
        _ns("text"),
        {
            "x": f"{SECTION_CUT_X:g}",
            "y": f"{_model_to_svg_y(y0, y1, label_y_bot):g}",
            "font-size": "28",
            "fill": "#E53935",
            "font-weight": "bold",
            "text-anchor": "middle",
            "data-layer": "ANNOTATION_SECTION_TEXT",
        },
    ).text = "A-301"


def add_section_cut_annotation(root: ET.Element, geo_group: ET.Element, text_group: ET.Element) -> None:
    """Add section cut to the plan view."""
    vx, vy, vw, vh = parse_viewbox(root)
    y0 = vy
    y1 = vy + vh

    # model_y min = y0 (bottom of plan), model_y max = y1 (top of plan)
    # due to the Y-flip transform: model_y = y0 + y1 - svg_y
    model_y_min = y0  # bottom of plan in model space = most negative Y
    model_y_max = y1  # top of plan in model space = most positive Y

    add_section_cut_line(root, geo_group, text_group, vx, vy, vw, vh, model_y_min, model_y_max)


# ---- elevation markers ------------------------------------------------------

def add_elevation_marker(
    root: ET.Element,
    geo_group: ET.Element,
    text_group: ET.Element,
    cx: float,
    cy: float,
    label: str,
    direction: str,
) -> None:
    """Add an elevation marker with triangle pointer.

    Args:
        cx, cy: Center of the marker circle in model coordinates.
        label: Sheet number (e.g. "A-201").
        direction: "up", "down", "left", or "right" — where the triangle points.
    """
    vx, vy, vw, vh = parse_viewbox(root)
    y0 = vy
    y1 = vy + vh
    r = 280.0  # circle radius
    tri_size = 500.0

    # Circle outline (24-sided polygon approximation)
    steps = 24
    circ_pts = [(cx + r * math.cos(2 * math.pi * i / steps),
                 cy + r * math.sin(2 * math.pi * i / steps))
                for i in range(steps)]

    ET.SubElement(
        geo_group,
        _ns("polygon"),
        {
            "points": _make_point(circ_pts),
            "fill": "#ffffff",
            "stroke": "#111111",
            "stroke-width": "3",
            "vector-effect": "non-scaling-stroke",
            "data-layer": "ANNOTATION_MARKER",
        },
    )

    # Direction triangle (tip points in view direction)
    if direction == "up":
        tri_points = [(cx, cy + tri_size),
                      (cx - tri_size * 0.6, cy - tri_size * 0.1),
                      (cx + tri_size * 0.6, cy - tri_size * 0.1)]
    elif direction == "down":
        tri_points = [(cx, cy - tri_size),
                      (cx - tri_size * 0.6, cy + tri_size * 0.1),
                      (cx + tri_size * 0.6, cy + tri_size * 0.1)]
    elif direction == "left":
        tri_points = [(cx - tri_size, cy),
                      (cx + tri_size * 0.1, cy + tri_size * 0.6),
                      (cx + tri_size * 0.1, cy - tri_size * 0.6)]
    elif direction == "right":
        tri_points = [(cx + tri_size, cy),
                      (cx - tri_size * 0.1, cy + tri_size * 0.6),
                      (cx - tri_size * 0.1, cy - tri_size * 0.6)]
    else:
        tri_points = [(cx, cy), (cx, cy), (cx, cy)]

    ET.SubElement(
        geo_group,
        _ns("polygon"),
        {
            "points": _make_point(tri_points),
            "fill": "#111111",
            "stroke": "#111111",
            "stroke-width": "2",
            "vector-effect": "non-scaling-stroke",
            "data-layer": "ANNOTATION_MARKER",
        },
    )

    # Label text (centered in circle, slightly offset in model coords)
    label_offset_y = -50.0
    ET.SubElement(
        text_group,
        _ns("text"),
        {
            "x": f"{cx:g}",
            "y": f"{_model_to_svg_y(y0, y1, cy + label_offset_y):g}",
            "font-size": "22",
            "fill": "#111111",
            "font-weight": "bold",
            "text-anchor": "middle",
            "data-layer": "ANNOTATION_MARKER_TEXT",
        },
    ).text = label


# ---- door/window schedule ---------------------------------------------------

def add_door_schedule(
    root: ET.Element,
    geo_group: ET.Element,
    text_group: ET.Element,
) -> None:
    """Add a small door/window schedule table overlay on the plan sheet."""
    vx, vy, vw, vh = parse_viewbox(root)
    y0 = vy
    y1 = vy + vh

    # Table position in model coordinates (bottom-left area of the plan)
    table_x = vx + vw * 0.04  # 4% from left edge
    # Model Y: header at table_y (higher value = appears higher in SVG).
    # Data rows go to LOWER model Y values (more negative = appear lower in SVG).
    table_y = y0 + 1400.0  # well within viewport when extended downward

    # SVG space Y for text (y = y0 + y1 - model_y)
    svg_table_y = _model_to_svg_y(y0, y1, table_y)

    col_x = [table_x, table_x + 2000.0, table_x + 4500.0, table_x + 6200.0]
    headers = ["Opening", "Type", "Width", "Height"]
    row_height = 350.0
    font_size = 18

    # Table header row
    for col, header in zip(col_x, headers):
        ET.SubElement(
            text_group,
            _ns("text"),
            {
                "x": f"{col:g}",
                "y": f"{svg_table_y:g}",
                "font-size": str(font_size),
                "font-weight": "bold",
                "fill": "#000000",
                "data-layer": "ANNOTATION_SCHEDULE",
            },
        ).text = header

    # Header underline (just below header text = more negative model_y)
    underline_y = table_y - 20.0
    ET.SubElement(
        geo_group,
        _ns("line"),
        {
            "x1": f"{col_x[0]:g}",
            "y1": f"{underline_y:g}",
            "x2": f"{col_x[-1] + 1500:g}",
            "y2": f"{underline_y:g}",
            "stroke": "#000000",
            "stroke-width": "2",
            "vector-effect": "non-scaling-stroke",
            "data-layer": "ANNOTATION_SCHEDULE",
        },
    )

    # Schedule data rows — values match the model's sliding door (6'0" x 7'0")
    rows = [
        ("SD-01", "Sliding Glass Door", '6\'-0" (1,829mm)', '7\'-0" (2,134mm)'),
    ]

    for i, (mark, type_name, width_str, height_str) in enumerate(rows):
        # Each data row goes below the previous (more negative model_y)
        model_row_y = table_y - (i + 1) * row_height
        row_svg_y = _model_to_svg_y(y0, y1, model_row_y)
        data = [mark, type_name, width_str, height_str]

        for col, value in zip(col_x, data):
            ET.SubElement(
                text_group,
                _ns("text"),
                {
                    "x": f"{col:g}",
                    "y": f"{row_svg_y:g}",
                    "font-size": str(font_size - 2),
                    "fill": "#333333",
                    "data-layer": "ANNOTATION_SCHEDULE",
                },
            ).text = value

        # Row separator line (just below data text)
        sep_y = model_row_y - 20.0
        ET.SubElement(
            geo_group,
            _ns("line"),
            {
                "x1": f"{col_x[0]:g}",
                "y1": f"{sep_y:g}",
                "x2": f"{col_x[-1] + 1500:g}",
                "y2": f"{sep_y:g}",
                "stroke": "#cccccc",
                "stroke-width": "1",
                "vector-effect": "non-scaling-stroke",
                "data-layer": "ANNOTATION_SCHEDULE",
            },
        )

    # Table border rectangle
    # Top at header level, bottom below last row
    border_bottom = table_y - (len(rows) + 1) * row_height - 200.0
    ET.SubElement(
        geo_group,
        _ns("polygon"),
        {
            "points": _make_point([
                (table_x, table_y),
                (col_x[-1] + 1500.0, table_y),
                (col_x[-1] + 1500.0, border_bottom),
                (table_x, border_bottom),
            ]),
            "fill": "none",
            "stroke": "#000000",
            "stroke-width": "2",
            "vector-effect": "non-scaling-stroke",
            "data-layer": "ANNOTATION_SCHEDULE",
        },
    )

    # Schedule title (above header = more positive model_y)
    title_model_y = table_y + 350.0
    title_svg_y = _model_to_svg_y(y0, y1, title_model_y)
    ET.SubElement(
        text_group,
        _ns("text"),
        {
            "x": f"{col_x[0]:g}",
            "y": f"{title_svg_y:g}",
            "font-size": str(font_size + 4),
            "font-weight": "bold",
            "fill": "#000000",
            "data-layer": "ANNOTATION_SCHEDULE",
        },
    ).text = "DOOR & WINDOW SCHEDULE"


# ---- SVG annotation ---------------------------------------------------------

def annotate_plan_svg(svg_path: Path) -> None:
    """Add all plan-specific annotations to the plan SVG."""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Strip any old annotations first (idempotency)
    _strip_old_annotations(root)

    groups = list(root.findall(_ns("g")))
    if len(groups) < 2:
        return

    geo_group = groups[0]  # geometry group with Y-flip transform
    text_group = groups[1]  # text group (no transform, y = y0+y1 - model_y)

    add_section_cut_annotation(root, geo_group, text_group)
    add_elevation_marker(root, geo_group, text_group, cx=5500.0, cy=1600.0, label="A-201", direction="down")
    add_elevation_marker(root, geo_group, text_group, cx=13500.0, cy=-3500.0, label="A-202", direction="left")
    add_door_schedule(root, geo_group, text_group)

    tree.write(svg_path, encoding="utf-8", xml_declaration=True)


def annotate_svg(svg_path: Path) -> bool:
    """Annotate an SVG file if it is a known sheet type.

    Returns True if annotations were added.
    """
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError:
        return False

    sheet = tree.getroot().get("data-sheet", "")

    if sheet == "A-101":
        annotate_plan_svg(svg_path)
        return True

    return False


# ---- DXF annotation ---------------------------------------------------------

def annotate_dxf(dxf_path: Path) -> bool:
    """Annotate a DXF file if it is a plan sheet.

    Returns True if annotations were added.
    """
    try:
        import ezdxf
    except ImportError:
        return False  # ezdxf not available

    try:
        doc = ezdxf.readfile(dxf_path)
    except Exception:
        return False

    # Check if this is the plan view
    # DXF files don't have sheet metadata, so we check by filename
    if "plan" not in dxf_path.stem.lower():
        return False

    msp = doc.modelspace()

    # Remove any existing annotation entities for idempotency
    ann_layer = "ANNOTATIONS"
    to_delete = [e for e in msp if e.dxf.layer == ann_layer]
    for e in to_delete:
        msp.delete_entity(e)

    # Create annotation layer if it doesn't exist
    if ann_layer not in doc.layers:
        doc.layers.new(ann_layer, dxfattribs={"color": 1, "lineweight": 25})

    # Section cut line (dashed)
    # DXF coordinates are in model space (same as SVG model coordinates)
    cut_x = SECTION_CUT_X

    # Find extents from existing geometry
    y_min = -17446.8  # default plan viewport bottom
    y_max = 2206.7   # default plan viewport top
    for entity in msp:
        if entity.dxftype() in ("LWPOLYLINE", "LINE", "POLYLINE"):
            if hasattr(entity, "get_points"):
                pts = list(entity.get_points("xy"))
                for pt in pts:
                    y_min = min(y_min, pt[1])
                    y_max = max(y_max, pt[1])
            elif entity.dxftype() == "LINE":
                y_min = min(y_min, entity.dxf.start.y, entity.dxf.end.y)
                y_max = max(y_max, entity.dxf.start.y, entity.dxf.end.y)

    margin = (y_max - y_min) * 0.02
    y_min += margin
    y_max -= margin

    # Section cut line
    msp.add_line((cut_x, y_min), (cut_x, y_max), dxfattribs={"layer": ann_layer, "linetype": "DASHED", "color": 1})

    # Section arrows
    arrow = 200.0
    for y_pos in (y_max, y_min):
        msp.add_line((cut_x, y_pos), (cut_x - arrow * 0.4, y_pos - arrow * 0.15), dxfattribs={"layer": ann_layer})
        msp.add_line((cut_x, y_pos), (cut_x - arrow * 0.4, y_pos + arrow * 0.15), dxfattribs={"layer": ann_layer})

    # A-301 label
    msp.add_text("A-301", height=350, dxfattribs={"layer": ann_layer}).set_placement((cut_x - 500, y_max - 300))

    # Elevation markers
    def add_dxf_elevation(cx, cy, label, direction):
        r = 280
        # Circle as polygon
        pts = [(cx + r * math.cos(2 * math.pi * i / 24),
                cy + r * math.sin(2 * math.pi * i / 24))
               for i in range(24)]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": ann_layer})

        # Direction triangle
        tri_size = 500
        if direction == "down":
            tri = [(cx, cy), (cx - tri_size * 0.6, cy + tri_size),
                   (cx + tri_size * 0.6, cy + tri_size)]
        elif direction == "left":
            tri = [(cx, cy), (cx - tri_size, cy - tri_size * 0.6),
                   (cx - tri_size, cy + tri_size * 0.6)]
        else:
            tri = [(cx, cy), (cx, cy), (cx, cy)]
        msp.add_lwpolyline(tri, close=True, dxfattribs={"layer": ann_layer})

        msp.add_text(label, height=250, dxfattribs={"layer": ann_layer}).set_placement((cx, cy + 100))

    add_dxf_elevation(5500.0, 1600.0, "A-201", "down")
    add_dxf_elevation(13500.0, -3500.0, "A-202", "left")

    # Door schedule
    sx = -1530.34
    sy = y_min + 600
    headers = ["Opening", "Type", "Width", "Height"]
    col_w = [2000, 2500, 1800, 1800]
    col_starts = [0]
    for cw in col_w:
        col_starts.append(col_starts[-1] + cw)
    total_w = col_starts[-1]
    row_h = 350

    for j, hdr in enumerate(headers):
        x_pos = sx + col_starts[j]
        msp.add_text(hdr, height=200, dxfattribs={"layer": ann_layer}).set_placement((x_pos, sy))

    # Schedule table line
    msp.add_line((sx, sy - 50), (sx + total_w, sy - 50), dxfattribs={"layer": ann_layer})

    # Data row
    data = ["SD-01", "Sliding Glass Door", '6\'-0"', '7\'-0"']
    for j, val in enumerate(data):
        x_pos = sx + col_starts[j]
        msp.add_text(val, height=180, dxfattribs={"layer": ann_layer}).set_placement((x_pos, sy - row_h))

    # Table border
    msp.add_lwpolyline([
        (sx, sy + 100),
        (sx + total_w, sy + 100),
        (sx + total_w, sy - row_h - 100),
        (sx, sy - row_h - 100),
    ], close=True, dxfattribs={"layer": ann_layer})

    doc.saveas(dxf_path)
    return True


# ---- main entry points ------------------------------------------------------

def annotate_all() -> list[Path]:
    """Find and annotate all CAD drawing files in the generated output.

    Returns paths to all annotated files (SVG and DXF).
    """
    annotated: list[Path] = []

    svg_dir = GENERATED_DIR / "drawings" / "svg"
    if svg_dir.exists():
        for svg_path in sorted(svg_dir.glob("*.svg")):
            if annotate_svg(svg_path):
                print(f"  Annotated SVG: {svg_path.name}")
                annotated.append(svg_path)

    dxf_dir = GENERATED_DIR / "drawings" / "dxf"
    if dxf_dir.exists():
        for dxf_path in sorted(dxf_dir.glob("*.dxf")):
            if annotate_dxf(dxf_path):
                print(f"  Annotated DXF: {dxf_path.name}")
                annotated.append(dxf_path)

    return annotated


def rebuild_and_annotate() -> int:
    """Run build.py then annotate."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "build.py")],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return result.returncode

    print("\n--- Post-processing annotations ---")
    return main()


def main() -> int:
    """Entry point: annotate all drawings."""
    print("Drawing annotation post-processor")
    paths = annotate_all()
    if not paths:
        print("  No files annotated")
        return 0
    print(f"  Total: {len(paths)} file(s) annotated")
    return 0


# ---- automatic registration (when imported by build) -------------------------

# Registered only when imported (not when run as __main__).  The managed build
# loads model.py which imports drawing_annotations, triggering registration.
# By the time Python exits the build pipeline has exported all drawings to
# generated/, so annotate_all() can post-process them without modifying managed
# tooling.  When run directly as __main__ the main() function handles calling
# annotate_all(), so registration would create a redundant at-exit pass.
if __name__ != "__main__":
    atexit.register(annotate_all)

if __name__ == "__main__":
    if "--rebuild" in sys.argv:
        raise SystemExit(rebuild_and_annotate())
    raise SystemExit(main())
