import math
import random
import OpenScad as vc
import os

title = "Cross-Section Slicing - What shape results from cutting a 3D object?"

prompt = """
You are given a 3D object and a cutting plane. Determine the 2D shape that results from 
slicing the object with that plane.

OBJECT_DESCRIPTION

PLANE_DESCRIPTION

Describe the resulting 2D cross-section shape in clear text, identifying the shape and 
any notable characteristics (symmetry, number of sides, relative proportions, etc.).
"""

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "shapeType": {
      "type":
      "string",
      "description":
      "Name of the shape (If multiple apply, use the most specific shape)",
      "enum": [
        "circle", "ellipse", "square", "rectangle", "triangle", "trapezoid", "parallelogram",
        "rhombus", "polygon", "pentagon", "hexagon", "heptagon", "octagon", "nonagon", "decagon",
        "dodecagon", "star", "heart", "diamond", "hexagram", "lens", "washer", "two_circles",
        "two_ellipses", "two_squares", "two_rectangles", "two_polygons", "two_hexagons",
        "two_octagons", "two_stars", "two_hearts", "two_diamonds", "two_pentagons", "two_hexagrams",
        "rhombus", "quadrilateral"
      ]
    },
    "shapeDescription": {
      "type": "string",
      "description": "Free-form text describing the resulting 2D shape."
    }
  },
  "propertyOrdering": ["reasoning", "shapeType", "shapeDescription"],
  "required": ["reasoning", "shapeType", "shapeDescription"],
  "additionalProperties": False
}


# Geometry helpers for plane placement and camera alignment
def _vec_length(vec):
  return math.sqrt(sum(float(v)**2 for v in vec))


def _normalize(vec):
  length = max(_vec_length(vec), 1e-9)
  return [float(v) / length for v in vec]


def _dot(a, b):
  return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
  return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _axis_angle_from_normal(normal):
  z_axis = [0.0, 0.0, 1.0]
  n = _normalize(normal)
  dot_val = max(-1.0, min(1.0, _dot(z_axis, n)))
  angle = math.degrees(math.acos(dot_val))
  axis = _cross(z_axis, n)
  if _vec_length(axis) < 1e-6:
    axis = [1.0, 0.0, 0.0]
  else:
    axis = _normalize(axis)
  return angle, axis


def make_plane_spec(point, normal, span=20.0, thickness=0.2, span_y=None, camera_distance=None):
  if isinstance(span, (list, tuple)):
    width = float(span[0])
    height = float(span[1]) if len(span) > 1 else float(span[0])
  else:
    width = float(span)
    height = float(span_y) if span_y is not None else float(span)

  spec = {
    "point": [float(v) for v in point],
    "normal": _normalize(normal),
    "size": [width, height, float(thickness)],
    "thickness": float(thickness)
  }
  spec["span"] = max(width, height)
  spec["camera_distance"] = (camera_distance if camera_distance is not None else max(
    6.0, spec["span"] * 1.2))
  return spec


def make_problem(name,
                 object_desc,
                 plane_desc,
                 expected_type,
                 object_scad,
                 plane_spec,
                 object_color=None):
  return {
    "name": name,
    "object": object_desc,
    "plane": plane_desc,
    "expected_type": expected_type,
    "object_scad": object_scad,
    "plane_spec": plane_spec,
    "object_color": object_color or [0.5, 0.7, 1.0, 0.8]
  }


