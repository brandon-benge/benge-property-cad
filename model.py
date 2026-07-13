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
    features_g = doc.addObject("App::Part", "Features")
    pool_g = doc.addObject("App::Part", "PoolArea")

    if parent is not None:
        parent.addObject(site)
        parent.addObject(house_g)
        parent.addObject(decks_g)
        parent.addObject(stairs_g)
        parent.addObject(rails_g)
        parent.addObject(features_g)
        parent.addObject(pool_g)

    # Coordinate convention:
    # X = left/right across front of house
    # Y = front-to-back (house positive Y, decks/pool negative Y)
    # Z = elevation

    # House placeholder wall — thin wall spanning the length of the top deck.
    house = helpers.box_at(cfg.HOUSE_WIDTH, cfg.HOUSE_DEPTH, cfg.HOUSE_HEIGHT,
                   0, 0, 0)
    helpers.add_shape(doc, house_g, "HouseMass", house, cfg.HOUSE_COLOR)

    # Deck slabs
    upper = helpers.box_at(cfg.UPPER_DECK_WIDTH, cfg.UPPER_DECK_DEPTH, cfg.DECK_THICKNESS,
                   0, -cfg.UPPER_DECK_DEPTH, cfg.UPPER_DECK_ELEVATION-cfg.DECK_THICKNESS)
    helpers.add_shape(doc, decks_g, "UpperDeck_24ft6x16ft", upper, cfg.DECK_COLOR)

    lower_x = cfg.UPPER_DECK_WIDTH
    lower = helpers.box_at(cfg.LOWER_DECK_WIDTH, cfg.LOWER_DECK_DEPTH, cfg.DECK_THICKNESS,
                   lower_x, -cfg.LOWER_DECK_DEPTH, cfg.LOWER_DECK_ELEVATION-cfg.DECK_THICKNESS)
    helpers.add_shape(doc, decks_g, "LowerHotTubDeck_15x19ft", lower, cfg.DECK_COLOR)

    # Full-length upper deck cover
    roof = helpers.box_at(cfg.UPPER_DECK_WIDTH + 2*cfg.ROOF_OVERHANG,
                  cfg.UPPER_DECK_DEPTH + 2*cfg.ROOF_OVERHANG,
                  cfg.ROOF_THICKNESS,
                  -cfg.ROOF_OVERHANG, -cfg.UPPER_DECK_DEPTH - cfg.ROOF_OVERHANG,
                  cfg.UPPER_DECK_ELEVATION + cfg.ROOF_HEIGHT_ABOVE_UPPER)
    helpers.add_shape(doc, features_g, "UpperDeckFullCover", roof, (0.18,0.20,0.22))

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
    fp = helpers.box_at(cfg.FIREPLACE_WIDTH, cfg.FIREPLACE_DEPTH, cfg.FIREPLACE_HEIGHT,
                0, -cfg.FIREPLACE_DEPTH, 0)
    helpers.add_shape(doc, features_g, "BrickFireplaceTVWall", fp, cfg.BRICK_COLOR)

    # Sliding door on the upper deck between fireplace and outdoor kitchen
    door = helpers.box_at(cfg.DOOR_WIDTH, 3 * cfg.INCH, 7 * cfg.FOOT,
                 8.5 * cfg.FOOT, -1.5 * cfg.INCH, cfg.UPPER_DECK_ELEVATION)
    helpers.add_shape(doc, features_g, "SlidingDoor", door, (0.55, 0.70, 0.82), 40)

    # Outdoor kitchen placeholder along house, right of the sliding door
    kitchen = helpers.box_at(10*cfg.FOOT, 30*cfg.INCH, 38*cfg.INCH,
                     14.5 * cfg.FOOT, -6*cfg.INCH,
                     cfg.UPPER_DECK_ELEVATION)
    helpers.add_shape(doc, features_g, "OutdoorKitchen", kitchen, (0.12,0.12,0.12))

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

    # Straight stair run along Y axis at the edge of the upper deck.
    # Centered on x=UPPER_DECK_WIDTH (24.5'), spanning x=22.5'–26.5'.
    stair_x = cfg.UPPER_DECK_WIDTH - cfg.STAIR_WIDTH / 2
    stair_start_y = -4 * cfg.FOOT
    stair_end_y = -9.5 * cfg.FOOT
    stair_start = (stair_x, stair_start_y)
    stair_end = (stair_x, stair_end_y)
    helpers.stair_run(doc, stairs_g, "UpperStraightTread",
              stair_start, stair_end,
              cfg.UPPER_DECK_ELEVATION, cfg.LOWER_DECK_ELEVATION,
              cfg.STAIR_WIDTH, cfg.TREAD_DEPTH, cfg.DECK_COLOR)

    # Upper deck platform — full width from house wall to stair edge
    platform = helpers.box_at(stair_x + cfg.STAIR_WIDTH, 4*cfg.FOOT, cfg.DECK_THICKNESS,
                     0, -4*cfg.FOOT,
                     cfg.UPPER_DECK_ELEVATION - cfg.DECK_THICKNESS)
    helpers.add_shape(doc, features_g, "UpperDeckPlatform", platform, (0.56, 0.38, 0.22))

    # Normal staircase from lower deck front edge to ground.
    # Positioned at the far left edge of the lower deck (x=24.5').
    stair_lower_x = cfg.UPPER_DECK_WIDTH
    stair_lower_start_y = -cfg.LOWER_DECK_DEPTH
    stair_lower_end_y = -(cfg.LOWER_DECK_DEPTH + 7 * cfg.FOOT)
    stair_lower_start = (stair_lower_x, stair_lower_start_y)
    stair_lower_end = (stair_lower_x, stair_lower_end_y)
    helpers.stair_run(doc, stairs_g, "LowerFrontTread",
              stair_lower_start, stair_lower_end,
              cfg.LOWER_DECK_ELEVATION, 0,
              cfg.STAIR_WIDTH, cfg.TREAD_DEPTH, cfg.DECK_COLOR)

    # Pool and pavers — pool starts 15' further from the house
    pool_y = -(cfg.LOWER_DECK_DEPTH + 7 * cfg.FOOT + 6 * cfg.FOOT + 15 * cfg.FOOT)
    pool_x = (cfg.HOUSE_WIDTH - cfg.POOL_LENGTH) / 2
    patio = helpers.box_at(cfg.POOL_LENGTH + 2*cfg.PATIO_BORDER,
                   cfg.POOL_WIDTH + 2*cfg.PATIO_BORDER,
                   4*cfg.INCH,
                   pool_x-cfg.PATIO_BORDER, pool_y-cfg.PATIO_BORDER, -4*cfg.INCH)
    helpers.add_shape(doc, pool_g, "PoolPaverPatio", patio, cfg.PAVER_COLOR)

    pool = helpers.box_at(cfg.POOL_LENGTH, cfg.POOL_WIDTH, cfg.POOL_DEPTH_VISUAL,
                  pool_x, pool_y, -cfg.POOL_DEPTH_VISUAL)
    helpers.add_shape(doc, pool_g, "PoolWater_34x12", pool, cfg.WATER_COLOR, 35)

    # Concept railings: upper front edge, lower outer/right edges.
    rail_h = 42 * cfg.INCH
    rail_t = 2 * cfg.INCH
    post_t = 4 * cfg.INCH

    def rail_segment(name, p1, p2, z):
        shape = helpers.line_box_between((p1[0],p1[1],z+rail_h-rail_t),
                                 (p2[0],p2[1],z+rail_h-rail_t),
                                 rail_t, rail_t)
        helpers.add_shape(doc, rails_g, name, shape, cfg.RAILING_COLOR)

    # Upper front rail stops before stair opening
    rail_segment("UpperFrontRail",
                 (0, -cfg.UPPER_DECK_DEPTH),
                 (stair_x - 6*cfg.INCH, -cfg.UPPER_DECK_DEPTH),
                 cfg.UPPER_DECK_ELEVATION)

    # Lower deck outer rails
    rail_segment("LowerRightRail",
                 (lower_x+cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
                 (lower_x+cfg.LOWER_DECK_WIDTH, 0),
                 cfg.LOWER_DECK_ELEVATION)
    rail_segment("LowerFrontRail",
                 (cfg.UPPER_DECK_WIDTH + cfg.STAIR_WIDTH + 6*cfg.INCH, -cfg.LOWER_DECK_DEPTH),
                 (lower_x+cfg.LOWER_DECK_WIDTH, -cfg.LOWER_DECK_DEPTH),
                 cfg.LOWER_DECK_ELEVATION)

    # Basic posts at corners
    for name,x,y,z in [
        ("UpperPost_L",0,-cfg.UPPER_DECK_DEPTH,cfg.UPPER_DECK_ELEVATION),
        ("UpperPost_R",stair_x - 6*cfg.INCH,
                       -cfg.UPPER_DECK_DEPTH,cfg.UPPER_DECK_ELEVATION),
        ("LowerPost_RH",lower_x+cfg.LOWER_DECK_WIDTH,0,cfg.LOWER_DECK_ELEVATION),
        ("LowerPost_RF",lower_x+cfg.LOWER_DECK_WIDTH,-cfg.LOWER_DECK_DEPTH,cfg.LOWER_DECK_ELEVATION),
    ]:
        helpers.add_shape(doc, rails_g, name,
                  helpers.box_at(post_t,post_t,rail_h,x-post_t/2,y-post_t/2,z),
                  cfg.RAILING_COLOR)

    doc.recompute()
    return doc
