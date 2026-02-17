import math, os

title = "Tetrahedron Shadow Coverage"

prompt = """
Here is the points and faces of a regular tetrahedron with all sides equal 1, resting on the Z=0 plane and with an edge along the X=0 plane:

polyhedron(
    points = [
        [0, 0, 0],                               // 0
        [1, 0, 0],                               // 1
        [0.5, sqrt(3)/2, 0],                     // 2
        [0.5, sqrt(3)/6, sqrt(2/3)]              // 3 (apex)
    ],
    faces = [
        [0, 2, 1],   // base (oriented outward)
        [0, 1, 3],
        [1, 2, 3],
        [2, 0, 3]
    ],
    convexity = 4
);

We define a 7-part rigid transform of (x,y,z,q0,q1,q2,q3), where q0,q1,q2,q3 is a normalised quaternion, and x, y, z are the translation.
Rotation is defined around the 0,0,0 point (Which is NOT THE CENTRE), and is performed before translation.

We create a scene with multiple tetrahedra, each with a different transform. Return the transforms of such a scene
such that a shadow projected vertically (onto the Z=0 plane) fully covers PARAM, centered at the origin.

Use as many tetrahedra as you need, scoring is based on shadow coverage, not the number of tetrahedra used.

Score will be deducted for:
- any shadow outside of the shape
- redundant tetrahedra
- non-normalised quaternions
- intersection tetrahedra
"""

structure = {
  "type": "object",
  "properties": {
    "tetrahedrons": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "x": {
            "type": "number"
          },
          "y": {
            "type": "number"
          },
          "z": {
            "type": "number"
          },
          "q0": {
            "type": "number"
          },
          "q1": {
            "type": "number"
          },
          "q2": {
            "type": "number"
          },
          "q3": {
            "type": "number"
          }
        },
        "required": ["x", "y", "z", "q0", "q1", "q2", "q3"],
        "additionalProperties": False
      }
    }
  },
  "required": ["tetrahedrons"],
  "additionalProperties": False
}

subpassParamSummary = [
  "Cover a square of side length 4.", "Cover a circle of diameter 4.",
  "Cover a square of side length 6, with a hole in the centre of side length 2.",
  "Cover an equilateral triangle of side length 4.", "Cover a regular hexagon with circumradius 2.",
  "Cover a rectangle of width 6 and height 2.", "Cover a diamond (rotated square) with diagonal 4.",
  "Cover a plus/cross shape with arm length 4 and arm width 1.",
  "Cover an L-shape with outer dimensions 4x4 and thickness 1.",
  "Cover an annulus (ring) with outer radius 2 and inner radius 1.",
  "Cover a regular pentagon with circumradius 2.",
  "Cover a 5-pointed star inscribed in a circle of radius 2.",
  "Cover an ellipse with semi-major axis 2 and semi-minor axis 1.",
  "Cover a semicircle of radius 2.", "Cover a right triangle with legs of length 4.",
  "Cover a parallelogram with base 4, height 2, and slant 1.",
  "Cover a trapezoid with parallel sides 4 and 2, and height 2.",
  "Cover a regular octagon with circumradius 2.",
  "Cover an arrow shape pointing right, 4 units long.",
  "Cover a chevron (V-shape) with span 4 and thickness 1."
]


def prepareSubpassPrompt(index: int) -> str:
  params = [
    "a square of side length 4", "a circle of diameter 4",
    "a square of side length 6, with a hole in the centre of side length 2",
    "an equilateral triangle of side length 4 (rotated such that one side parallel to Y=0)",
    "a regular hexagon with circumradius 2 (vertex to center distance) (rotated such that one side parallel to Y=0)",
    "a rectangle of width 6 and height 2", "a diamond (square rotated 45 degrees) with diagonal 4",
    "a plus/cross shape with arm length 4 and arm width 1",
    "an L-shape with outer dimensions 4x4 and thickness 1",
    "an annulus (ring) with outer radius 2 and inner radius 1",
    "a regular pentagon with circumradius 2", "a 5-pointed star inscribed in a circle of radius 2",
    "an ellipse with semi-major axis 2 and semi-minor axis 1",
    "a semicircle of radius 2 (flat edge along X axis)",
    "a right triangle with legs of length 4 along the X and Y axes",
    "a parallelogram with base 4, height 2, and horizontal offset 1",
    "a trapezoid with sides parallel to Y=0 of length 4 (bottom) and 2 (top), and height 2",
    "a regular octagon with circumradius 2",
    "an arrow shape pointing right, 4 units long and 2 units tall",
    "a chevron (V-shape) pointing right with span 2 and thickness 1"
  ]
  if index < len(params):
    return prompt.replace("PARAM", params[index])
  raise StopIteration