# Shared OpenSCAD snippets for solids
SCAD_CUBE = "cube([2,2,2], center=true);"
SCAD_RECT = "cube([4,2,1], center=true);"
SCAD_SPHERE = "$fn=96; sphere(r=5);"
SCAD_CYL = "$fn=96; cylinder(r=3, h=10, center=true);"
SCAD_CONE = "$fn=96; translate([0,0,-5]) cylinder(r1=4, r2=0, h=10);"
SCAD_TRI_PRISM = "$fn=96; translate([0,0,-3]) linear_extrude(height=6) polygon(points=[[2,0],[-1.5,2.598],[-1.5,-2.598]]);"
SCAD_HEX_PRISM = "$fn=6; translate([0,0,-3]) cylinder(r=3, h=6);"
SCAD_OCT_PRISM = "$fn=8; translate([0,0,-4]) cylinder(r=3, h=8);"
SCAD_SQ_PYRAMID = "$fn=4; translate([0,0,-1]) cylinder(r1=3, r2=0, h=6);"
SCAD_TRI_PYRAMID = "$fn=3; translate([0,0,-1]) cylinder(r1=2.6, r2=0, h=4);"
SCAD_TORUS = "$fn=96; rotate_extrude() translate([5,0,0]) circle(r=2);"
SCAD_INTERSECTING_CYLS = """$fn=96;
intersection() {
  cylinder(r=3, h=16, center=true);
  rotate([0,90,0]) cylinder(r=3, h=16, center=true);
}"""
SCAD_TWISTED = """$fn=48;
linear_extrude(height=6, twist=60)
    polygon(points=[[2,0], [-1,1.732], [-1,-1.732]]);
"""
SCAD_DODECA = """$fn=32;
phi = (1 + sqrt(5)) / 2;
scale([phi,phi,phi]) {
    hull() {
        for(i=[0:4]) rotate([0,0,i*72]) translate([1.17,0,0.85]) sphere(r=0.3);
        for(i=[0:4]) rotate([0,0,i*72+36]) translate([1.17,0,-0.85]) sphere(r=0.3);
        translate([0,0,1.4]) sphere(r=0.3);
        translate([0,0,-1.4]) sphere(r=0.3);
    }
}
"""

# Define slicing problems
problems = []

# Cube scenarios
cube_desc = """
A solid cube with side length 2 centered at the origin.
"""
cube_planes = [
  ("Cube mid horizontal slice", "Plane: Z = 0 cuts through the cube's center.", "square",
   make_plane_spec([0, 0, 0], [0, 0, 1], span=8, thickness=0.03)),
  ("Cube upper horizontal slice", "Plane: Z = 0.75 remains parallel to the base near the top.",
   "square", make_plane_spec([0, 0, 0.75], [0, 0, 1], span=8, thickness=0.03)),
  ("Cube central YZ slice", "Plane: X = 0 forms a YZ-plane cross-section.", "square",
   make_plane_spec([0, 0, 0], [1, 0, 0], span=8, thickness=0.03)),
  ("Cube offset vertical slice", "Plane: Y = 0.8 is parallel to XZ but shifted toward +Y.",
   "square", make_plane_spec([0, 0.8, 0], [0, 1, 0], span=8, thickness=0.03)),
  ("Cube diagonal hexagon slice",
   "Plane: Normal (1,1,1) through the center yields a regular hexagon.", "hexagon",
   make_plane_spec([0, 0, 0], [1, 1, 1], span=9, thickness=0.03))
]
for name, plane_desc, shape, spec in cube_planes:
  problems.append(make_problem(name, cube_desc, plane_desc, shape, SCAD_CUBE, spec))

# Rectangular prism scenarios
rect_desc = """
A rectangular prism measuring 4×2×1 units, centered at the origin.
"""
rect_planes = [("Prism horizontal mid slice", "Plane: Z = 0 bisects the prism.", "rectangle",
                make_plane_spec([0, 0, 0], [0, 0, 1], span=[12, 8], thickness=0.03)),
               ("Prism long-axis slice", "Plane: X = 0 cuts parallel to long faces.", "rectangle",
                make_plane_spec([0, 0, 0], [1, 0, 0], span=[10, 6], thickness=0.03)),
               ("Prism angled parallelogram slice",
                "Plane: Normal (1,1,0) through the origin forms a parallelogram.", "rectangle",
                make_plane_spec([0, 0, 0], [1, 1, 0], span=[12, 8], thickness=0.03)),
               ("Prism tri-diagonal slice", "Plane: Normal (1,1,1) creates a six-sided profile.",
                "parallelogram", make_plane_spec([0, 0, 0], [1, 1, 1], span=11, thickness=0.03))]
