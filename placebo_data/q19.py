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


def _inside_orthoscheme_scaled10(x: float, y: float, z: float) -> bool:
  return (x >= -EPS) and (y >= -EPS) and (z >= -EPS) and (x <= 10.0 +
                                                          EPS) and (z <= y + EPS) and (y <= x + EPS)


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
    r = 2.0 + 0.4  # To get extra tetras, Reference is 650mm3, perfect inside check is 400mm3 short.
    xy2 = x * x + y * y
    s = xy2 + z * z + (R * R - r * r)  # R^2 - r^2 = 64 - 4 = 60
    return (s * s) <= (4.0 * R * R * xy2 + EPS)

  if index == 2:
    # Dumbbells: two spheres radius 3 centred at x = +/-4, plus a connecting cylinder of diameter 1.
    rs = 3.0 + 0.4
    cx = 4.0
    cyl_r = 1

    in_sphere_pos = ((x - cx) * (x - cx) + y * y + z * z) <= (rs * rs + EPS)
    in_sphere_neg = ((x + cx) * (x + cx) + y * y + z * z) <= (rs * rs + EPS)

    # Cylinder along X axis, spanning between the sphere centres [-4, +4].
    in_cylinder = _between(x, -cx, cx) and ((y * y + z * z) <= (cyl_r * cyl_r + EPS))

    return in_sphere_pos or in_sphere_neg or in_cylinder

  if index == 3:
    # Square pyramid: base side 8 on z=0, centred at origin, height 8 (apex at (0,0,8)).
    if not _between(z, 0.0, 8.0):
      return False
    half_side = 4.0 * (1.0 - z / 8.0)
    return (abs(x) <= half_side + EPS) and (abs(y) <= half_side + EPS)

  if index == 4:
    # Cylinder: radius 3, height 6, centred at origin, aligned with Z axis.
    return ((x * x + y * y) <= (3.2 * 3.2 + EPS)) and (abs(z) <= 3.0 + EPS)

  if index == 5:
    # Cube: side length 4, centred at origin.
    return (abs(x) <= 2.0 + EPS) and (abs(y) <= 2.0 + EPS) and (abs(z) <= 2.0 + EPS)

  if index == 6:
    # Octagonal prism: cylinder(r=4, h=2, center=true, $fn=8)
    return ((x * x + y * y) <= (4.5 * 4.5 + EPS)) and (abs(z) <= 1.0 + EPS)

  if index == 7:
    return _inside_orthoscheme_scaled10(x, y, z)

  if index == 8:
    # Sphere: radius 6, centred at origin.
    return (x * x + y * y + z * z) <= (6.2 * 6.2 + EPS)

  raise ValueError(f"Unknown index: {index}")