referenceScad = """
module reference(){
    translate([0,0,0.05]) cube([4,4,0.1], center=true);
}
"""


def prepareSubpassReferenceScad(index: int) -> str:
  scads = [
    # 0: Square 4x4
    """
module reference(){
    translate([0,0,0.05]) cube([4,4,0.1], center=true);
}
""",
    # 1: Circle diameter 4
    """
module reference(){
    translate([0,0,0.05]) cylinder(r=2, h=0.1, center=true, $fn=100);
}
""",
    # 2: Square with hole
    """
module reference(){
  difference() {
    translate([0,0,0.05]) cube([6,6,0.1], center=true);
    translate([0,0,0.05]) cube([2,2,2], center=true);
  }
}
""",
    # 3: Equilateral triangle side 4
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[
      [-2, -4*sqrt(3)/6],
      [2, -4*sqrt(3)/6],
      [0, 4*sqrt(3)/3]
    ]);
}
""",
    # 4: Regular hexagon circumradius 2
    """
module reference(){
  translate([0,0,0.05]) cylinder(r=2, h=0.1, center=true, $fn=6);
}
""",
    # 5: Rectangle 6x2
    """
module reference(){
  translate([0,0,0.05]) cube([6,2,0.1], center=true);
}
""",
    # 6: Diamond (rotated square) diagonal 4
    """
module reference(){
  translate([0,0,0.05]) rotate([0,0,45]) cube([4/sqrt(2),4/sqrt(2),0.1], center=true);
}
""",
    # 7: Plus/cross shape
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true) {
    square([4,1], center=true);
    square([1,4], center=true);
  }
}
""",
    # 8: L-shape
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[
      [-2,-2], [2,-2], [2,-1], [-1,-1], [-1,2], [-2,2]
    ]);
}
""",
    # 9: Annulus (ring)
    """
module reference(){
  translate([0,0,0.05]) difference() {
    cylinder(r=2, h=0.1, center=true, $fn=100);
    cylinder(r=1, h=1, center=true, $fn=100);
  }
}
""",
    # 10: Regular pentagon circumradius 2
    """
module reference(){
  translate([0,0,0.05]) cylinder(r=2, h=0.1, center=true, $fn=5);
}
""",
    # 11: 5-pointed star
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true) {
    polygon(points=[
      for (i=[0:4]) each [
        [2*cos(90+i*72), 2*sin(90+i*72)],
        [0.8*cos(90+i*72+36), 0.8*sin(90+i*72+36)]
      ]
    ]);
  }
}
""",
    # 12: Ellipse 4x2
    """
module reference(){
  translate([0,0,0.05]) scale([2,1,1]) cylinder(r=1, h=0.1, center=true, $fn=100);
}
""",
    # 13: Semicircle radius 2
    """
module reference(){
  translate([0,0,0.05]) intersection() {
    cylinder(r=2, h=0.1, center=true, $fn=100);
    translate([0,1,0]) cube([4,2,1], center=true);
  }
}
""",
    # 14: Right triangle legs 4
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[[-2,-2], [2,-2], [-2,2]]);
}
""",
    # 15: Parallelogram
    """
