import math

import scad_format

import OpenScad

title = "Tetrahedron Packing in 3D"
true = True

prompt = """
Here is the points and faces of a tetrahedron
It has three edges of length 1, two edges of length sqrt(2), and one edge of length sqrt(3).

polyhedron(
    points = [
        [0, 0, 0],                               // 0 (origin corner)
        [1, 0, 0],                               // 1 (along X)
        [1, 1, 0],                               // 2 (along Y)
        [1, 1, 1]                                // 3 (along Z)
    ],
    faces = [
        [0, 2, 1],   // Z=0 face
        [0, 1, 3],   // y=z face
        [0, 3, 2],   // x=y face
        [1, 2, 3]    // x=1 face
    ],
    convexity = 4
);

We define an 8-part rigid transform of (x,y,z,q0,q1,q2,q3,m), where q0,q1,q2,q3 is a normalised quaternion, x, y, z are the translation, and m is an optional mirror flag.
If m is non-zero, the tetrahedron is mirrored along the X-axis before rotation. This allows both chiralities of the tetrahedron to be used.
Rotation is defined around the 0,0,0 point (which is not the centre), and is performed before translation.

We create a scene with multiple tetrahedra, each with a different transform. Now we can pack them in as tightly as possible
in order to create a 3D shape, trying to maximize packing density and recreate the target shape.

Return the transform array of tetrahedra in order to create a:
"""

structure = {
  "type": "object",
  "properties": {
    "tetrahedra": {
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
          },
          "m": {
            "type": "number",
            "description": "Mirror flag. If non-zero, mirror along X-axis before rotation."
          }
        },
        "additionalProperties": False,
        "required": ["x", "y", "z", "q0", "q1", "q2", "q3", "m"],
        "propertyOrdering": ["x", "y", "z", "q0", "q1", "q2", "q3", "m"]
      }
    }
  },
  "propertyOrdering": ["tetrahedra"],
  "required": ["tetrahedra"],
  "additionalProperties": False
}

earlyFail = True

subpassParamSummary = [
  "Create a unit cube",
  "Create a torus with major radius 8 and minor radius 2",
  "Create a set of dumbbells with spheres of radius 3 and a connecting cylinder of diameter 2",
  "Create an axially aligned square based pyramid with base side 8 and height 8, sitting on the Z=0 plane, centered at origin",
  "Create a cylinder with radius 3 and height 6, centered at origin and aligned along the Z-axis",
  "Create a cube of side length 4, centered at origin",
  "Create an octagonal prism (cylinder with $fn=8) with radius 4 and height 2, centered at origin",
  "Create the provided tetrahedron scaled up by a factor of 10",
  "Create a sphere of radius 6",
]

noMinkowski = True


def prepareSubpassPrompt(index: int) -> str:
  if index == 0:
    return prompt + "Unit cube (0,0,0) -> (1,1,1)"
  if index == 1:
    return prompt + "Torus of major radius 8, and minor radius 2, with the center at origin."
  if index == 2:
    return prompt + "Set of dumbbells. 2 spheres of radius 3, with centers x = +/-4, and a cylinder of diameter 2 connecting them."
  if index == 3:
    return prompt + "Axially aligned square based pyramid with base side 8 and height 8, sitting on the Z=0 plane, centered at origin."
  if index == 4:
    return prompt + "Cylinder of radius 3 and height 6, centered at origin and aligned along the Z-axis."
  if index == 5:
    return prompt + "Cube of side length 4, centered at origin."
  if index == 6:
    return prompt + "Octagonal prism (cylinder with $fn=8) of radius 4 and height 2, centered at origin."
  if index == 7:
    return prompt + "The provided tetrahedron scaled up by a factor of 10."
  if index == 8:
    return prompt + "Sphere of radius 6, with the center at origin."
  raise StopIteration


referenceScad = """
module reference(){
    cube(1);
}
"""


def prepareSubpassReferenceScad(index: int) -> str:
  if index == 0:
    return """
module reference(){
  cube(1);
}
        """

  if index == 1:
    return """
module reference(){
    rotate_extrude()
        translate([8, 0, 0])
            circle(r = 2, $fn = 16);
}
"""
  if index == 2:
    return """
module reference(){
  union() {
    translate([-4,0,0]) sphere(r=3);
    translate([ 4,0,0]) sphere(r=3);
    translate([0,0,0]) rotate([0,90,0]) cylinder(r=1, h=8, center=true, $fn=30);
  }
}
"""
  if index == 3:
    return """
module reference(){
    rotate([0,0,45]) cylinder(r1=4, r2=0,h=8, $fn=4);
}
"""

  if index == 4:
    return """
module reference(){
    cylinder(r=3, h=6, center=true, $fn=50);
}
"""

  if index == 5:
    return """
module reference(){
    cube([4,4,4], center=true);
}
"""

  if index == 6:
    return """
module reference(){
    cylinder(r=4, h=2, center=true, $fn=8);
}
"""

  if index == 7:
    return """
module reference(){
    scale([10,10,10]) tetrahedron();
}
"""
  if index == 8:
    return """
module reference(){
    sphere(r=6, $fn=20);
}
"""