for name, plane_desc, shape, spec in rect_planes:
  problems.append(
    make_problem(name, rect_desc, plane_desc, shape, SCAD_RECT, spec, [0.7, 0.5, 1.0, 0.85]))

# Sphere scenarios
sphere_desc = """
A solid sphere of radius 5 centered at the origin.
"""
sphere_planes = [
  ("Sphere equatorial slice", "Plane: Z = 0 passes through the equator.", "circle",
   make_plane_spec([0, 0, 0], [0, 0, 1], span=14, thickness=0.03)),
  ("Sphere upper slice", "Plane: Z = 3 is parallel to XY above the center.", "circle",
   make_plane_spec([0, 0, 3], [0, 0, 1], span=14, thickness=0.03)),
  ("Sphere near-cap slice", "Plane: Z = 4.2 trims a small cap.", "circle",
   make_plane_spec([0, 0, 4.2], [0, 0, 1], span=12, thickness=0.03)),
  ("Sphere vertical chord slice", "Plane: X = 2 forms a vertical circle.", "circle",
   make_plane_spec([2, 0, 0], [1, 0, 0], span=14, thickness=0.03)),
  ("Sphere diagonal slice", "Plane: Normal (1,1,0) through center gives a great circle.", "circle",
   make_plane_spec([0, 0, 0], [1, 1, 0], span=15, thickness=0.03))
]
for name, plane_desc, shape, spec in sphere_planes:
  problems.append(
    make_problem(name, sphere_desc, plane_desc, shape, SCAD_SPHERE, spec, [0.9, 0.6, 0.4, 0.85]))

# Cylinder scenarios
cyl_desc = """
A right circular cylinder of radius 3 and height 10 centered on the Z-axis.
"""
cyl_planes = [("Cylinder mid horizontal slice", "Plane: Z = 0 produces a central circle.", "circle",
               make_plane_spec([0, 0, 0], [0, 0, 1], span=16, thickness=0.03)),
              ("Cylinder near-top slice", "Plane: Z = 4 stays parallel near the top.", "circle",
               make_plane_spec([0, 0, 4], [0, 0, 1], span=16, thickness=0.03)),
              ("Cylinder axial rectangle", "Plane: X = 0 splits along the axis.", "rectangle",
               make_plane_spec([0, 0, 0], [1, 0, 0], span=[16, 16], thickness=0.03)),
              ("Cylinder offset axial slice", "Plane: Y = 1 parallels the axis but offset.",
               "rectangle", make_plane_spec([0, 1, 0], [0, 1, 0], span=[16, 16], thickness=0.03)),
              ("Cylinder angled ellipse slice", "Plane: Normal (0,1,1) gives an ellipse.",
               "ellipse", make_plane_spec([0, 0, 0], [0, 1, 1], span=17, thickness=0.03))]
for name, plane_desc, shape, spec in cyl_planes:
  problems.append(
    make_problem(name, cyl_desc, plane_desc, shape, SCAD_CYL, spec, [0.4, 0.8, 0.6, 0.85]))

# Cone scenarios
cone_desc = """
A cone with apex at Z = 5, base radius 4 at Z = -5, centered on the Z-axis.
"""
cone_planes = [("Cone central slice", "Plane: Z = 0 forms a mid-level circle.", "circle",
                make_plane_spec([0, 0, 0], [0, 0, 1], span=12, thickness=0.03)),
               ("Cone near apex slice", "Plane: Z = 3 captures a small circle near the tip.",
                "circle", make_plane_spec([0, 0, 3], [0, 0, 1], span=9, thickness=0.03)),
               ("Cone tilted ellipse slice", "Plane: Normal (0,1,1) produces an ellipse.",
                "ellipse", make_plane_spec([0, 0, 0], [0, 1, 1], span=13, thickness=0.03)),
               ("Cone meridian slice", "Plane: X = 0 contains the axis yielding a triangle.",
                "triangle", make_plane_spec([0, 0, 0], [1, 0, 0], span=[14, 14], thickness=0.03))]
for name, plane_desc, shape, spec in cone_planes:
  problems.append(
    make_problem(name, cone_desc, plane_desc, shape, SCAD_CONE, spec, [0.9, 0.5, 0.3, 0.9]))