module reference(){
  translate([-0.25,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[[-2,-1], [2,-1], [3,1], [-1,1]]);
}
""",
    # 16: Trapezoid
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[[-2,-1], [2,-1], [1,1], [-1,1]]);
}
""",
    # 17: Regular octagon circumradius 2
    """
module reference(){
  translate([0,0,0.05]) cylinder(r=2, h=0.1, center=true, $fn=8);
}
""",
    # 18: Arrow pointing right
    """
module reference(){
  translate([0,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[
      [-2,-0.5], [0,-0.5], [0,-1], [2,0], [0,1], [0,0.5], [-2,0.5]
    ]);
}
""",
    # 19: Chevron (V-shape)
    """
module reference(){
  translate([0.5,0,0.05]) linear_extrude(0.1, center=true)
    polygon(points=[
      [-2,-1], [-1,-1], [0,0], [-1,1], [-2,1], [-1,0]
    ]);
}
"""
  ]
  if index < len(scads):
    return scads[index]


def quaternionToPitchRollYawInDegrees(q0, q1, q2, q3):
  return [
    math.degrees(math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))),
    math.degrees(math.asin(2 * (q0 * q2 - q1 * q3))),
    math.degrees(math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3)))
  ]


scadModules = """
module tetrahedron(){
    polyhedron(
        points = [
            [0, 0, 0],                               // 0
            [1, 0, 0],                               // 1
            [0.5, sqrt(3)/2, 0],                     // 2
            [0.5, sqrt(3)/6, sqrt(2/3)]              // 3 (apex)
        ],
        faces = [
            [0, 2, 1],   // base (oriented outward)
            [0, 1, 3],
            [1, 2, 3],
            [2, 0, 3]
        ],
        convexity = 4
    );
  
}
"""


def resultToScad(result, aiEngineName, flattern=True):
  try:
    scad = "module result(){ "
    if flattern:
      scad += "linear_extrude(height=0.1){ projection() { minkowski(){cube(0.001); union() { "
    else:
      scad += "union() { "
    for transform in result["tetrahedrons"]:
      scad += "translate([" + str(transform["x"]) + "," + \
          str(transform["y"]) + "," + str(transform["z"]) + "]) rotate(" + \
      str(quaternionToPitchRollYawInDegrees(transform["q0"], transform["q1"], transform["q2"], transform["q3"])) + ") tetrahedron();\n"

    if flattern:
      scad += "}}}}}\n\n"
    else:
      scad += "}}\n\n"
    return scad

  except Exception as e:
    print("Error converting result to SCAD:", e)
    return ""


def _rotate_by_quaternion(point, q0, q1, q2, q3):
  """Rotate a point by a quaternion (q0 is scalar/w component)."""
  # Using quaternion rotation: p' = q * p * q^-1
  px, py, pz = point
  # For unit quaternion, q^-1 = conjugate
  # Simplified rotation formula:
  t0 = 2 * (q1 * pz - q3 * px + q2 * py)
  t1 = 2 * (q2 * pz - q1 * py + q3 * px)
  t2 = 2 * (q3 * pz - q2 * px + q1 * py)
  return [
    px + q0 * t0 + q2 * t2 - q3 * t1, py + q0 * t1 + q3 * t0 - q1 * t2,
    pz + q0 * t2 + q1 * t1 - q2 * t0
  ]


def _get_tetrahedron_vertices(t):
  """Get transformed vertices of a tetrahedron."""
  # Base tetrahedron vertices (from scad definition)
  base_verts = [[0, 0, 0], [1, 0, 0], [0.5, math.sqrt(3) / 2, 0],
                [0.5, math.sqrt(3) / 6, math.sqrt(2 / 3)]]
  verts = []
  for v in base_verts:
    rv = _rotate_by_quaternion(v, t["q0"], t["q1"], t["q2"], t["q3"])
    verts.append([rv[0] + t["x"], rv[1] + t["y"], rv[2] + t["z"]])
  return verts