def get_response(subPass: int):
  """Get the placebo response for this question."""

  # Hill tetrahedra space-filling tiling
  # The base Hill tetrahedron has vertices: (0,0,0), (1,0,0), (0,1,0), (0,0,1)
  # It fills the region where x >= 0, y >= 0, z >= 0, and x + y + z <= 1
  #
  # Space is tiled by pairs of tetrahedra (one of each chirality) that form right
  # triangular prisms. Three such prisms (6 tetrahedra) tile a unit cube.
  #
  # The key insight: T1 at origin fills x+y+z <= 1. Its mirror T2 at (1,0,0) fills
  # the region where x >= y+z (within [0,1]×[0,1]×[0,1] near the X edge).
  # Together they form a triangular prism. Rotating this pattern around the 3 axes
  # tiles the cube.

  sqrt2_2 = 0.7071067811865476  # sqrt(2)/2 = cos(45°) = sin(45°)

  # 6 orthoschemes tile unit cube via sorted-coordinates decomposition
  # Base tetrahedron: (0,0,0), (1,0,0), (1,1,0), (1,1,1) - region z≤y≤x
  # Format: (tx, ty, tz, q0, q1, q2, q3, mirror)
  cube_tiling_base = [
    (0, 0, 0, 1, 0, 0, 0, 0),
    (0, 0, 0, 0.5, 0.5, 0.5, 0.5, 0),
    (0, 0, 0, 0.5, -0.5, -0.5, -0.5, 0),
    (0, 0, 0, sqrt2_2, 0, 0, -sqrt2_2, 1),
    (0, 0, 0, 0, 0, sqrt2_2, sqrt2_2, 1),
    (0, 0, 0, sqrt2_2, 0, sqrt2_2, 0, 1),
  ]

  def quat_multiply(a, b):
    """Multiply quaternions a * b. Format: (w, x, y, z)"""
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
      aw * bw - ax * bx - ay * by - az * bz,
      aw * bx + ax * bw + ay * bz - az * by,
      aw * by - ax * bz + ay * bw + az * bx,
      aw * bz + ax * by - ay * bx + az * bw,
    )

  def rotate_point_by_quat(p, q):
    """Rotate point p by quaternion q."""
    w, x, y, z = q
    px, py, pz = p
    r00 = 1 - 2 * (y * y + z * z)
    r01 = 2 * (x * y - z * w)
    r02 = 2 * (x * z + y * w)
    r10 = 2 * (x * y + z * w)
    r11 = 1 - 2 * (x * x + z * z)
    r12 = 2 * (y * z - x * w)
    r20 = 2 * (x * z - y * w)
    r21 = 2 * (y * z + x * w)
    r22 = 1 - 2 * (x * x + y * y)
    return (
      r00 * px + r01 * py + r02 * pz,
      r10 * px + r11 * py + r12 * pz,
      r20 * px + r21 * py + r22 * pz,
    )

  def generate_cube_tiling_at(cx, cy, cz):
    """Generate 6 tetrahedra for one cube cell at integer coordinates."""
    tetras = []
    for tx, ty, tz, q0, q1, q2, q3, m in cube_tiling_base:
      tetras.append({
        "x": cx + tx,
        "y": cy + ty,
        "z": cz + tz,
        "q0": q0,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "m": m
      })
    return tetras

  def generate_space_filling_tetrahedra(x_range, y_range, z_range):
    """Generate tetrahedra that tile 3D space."""
    tetrahedra = []
    for cx in range(x_range[0], x_range[1]):
      for cy in range(y_range[0], y_range[1]):
        for cz in range(z_range[0], z_range[1]):
          tetrahedra.extend(generate_cube_tiling_at(cx, cy, cz))
    return tetrahedra

  def getCoordsOfTetrahedron(tetra: dict):
    """Returns all 4 vertices of the tetrahedron after mirror, rotation, translation."""
    # Base orthoscheme vertices (matches scadModules tetrahedron)
    base_verts = [
      [0.0, 0.0, 0.0],
      [1.0, 0.0, 0.0],
      [1.0, 1.0, 0.0],
      [1.0, 1.0, 1.0],
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

  def score_tetra_for_shape(tetra, subpass_idx):
    """Score a tetrahedron by how many vertices are inside the target shape."""
    points = getCoordsOfTetrahedron(tetra)
    return sum(1 for pt in points if inside(subpass_idx, pt[0], pt[1], pt[2]))

  # For subPass 0 (unit cube), generate just the 1 cube cell
  if subPass == 0:
    tetrahedra = generate_space_filling_tetrahedra((0, 1), (0, 1), (0, 1))
    return {"tetrahedra": tetrahedra}, "Placebo thinking... hmmm..."

  # For subPass 7 (scaled tetrahedron), use simple approach - the shape is already aligned
  if subPass == 7:
    world = generate_space_filling_tetrahedra((0, 11), (0, 11), (0, 11))
    shape = []
    for tetra in world:
      if score_tetra_for_shape(tetra, subPass) == 4:
        shape.append(tetra)
    return {"tetrahedra": shape}, "Orthoscheme scaled by 10"

  # For other shapes, generate grid and filter by all-vertices-inside
  world = generate_space_filling_tetrahedra((-11, 11), (-11, 11), (-11, 11))
  shape = []
  for tetra in world:
    if score_tetra_for_shape(tetra, subPass) == 4:
      shape.append(tetra)

  return {"tetrahedra": shape}, "Space-filling tetrahedra tiling, filtered by shape boundary."


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  count = rng.randint(5, 15)
  tetrahedra = []
  for _ in range(count):
    q = [rng.uniform(-1.0, 1.0) for _ in range(4)]
    norm = math.sqrt(sum(v * v for v in q)) or 1.0
    tetrahedra.append({
      "x": rng.uniform(-5.0, 5.0),
      "y": rng.uniform(-5.0, 5.0),
      "z": rng.uniform(-5.0, 5.0),
      "q0": q[0] / norm,
      "q1": q[1] / norm,
      "q2": q[2] / norm,
      "q3": q[3] / norm,
      "m": rng.choice([0, 1]),
    })
  return {"tetrahedra": tetrahedra}, "Random guess"