# Triangular prism scenarios
tri_desc = """
An equilateral triangular prism extruded 6 units along Z, centered at the origin.
"""
tri_planes = [("Triangular prism mid slice", "Plane: Z = 0 yields a congruent triangle.",
               "triangle", make_plane_spec([0, 0, 0], [0, 0, 1], span=11, thickness=0.03)),
              ("Triangular prism upper slice", "Plane: Z = 1 stays parallel to the base.",
               "triangle", make_plane_spec([0, 0, 1], [0, 0, 1], span=11, thickness=0.03)),
              ("Triangular prism axial rectangle", "Plane: X = 0 intersects the rectangular faces.",
               "rectangle", make_plane_spec([0, 0, 0], [1, 0, 0], span=[12, 12], thickness=0.03)),
              ("Triangular prism oblique trapezoid", "Plane: Normal (1,0,1) makes a trapezoid.",
               "trapezoid", make_plane_spec([0, 0, 0], [1, 0, 1], span=12, thickness=0.03))]
for name, plane_desc, shape, spec in tri_planes:
  problems.append(
    make_problem(name, tri_desc, plane_desc, shape, SCAD_TRI_PRISM, spec, [0.4, 0.4, 0.9, 0.85]))

# Hexagonal prism scenarios
hex_desc = """
A regular hexagonal prism of radius 3 and height 6 centered on the origin.
"""
hex_planes = [("Hex prism middle slice", "Plane: Z = 0 produces a regular hexagon.", "hexagon",
               make_plane_spec([0, 0, 0], [0, 0, 1], span=14, thickness=0.03)),
              ("Hex prism offset slice", "Plane: Z = 2 stays parallel to the bases.", "hexagon",
               make_plane_spec([0, 0, 2], [0, 0, 1], span=14, thickness=0.03)),
              ("Hex prism axial rectangle", "Plane: X = 0 intersects opposing faces.", "rectangle",
               make_plane_spec([0, 0, 0], [1, 0, 0], span=[14, 14], thickness=0.03)),
              ("Hex prism diagonal rhombus", "Plane: Normal (1,1,0) clips a rectangle.",
               "rectangle", make_plane_spec([0, 0, 0], [1, 1, 0], span=15, thickness=0.03))]
for name, plane_desc, shape, spec in hex_planes:
  problems.append(
    make_problem(name, hex_desc, plane_desc, shape, SCAD_HEX_PRISM, spec, [0.3, 0.9, 0.7, 0.85]))

# Octagonal prism scenarios
oct_desc = """
A regular octagonal prism of radius 3 and height 8 centered at the origin.
"""
oct_planes = [("Oct prism mid slice", "Plane: Z = 0 reveals an octagon.", "octagon",
               make_plane_spec([0, 0, 0], [0, 0, 1], span=16, thickness=0.03)),
              ("Oct prism axial rectangle", "Plane: Y = 0 intersects opposite faces.", "rectangle",
               make_plane_spec([0, 0, 0], [0, 1, 0], span=[16, 16], thickness=0.03)),
              ("Oct prism steep diagonal", "Plane: Normal (1,0,1) creates a hexagon-like cut.",
               "hexagon", make_plane_spec([0, 0, 0], [1, 0, 1], span=16, thickness=0.03))]
for name, plane_desc, shape, spec in oct_planes:
  problems.append(
    make_problem(name, oct_desc, plane_desc, shape, SCAD_OCT_PRISM, spec, [0.8, 0.4, 0.6, 0.85]))

# Pyramid scenarios
pyr_desc = """
A square pyramid with base in z=-1 and apex at z=5.
"""
pyr_planes = [("Square pyramid mid slice", "Plane: Z = 1 forms a scaled square cross-section.",
               "square", make_plane_spec([0, 0, 1], [0, 0, 1], span=10, thickness=0.03)),
              ("Square pyramid near apex", "Plane: Z = 3.5 yields a small square near the apex.",
               "square", make_plane_spec([0, 0, 3.5], [0, 0, 1], span=8, thickness=0.03)),
              ("Square pyramid diagonal slice", "Plane: Normal (1,0,1) produces a pentagon.",
               "pentagon ", make_plane_spec([0, 0, 0], [1, 0, 1], span=12, thickness=0.03))]
