import FreeCAD as App
import Part
import config as cfg
import helpers

def build_model(doc, parent=None):
    site = doc.addObject("App::Part", "Site")
    house_g = doc.addObject("App::Part", "House")
    decks_g = doc.addObject("App::Part", "Decks")
    stairs_g = doc.addObject("App::Part", "Stairs")
    rails_g = doc.addObject("App::Part", "Railings")
    skirting_g = doc.addObject("App::Part", "Skirting")
    features_g = doc.addObject("App::Part", "Features")
    pool_g = doc.addObject("App::Part", "PoolArea")

    if parent is not None:
        parent.addObject(site)
        parent.addObject(house_g)
        parent.addObject(decks_g)
        parent.addObject(stairs_g)
        parent.addObject(rails_g)
        parent.addObject(skirting_g)
        parent.addObject(features_g)
        parent.addObject(pool_g)

    # Coordinate convention:
    # X = left/right across front of house
    # Y = front-to-back (house positive Y, decks/pool negative Y)
    # Z = elevation

    def add_box(group, name, length, depth, height, x, y, z, color):
        return helpers.add_shape(
            doc,
            group,
            name,
            helpers.box_at(length, depth, height, x, y, z),
            color,
        )

    def add_deck_boards(group, prefix, x, y, length, depth, z, direction="x"):
        board_z = z - cfg.DECK_BOARD_THICKNESS
        pitch = cfg.DECK_BOARD_WIDTH + cfg.DECK_BOARD_GAP
        index = 1
        if direction == "x":
            board_y = y
            while board_y < y + depth:
                board_depth = min(cfg.DECK_BOARD_WIDTH, y + depth - board_y)
                add_box(group, f"{prefix}DeckBoard_{index:02d}",
                        length, board_depth, cfg.DECK_BOARD_THICKNESS,
                        x, board_y, board_z, cfg.DECK_COLOR)
                board_y += pitch
                index += 1
        else:
            board_x = x
            while board_x < x + length:
                board_length = min(cfg.DECK_BOARD_WIDTH, x + length - board_x)
                add_box(group, f"{prefix}DeckBoard_{index:02d}",
                        board_length, depth, cfg.DECK_BOARD_THICKNESS,
                        board_x, y, board_z, cfg.DECK_COLOR)
                board_x += pitch
                index += 1

    def add_deck_framing(prefix, x, y, length, depth, z, post_points):
        frame_top = z - cfg.DECK_BOARD_THICKNESS
        joist_z = frame_top - cfg.JOIST_HEIGHT
        beam_z = joist_z - cfg.BEAM_HEIGHT

        add_box(decks_g, f"{prefix}FrontRimJoist",
                length, cfg.JOIST_WIDTH, cfg.JOIST_HEIGHT,
                x, y, joist_z, cfg.SKIRTING_COLOR)
        add_box(decks_g, f"{prefix}BackLedger",
                length, cfg.JOIST_WIDTH, cfg.JOIST_HEIGHT,
                x, y + depth - cfg.JOIST_WIDTH, joist_z, cfg.SKIRTING_COLOR)
        add_box(decks_g, f"{prefix}LeftRimJoist",
                cfg.JOIST_WIDTH, depth, cfg.JOIST_HEIGHT,
                x, y, joist_z, cfg.SKIRTING_COLOR)
        add_box(decks_g, f"{prefix}RightRimJoist",
                cfg.JOIST_WIDTH, depth, cfg.JOIST_HEIGHT,
                x + length - cfg.JOIST_WIDTH, y, joist_z, cfg.SKIRTING_COLOR)

        joist_x = x + cfg.JOIST_SPACING
        joist_index = 1
        while joist_x < x + length - cfg.JOIST_WIDTH:
            add_box(decks_g, f"{prefix}Joist_{joist_index:02d}",
                    cfg.JOIST_WIDTH, depth, cfg.JOIST_HEIGHT,
                    joist_x, y, joist_z, cfg.SKIRTING_COLOR)
            joist_x += cfg.JOIST_SPACING
            joist_index += 1

        add_box(decks_g, f"{prefix}FrontBeam",
                length, cfg.BEAM_WIDTH, cfg.BEAM_HEIGHT,
                x, y - cfg.BEAM_WIDTH, beam_z, cfg.RAILING_COLOR)
        if depth > 8 * cfg.FOOT:
            add_box(decks_g, f"{prefix}MidBeam",
                    length, cfg.BEAM_WIDTH, cfg.BEAM_HEIGHT,
                    x, y + depth / 2 - cfg.BEAM_WIDTH / 2, beam_z, cfg.RAILING_COLOR)

        for idx, (px, py) in enumerate(post_points, 1):
            add_box(decks_g, f"{prefix}SupportPost_{idx:02d}",
                    cfg.SUPPORT_POST_SIZE, cfg.SUPPORT_POST_SIZE, beam_z,
                    px - cfg.SUPPORT_POST_SIZE / 2,
                    py - cfg.SUPPORT_POST_SIZE / 2,
                    0,
                    cfg.RAILING_COLOR)

    # House placeholder wall — thin wall spanning the length of the top deck.
    add_box(house_g, "HouseMass",
            cfg.HOUSE_WIDTH, cfg.HOUSE_DEPTH, cfg.HOUSE_HEIGHT,
            0, 0, 0, cfg.HOUSE_COLOR)

    # Deck boards run parallel to the house so seams read across the deck depth.
    add_deck_boards(decks_g, "Upper",
                    0, -cfg.UPPER_DECK_DEPTH,
                    cfg.UPPER_DECK_WIDTH, cfg.UPPER_DECK_DEPTH,
                    cfg.UPPER_DECK_ELEVATION, "x")
    add_deck_framing("Upper",
                     0, -cfg.UPPER_DECK_DEPTH,
                     cfg.UPPER_DECK_WIDTH, cfg.UPPER_DECK_DEPTH,
                     cfg.UPPER_DECK_ELEVATION,
                     [
                         (0, -cfg.UPPER_DECK_DEPTH),
                         (cfg.UPPER_DECK_WIDTH / 2, -cfg.UPPER_DECK_DEPTH),
                         (cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH),
                         (0, -cfg.UPPER_DECK_DEPTH / 2),
                         (cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH / 2),
                     ])

    lower_x = cfg.UPPER_DECK_WIDTH
    add_deck_boards(decks_g, "Lower",
                    lower_x, -cfg.LOWER_DECK_DEPTH,
                    cfg.LOWER_DECK_WIDTH, cfg.LOWER_DECK_DEPTH,
                    cfg.LOWER_DECK_ELEVATION, "y")
    add_deck_framing("Lower",
                     lower_x, -cfg.LOWER_DECK_DEPTH,
                     cfg.LOWER_DECK_WIDTH, cfg.LOWER_DECK_DEPTH,
                     cfg.LOWER_DECK_ELEVATION,
                     [
                         (lower_x, -cfg.LOWER_DECK_DEPTH),
                         (lower_x + cfg.LOWER_DECK_WIDTH / 2, -cfg.LOWER_DECK_DEPTH),
                         (lower_x + cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
                         (lower_x + cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH / 2),
                     ])

    # Full-length upper deck cover
    roof = helpers.box_at(cfg.UPPER_DECK_WIDTH + 2*cfg.ROOF_OVERHANG,
                  cfg.UPPER_DECK_DEPTH + 2*cfg.ROOF_OVERHANG,
                  cfg.ROOF_THICKNESS,
                  -cfg.ROOF_OVERHANG, -cfg.UPPER_DECK_DEPTH - cfg.ROOF_OVERHANG,
                  cfg.UPPER_DECK_ELEVATION + cfg.ROOF_HEIGHT_ABOVE_UPPER)
    helpers.add_shape(doc, features_g, "UpperDeckFullCover", roof, (0.18,0.20,0.22))
    roof_x = -cfg.ROOF_OVERHANG
    roof_y = -cfg.UPPER_DECK_DEPTH - cfg.ROOF_OVERHANG
    roof_w = cfg.UPPER_DECK_WIDTH + 2 * cfg.ROOF_OVERHANG
    roof_d = cfg.UPPER_DECK_DEPTH + 2 * cfg.ROOF_OVERHANG
    roof_z = cfg.UPPER_DECK_ELEVATION + cfg.ROOF_HEIGHT_ABOVE_UPPER
    add_box(features_g, "RoofFrontFascia",
            roof_w, cfg.ROOF_RAFTER_WIDTH, cfg.ROOF_FASCIA_HEIGHT,
            roof_x, roof_y, roof_z - cfg.ROOF_FASCIA_HEIGHT, cfg.RAILING_COLOR)
    add_box(features_g, "RoofLeftFascia",
            cfg.ROOF_RAFTER_WIDTH, roof_d, cfg.ROOF_FASCIA_HEIGHT,
            roof_x, roof_y, roof_z - cfg.ROOF_FASCIA_HEIGHT, cfg.RAILING_COLOR)
    add_box(features_g, "RoofRightFascia",
            cfg.ROOF_RAFTER_WIDTH, roof_d, cfg.ROOF_FASCIA_HEIGHT,
            roof_x + roof_w - cfg.ROOF_RAFTER_WIDTH, roof_y,
            roof_z - cfg.ROOF_FASCIA_HEIGHT, cfg.RAILING_COLOR)
    rafter_x = roof_x + cfg.ROOF_RAFTER_SPACING
    rafter_idx = 1
    while rafter_x < roof_x + roof_w - cfg.ROOF_RAFTER_WIDTH:
        add_box(features_g, f"RoofRafter_{rafter_idx:02d}",
                cfg.ROOF_RAFTER_WIDTH, roof_d, cfg.ROOF_RAFTER_HEIGHT,
                rafter_x, roof_y, roof_z - cfg.ROOF_RAFTER_HEIGHT,
                (0.92,0.92,0.90))
        rafter_x += cfg.ROOF_RAFTER_SPACING
        rafter_idx += 1

    fan_cx = cfg.UPPER_DECK_WIDTH / 2
    fan_cy = -cfg.UPPER_DECK_DEPTH / 2
    fan_hub_z = roof_z - 28 * cfg.INCH
    helpers.add_shape(doc, features_g, "CoveredDeckFanDownrod",
              helpers.cylinder_between(
                  (fan_cx, fan_cy, roof_z - cfg.ROOF_RAFTER_HEIGHT),
                  (fan_cx, fan_cy, fan_hub_z),
                  1.25 * cfg.INCH),
              cfg.RAILING_COLOR)
    helpers.add_shape(doc, features_g, "CoveredDeckFanMotor",
              helpers.cylinder_between(
                  (fan_cx, fan_cy, fan_hub_z - 3 * cfg.INCH),
                  (fan_cx, fan_cy, fan_hub_z + 3 * cfg.INCH),
                  7 * cfg.INCH),
              cfg.RAILING_COLOR)
    blade_len = cfg.FAN_DIAMETER / 2
    blade_z = fan_hub_z
    add_box(features_g, "CoveredDeckFanBlade_X_Pos",
            blade_len, cfg.FAN_BLADE_WIDTH, cfg.INCH,
            fan_cx, fan_cy - cfg.FAN_BLADE_WIDTH / 2, blade_z,
            cfg.SKIRTING_COLOR)
    add_box(features_g, "CoveredDeckFanBlade_X_Neg",
            blade_len, cfg.FAN_BLADE_WIDTH, cfg.INCH,
            fan_cx - blade_len, fan_cy - cfg.FAN_BLADE_WIDTH / 2, blade_z,
            cfg.SKIRTING_COLOR)
    add_box(features_g, "CoveredDeckFanBlade_Y_Pos",
            cfg.FAN_BLADE_WIDTH, blade_len, cfg.INCH,
            fan_cx - cfg.FAN_BLADE_WIDTH / 2, fan_cy, blade_z,
            cfg.SKIRTING_COLOR)
    add_box(features_g, "CoveredDeckFanBlade_Y_Neg",
            cfg.FAN_BLADE_WIDTH, blade_len, cfg.INCH,
            fan_cx - cfg.FAN_BLADE_WIDTH / 2, fan_cy - blade_len, blade_z,
            cfg.SKIRTING_COLOR)

    # Roof support posts
    post = 8 * cfg.INCH
    for idx, (x,y) in enumerate([
        (0,-cfg.UPPER_DECK_DEPTH), (cfg.UPPER_DECK_WIDTH-post,-cfg.UPPER_DECK_DEPTH),
        (0,-post),
        (cfg.UPPER_DECK_WIDTH-post,-post)
    ], 1):
        p = helpers.box_at(post, post, cfg.ROOF_HEIGHT_ABOVE_UPPER,
                   x, y, cfg.UPPER_DECK_ELEVATION)
        helpers.add_shape(doc, features_g, f"RoofPost_{idx}", p, (0.92,0.92,0.90))

    # Brick fireplace against the house wall.
    # Back edge at y=0, extends 6' forward onto the upper deck.
    # Goes from ground (z=0) to 9' above the upper deck.
    add_box(features_g, "FireplaceMasonryBody",
            cfg.FIREPLACE_WIDTH, cfg.FIREPLACE_DEPTH, cfg.FIREPLACE_HEIGHT,
            0, -cfg.FIREPLACE_DEPTH, 0, cfg.BRICK_COLOR)
    fireplace_face_x = cfg.FIREPLACE_WIDTH
    fireplace_center_y = -cfg.FIREPLACE_DEPTH / 2
    add_box(features_g, "FireplaceOpening",
            cfg.INCH, cfg.FIREPLACE_OPENING_WIDTH, cfg.FIREPLACE_OPENING_HEIGHT,
            fireplace_face_x, fireplace_center_y - cfg.FIREPLACE_OPENING_WIDTH / 2,
            cfg.UPPER_DECK_ELEVATION + 12 * cfg.INCH,
            (0.03, 0.03, 0.03))
    add_box(features_g, "ElectricFireplaceGlow",
            1.5 * cfg.INCH, cfg.FIREPLACE_OPENING_WIDTH - 4 * cfg.INCH,
            cfg.FIREPLACE_OPENING_HEIGHT - 6 * cfg.INCH,
            fireplace_face_x + cfg.INCH,
            fireplace_center_y - (cfg.FIREPLACE_OPENING_WIDTH - 4 * cfg.INCH) / 2,
            cfg.UPPER_DECK_ELEVATION + 15 * cfg.INCH,
            (0.90, 0.28, 0.08))
    add_box(features_g, "FireplaceTV",
            cfg.INCH, cfg.TV_WIDTH, cfg.TV_HEIGHT,
            fireplace_face_x + 1.5 * cfg.INCH,
            fireplace_center_y - cfg.TV_WIDTH / 2,
            cfg.UPPER_DECK_ELEVATION + 56 * cfg.INCH,
            (0.02, 0.02, 0.025))

    # Sliding door on the upper deck, 12" from the fireplace
    door = helpers.box_at(cfg.DOOR_WIDTH, 3 * cfg.INCH, 7 * cfg.FOOT,
                 3 * cfg.FOOT, -1.5 * cfg.INCH, cfg.UPPER_DECK_ELEVATION)
    helpers.add_shape(doc, features_g, "SlidingDoor", door, (0.55, 0.70, 0.82), 40)

    # Outdoor kitchen placeholder 2ft forward from the wall
    kitchen_x = 10.5 * cfg.FOOT
    kitchen_y = -2.5 * cfg.FOOT
    add_box(features_g, "OutdoorKitchenCabinetRun",
            cfg.KITCHEN_LENGTH, cfg.KITCHEN_DEPTH,
            cfg.KITCHEN_COUNTER_HEIGHT - cfg.KITCHEN_COUNTER_THICKNESS,
            kitchen_x, kitchen_y, cfg.UPPER_DECK_ELEVATION,
            (0.12,0.12,0.12))
    add_box(features_g, "OutdoorKitchenCountertop",
            cfg.KITCHEN_LENGTH + 4 * cfg.INCH,
            cfg.KITCHEN_DEPTH + 4 * cfg.INCH,
            cfg.KITCHEN_COUNTER_THICKNESS,
            kitchen_x - 2 * cfg.INCH, kitchen_y - 2 * cfg.INCH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - cfg.KITCHEN_COUNTER_THICKNESS,
            (0.45,0.45,0.42))
    sink_x = kitchen_x + 18 * cfg.INCH
    sink_y = kitchen_y + (cfg.KITCHEN_DEPTH - cfg.KITCHEN_SINK_DEPTH) / 2
    add_box(features_g, "OutdoorKitchenSinkBasin",
            cfg.KITCHEN_SINK_WIDTH, cfg.KITCHEN_SINK_DEPTH, 5 * cfg.INCH,
            sink_x, sink_y,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - 5 * cfg.INCH,
            (0.12, 0.15, 0.16))
    helpers.add_shape(doc, features_g, "OutdoorKitchenFaucet",
              helpers.cylinder_between(
                  (sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
                   sink_y + cfg.KITCHEN_SINK_DEPTH,
                   cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT),
                  (sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
                   sink_y + cfg.KITCHEN_SINK_DEPTH,
                   cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT + 10 * cfg.INCH),
                  cfg.INCH),
              (0.75, 0.75, 0.72))
    add_box(features_g, "OutdoorKitchenGrill",
            cfg.KITCHEN_GRILL_WIDTH, cfg.KITCHEN_DEPTH + 2 * cfg.INCH,
            8 * cfg.INCH,
            kitchen_x + cfg.KITCHEN_LENGTH - cfg.KITCHEN_GRILL_WIDTH - 12 * cfg.INCH,
            kitchen_y - cfg.INCH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT,
            (0.05,0.05,0.05))
    for idx, door_x in enumerate((kitchen_x + 12 * cfg.INCH,
                                  kitchen_x + 36 * cfg.INCH,
                                  kitchen_x + 60 * cfg.INCH), 1):
        add_box(features_g, f"OutdoorKitchenDoor_{idx}",
                cfg.KITCHEN_DOOR_WIDTH, cfg.INCH, 24 * cfg.INCH,
                door_x, kitchen_y - cfg.INCH,
                cfg.UPPER_DECK_ELEVATION + 8 * cfg.INCH,
                (0.22,0.22,0.22))

    # Hot tub placeholder — 1' short of far right of the lower deck, 1' above deck
    ht_x = cfg.UPPER_DECK_WIDTH + cfg.LOWER_DECK_WIDTH - cfg.HOT_TUB_WIDTH - 1*cfg.FOOT
    ht_y = -13 * cfg.FOOT
    hot_tub = helpers.box_at(cfg.HOT_TUB_WIDTH, cfg.HOT_TUB_DEPTH, cfg.HOT_TUB_ABOVE_DECK,
                     ht_x, ht_y, cfg.LOWER_DECK_ELEVATION)
    helpers.add_shape(doc, features_g, "HotTubPlaceholder", hot_tub, (0.08,0.10,0.12))

    # Hot tub support platform below the deck
    ht_platform = helpers.box_at(cfg.HOT_TUB_WIDTH, cfg.HOT_TUB_DEPTH,
                        cfg.LOWER_DECK_ELEVATION,
                        ht_x, ht_y, 0)
    helpers.add_shape(doc, features_g, "HotTubPlatform", ht_platform, (0.15,0.15,0.15))

    # Railing dimensions and helper used by upper, lower, and extension rails.
    rail_h = 42 * cfg.INCH
    rail_t = 2 * cfg.INCH
    post_t = 4 * cfg.INCH

    def rail_segment(name, p1, p2, z):
        shape = helpers.line_box_between((p1[0],p1[1],z+rail_h-rail_t),
                                 (p2[0],p2[1],z+rail_h-rail_t),
                                 rail_t, rail_t)
        helpers.add_shape(doc, rails_g, name, shape, cfg.RAILING_COLOR)

    def rail_post(name, x, y, z):
        helpers.add_shape(doc, rails_g, name,
                  helpers.box_at(post_t, post_t, rail_h,
                        x - post_t/2, y - post_t/2, z),
                  cfg.RAILING_COLOR)

    def stair_guardrails(prefix, start, end, start_z, end_z, width):
        dx, dy = end[0] - start[0], end[1] - start[1]
        run = (dx**2 + dy**2) ** 0.5
        ux, uy = dx / run, dy / run
        px, py = -uy, ux

        # Match helpers.stair_run(): tread boxes start at start + perpendicular * width/2
        # and extend another full stair width across the run.
        for side_name, offset in (("Left", width / 2), ("Right", 1.5 * width)):
            sx = start[0] + px * offset
            sy = start[1] + py * offset
            ex = end[0] + px * offset
            ey = end[1] + py * offset
            mx = (sx + ex) / 2
            my = (sy + ey) / 2
            mz = (start_z + end_z) / 2

            helpers.add_shape(doc, rails_g, f"{prefix}{side_name}Handrail",
                      helpers.cylinder_between(
                          (sx, sy, start_z + rail_h),
                          (ex, ey, end_z + rail_h),
                          rail_t),
                      cfg.RAILING_COLOR)
            helpers.add_shape(doc, rails_g, f"{prefix}{side_name}Midrail",
                      helpers.cylinder_between(
                          (sx, sy, start_z + rail_h / 2),
                          (ex, ey, end_z + rail_h / 2),
                          rail_t / 2),
                      cfg.RAILING_COLOR)

            for label, x, y, z in (
                ("Top", sx, sy, start_z),
                ("Mid", mx, my, mz),
                ("Bottom", ex, ey, end_z),
            ):
                rail_post(f"{prefix}{side_name}Post_{label}", x, y, z)

    def stair_skirt_boards(prefix, start, end, start_z, end_z, width):
        dx, dy = end[0] - start[0], end[1] - start[1]
        run = (dx**2 + dy**2) ** 0.5
        px, py = -dy / run, dx / run
        board_t = 2 * cfg.INCH
        board_h = 10 * cfg.INCH
        z_drop = 8 * cfg.INCH

        for side_name, offset in (("Left", width / 2), ("Right", 1.5 * width)):
            sx = start[0] + px * offset
            sy = start[1] + py * offset
            ex = end[0] + px * offset
            ey = end[1] + py * offset
            helpers.add_shape(doc, skirting_g, f"{prefix}{side_name}StairSkirt",
                      helpers.box_between(
                          (sx, sy, start_z - z_drop),
                          (ex, ey, end_z - z_drop),
                          board_t,
                          board_h),
                      cfg.SKIRTING_COLOR)

    def stair_risers(prefix, start, end, start_z, end_z, width):
        dx, dy = end[0] - start[0], end[1] - start[1]
        run = (dx**2 + dy**2) ** 0.5
        steps = max(1, int((abs(start_z - end_z) + cfg.MAX_RISER - 1) // cfg.MAX_RISER))
        ux, uy = dx / run, dy / run
        px, py = -uy, ux
        rise = abs(start_z - end_z) / steps
        for i in range(1, steps + 1):
            t = i / steps
            x = start[0] + dx * t + px * width / 2
            y = start[1] + dy * t + py * width / 2
            z = max(start_z, end_z) - rise * i
            riser = helpers.line_box_between(
                (x, y, z),
                (x + px * width, y + py * width, z),
                1.25 * cfg.INCH,
                rise,
            )
            helpers.add_shape(doc, stairs_g, f"{prefix}Riser_{i:02d}",
                              riser, cfg.SKIRTING_COLOR)

    def skirt_panel(name, length, depth, height, x, y):
        if height <= 0:
            return
        helpers.add_shape(doc, skirting_g, name,
                  helpers.box_at(length, depth, height, x, y, 0),
                  cfg.SKIRTING_COLOR)

    skirt_t = 2 * cfg.INCH
    upper_skirt_h = cfg.UPPER_DECK_ELEVATION - cfg.DECK_THICKNESS
    lower_skirt_h = cfg.LOWER_DECK_ELEVATION - cfg.DECK_THICKNESS

    skirt_panel("UpperDeckFrontSkirt",
                cfg.UPPER_DECK_WIDTH, skirt_t, upper_skirt_h,
                0, -cfg.UPPER_DECK_DEPTH - skirt_t)
    skirt_panel("UpperDeckLeftSkirt",
                skirt_t, cfg.UPPER_DECK_DEPTH, upper_skirt_h,
                -skirt_t, -cfg.UPPER_DECK_DEPTH)
    skirt_panel("UpperDeckRightSkirt",
                skirt_t, cfg.UPPER_DECK_DEPTH, upper_skirt_h,
                cfg.UPPER_DECK_WIDTH, -cfg.UPPER_DECK_DEPTH)
    skirt_panel("LowerDeckFrontSkirt",
                cfg.LOWER_DECK_WIDTH - cfg.STAIR_WIDTH, skirt_t, lower_skirt_h,
                lower_x + cfg.STAIR_WIDTH, -cfg.LOWER_DECK_DEPTH - skirt_t)
    skirt_panel("LowerDeckRightSkirt",
                skirt_t, cfg.LOWER_DECK_DEPTH, lower_skirt_h,
                lower_x + cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH)

    # Straight stair run along Y axis at the edge of the upper deck.
    # Centered on x=UPPER_DECK_WIDTH (24.5'), spanning x=22.5'–26.5'.
    stair_x = cfg.UPPER_DECK_WIDTH - cfg.STAIR_WIDTH / 2
    stair_start_y = -6 * cfg.FOOT
    stair_end_y = -6 * cfg.FOOT - 44 * cfg.INCH
    stair_start = (stair_x, stair_start_y)
    stair_end = (stair_x, stair_end_y)
    helpers.stair_run(doc, stairs_g, "UpperStraightTread",
              stair_start, stair_end,
              cfg.UPPER_DECK_ELEVATION, cfg.LOWER_DECK_ELEVATION,
              cfg.STAIR_WIDTH, cfg.TREAD_DEPTH, cfg.DECK_COLOR)
    stair_risers("UpperStair", stair_start, stair_end,
                 cfg.UPPER_DECK_ELEVATION, cfg.LOWER_DECK_ELEVATION,
                 cfg.STAIR_WIDTH)
    stair_guardrails("UpperStair", stair_start, stair_end,
                     cfg.UPPER_DECK_ELEVATION, cfg.LOWER_DECK_ELEVATION,
                     cfg.STAIR_WIDTH)
    stair_skirt_boards("UpperStair", stair_start, stair_end,
                       cfg.UPPER_DECK_ELEVATION, cfg.LOWER_DECK_ELEVATION,
                       cfg.STAIR_WIDTH)

    # Upper deck extension, matching stair width.
    add_deck_boards(decks_g, "UpperExtension",
                    cfg.UPPER_DECK_WIDTH, -6 * cfg.FOOT,
                    cfg.STAIR_WIDTH, 6 * cfg.FOOT,
                    cfg.UPPER_DECK_ELEVATION, "y")
    add_deck_framing("UpperExtension",
                     cfg.UPPER_DECK_WIDTH, -6 * cfg.FOOT,
                     cfg.STAIR_WIDTH, 6 * cfg.FOOT,
                     cfg.UPPER_DECK_ELEVATION,
                     [
                         (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, -6 * cfg.FOOT),
                         (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, -3 * cfg.FOOT),
                     ])
    skirt_panel("UpperDeckExtensionRightSkirt",
                skirt_t, 6 * cfg.FOOT, upper_skirt_h,
                cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, -6 * cfg.FOOT)

    # Rails and posts for the upper deck extension (back + right side)
    rail_segment("ExtBackRail",
                 (cfg.UPPER_DECK_WIDTH, 0),
                 (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, 0),
                 cfg.UPPER_DECK_ELEVATION)
    rail_segment("ExtRightRail",
                 (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, 0),
                 (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, stair_start_y),
                 cfg.UPPER_DECK_ELEVATION)
    for name,x,y in [
        ("ExtPost_LB", cfg.UPPER_DECK_WIDTH, 0),
        ("ExtPost_RB", cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, 0),
        ("ExtPost_RF", cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH, stair_start_y),
    ]:
        helpers.add_shape(doc, rails_g, name,
                  helpers.box_at(post_t, post_t, rail_h,
                        x - post_t/2, y - post_t/2,
                        cfg.UPPER_DECK_ELEVATION),
                  cfg.RAILING_COLOR)

    # Normal staircase from lower deck front edge to ground.
    # Positioned at the left edge of the lower deck.
    stair_lower_x = lower_x - cfg.STAIR_WIDTH / 2
    stair_lower_start_y = -cfg.LOWER_DECK_DEPTH
    stair_lower_end_y = -cfg.LOWER_DECK_DEPTH - 55 * cfg.INCH
    stair_lower_start = (stair_lower_x, stair_lower_start_y)
    stair_lower_end = (stair_lower_x, stair_lower_end_y)
    helpers.stair_run(doc, stairs_g, "LowerFrontTread",
              stair_lower_start, stair_lower_end,
              cfg.LOWER_DECK_ELEVATION, 0,
              cfg.STAIR_WIDTH, cfg.TREAD_DEPTH, cfg.DECK_COLOR)
    stair_risers("LowerStair", stair_lower_start, stair_lower_end,
                 cfg.LOWER_DECK_ELEVATION, 0,
                 cfg.STAIR_WIDTH)
    stair_guardrails("LowerStair", stair_lower_start, stair_lower_end,
                     cfg.LOWER_DECK_ELEVATION, 0,
                     cfg.STAIR_WIDTH)
    stair_skirt_boards("LowerStair", stair_lower_start, stair_lower_end,
                       cfg.LOWER_DECK_ELEVATION, 0,
                       cfg.STAIR_WIDTH)

    # Pool and pavers — moved right so patio doesn't extend past left deck edge
    pool_y = -(cfg.LOWER_DECK_DEPTH + 7 * cfg.FOOT + 6 * cfg.FOOT + 15 * cfg.FOOT)
    pool_x = cfg.PATIO_BORDER
    patio = helpers.box_at(cfg.POOL_LENGTH + 2*cfg.PATIO_BORDER,
                   cfg.POOL_WIDTH + 2*cfg.PATIO_BORDER,
                   4*cfg.INCH,
                   pool_x-cfg.PATIO_BORDER, pool_y-cfg.PATIO_BORDER, -4*cfg.INCH)
    helpers.add_shape(doc, pool_g, "PoolPaverPatio", patio, cfg.PAVER_COLOR)

    pool = helpers.sloped_pool_at(cfg.POOL_LENGTH, cfg.POOL_WIDTH,
                  cfg.POOL_SHALLOW_DEPTH, cfg.POOL_DEEP_DEPTH,
                  pool_x, pool_y, 0)
    helpers.add_shape(doc, pool_g, "PoolWater_34x12_5ftTo8ft", pool, cfg.WATER_COLOR, 35)

    # Concept railings: upper front edge, lower outer/right edges.
    # Upper front rail extends full width to UpperPost_R
    rail_segment("UpperFrontRail",
                 (0, -cfg.UPPER_DECK_DEPTH),
                 (cfg.UPPER_DECK_WIDTH - post_t, -cfg.UPPER_DECK_DEPTH),
                 cfg.UPPER_DECK_ELEVATION)

    # Side rail from UpperPost_R to the top of the stairs
    rail_segment("StairSideRail",
                 (cfg.UPPER_DECK_WIDTH - post_t, -cfg.UPPER_DECK_DEPTH),
                 (cfg.UPPER_DECK_WIDTH, stair_start_y),
                 cfg.UPPER_DECK_ELEVATION)

    # Post at the edge where extension meets the main deck
    helpers.add_shape(doc, rails_g, "UpperStairPost",
              helpers.box_at(post_t, post_t, rail_h,
                    cfg.UPPER_DECK_WIDTH - post_t/2, stair_start_y - post_t/2,
                    cfg.UPPER_DECK_ELEVATION),
              cfg.RAILING_COLOR)

    # Left edge rail from fireplace front to RoofPost_1
    rail_segment("LeftEdgeRail",
                 (0, -cfg.FIREPLACE_DEPTH),
                 (0, -cfg.UPPER_DECK_DEPTH),
                 cfg.UPPER_DECK_ELEVATION)

    # Post at the right side of the lower stair opening
    helpers.add_shape(doc, rails_g, "LowerStairPost",
              helpers.box_at(post_t, post_t, rail_h,
                    lower_x + cfg.STAIR_WIDTH - post_t/2,
                    -cfg.LOWER_DECK_DEPTH - post_t/2,
                    cfg.LOWER_DECK_ELEVATION),
              cfg.RAILING_COLOR)

    # Lower deck outer rails
    rail_segment("LowerRightRail",
                 (lower_x+cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
                 (lower_x+cfg.LOWER_DECK_WIDTH, 0),
                 cfg.LOWER_DECK_ELEVATION)
    rail_segment("LowerFrontRail",
                 (lower_x + cfg.STAIR_WIDTH, -cfg.LOWER_DECK_DEPTH),
                 (lower_x + cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
                 cfg.LOWER_DECK_ELEVATION)
    rail_segment("LowerBackRail",
                 (lower_x, 0),
                 (lower_x + cfg.LOWER_DECK_WIDTH, 0),
                 cfg.LOWER_DECK_ELEVATION)

    # Basic posts at corners
    for name,x,y,z in [
        ("UpperPost_L",0,-cfg.UPPER_DECK_DEPTH,cfg.UPPER_DECK_ELEVATION),
        ("UpperPost_R",cfg.UPPER_DECK_WIDTH - post_t,
                       -cfg.UPPER_DECK_DEPTH,cfg.UPPER_DECK_ELEVATION),
        ("LowerPost_LH",lower_x,0,cfg.LOWER_DECK_ELEVATION),
        ("LowerPost_RH",lower_x+cfg.LOWER_DECK_WIDTH,0,cfg.LOWER_DECK_ELEVATION),
        ("LowerPost_RF",lower_x+cfg.LOWER_DECK_WIDTH,-cfg.LOWER_DECK_DEPTH,cfg.LOWER_DECK_ELEVATION),
    ]:
        helpers.add_shape(doc, rails_g, name,
                  helpers.box_at(post_t,post_t,rail_h,x-post_t/2,y-post_t/2,z),
                  cfg.RAILING_COLOR)

    doc.recompute()
    return doc
