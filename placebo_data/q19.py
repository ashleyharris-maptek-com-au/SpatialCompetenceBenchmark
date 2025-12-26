import math
from textwrap import dedent

EPS = 1e-9


def _between(value: float, lo: float, hi: float) -> bool:
  return (value >= lo - EPS) and (value <= hi + EPS)


def _det3(a: float, b: float, c: float, d: float, e: float, f: float, g: float, h: float,
          i: float) -> float:
  return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _solve3x3(M, rhs):
  # Solves M * [u, v, w]^T = rhs via Cramer's rule.
  (a, b, c), (d, e, f), (g, h, i) = M
  r0, r1, r2 = rhs

  det = _det3(a, b, c, d, e, f, g, h, i)
  if abs(det) < 1e-15:
    raise ValueError("Degenerate 3x3 system")

  det_u = _det3(r0, b, c, r1, e, f, r2, h, i)
  det_v = _det3(a, r0, c, d, r1, f, g, r2, i)
  det_w = _det3(a, b, r0, d, e, r1, g, h, r2)

  inv_det = 1.0 / det
  return det_u * inv_det, det_v * inv_det, det_w * inv_det


def _inside_regular_tetrahedron_edge10(x: float, y: float, z: float) -> bool:
  # Assumption: regular tetrahedron of edge length 10 with one edge from (0,0,0) to (10,0,0).
  a = 10.0
  sqrt3 = math.sqrt(3.0)

  A = (0.0, 0.0, 0.0)
  B = (a, 0.0, 0.0)
  C = (0.5 * a, 0.5 * sqrt3 * a, 0.0)
  D = (0.5 * a, (sqrt3 * a) / 6.0, a * math.sqrt(2.0 / 3.0))

  # P = A + u(B-A) + v(C-A) + w(D-A), inside iff u,v,w >= 0 and u+v+w <= 1.
  M = [
    [B[0] - A[0], C[0] - A[0], D[0] - A[0]],
    [B[1] - A[1], C[1] - A[1], D[1] - A[1]],
    [B[2] - A[2], C[2] - A[2], D[2] - A[2]],
  ]
  u, v, w = _solve3x3(M, (x - A[0], y - A[1], z - A[2]))
  return (u >= -EPS) and (v >= -EPS) and (w >= -EPS) and ((u + v + w) <= 1.0 + EPS)


def _inside_hill_tetrahedron(x: float, y: float, z: float, scale: float) -> bool:
  # Vertices:
  # (0,0,0), (scale,0,0), (0,scale,0), (0,0,scale)
  return (x >= -EPS) and (y >= -EPS) and (z >= -EPS) and ((x + y + z) <= scale + EPS)