def _tetrahedrons_intersect(a, b):
  """Check if two tetrahedrons intersect using Separating Axis Theorem."""
  verts_a = _get_tetrahedron_vertices(a)
  verts_b = _get_tetrahedron_vertices(b)

  def cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]

  def sub(p1, p2):
    return [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]

  def dot(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

  def get_face_normals(verts):
    faces = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]]
    normals = []
    for f in faces:
      e1 = sub(verts[f[1]], verts[f[0]])
      e2 = sub(verts[f[2]], verts[f[0]])
      normals.append(cross(e1, e2))
    return normals

  def get_edges(verts):
    edge_pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    return [sub(verts[e[1]], verts[e[0]]) for e in edge_pairs]

  def project(verts, axis):
    dots = [dot(v, axis) for v in verts]
    return min(dots), max(dots)

  def separated_on_axis(axis, verts_a, verts_b):
    if abs(dot(axis, axis)) < 1e-10:  # Degenerate axis
      return False
    min_a, max_a = project(verts_a, axis)
    min_b, max_b = project(verts_b, axis)
    return max_a < min_b or max_b < min_a

  # Test face normals of A and B
  for normal in get_face_normals(verts_a) + get_face_normals(verts_b):
    if separated_on_axis(normal, verts_a, verts_b):
      return False

  # Test cross products of edges
  edges_a = get_edges(verts_a)
  edges_b = get_edges(verts_b)
  for ea in edges_a:
    for eb in edges_b:
      axis = cross(ea, eb)
      if separated_on_axis(axis, verts_a, verts_b):
        return False

  return True  # No separating axis found, they intersect


def validatePostVolume(result, score, resultVolume, referenceVolume, intersectionVolume,
                       differenceVolume):
  tetrahedrons = result["tetrahedrons"]
  for tetrahedron in tetrahedrons:
    if abs(tetrahedron["q0"]**2 + tetrahedron["q1"]**2 + tetrahedron["q2"]**2 +
           tetrahedron["q3"]**2 - 1) > 0.01:
      return score * 0.25, "Quaternion is not normalised. 75% penalty."

  for i, a in enumerate(tetrahedrons):
    for j, b in enumerate(tetrahedrons):
      if i < j and _tetrahedrons_intersect(a, b):
        return score * 0.5, f"Tetrahedrons {i} and {j} intersect. 50% penalty."

  return score, ""


def postProcessScore(score, subPassIndex):
  if subPassIndex == 1:
    return min(1, score / 0.90)  # Circle and ellipse are impossible to cover.

  # Adjust the following to match the best human-found solutions.

  if subPassIndex == 11:
    # Star is impossible as the points are narrower than the tetrahedral angle.
    return min(1, score / 0.4)

  if subPassIndex > 4:
    return min(1, score / 0.6)

  return score


def additionalRenderings(result, subPass, aiEngineName, reference_cache_dir):
  import OpenScad

  structure = resultToScad(result, aiEngineName, False)

  scad = scadModules + structure + """
result();
color([0.2,0.2,0.2]) linear_extrude(height=0.1){ projection() { minkowski(){cube(0.001); result();}}}
"""

  fileName1 = os.path.join(reference_cache_dir, "Tetras_with_shadow1.png")
  fileName2 = os.path.join(reference_cache_dir, "Tetras_with_shadow2.png")
  fileName3 = os.path.join(reference_cache_dir, "Tetras_with_shadow3.png")

  OpenScad.render_scadText_to_png(scad, fileName1)
  OpenScad.render_scadText_to_png(scad, fileName2, "--camera=20,0,100,0,0,0", ["--no-autocenter"])
  OpenScad.render_scadText_to_png(scad, fileName3, "--camera=-30,10,100,0,0,0", ["--no-autocenter"])

  return [fileName1, fileName2, fileName3]


highLevelSummary = """
Creating 2D shapes with regular tetrahedrons isn't something that appears in much
training data, because, why on earth would you want to do that?
<br><br>

Perfect scores are possible for the square and holed square (a single tetrahedron
can make a shadow that casts to a perfect square, but care needs to be taken to avoid intersection 
as you can't tile the plane with them all at the same z level).

<br><br>

Note that multiple rings of tetrahedra stacked in z and projected to z can
approximate a circle very precisely, pixel perfect even.
"""