def quaternionToPitchRollYawInDegrees(q0, q1, q2, q3):
  # Convert quaternion to Euler angles for OpenSCAD's rotate([x,y,z]) which applies X then Y then Z
  # This is equivalent to intrinsic ZYX Euler angles
  # q0=w, q1=x, q2=y, q3=z
  w, x, y, z = q0, q1, q2, q3

  # Check for gimbal lock (pitch = ±90°)
  sinp = 2 * (w * y - z * x)
  sinp = max(-1.0, min(1.0, sinp))  # Clamp for floating point

  if abs(sinp) >= 0.999:
    # Gimbal lock: set roll to 0 and compute yaw
    pitch = math.copysign(math.pi / 2, sinp)
    roll = 0
    yaw = 2 * math.atan2(x, w)
  else:
    pitch = math.asin(sinp)
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

  return [math.degrees(roll), math.degrees(pitch), math.degrees(yaw)]


scadModules = """
module tetrahedron(){
    // Orthoscheme - 1/6 of a unit cube via sorted-coordinates decomposition
    // This tetrahedron tiles the cube when combined with 5 rotated copies
    // Vertices follow the path (0,0,0) -> (1,0,0) -> (1,1,0) -> (1,1,1)
    // Region: z <= y <= x (one of 6 permutation regions)
    hull() {
        translate([0, 0, 0]) cube(0.001);
        translate([1, 0, 0]) cube(0.001);
        translate([1, 1, 0]) cube(0.001);
        translate([1, 1, 1]) cube(0.001);
    }
}
"""


def resultToScad(result, aiEngineName):
  colors = [
    "\"White\"", "\"Red\"", "\"Blue\"", "\"Yellow\"", "\"Green\"", "[0,0,0.5]", "[0.5,0,0]",
    "\"Orange\"", "[210/255, 180/255, 140/255]", "[170/255, 140/255, 100/255]",
    "[92/255, 64/255, 51/255]", "[62/255, 38/255, 20/255]"
  ]

  scad = "module result(){ "
  #scad += "minkowski(){cube(0.001); union() { "
  tetras = []
  printedTetrahedra = 0
  for transform in result["tetrahedra"]:
    try:
      # if any nans or infinites, skip
      if any([math.isnan(x) or math.isinf(x) for x in transform.values()]):
        print("Dropping a tetrahedron that wasn't finite: " + str(transform))
        continue

      # If quaternion is not normalised, skip it.
      magnitude = abs(transform["q0"]**2 + transform["q1"]**2 + transform["q2"]**2 +
                      transform["q3"]**2)
      if magnitude - 1 > 0.001:
        print("Dropping a tetrahedron that wasn't normalised |q| = " + str(magnitude) + ": " +
              str(transform))
        continue

      mirror_str = "mirror([1,0,0]) " if transform.get("m", 0) != 0 else ""
      tetras.append("color(" + colors[printedTetrahedra % len(colors)] + ") translate([" + str(transform["x"]) + "," + \
          str(transform["y"]) + "," + str(transform["z"]) + "]) rotate(" + \
          str(quaternionToPitchRollYawInDegrees(transform["q0"], transform["q1"], transform["q2"], transform["q3"])) + ") " + mirror_str + "tetrahedron();\n")
      printedTetrahedra += 1
    except Exception as e:
      print("Dropping a tetrahedron that wasn't valid: " + str(transform) + " " + str(e))

  if printedTetrahedra == 0:
    print("Test 19: No valid tetrahedra were provided by the LLM.")
    return ""

  scad += "\n".join(tetras)

  scad += "}\n\n"
  scad = scad_format.format_code(scad, OpenScad.formatConfig)
  return scad