for name, plane_desc, shape, spec in pyr_planes:
  problems.append(
    make_problem(name, pyr_desc, plane_desc, shape, SCAD_SQ_PYRAMID, spec, [0.95, 0.8, 0.3, 0.9]))

# Triangular pyramid scenarios
tet_desc = """
A tetrahedron-style pyramid centered near the origin.
"""
tet_planes = [("Tri pyramid horizontal slice", "Plane: Z = 0 produces a triangle.", "triangle",
               make_plane_spec([0, 0, 0], [0, 0, 1], span=9, thickness=0.2)),
              ("Tri pyramid diagonal slice", "Plane: Normal (1,1,0) forms a quadrilateral.",
               "quadrilateral", make_plane_spec([0, 0, 0], [1, 1, 0], span=10, thickness=0.2))]
for name, plane_desc, shape, spec in tet_planes:
  problems.append(
    make_problem(name, tet_desc, plane_desc, shape, SCAD_TRI_PYRAMID, spec, [0.9, 0.4, 0.4, 0.9]))

# Torus scenarios
torus_desc = """
A torus with major radius 5 and minor radius 2 centered at the origin.
"""
torus_planes = [("Torus central slice", "Plane: Z = 0 yields two tangent circles.", "washer",
                 make_plane_spec([0, 0, 0], [0, 0, 1], span=18, thickness=0.03)),
                ("Torus elevated slice", "Plane: Z = 1 yields two disjoint circles.", "washer",
                 make_plane_spec([0, 0, 1], [0, 0, 1], span=18, thickness=0.03)),
                ("Torus diagonal slice", "Plane: Normal (0,1,0) creates two circles.",
                 "two_circles", make_plane_spec([0, 0, 0], [0, 1, 0], span=18, thickness=0.03))]
for name, plane_desc, shape, spec in torus_planes:
  problems.append(
    make_problem(name, torus_desc, plane_desc, shape, SCAD_TORUS, spec, [0.8, 0.5, 0.2, 0.85]))

# Advanced solids
problems.append(
  make_problem("Dodecahedron equatorial slice", "A regular dodecahedron centered at the origin.",
               "Plane: Z = 0 passes through the center perpendicular to a face axis.",
               "decagon", SCAD_DODECA, make_plane_spec([0, 0, 0], [0, 0, 1],
                                                       span=16,
                                                       thickness=0.03), [0.9, 0.7, 0.2, 0.85]))

problems.append(
  make_problem("Twisted prism mid slice",
               "A twisted triangular prism with 60° twist between base and top.",
               "Plane: Z = 0 intersects halfway creating a rotated triangle.", "triangle",
               SCAD_TWISTED, make_plane_spec([0, 0, 0], [0, 0, 1], span=12,
                                             thickness=0.03), [0.5, 0.2, 0.7, 0.9]))

problems.append(
  make_problem("Steinmetz horizontal slice",
               "Two perpendicular cylinders of radius 3 (Steinmetz solid).",
               "Plane: Z = 2 forms a lens bounded by circular arcs and straight sides.", "lens",
               SCAD_INTERSECTING_CYLS, make_plane_spec([0, 0, 2], [0, 0, 1],
                                                       span=18,
                                                       thickness=0.03), [0.6, 0.9, 0.4, 0.85]))

