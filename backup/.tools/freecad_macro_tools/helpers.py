import math

import FreeCAD as App
import Part


def add_shape(doc, group, name, shape, color=None, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if obj.ViewObject is not None and color:
        obj.ViewObject.ShapeColor = color
    if obj.ViewObject is not None:
        obj.ViewObject.Transparency = transparency
    group.addObject(obj)
    return obj


def box_at(length, width, height, x=0, y=0, z=0):
    shape = Part.makeBox(length, width, height)
    shape.translate(App.Vector(x, y, z))
    return shape


def cylinder_between(p1, p2, radius):
    v1 = App.Vector(*p1)
    v2 = App.Vector(*p2)
    direction = v2 - v1
    shape = Part.makeCylinder(radius, direction.Length)
    shape.Placement = App.Placement(
        v1,
        App.Rotation(App.Vector(0, 0, 1), direction),
    )
    return shape


def line_box_between(p1, p2, thickness, height):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    shape = Part.makeBox(length, thickness, height)
    shape.rotate(
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1),
        math.degrees(math.atan2(dy, dx)),
    )
    shape.translate(App.Vector(x1, y1, z1))
    return shape