def lateFailTest(result, subPass):
  tetras = result.get("tetrahedra", []) if isinstance(result, dict) else []
  if not tetras or len(tetras) < 2:
    return None

  base_verts = [
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [1.0, 1.0, 0.0],
    [1.0, 1.0, 1.0],
  ]

  def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

  def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

  def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

  def _norm_axis(a, eps=1e-12):
    lsq = a[0] * a[0] + a[1] * a[1] + a[2] * a[2]
    if lsq <= eps * eps:
      return None
    inv = 1.0 / math.sqrt(lsq)
    return (a[0] * inv, a[1] * inv, a[2] * inv)

  def _verts_world(t):
    verts = [v[:] for v in base_verts]
    if t.get("m", 0) != 0:
      for v in verts:
        v[0] = -v[0]

    w = t["q0"]
    x = t["q1"]
    y = t["q2"]
    z = t["q3"]

    r00 = 1 - 2 * (y * y + z * z)
    r01 = 2 * (x * y - z * w)
    r02 = 2 * (x * z + y * w)
    r10 = 2 * (x * y + z * w)
    r11 = 1 - 2 * (x * x + z * z)
    r12 = 2 * (y * z - x * w)
    r20 = 2 * (x * z - y * w)
    r21 = 2 * (y * z + x * w)
    r22 = 1 - 2 * (x * x + y * y)

    tx = t["x"]
    ty = t["y"]
    tz = t["z"]

    out = []
    for vx, vy, vz in verts:
      rx = r00 * vx + r01 * vy + r02 * vz
      ry = r10 * vx + r11 * vy + r12 * vz
      rz = r20 * vx + r21 * vy + r22 * vz
      out.append((rx + tx, ry + ty, rz + tz))
    return out

  def _aabb(verts):
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

  def _aabb_overlap(a, b, tol):
    return not (a[1] <= b[0] + tol or b[1] <= a[0] + tol or a[3] <= b[2] + tol or b[3] <= a[2] + tol
                or a[5] <= b[4] + tol or b[5] <= a[4] + tol)

  def _project_interval(verts, axis):
    p0 = _dot(verts[0], axis)
    mn = p0
    mx = p0
    for v in verts[1:]:
      p = _dot(v, axis)
      if p < mn:
        mn = p
      if p > mx:
        mx = p
    return mn, mx

  def _tetra_intersect(a_verts, b_verts, tol):
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    axes = []

    for i, j, k in faces:
      na = _cross(_sub(a_verts[j], a_verts[i]), _sub(a_verts[k], a_verts[i]))
      na = _norm_axis(na)
      if na is not None:
        axes.append(na)
      nb = _cross(_sub(b_verts[j], b_verts[i]), _sub(b_verts[k], b_verts[i]))
      nb = _norm_axis(nb)
      if nb is not None:
        axes.append(nb)

    a_edges = [_sub(a_verts[j], a_verts[i]) for i, j in edges]
    b_edges = [_sub(b_verts[j], b_verts[i]) for i, j in edges]
    for ea in a_edges:
      for eb in b_edges:
        ax = _norm_axis(_cross(ea, eb))
        if ax is not None:
          axes.append(ax)

    for axis in axes:
      a_min, a_max = _project_interval(a_verts, axis)
      b_min, b_max = _project_interval(b_verts, axis)
      if a_max <= b_min + tol or b_max <= a_min + tol:
        return False
    return True

  tol = 1e-6
  cell_size = 1.5
  grid = {}
  verts_cache = []
  aabb_cache = []

  for t in tetras:
    verts = _verts_world(t)
    verts_cache.append(verts)
    aabb_cache.append(_aabb(verts))

  for i, a in enumerate(aabb_cache):
    x0 = int(math.floor(a[0] / cell_size))
    x1 = int(math.floor(a[1] / cell_size))
    y0 = int(math.floor(a[2] / cell_size))
    y1 = int(math.floor(a[3] / cell_size))
    z0 = int(math.floor(a[4] / cell_size))
    z1 = int(math.floor(a[5] / cell_size))

    candidates = set()
    for cx in range(x0, x1 + 1):
      for cy in range(y0, y1 + 1):
        for cz in range(z0, z1 + 1):
          key = (cx, cy, cz)
          if key in grid:
            for j in grid[key]:
              if j < i:
                candidates.add(j)
          grid.setdefault(key, []).append(i)

    for j in candidates:
      if not _aabb_overlap(aabb_cache[i], aabb_cache[j], tol):
        continue
      if _tetra_intersect(verts_cache[i], verts_cache[j], tol):
        return f"Intersecting tetrahedra {j} and {i}"
  return None


def postProcessScore(score, subPass):
  if subPass in [0, 5, 7]:
    # These passes it's possible to perfectly solve - the interior angles match the angles of an integer number
    # of tetrahedra. We allow a 5% margin of error as there's a 0.001 error in the tetrahedron model as a
    # result of working around CSG issues in OpenSCAD.
    return min(1, score / 0.95)

  # These other ones are impossible to perfectly solve - they have curves or the tetrahedra doesn't fit
  # right up tight in the corners.
  return min(1, score / 0.75)


highLevelSummary = """
Can the LLM create complex shapes out of tetrahedra?
<br><br>
The tetrahedra given to the LLM are not regular, but can tile 3D space
perfectly - 6 of them combine to form a cube. However, they are chiral 
(come in left and right-handed versions),
so both chiralities are needed for perfect tiling.
<br><br>
The LLM needs to figure out the correct rotations and translations to pack these
tetrahedra into the target shapes without gaps or overlaps.
"""