# Extra variety to reach ~40 challenges
extra_shapes = [
  ("Sphere shallow slice", sphere_desc, "Plane: Z = -2 cuts below the center.", "circle",
   SCAD_SPHERE, make_plane_spec([0, 0, -2], [0, 0, 1], span=14,
                                thickness=0.03), [0.9, 0.6, 0.4, 0.85]),
  ("Cylinder steep diagonal slice", cyl_desc,
   "Plane: Normal (1,1,1) produces an elongated ellipse.", "ellipse", SCAD_CYL,
   make_plane_spec([0, 0, 0], [1, 1, 1], span=18, thickness=0.03), [0.4, 0.8, 0.6, 0.85]),
  ("Rect prism shallow slice", rect_desc, "Plane: Z = -0.3 skims below center.", "rectangle",
   SCAD_RECT, make_plane_spec([0, 0, -0.3], [0, 0, 1], span=[12, 8],
                              thickness=0.03), [0.7, 0.5, 1.0, 0.85]),
  ("Triangular prism steep diagonal", tri_desc,
   "Plane: Normal (1,1,1) creates a pentagon-like polygon. (A triangle with 2 of the corners clipped)",
   "pentagon", SCAD_TRI_PRISM, make_plane_spec([0, 0, 0], [1, 1, 1], span=13,
                                               thickness=0.03), [0.4, 0.4, 0.9, 0.85]),
  ("Cone shallow diagonal", cone_desc,
   "Plane: Normal (1,0,1) yields a skew ellipse resembling a parabola.", "ellipse", SCAD_CONE,
   make_plane_spec([0, 0, 0.5], [1, 0, 1], span=13, thickness=0.03), [0.9, 0.5, 0.3, 0.9]),
  ("Hex prism shallow tilt", hex_desc, "Plane: Normal (0,1,1) creates a skewed hexagon.", "hexagon",
   SCAD_HEX_PRISM, make_plane_spec([0, 0, 0], [0, 1, 1], span=15,
                                   thickness=0.03), [0.3, 0.9, 0.7, 0.85]),
  ("Oct prism offset horizontal", oct_desc, "Plane: Z = -2 creates a lower octagon.", "octagon",
   SCAD_OCT_PRISM, make_plane_spec([0, 0, -2], [0, 0, 1], span=16,
                                   thickness=0.03), [0.8, 0.4, 0.6, 0.85]),
  ("Square pyramid base slice", pyr_desc, "Plane: Z = -1 coincides with the base square.", "square",
   SCAD_SQ_PYRAMID, make_plane_spec([0, 0, -1], [0, 0, 1], span=10,
                                    thickness=0.03), [0.95, 0.8, 0.3, 0.9]),
  ("Tri pyramid high slice", tet_desc, "Plane: Z = 1.2 captures a tiny top triangle.", "triangle",
   SCAD_TRI_PYRAMID, make_plane_spec([0, 0, 1.2], [0, 0, 1], span=8,
                                     thickness=0.2), [0.9, 0.4, 0.4, 0.9]),
  ("Torus shallow offset slice", torus_desc, "Plane: Z = -1.2 yields a washer.", "washer",
   SCAD_TORUS, make_plane_spec([0, 0, -1.2], [0, 0, 1], span=18,
                               thickness=0.03), [0.8, 0.5, 0.2, 0.85])
]

for name, obj_desc, plane_desc, shape, scad, spec, color in extra_shapes:
  problems.append(make_problem(name, obj_desc, plane_desc, shape, scad, spec, color))

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Different 3D objects and cutting planes"


def prepareSubpassPrompt(index: int) -> str:

  if index >= len(problems):
    raise StopIteration
  prob = problems[index]
  p = prompt.replace("OBJECT_DESCRIPTION", prob["object"])
  p = p.replace("PLANE_DESCRIPTION", prob["plane"])
  return p


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  prob = problems[subPass]

  shape_type = answer.get("shapeType", "").lower()
  expected_type = prob["expected_type"].lower()
  description = answer.get("shapeDescription", "").lower()

  # Check shape type (partial credit for close matches)
  type_score = 0
  if shape_type == expected_type:
    type_score = 1
  elif shape_type in expected_type or expected_type in shape_type:
    type_score = 0.5

  # Evaluate textual description
  desc_score = 0
  if expected_type in description:
    desc_score = 1
  elif any(word in description for word in ["polygon", "shape", "section"]):
    desc_score = 0.25

  details = [
    f"Shape type: {shape_type} (expected {expected_type}) - {type_score:.1f} pts",
    f"Description mentions expected shape: {desc_score:.2f} pts"
  ]

  total_score = (type_score + desc_score) / 2
  return total_score, "<br>".join(details)


