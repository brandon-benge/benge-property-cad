"""Deck board and framing geometry; keep this focused module below 400 lines."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.elements import Dimensions, IfcMapping
from python_cad_tools.geometry import bounds, box
from python_cad_tools.units import MM, Length, to_mm

from models.shared import Color, Point2, _cut_capsule


def add_decks(builder: Any, cfg: Any) -> None:
    """Append upper and lower deck boards and framing in stable order."""

    def add_deck_boards(
        prefix: str,
        x: Length,
        y: Length,
        length: Length,
        depth: Length,
        z: Length,
        direction: str,
        cutouts: list[tuple[Length, Length, Length, Length]] | None = None,
        capsule_cutouts: list[tuple[Length, Length, Length, Length]] | None = None,
    ) -> None:
        board_z = z - cfg.DECK_BOARD_THICKNESS
        pitch = cfg.DECK_BOARD_WIDTH + cfg.DECK_BOARD_GAP
        index = 1
        deck_cutouts = cutouts or []
        deck_capsules = capsule_cutouts or []

        def subtract_spans(
            spans: list[tuple[Length, Length]],
            cut_start: Length,
            cut_end: Length,
        ) -> list[tuple[Length, Length]]:
            remaining: list[tuple[Length, Length]] = []
            for span_start, span_end in spans:
                if cut_end <= span_start or cut_start >= span_end:
                    remaining.append((span_start, span_end))
                    continue
                if span_start < cut_start:
                    remaining.append((span_start, cut_start))
                if cut_end < span_end:
                    remaining.append((cut_end, span_end))
            return remaining

        def capsule_cutout_span(
            board_start_y: Length,
            board_end_y: Length,
            cut_x: Length,
            cut_y: Length,
            cut_length: Length,
            cut_width: Length,
        ) -> tuple[Length, Length] | None:
            overlap_start = max(board_start_y, cut_y)
            overlap_end = min(board_end_y, cut_y + cut_width)
            if overlap_end <= overlap_start:
                return None

            center_y = cut_y + cut_width / 2
            if overlap_start <= center_y <= overlap_end:
                return cut_x, cut_x + cut_length

            sample_y = (
                overlap_start
                if to_mm(abs(overlap_start - center_y)) <= to_mm(abs(overlap_end - center_y))
                else overlap_end
            )
            radius_mm = to_mm(cut_width / 2)
            dy_mm = to_mm(abs(sample_y - center_y))
            if dy_mm >= radius_mm:
                return cut_x + cut_width / 2, cut_x + cut_length - cut_width / 2
            inset_mm = radius_mm - math.sqrt(max(0.0, radius_mm * radius_mm - dy_mm * dy_mm))
            inset = inset_mm * MM
            return cut_x + inset, cut_x + cut_length - inset

        if direction == "x":
            board_y = y
            while board_y < y + depth:
                board_depth = min(cfg.DECK_BOARD_WIDTH, y + depth - board_y)
                board_spans: list[tuple[Length, Length]] = [(x, x + length)]
                for cut_x0, cut_x1, cut_y0, cut_y1 in deck_cutouts:
                    if board_y < cut_y1 and board_y + board_depth > cut_y0:
                        board_spans = subtract_spans(board_spans, cut_x0, cut_x1)
                for cut_x, cut_y, cut_length, cut_width in deck_capsules:
                    capsule_span = capsule_cutout_span(
                        board_y, board_y + board_depth, cut_x, cut_y, cut_length, cut_width
                    )
                    if capsule_span is not None:
                        board_spans = subtract_spans(board_spans, capsule_span[0], capsule_span[1])
                for segment_index, (span_start, span_end) in enumerate(board_spans, 1):
                    segment_length = span_end - span_start
                    if to_mm(segment_length) <= 0:
                        continue
                    segment_suffix = ""
                    if len(board_spans) > 1:
                        segment_suffix = "_Left" if segment_index == 1 else "_Right"
                    builder.add_box(
                        "deck-board",
                        f"{prefix}DeckBoard_{index:02d}{segment_suffix}",
                        segment_length,
                        board_depth,
                        cfg.DECK_BOARD_THICKNESS,
                        span_start,
                        board_y,
                        board_z,
                        cfg.DECK_COLOR,
                    )
                board_y = board_y + pitch
                index += 1
        else:
            board_x = x
            while board_x < x + length:
                board_length = min(cfg.DECK_BOARD_WIDTH, x + length - board_x)
                builder.add_box(
                    "deck-board",
                    f"{prefix}DeckBoard_{index:02d}",
                    board_length,
                    depth,
                    cfg.DECK_BOARD_THICKNESS,
                    board_x,
                    y,
                    board_z,
                    cfg.DECK_COLOR,
                )
                board_x = board_x + pitch
                index += 1

    def add_deck_framing(
        prefix: str,
        x: Length,
        y: Length,
        length: Length,
        depth: Length,
        z: Length,
        post_points: list[Point2],
        *,
        mid_beam_y: Length | None = None,
        mid_beam_properties: dict[str, Any] | None = None,
        capsule_cutouts: list[tuple[Length, Length, Length, Length]] | None = None,
    ) -> None:
        frame_top = z - cfg.DECK_BOARD_THICKNESS
        joist_z = frame_top - cfg.JOIST_HEIGHT
        beam_z = joist_z - cfg.BEAM_HEIGHT
        joist_cutouts = [
            _cut_capsule(cut_length, cut_width, cfg.JOIST_HEIGHT, origin=(cut_x, cut_y, joist_z))
            for cut_x, cut_y, cut_length, cut_width in (capsule_cutouts or [])
        ]

        def add_framing_box(
            name: str,
            length: Length,
            depth: Length,
            height: Length,
            x: Length,
            y: Length,
            z: Length,
            color: Color,
            *,
            drawing_label: bool = False,
            properties: dict[str, Any] | None = None,
            physical: bool = True,
            parent_id: str | None = None,
            export_formats: set[str] | None = None,
            stable_id: str | None = None,
            ifc_mapping: IfcMapping | None = None,
        ) -> None:
            shape = box(length, depth, height, origin=(x, y, z))
            for cutout in joist_cutouts:
                shape = shape.cut(cutout)
            pieces = shape.solids()
            if len(pieces) <= 1:
                builder.add_shape(
                    "deck-framing",
                    name,
                    shape,
                    color,
                    Dimensions(to_mm(length), to_mm(depth), to_mm(height)),
                    placement=(x, y, z),
                    drawing_label=drawing_label,
                    properties=properties,
                    physical=physical,
                    parent_id=parent_id,
                    export_formats=export_formats,
                    stable_id=stable_id,
                    ifc_mapping=ifc_mapping,
                )
                return
            ordered_pieces = sorted(pieces, key=lambda solid: bounds(solid)[0])
            suffixes = (
                ["_Left", "_Right"] if len(pieces) == 2 else [f"_{index:02d}" for index in range(1, len(pieces) + 1)]
            )
            for suffix, solid in zip(suffixes, ordered_pieces, strict=True):
                piece_bounds = bounds(solid)
                builder.add_shape(
                    "deck-framing",
                    f"{name}{suffix}",
                    solid,
                    color,
                    Dimensions(
                        piece_bounds[3] - piece_bounds[0],
                        piece_bounds[4] - piece_bounds[1],
                        piece_bounds[5] - piece_bounds[2],
                    ),
                    placement=(piece_bounds[0] * MM, piece_bounds[1] * MM, piece_bounds[2] * MM),
                    drawing_label=drawing_label,
                    properties=properties,
                    physical=physical,
                    parent_id=parent_id,
                    export_formats=export_formats,
                    stable_id=None,
                    ifc_mapping=ifc_mapping,
                )

        add_framing_box(
            f"{prefix}FrontRimJoist", length, cfg.JOIST_WIDTH, cfg.JOIST_HEIGHT, x, y, joist_z, cfg.SKIRTING_COLOR
        )
        add_framing_box(
            f"{prefix}BackLedger",
            length,
            cfg.JOIST_WIDTH,
            cfg.JOIST_HEIGHT,
            x,
            y + depth - cfg.JOIST_WIDTH,
            joist_z,
            cfg.SKIRTING_COLOR,
        )
        add_framing_box(
            f"{prefix}LeftRimJoist", cfg.JOIST_WIDTH, depth, cfg.JOIST_HEIGHT, x, y, joist_z, cfg.SKIRTING_COLOR
        )
        add_framing_box(
            f"{prefix}RightRimJoist",
            cfg.JOIST_WIDTH,
            depth,
            cfg.JOIST_HEIGHT,
            x + length - cfg.JOIST_WIDTH,
            y,
            joist_z,
            cfg.SKIRTING_COLOR,
        )
        joist_x = x + cfg.JOIST_SPACING
        joist_index = 1
        while joist_x < x + length - cfg.JOIST_WIDTH:
            add_framing_box(
                f"{prefix}Joist_{joist_index:02d}",
                cfg.JOIST_WIDTH,
                depth,
                cfg.JOIST_HEIGHT,
                joist_x,
                y,
                joist_z,
                cfg.SKIRTING_COLOR,
            )
            joist_x = joist_x + cfg.JOIST_SPACING
            joist_index += 1
        add_framing_box(
            f"{prefix}FrontBeam",
            length,
            cfg.BEAM_WIDTH,
            cfg.BEAM_HEIGHT,
            x,
            y - cfg.BEAM_WIDTH,
            beam_z,
            cfg.RAILING_COLOR,
        )
        if depth > 8 * cfg.FOOT:
            resolved_mid_beam_y = mid_beam_y if mid_beam_y is not None else y + depth / 2 - cfg.BEAM_WIDTH / 2
            add_framing_box(
                f"{prefix}MidBeam",
                length,
                cfg.BEAM_WIDTH,
                cfg.BEAM_HEIGHT,
                x,
                resolved_mid_beam_y,
                beam_z,
                cfg.RAILING_COLOR,
                properties=mid_beam_properties,
            )
        for index, (post_x, post_y) in enumerate(post_points, 1):
            add_framing_box(
                f"{prefix}SupportPost_{index:02d}",
                cfg.SUPPORT_POST_SIZE,
                cfg.SUPPORT_POST_SIZE,
                beam_z,
                post_x - cfg.SUPPORT_POST_SIZE / 2,
                post_y - cfg.SUPPORT_POST_SIZE / 2,
                0 * MM,
                cfg.RAILING_COLOR,
            )

    add_deck_boards(
        "Upper",
        0 * MM,
        -cfg.UPPER_DECK_DEPTH,
        cfg.UPPER_DECK_WIDTH,
        cfg.UPPER_DECK_DEPTH,
        cfg.UPPER_DECK_ELEVATION,
        "x",
    )
    add_deck_framing(
        "Upper",
        0 * MM,
        -cfg.UPPER_DECK_DEPTH,
        cfg.UPPER_DECK_WIDTH,
        cfg.UPPER_DECK_DEPTH,
        cfg.UPPER_DECK_ELEVATION,
        [
            (0 * MM, -cfg.UPPER_DECK_DEPTH),
            (cfg.UPPER_DECK_WIDTH / 2, -cfg.UPPER_DECK_DEPTH),
            (cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH),
            (0 * MM, -cfg.UPPER_DECK_DEPTH / 2),
            (cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH / 2),
        ],
        mid_beam_properties={
            "complex_type": "deck_support_beam",
            "assembly_role": "mid_span_support",
            "supports": "complex.deck_board.upper_*",
            "clear_of": "complex.skirting.upper_deck_left_skirt_access_panel",
        },
    )

    lower_x = 0 * MM
    pool_length = cfg.POOL_LENGTH
    pool_width = cfg.POOL_WIDTH
    pool_x = cfg.POOL_CENTER_X - pool_length / 2
    pool_y = cfg.POOL_CENTER_Y - pool_width / 2
    lower_mid_beam_y = -(cfg.HOT_TUB_DEPTH + cfg.FOOT) - cfg.BEAM_FEATURE_CLEARANCE - cfg.BEAM_WIDTH
    capsule_cutouts = [(pool_x, pool_y, pool_length, pool_width)]
    add_deck_boards(
        "Lower",
        lower_x,
        -cfg.LOWER_DECK_DEPTH,
        cfg.LOWER_DECK_WIDTH,
        cfg.LOWER_DECK_DEPTH,
        cfg.LOWER_DECK_ELEVATION,
        "x",
        capsule_cutouts=capsule_cutouts,
    )
    add_deck_framing(
        "Lower",
        lower_x,
        -cfg.LOWER_DECK_DEPTH,
        cfg.LOWER_DECK_WIDTH,
        cfg.LOWER_DECK_DEPTH,
        cfg.LOWER_DECK_ELEVATION,
        [
            (lower_x, -cfg.LOWER_DECK_DEPTH),
            (lower_x + cfg.LOWER_DECK_WIDTH / 2, -cfg.LOWER_DECK_DEPTH),
            (lower_x + cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
            (lower_x + cfg.LOWER_DECK_WIDTH, lower_mid_beam_y + cfg.BEAM_WIDTH / 2),
        ],
        mid_beam_y=lower_mid_beam_y,
        mid_beam_properties={
            "complex_type": "deck_support_beam",
            "assembly_role": "mid_span_support",
            "supports": "complex.deck_board.lower_*",
            "clear_of": "complex.feature.hot_tub_placeholder",
            "minimum_clearance_mm": to_mm(cfg.BEAM_FEATURE_CLEARANCE),
        },
        capsule_cutouts=capsule_cutouts,
    )