def inside(index: int, x: float, y: float, z: float) -> bool:
  if index == 0:
    # Unit cube: (0,0,0) -> (1,1,1)
    return _between(x, 0.0, 1.0) and _between(y, 0.0, 1.0) and _between(z, 0.0, 1.0)

  if index == 1:
    # Torus about Z axis, centre at origin: major radius 8, minor radius 2.
    # Implicit form (avoids sqrt):
    # (x^2+y^2+z^2 + R^2 - r^2)^2 <= 4 R^2 (x^2+y^2)
    R = 8.0
    r = 2.0
    xy2 = x * x + y * y
    s = xy2 + z * z + (R * R - r * r)  # R^2 - r^2 = 64 - 4 = 60
    return (s * s) <= (4.0 * R * R * xy2 + EPS)

  if index == 2:
    # Dumbbells: two spheres radius 2 centred at x = +/-4, plus a connecting cylinder of diameter 1.
    rs = 2.0
    cx = 4.0
    cyl_r = 0.5

    in_sphere_pos = ((x - cx) * (x - cx) + y * y + z * z) <= (rs * rs + EPS)
    in_sphere_neg = ((x + cx) * (x + cx) + y * y + z * z) <= (rs * rs + EPS)

    # Cylinder along X axis, spanning between the sphere centres [-4, +4].
    in_cylinder = _between(x, -cx, cx) and ((y * y + z * z) <= (cyl_r * cyl_r + EPS))

    return in_sphere_pos or in_sphere_neg or in_cylinder

  if index == 3:
    # Square pyramid: base side 4 on z=0, centred at origin, height 4 (apex at (0,0,4)).
    if not _between(z, 0.0, 4.0):
      return False
    half_side = 2.0 * (1.0 - z / 4.0)  # = 2 - z/2
    return (abs(x) <= half_side + EPS) and (abs(y) <= half_side + EPS)

  if index == 4:
    # Cylinder: radius 3, height 6, centred at origin, aligned with Z axis.
    return ((x * x + y * y) <= (3.0 * 3.0 + EPS)) and (abs(z) <= 3.0 + EPS)

  if index == 5:
    # Cube: side length 4, centred at origin.
    return (abs(x) <= 2.0 + EPS) and (abs(y) <= 2.0 + EPS) and (abs(z) <= 2.0 + EPS)

  if index == 6:
    # Regular octahedron, centred at origin, with vertices on axes.
    # For vertices at (±a,0,0),(0,±a,0),(0,0,±a): inside iff |x|+|y|+|z| <= a.
    # Edge length = a * sqrt(2) => a = 4 / sqrt(2) = 2*sqrt(2).
    a = 2.0 * math.sqrt(2.0)
    return (abs(x) + abs(y) + abs(z)) <= a + EPS

  if index == 7:
    return _inside_hill_tetrahedron(x, y, z, 10)

  if index == 8:
    # Sphere: radius 4, centred at origin.
    return (x * x + y * y + z * z) <= (4.0 * 4.0 + EPS)

  raise ValueError(f"Unknown index: {index}")


