import FreeCAD as App
import Part
import math

def add_shape(doc, group, name, shape, color=None, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if color:
        obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = transparency
    group.addObject(obj)
    return obj

def box_at(length, width, height, x=0, y=0, z=0):
    shape = Part.makeBox(length, width, height)
    shape.translate(App.Vector(x, y, z))
    return shape

def line_box_between(p1, p2, thickness, height):
    """Horizontal rectangular rail between two XY points."""
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    dx, dy = x2-x1, y2-y1
    length = math.hypot(dx, dy)
    shape = Part.makeBox(length, thickness, height)
    shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), math.degrees(math.atan2(dy, dx)))
    shape.translate(App.Vector(x1, y1, z1))
    return shape

def stair_run(doc, group, name_prefix, start, end, start_z, end_z,
              width, tread_depth, color):
    """Create a straight stair run as individual treads between two plan points."""
    dx, dy = end[0]-start[0], end[1]-start[1]
    run = math.hypot(dx, dy)
    rise = abs(start_z-end_z)
    steps = max(1, int(math.ceil(rise / (7.5 * 25.4))))
    ux, uy = dx/run, dy/run
    actual_tread = run / steps
    for i in range(steps):
        t = i / steps
        z = start_z + (end_z-start_z) * t
        x = start[0] + dx*t
        y = start[1] + dy*t
        tread = Part.makeBox(actual_tread + 15, width, 45)
        tread.rotate(App.Vector(0,0,0), App.Vector(0,0,1),
                     math.degrees(math.atan2(dy, dx)))
        # offset across stair width
        tread.translate(App.Vector(x - uy*width/2, y + ux*width/2, z-45))
        add_shape(doc, group, f"{name_prefix}_{i+1:02d}", tread, color)
    return steps