def generate_3d_object_scad(prob):
  """Generate OpenSCAD code for the 3D object in the problem."""
  return prob.get("object_scad", "cube([1,1,1]);")


def plane_solid_scad(plane_spec, thickness=None):
  point = plane_spec["point"]
  normal = plane_spec["normal"]
  span_x, span_y, base_thickness = plane_spec["size"]
  use_thickness = float(thickness) if thickness is not None else base_thickness
  angle, axis = _axis_angle_from_normal(normal)
  return (f"translate([{point[0]},{point[1]},{point[2]}])"
          f" rotate(a={angle}, v=[{axis[0]},{axis[1]},{axis[2]}])"
          f" translate([-{span_x / 2}, -{span_y / 2}, -{use_thickness / 2}])"
          f" cube([{span_x},{span_y},{use_thickness}], center=false);")


def generate_plane_scad(plane_spec, color=None, thickness=None):
  rgba = color or [1, 0, 0, 0.35]
  return f"color({rgba}) {plane_solid_scad(plane_spec, thickness)}"


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
  prob = problems[subPass]
  shape_type = answer.get("shapeType", "unknown")
  html = f"<b>Shape type:</b> {shape_type}<br>"

  desc = answer.get("shapeDescription")
  if desc:
    html += f"<b>Description:</b> {desc}<br>"

  # Generate 3D visualization with cutting plane
  try:
    object_scad = prob.get("object_scad", "cube([1,1,1], center=true);")
    plane_spec = prob["plane_spec"]
    plane_overlay = generate_plane_scad(plane_spec)

    full_scad = f"""// 3D Object with cutting plane
color({prob.get('object_color', [0.5,0.7,1.0,0.8])}) {{
{object_scad}
}}
{plane_overlay}
"""

    output_3d = f"results/36_{subPass}_{aiEngineName}_3d.png"
    vc.render_scadText_to_png(full_scad, output_3d)
    html += f'<br><b>3D Object with Cutting Plane:</b><br><img src="{os.path.basename(output_3d)}" /><br>'

    thin = max(0.05, plane_spec["span"] * 0.015)
    plane_slice = plane_solid_scad(plane_spec, thickness=thin)
    section_raw = f"""intersection() {{
{object_scad}
{plane_slice}
}}"""

    angle, axis = _axis_angle_from_normal(plane_spec["normal"])
    px, py, pz = plane_spec["point"]
    align_section = (f"color([1,0,0,0.9]) rotate(a={-angle}, v=[{axis[0]},{axis[1]},{axis[2]}]) "
                     f"translate([-{px},-{py},-{pz}]) {section_raw}")

    expected_section = (
      f"color([0,1,0,0.45]) rotate(a={-angle}, v=[{axis[0]},{axis[1]},{axis[2]}]) "
      f"translate([-{px},-{py},-{pz}]) {plane_slice}")

    combined_2d = f"""// Cross-section via plane intersection
{align_section}
{expected_section}
"""

    output_2d = f"results/36_{subPass}_{aiEngineName}_cross_section.png"
    view_dist = plane_spec.get("camera_distance", plane_spec["span"] * 1.5)
    camera_arg = f"--camera=0,0,{view_dist},0,0,0"
    vc.render_scadText_to_png(combined_2d, output_2d, cameraArg=camera_arg)
    html += f'<br><b>Cross-Section (Intersection View):</b><br><img src="{os.path.basename(output_2d)}" /><br>'

  except Exception as e:
    html += f"<br><i>Visualization error: {e}</i><br>"

  return html


highLevelSummary = """
Tests the ability to mentally slice 3D objects and predict the resulting 2D cross-section.
<br><br>
This is a fundamental spatial reasoning skill:
<ul>
<li>Horizontal slices through regular solids</li>
<li>Diagonal/angled cuts</li>
<li>Understanding how circles become ellipses when cylinders are cut at angles</li>
<li>Recognizing that cube diagonals create rectangles</li>
</ul>
"""