def get_response(subPass: int):
  """Get the placebo response for this question."""
  # Unit cube from 6 Hill tetrahedra
  # Base tetrahedron vertices: (0,0,0), (1,0,0), (0,1,0), (0,0,1)
  # Mirrored tetrahedron (m=1) has vertices: (0,0,0), (-1,0,0), (0,1,0), (0,0,1)
  # 6 tetrahedra tile a unit cube perfectly when using both chiralities
  # Working out the 6 tetrahedra step by step:
  # Base tetrahedron vertices: (0,0,0), (1,0,0), (0,1,0), (0,0,1)
  # T1: identity at origin -> fills corner where x+y+z <= 1
  # T2: mirror + 180°X at (1,1,1) -> fills corner where x+y+z >= 2
  # T3-T6: fill the middle layer (1 <= x+y+z <= 2)
  #
  # For middle tetrahedra, I need to find positions where the tetrahedron
  # stays inside the cube. Using mirror at edge midpoints:
  # T3: mirror at (1,0,0) - vertices (1,0,0), (0,0,0), (1,1,0), (1,0,1)
  # T4: mirror + 180°Y at (0,1,0)
  # T5: mirror + 180°Z at (0,0,1)
  # T6: 180°X at (0,1,1)
  # Cube decomposition: T1 fills x+y+z<=1, T2 fills x+y+z>=2
  # Together they cover 2/6 = 1/3 of the cube with no overlap
  # The middle region (1 <= x+y+z <= 2) needs 4 more tetrahedra
  tetraInUnitCube = [
    # T1: Corner (0,0,0), identity - fills x+y+z <= 1
    {
      "x": 0,
      "y": 0,
      "z": 0,
      "q0": 1,
      "q1": 0,
      "q2": 0,
      "q3": 0
    },

    # T2: Corner (1,1,1), mirror + 180°X - fills x+y+z >= 2
    {
      "x": 1,
      "y": 1,
      "z": 1,
      "q0": 0,
      "q1": 1,
      "q2": 0,
      "q3": 0,
      "m": 1
    },

    # T3: mirror at (1,0,0) - shares edge with T1, fills part of middle
    {
      "x": 1,
      "y": 0,
      "z": 0,
      "q0": 1,
      "q1": 0,
      "q2": 0,
      "q3": 0,
      "m": 1
    },

    # T4: 180°X at (0,1,1) - shares edge with T2, fills part of middle
    {
      "x": 0,
      "y": 1,
      "z": 1,
      "q0": 0,
      "q1": 1,
      "q2": 0,
      "q3": 0
    },

    # T5: 90° X at (0,1,0) - fills another part of middle
    {
      "x": 0,
      "y": 1,
      "z": 0,
      "q0": 0.7071,
      "q1": 0.7071,
      "q2": 0,
      "q3": 0
    },

    # T6: 180°Y mirror at (0,0,1)
    {
      "x": 0,
      "y": 0,
      "z": 1,
      "q0": 0,
      "q1": 0,
      "q2": 1,
      "q3": 0,
      "m": 1
    },
  ]

  def getCoordsOfTetrahedron(tetra: dict):
    """Returns all 4 vertices of the tetrahedron after mirror, rotation, translation."""
    # Base tetrahedron vertices
    base_verts = [
      [0.0, 0.0, 0.0],
      [1.0, 0.0, 0.0],
      [0.0, 1.0, 0.0],
      [0.0, 0.0, 1.0],
    ]

    # Step 1: Mirror along X if m is set
    if tetra.get("m", 0):
      for v in base_verts:
        v[0] = -v[0]

    # Step 2: Apply quaternion rotation
    # Quaternion: q0=w, q1=x, q2=y, q3=z
    w, x, y, z = tetra["q0"], tetra["q1"], tetra["q2"], tetra["q3"]

    # Rotation matrix from quaternion
    # https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation
    def rotate_point(p):
      px, py, pz = p
      # Rotation matrix elements
      r00 = 1 - 2 * (y * y + z * z)
      r01 = 2 * (x * y - z * w)
      r02 = 2 * (x * z + y * w)
      r10 = 2 * (x * y + z * w)
      r11 = 1 - 2 * (x * x + z * z)
      r12 = 2 * (y * z - x * w)
      r20 = 2 * (x * z - y * w)
      r21 = 2 * (y * z + x * w)
      r22 = 1 - 2 * (x * x + y * y)
      return [
        r00 * px + r01 * py + r02 * pz,
        r10 * px + r11 * py + r12 * pz,
        r20 * px + r21 * py + r22 * pz,
      ]

    rotated_verts = [rotate_point(v) for v in base_verts]

    # Step 3: Translate
    tx, ty, tz = tetra["x"], tetra["y"], tetra["z"]
    result = []
    for v in rotated_verts:
      result.append((v[0] + tx, v[1] + ty, v[2] + tz))

    return result

  for tetra in tetraInUnitCube:
    points = getCoordsOfTetrahedron(tetra)
    for pt in points:
      for dimension in pt:
        assert (dimension >= -0.001 and dimension <= 1.001), f"Vertex {pt} out of bounds"

  if subPass == 0:
    return {"tetrahedra": tetraInUnitCube}, "6 Hill tetrahedra tiling unit cube"

  world = []
  for tetra in tetraInUnitCube:
    for dx in range(-5, 11):
      for dy in range(-5, 11):
        for dz in range(-5, 11):
          t = tetra.copy()
          t['x'] += dx
          t['y'] += dy
          t['z'] += dz
          world.append(t)

  shape = []

  for tetra in world:
    points = getCoordsOfTetrahedron(tetra)
    insideCount = 0
    for pt in points:
      if inside(subPass, pt[0], pt[1], pt[2]):
        insideCount += 1
    if insideCount >= 3:
      shape.append(tetra)

  return {
    "tetrahedra": shape
  }, "Brute forcing a 16*16*16 voxel grid, and then subtracting the shape."
