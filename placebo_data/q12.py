"""
Physics-based spring dynamics solver for loop fitting problem.

Each constraint is modeled as a spring or force:
- Pipe length: springs pulling each edge to unit length
- Fixed start: force pulling point 0 to target position
- Boundary touch: force pulling closest point toward untouched boundary
- Angle range: torque springs keeping angles within valid range
- No crossings: repulsive forces between crossing segments
- Centroid: force shifting all points to center the centroid
- Quadrants: force pushing points into missing quadrants
- Convex hull: repulsive forces spreading vertices outward
- Point separation: repulsive forces between close non-adjacent points
"""

import importlib.util
import json
import math
import os
import random
import sys
import tempfile
import time
import filelock  # pip install filelock for concurrency-safe caching
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Load problem definition from parent directory
basePath = Path(__file__).resolve().parent.parent
sys.path.append(str(basePath))


def _load_problem():
  mod_path = basePath / "12.py"
  spec = importlib.util.spec_from_file_location("bench12", mod_path)
  mod = importlib.util.module_from_spec(spec)
  assert spec.loader is not None
  spec.loader.exec_module(mod)
  return mod.testParams, mod.gradeAnswer


# ---------------------------------------------------------------------------
# Vector math helpers
# ---------------------------------------------------------------------------


def _clamp(v: float, lo: float, hi: float) -> float:
  return max(lo, min(hi, v))


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
  return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _normalize(dx: float, dy: float) -> Tuple[float, float]:
  mag = math.hypot(dx, dy)
  if mag < 1e-10:
    return (0.0, 0.0)
  return (dx / mag, dy / mag)


def _dot(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
  return v1[0] * v2[0] + v1[1] * v2[1]


def _cross_2d(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
  """2D cross product (z-component of 3D cross)."""
  return v1[0] * v2[1] - v1[1] * v2[0]


def _angle_deg(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
  """Angle at vertex b formed by points a-b-c."""
  v1 = (a[0] - b[0], a[1] - b[1])
  v2 = (c[0] - b[0], c[1] - b[1])
  len1 = math.hypot(v1[0], v1[1])
  len2 = math.hypot(v2[0], v2[1])
  if len1 < 1e-10 or len2 < 1e-10:
    return 180.0
  dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
  dot = max(-1.0, min(1.0, dot))
  return math.degrees(math.acos(dot))


def _segments_intersect(p1, p2, p3, p4) -> bool:
  """Check if segment p1-p2 intersects segment p3-p4 (excluding endpoints)."""
  eps = 1e-9
  # Skip if sharing endpoints
  if (abs(p1[0] - p3[0]) < eps and abs(p1[1] - p3[1]) < eps) or \
     (abs(p1[0] - p4[0]) < eps and abs(p1[1] - p4[1]) < eps) or \
     (abs(p2[0] - p3[0]) < eps and abs(p2[1] - p3[1]) < eps) or \
     (abs(p2[0] - p4[0]) < eps and abs(p2[1] - p4[1]) < eps):
    return False

  def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

  return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def _segment_midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
  return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def _convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
  pts = sorted(set(points))
  if len(pts) <= 1:
    return pts

  def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

  lower = []
  for p in pts:
    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
      lower.pop()
    lower.append(p)
  upper = []
  for p in reversed(pts):
    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
      upper.pop()
    upper.append(p)
  return lower[:-1] + upper[:-1]


def _polygon_area(poly: List[Tuple[float, float]]) -> float:
  if len(poly) < 3:
    return 0.0
  area = 0.0
  for i in range(len(poly)):
    x1, y1 = poly[i]
    x2, y2 = poly[(i + 1) % len(poly)]
    area += x1 * y2 - x2 * y1
  return abs(area) / 2.0


# ---------------------------------------------------------------------------
# Solution caching (concurrency-safe)
# ---------------------------------------------------------------------------

CACHE_DIR = Path(tempfile.gettempdir()) / "q12_cache"


def _get_cache_path(subPass: int) -> Path:
  """Get the cache file path for a subpass."""
  return CACHE_DIR / f"subpass_{subPass}.json"


def _load_cached_solution(subPass: int) -> Optional[Dict]:
  """Load a cached solution if it exists and is valid."""
  cache_path = _get_cache_path(subPass)
  lock_path = cache_path.with_suffix(".lock")

  if not cache_path.exists():
    return None

  try:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with filelock.FileLock(lock_path, timeout=5):
      if cache_path.exists():
        with open(cache_path, "r") as f:
          return json.load(f)
  except (filelock.Timeout, json.JSONDecodeError, IOError):
    pass
  return None


def _save_cached_solution(subPass: int, answer: Dict) -> None:
  """Save a solution to cache (concurrency-safe)."""
  cache_path = _get_cache_path(subPass)
  lock_path = cache_path.with_suffix(".lock")

  try:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with filelock.FileLock(lock_path, timeout=5):
      with open(cache_path, "w") as f:
        json.dump(answer, f)
  except (filelock.Timeout, IOError):
    pass  # Failed to cache, not critical


# ---------------------------------------------------------------------------
# Physics simulation
# ---------------------------------------------------------------------------


class SpringSimulation:
  """
  Physics-based solver using spring dynamics to satisfy loop constraints.
  
  Each point has position and velocity. Forces are computed from:
  - Edge springs (target length = 1.0)
  - Constraint-specific forces based on error feedback
  """

  def __init__(self,
               subPass: int,
               seed: Optional[int] = None,
               lastSolver: Optional['SpringSimulation'] = None):
    self.subPass = subPass
    self.rng = random.Random(seed or int(time.time() * 1000))
    self.testParams, self.gradeAnswer = _load_problem()
    params = self.testParams[subPass]
    self.n = params["pipes"]
    self.boundary = params["boundary"]
    self.tolerance = params.get("tolerance", 0.05)
    self.complications = params.get("complications", [])

    # Parse complications into easy-to-use structure
    self.constraints = self._parse_constraints()

    # Physics parameters
    self.dt = 0.05  # time step
    self.damping = 0.85  # velocity damping per step
    self.max_velocity = 2.0  # cap velocity magnitude

    # Spring constants - structural constraints at full strength from start
    self.k_boundary = 8.0  # boundary constraint
    self.k_fixed = 25.0  # fixed start constraint
    self.k_crossing = 15.0  # crossing repulsion
    self.k_centroid = 3.0  # centroid constraint
    self.k_quadrant = 4.0  # quadrant coverage
    self.k_hull = 2.0  # hull expansion
    self.k_separation = 10.0  # point separation
    self.k_margin = 8.0  # margin avoidance
    self.k_backtrack = 15.0  # backtrack prevention
    self.k_turn = 3.0  # turn encouragement

    # Edge spring ramps up over time - start soft, get rigid
    self.k_edge_min = 1.0  # initial edge spring strength (very soft)
    self.k_edge_max = 100.0  # final edge spring strength (very rigid)

    # Angle spring ramps up over time - start soft, get rigid
    self.k_angle_min = 1.0  # initial angle spring strength (very soft)
    self.k_angle_max = 50.0  # final angle spring strength (very rigid)

    if lastSolver:
      self.k_edge_min = lastSolver.k_edge_min
      self.k_edge_max = lastSolver.k_edge_max
      self.k_angle_min = lastSolver.k_angle_min
      self.k_angle_max = lastSolver.k_angle_max

  def _parse_constraints(self) -> Dict[str, Any]:
    """Parse complications into a constraint dictionary."""
    constraints = {
      "max_crossings": None,
      "exact_crossings": None,
      "angle_range": None,
      "centroid_box": None,
      "must_touch_boundary": None,
      "min_turns": None,
      "max_straight_run": None,
      "coverage_quadrants": False,
      "avoid_margin": None,
      "min_convex_hull_area": None,
      "fixed_start": None,
      "min_point_separation": None,
    }
    for comp in self.complications:
      ctype = comp["type"]
      if ctype == "max_crossings":
        constraints["max_crossings"] = comp["max"]
      elif ctype == "exact_crossings":
        constraints["exact_crossings"] = comp["count"]
      elif ctype == "angle_range":
        constraints["angle_range"] = (comp["min_deg"], comp["max_deg"])
      elif ctype == "centroid_box":
        constraints["centroid_box"] = (
          self.boundary * comp["xmin_ratio"],
          self.boundary * comp["xmax_ratio"],
          self.boundary * comp["ymin_ratio"],
          self.boundary * comp["ymax_ratio"],
        )
      elif ctype == "must_touch_boundary":
        constraints["must_touch_boundary"] = comp["edges_needed"]
      elif ctype == "min_turns":
        constraints["min_turns"] = comp["min_turns"]
      elif ctype == "max_straight_run":
        constraints["max_straight_run"] = comp["max_run"]
      elif ctype == "coverage_quadrants":
        constraints["coverage_quadrants"] = True
      elif ctype == "avoid_margin":
        constraints["avoid_margin"] = self.boundary * comp["margin_ratio"]
      elif ctype == "min_convex_hull_area":
        constraints["min_convex_hull_area"] = (self.boundary**2) * comp["min_area_ratio"]
      elif ctype == "fixed_start":
        constraints["fixed_start"] = (self.boundary * comp["x_ratio"],
                                      self.boundary * comp["y_ratio"], comp.get("tolerance", 0.25))
      elif ctype == "min_point_separation":
        constraints["min_point_separation"] = comp["min_dist"]
    return constraints

  def _init_positions(self) -> List[List[float]]:
    """Initialize positions based on constraints."""
    center = self.boundary / 2

    # If exact_crossings is required, start with a figure-8 pattern
    if self.constraints["exact_crossings"] and self.constraints["exact_crossings"] > 0:
      return self._init_figure_eight()

    # Otherwise use regular polygon
    # For n points around a circle, chord length = 2*r*sin(pi/n)
    # For chord = 1, r = 1/(2*sin(pi/n))
    if self.n >= 3:
      ideal_r = 1.0 / (2 * math.sin(math.pi / self.n))
    else:
      ideal_r = 1.0
    max_r = (self.boundary - 0.4) / 2
    r = min(ideal_r, max_r)

    # If fixed_start constraint, shift the polygon to start near that point
    if self.constraints["fixed_start"]:
      fx, fy, _ = self.constraints["fixed_start"]
      # Calculate where point 0 would be in a centered polygon
      start_x = center + r
      start_y = center
      # Shift entire polygon
      shift_x = fx - start_x
      shift_y = fy - start_y
      center_x = center + shift_x * 0.5  # partial shift to stay in bounds
      center_y = center + shift_y * 0.5
    else:
      center_x, center_y = center, center

    pts = []
    for i in range(self.n):
      ang = 2 * math.pi * i / self.n
      x = center_x + r * math.cos(ang)
      y = center_y + r * math.sin(ang)
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])
    return pts

  def _init_figure_eight(self) -> List[List[float]]:
    """Initialize as a figure-8 pattern that has crossings."""
    center = self.boundary / 2
    # Scale to fit in boundary
    scale = min(self.boundary * 0.35, self.n / (2 * math.pi) * 0.5)

    pts = []
    crossings_needed = self.constraints["exact_crossings"]

    # Lissajous curve: x = sin(t), y = sin(2t) creates figure-8 with 1 crossing
    # For more crossings, use higher frequency: y = sin((crossings+1)*t)
    freq = crossings_needed + 1

    for i in range(self.n):
      t = 2 * math.pi * i / self.n
      x = center + scale * math.sin(t)
      y = center + scale * math.sin(freq * t) * 0.8
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])
    return pts

  def _init_velocities(self) -> List[List[float]]:
    """Initialize velocities to zero."""
    return [[0.0, 0.0] for _ in range(self.n)]

  def _compute_forces(self, pos: List[List[float]], progress: float = 0.0) -> List[List[float]]:
    """Compute all forces on each point.
    
    Args:
      pos: Current positions of all points
      progress: 0.0 to 1.0 indicating simulation progress, used for ramping edge strength
    """
    forces = [[0.0, 0.0] for _ in range(self.n)]
    n = self.n

    # Edge and angle spring strength ramps up and down (out of sync with each other) with progress
    k_edge = self.k_edge_min + (self.k_edge_max - self.k_edge_min) * min(
      0, math.sin(progress * .013))
    k_angle = self.k_angle_min + (self.k_angle_max - self.k_angle_min) * min(
      0, math.sin(progress * .037))

    # 1. Edge length springs - each edge wants to be length 1.0
    for i in range(n):
      j = (i + 1) % n
      dx = pos[j][0] - pos[i][0]
      dy = pos[j][1] - pos[i][1]
      dist = math.hypot(dx, dy)
      if dist > 1e-10:
        # Spring force: F = k * (dist - rest_length) * direction
        stretch = dist - 1.0
        fx = k_edge * stretch * dx / dist
        fy = k_edge * stretch * dy / dist
        forces[i][0] += fx
        forces[i][1] += fy
        forces[j][0] -= fx
        forces[j][1] -= fy

    # 2. Boundary forces - keep points inside
    margin = 0.05
    for i in range(n):
      x, y = pos[i]
      # Push away from walls
      if x < margin:
        forces[i][0] += self.k_boundary * (margin - x)
      if x > self.boundary - margin:
        forces[i][0] -= self.k_boundary * (x - (self.boundary - margin))
      if y < margin:
        forces[i][1] += self.k_boundary * (margin - y)
      if y > self.boundary - margin:
        forces[i][1] -= self.k_boundary * (y - (self.boundary - margin))

    # 3. Fixed start constraint
    if self.constraints["fixed_start"]:
      fx, fy, tol = self.constraints["fixed_start"]
      dx = fx - pos[0][0]
      dy = fy - pos[0][1]
      dist = math.hypot(dx, dy)
      if dist > tol * 0.1:  # Apply force even within tolerance to center it
        forces[0][0] += self.k_fixed * dx
        forces[0][1] += self.k_fixed * dy

    # 4. Boundary touch constraint - push points toward untouched edges
    if self.constraints["must_touch_boundary"]:
      edges_needed = self.constraints["must_touch_boundary"]
      tol_edge = max(1e-3, self.boundary * 0.001)
      edges_hit = set()
      edge_points = {"left": [], "right": [], "bottom": [], "top": []}

      for i in range(n):
        x, y = pos[i]
        if abs(x) <= tol_edge:
          edges_hit.add("left")
        if abs(x - self.boundary) <= tol_edge:
          edges_hit.add("right")
        if abs(y) <= tol_edge:
          edges_hit.add("bottom")
        if abs(y - self.boundary) <= tol_edge:
          edges_hit.add("top")
        # Track closest point to each edge
        edge_points["left"].append((x, i))
        edge_points["right"].append((self.boundary - x, i))
        edge_points["bottom"].append((y, i))
        edge_points["top"].append((self.boundary - y, i))

      missing_edges = {"left", "right", "bottom", "top"} - edges_hit
      if len(edges_hit) < edges_needed and missing_edges:
        # For each missing edge, push the closest point toward it
        for edge in missing_edges:
          if edge == "left":
            closest = min(edge_points["left"], key=lambda x: x[0])
            forces[closest[1]][0] -= self.k_boundary * 2
          elif edge == "right":
            closest = min(edge_points["right"], key=lambda x: x[0])
            forces[closest[1]][0] += self.k_boundary * 2
          elif edge == "bottom":
            closest = min(edge_points["bottom"], key=lambda x: x[0])
            forces[closest[1]][1] -= self.k_boundary * 2
          elif edge == "top":
            closest = min(edge_points["top"], key=lambda x: x[0])
            forces[closest[1]][1] += self.k_boundary * 2

    # 5. Angle constraints - apply torque to keep angles in range
    if self.constraints["angle_range"]:
      min_deg, max_deg = self.constraints["angle_range"]
      mid_angle = (min_deg + max_deg) / 2

      for i in range(n):
        prev_pt = (pos[(i - 1) % n][0], pos[(i - 1) % n][1])
        curr_pt = (pos[i][0], pos[i][1])
        next_pt = (pos[(i + 1) % n][0], pos[(i + 1) % n][1])

        angle = _angle_deg(prev_pt, curr_pt, next_pt)

        if angle < min_deg or angle > max_deg:
          # Apply force to adjust angle
          # Move current point perpendicular to the line prev->next
          line_dx = next_pt[0] - prev_pt[0]
          line_dy = next_pt[1] - prev_pt[1]
          line_len = math.hypot(line_dx, line_dy)

          if line_len > 1e-10:
            perp_x = -line_dy / line_len
            perp_y = line_dx / line_len

            # Determine which way to push based on current angle vs target
            mid_x = (prev_pt[0] + next_pt[0]) / 2
            mid_y = (prev_pt[1] + next_pt[1]) / 2
            to_curr_x = curr_pt[0] - mid_x
            to_curr_y = curr_pt[1] - mid_y

            # Current offset in perpendicular direction
            curr_offset = to_curr_x * perp_x + to_curr_y * perp_y

            # Target offset for mid_angle
            # For angle ~180, offset ~0; for smaller angles, larger offset
            target_offset = 0.5 * math.tan(math.radians((180 - mid_angle) / 2)) * line_len * 0.5

            # Keep same sign as current offset (stay on same side)
            if curr_offset < 0:
              target_offset = -target_offset

            # Force toward target offset
            force_scale = k_angle * (target_offset - curr_offset)
            forces[i][0] += perp_x * force_scale
            forces[i][1] += perp_y * force_scale

    # 6. Crossing management - push toward target crossing count
    max_allowed = self.constraints["max_crossings"]
    exact_required = self.constraints["exact_crossings"]

    # Determine target crossing count
    if exact_required is not None:
      target_crossings = exact_required
    elif max_allowed is not None:
      target_crossings = 0  # Push toward 0 when max is set
    else:
      target_crossings = 0  # Default: no crossings

    # Find all crossings
    crossings = []
    for i in range(n):
      for j in range(i + 2, n):
        if i == 0 and j == n - 1:
          continue
        p1, p2 = (pos[i][0], pos[i][1]), (pos[(i + 1) % n][0], pos[(i + 1) % n][1])
        p3, p4 = (pos[j][0], pos[j][1]), (pos[(j + 1) % n][0], pos[(j + 1) % n][1])
        if _segments_intersect(p1, p2, p3, p4):
          crossings.append((i, j))

    if len(crossings) > target_crossings:
      # Too many crossings - push segments apart
      for seg_i, seg_j in crossings:
        mid1 = _segment_midpoint((pos[seg_i][0], pos[seg_i][1]),
                                 (pos[(seg_i + 1) % n][0], pos[(seg_i + 1) % n][1]))
        mid2 = _segment_midpoint((pos[seg_j][0], pos[seg_j][1]),
                                 (pos[(seg_j + 1) % n][0], pos[(seg_j + 1) % n][1]))
        dx = mid1[0] - mid2[0]
        dy = mid1[1] - mid2[1]
        dist = math.hypot(dx, dy)
        if dist < 1e-10:
          dx, dy = self.rng.random() - 0.5, self.rng.random() - 0.5
          dist = math.hypot(dx, dy)
        force = self.k_crossing / max(dist, 0.1)
        fx = force * dx / dist
        fy = force * dy / dist
        forces[seg_i][0] += fx * 0.5
        forces[seg_i][1] += fy * 0.5
        forces[(seg_i + 1) % n][0] += fx * 0.5
        forces[(seg_i + 1) % n][1] += fy * 0.5
        forces[seg_j][0] -= fx * 0.5
        forces[seg_j][1] -= fy * 0.5
        forces[(seg_j + 1) % n][0] -= fx * 0.5
        forces[(seg_j + 1) % n][1] -= fy * 0.5

    elif len(crossings) < target_crossings and target_crossings > 0:
      # Need MORE crossings - push segments toward each other
      best_pair = None
      best_dist = 0
      for i in range(n):
        for j in range(i + 3, n - 1):
          if i == 0 and j >= n - 2:
            continue
          mid1 = _segment_midpoint((pos[i][0], pos[i][1]),
                                   (pos[(i + 1) % n][0], pos[(i + 1) % n][1]))
          mid2 = _segment_midpoint((pos[j][0], pos[j][1]),
                                   (pos[(j + 1) % n][0], pos[(j + 1) % n][1]))
          dist = _distance(mid1, mid2)
          score = dist if dist < self.boundary else self.boundary * 2 - dist
          if score > best_dist and (i, j) not in crossings:
            best_dist = score
            best_pair = (i, j)

      if best_pair:
        seg_i, seg_j = best_pair
        mid1 = _segment_midpoint((pos[seg_i][0], pos[seg_i][1]),
                                 (pos[(seg_i + 1) % n][0], pos[(seg_i + 1) % n][1]))
        mid2 = _segment_midpoint((pos[seg_j][0], pos[seg_j][1]),
                                 (pos[(seg_j + 1) % n][0], pos[(seg_j + 1) % n][1]))
        dx = mid2[0] - mid1[0]
        dy = mid2[1] - mid1[1]
        dist = math.hypot(dx, dy)
        if dist > 1e-10:
          force = self.k_crossing * 0.5
          fx = force * dx / dist
          fy = force * dy / dist
          forces[seg_i][0] += fx * 0.5
          forces[seg_i][1] += fy * 0.5
          forces[(seg_i + 1) % n][0] += fx * 0.5
          forces[(seg_i + 1) % n][1] += fy * 0.5
          forces[seg_j][0] -= fx * 0.5
          forces[seg_j][1] -= fy * 0.5
          forces[(seg_j + 1) % n][0] -= fx * 0.5
          forces[(seg_j + 1) % n][1] -= fy * 0.5

    # 7. Centroid constraint
    if self.constraints["centroid_box"]:
      xmin, xmax, ymin, ymax = self.constraints["centroid_box"]
      cx = sum(p[0] for p in pos) / n
      cy = sum(p[1] for p in pos) / n
      target_x = (xmin + xmax) / 2
      target_y = (ymin + ymax) / 2

      # Push all points to shift centroid toward target
      shift_x = (target_x - cx) * self.k_centroid / n
      shift_y = (target_y - cy) * self.k_centroid / n
      for i in range(n):
        forces[i][0] += shift_x
        forces[i][1] += shift_y

    # 8. Quadrant coverage
    if self.constraints["coverage_quadrants"]:
      mid = self.boundary / 2
      quadrants = {"bottom_left": [], "top_left": [], "bottom_right": [], "top_right": []}

      for i in range(n):
        x, y = pos[i]
        if x <= mid and y <= mid:
          quadrants["bottom_left"].append(i)
        if x <= mid and y >= mid:
          quadrants["top_left"].append(i)
        if x >= mid and y <= mid:
          quadrants["bottom_right"].append(i)
        if x >= mid and y >= mid:
          quadrants["top_right"].append(i)

      # Push points toward missing quadrants
      for qname, indices in quadrants.items():
        if not indices:
          # Find point closest to this quadrant and push it there
          if qname == "bottom_left":
            target = (mid * 0.5, mid * 0.5)
          elif qname == "top_left":
            target = (mid * 0.5, mid * 1.5)
          elif qname == "bottom_right":
            target = (mid * 1.5, mid * 0.5)
          else:  # top_right
            target = (mid * 1.5, mid * 1.5)

          # Find closest point
          best_i = min(range(n), key=lambda i: _distance((pos[i][0], pos[i][1]), target))
          dx = target[0] - pos[best_i][0]
          dy = target[1] - pos[best_i][1]
          forces[best_i][0] += self.k_quadrant * dx
          forces[best_i][1] += self.k_quadrant * dy

    # 9. Convex hull area constraint
    if self.constraints["min_convex_hull_area"]:
      required_area = self.constraints["min_convex_hull_area"]
      hull_pts = _convex_hull([(p[0], p[1]) for p in pos])
      current_area = _polygon_area(hull_pts)

      if current_area < required_area:
        # Push all points outward from centroid
        cx = sum(p[0] for p in pos) / n
        cy = sum(p[1] for p in pos) / n
        expansion = self.k_hull * (required_area - current_area) / required_area

        for i in range(n):
          dx = pos[i][0] - cx
          dy = pos[i][1] - cy
          dist = math.hypot(dx, dy)
          if dist > 1e-10:
            forces[i][0] += expansion * dx / dist
            forces[i][1] += expansion * dy / dist

    # 10. Margin avoidance
    if self.constraints["avoid_margin"]:
      margin = self.constraints["avoid_margin"]
      for i in range(n):
        x, y = pos[i]
        if x < margin:
          forces[i][0] += self.k_margin * (margin - x)
        if x > self.boundary - margin:
          forces[i][0] -= self.k_margin * (x - (self.boundary - margin))
        if y < margin:
          forces[i][1] += self.k_margin * (margin - y)
        if y > self.boundary - margin:
          forces[i][1] -= self.k_margin * (y - (self.boundary - margin))

    # 11. Point separation constraint
    if self.constraints["min_point_separation"]:
      min_dist = self.constraints["min_point_separation"]
      for i in range(n):
        for j in range(i + 2, n):
          dist = _distance((pos[i][0], pos[i][1]), (pos[j][0], pos[j][1]))
          if dist < min_dist and dist > 1e-10:
            # Repulsive force
            dx = pos[i][0] - pos[j][0]
            dy = pos[i][1] - pos[j][1]
            force = self.k_separation * (min_dist - dist) / dist
            forces[i][0] += force * dx
            forces[i][1] += force * dy
            forces[j][0] -= force * dx
            forces[j][1] -= force * dy

    # 12. Backtrack prevention - penalize sharp 180° reversals
    for i in range(n):
      # Vector from prev to curr
      prev_pt = (pos[(i - 1) % n][0], pos[(i - 1) % n][1])
      curr_pt = (pos[i][0], pos[i][1])
      next_pt = (pos[(i + 1) % n][0], pos[(i + 1) % n][1])

      v1 = (curr_pt[0] - prev_pt[0], curr_pt[1] - prev_pt[1])
      v2 = (next_pt[0] - curr_pt[0], next_pt[1] - curr_pt[1])
      len1 = math.hypot(v1[0], v1[1])
      len2 = math.hypot(v2[0], v2[1])

      if len1 > 1e-10 and len2 > 1e-10:
        # Normalized dot product
        dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
        if dot < -0.9:  # Almost backtracking
          # Push next point perpendicular to v1
          perp_x = -v1[1] / len1
          perp_y = v1[0] / len1
          # Choose side that moves away from backtrack
          side = 1 if self.rng.random() < 0.5 else -1
          forces[(i + 1) % n][0] += perp_x * self.k_backtrack * (-dot - 0.9) * side
          forces[(i + 1) % n][1] += perp_y * self.k_backtrack * (-dot - 0.9) * side

    # 13. Min turns constraint - encourage direction changes
    if self.constraints["min_turns"]:
      min_turns = self.constraints["min_turns"]
      # Count current turns (angle < 175 degrees)
      turns = 0
      for i in range(n):
        prev_pt = (pos[(i - 1) % n][0], pos[(i - 1) % n][1])
        curr_pt = (pos[i][0], pos[i][1])
        next_pt = (pos[(i + 1) % n][0], pos[(i + 1) % n][1])
        angle = _angle_deg(prev_pt, curr_pt, next_pt)
        if angle < 175:
          turns += 1

      if turns < min_turns:
        # Need more turns - push some nearly-straight points perpendicular
        for i in range(n):
          prev_pt = (pos[(i - 1) % n][0], pos[(i - 1) % n][1])
          curr_pt = (pos[i][0], pos[i][1])
          next_pt = (pos[(i + 1) % n][0], pos[(i + 1) % n][1])
          angle = _angle_deg(prev_pt, curr_pt, next_pt)
          if angle > 170:  # Nearly straight
            line_dx = next_pt[0] - prev_pt[0]
            line_dy = next_pt[1] - prev_pt[1]
            line_len = math.hypot(line_dx, line_dy)
            if line_len > 1e-10:
              perp_x = -line_dy / line_len
              perp_y = line_dx / line_len
              # Push perpendicular
              forces[i][0] += perp_x * self.k_turn
              forces[i][1] += perp_y * self.k_turn

    # 14. Max straight run constraint - break long straight sequences
    if self.constraints["max_straight_run"]:
      max_run = self.constraints["max_straight_run"]
      run_start = 0
      in_run = False

      for i in range(n + max_run):  # wrap around
        idx = i % n
        prev_pt = (pos[(idx - 1) % n][0], pos[(idx - 1) % n][1])
        curr_pt = (pos[idx][0], pos[idx][1])
        next_pt = (pos[(idx + 1) % n][0], pos[(idx + 1) % n][1])
        angle = _angle_deg(prev_pt, curr_pt, next_pt)

        if angle > 175:  # Straight
          if not in_run:
            run_start = idx
            in_run = True
        else:
          if in_run:
            run_length = (idx - run_start) % n
            if run_length > max_run:
              # Break up this run - push middle point perpendicular
              mid_idx = (run_start + run_length // 2) % n
              prev_pt = (pos[(mid_idx - 1) % n][0], pos[(mid_idx - 1) % n][1])
              next_pt = (pos[(mid_idx + 1) % n][0], pos[(mid_idx + 1) % n][1])
              line_dx = next_pt[0] - prev_pt[0]
              line_dy = next_pt[1] - prev_pt[1]
              line_len = math.hypot(line_dx, line_dy)
              if line_len > 1e-10:
                perp_x = -line_dy / line_len
                perp_y = line_dx / line_len
                forces[mid_idx][0] += perp_x * self.k_turn * 2
                forces[mid_idx][1] += perp_y * self.k_turn * 2
            in_run = False

    return forces

  def _step(self, pos: List[List[float]], vel: List[List[float]], progress: float = 0.0) -> None:
    """Perform one simulation step (in-place update)."""
    forces = self._compute_forces(pos, progress)

    for i in range(self.n):
      # Update velocity with force and damping
      vel[i][0] = (vel[i][0] + forces[i][0] * self.dt) * self.damping
      vel[i][1] = (vel[i][1] + forces[i][1] * self.dt) * self.damping

      # Cap velocity
      v_mag = math.hypot(vel[i][0], vel[i][1])
      if v_mag > self.max_velocity:
        vel[i][0] *= self.max_velocity / v_mag
        vel[i][1] *= self.max_velocity / v_mag

      # Update position
      pos[i][0] += vel[i][0] * self.dt
      pos[i][1] += vel[i][1] * self.dt

      # Hard clamp to boundary
      pos[i][0] = _clamp(pos[i][0], 0.001, self.boundary - 0.001)
      pos[i][1] = _clamp(pos[i][1], 0.001, self.boundary - 0.001)

  def _to_tuples(self, pos: List[List[float]]) -> List[Tuple[float, float]]:
    return [(p[0], p[1]) for p in pos]

  def _evaluate(self, pos: List[List[float]]) -> List[Dict[str, Any]]:
    """Evaluate current configuration using gradeAnswer."""
    pts = self._to_tuples(pos)
    answer = {"points": [{"x": x, "y": y} for x, y in pts]}
    try:
      res = self.gradeAnswer(answer, self.subPass, "solver", returnedStructuredErrors=True)
    except TypeError:
      res = self.gradeAnswer(answer, self.subPass, "solver")
      if isinstance(res, tuple):
        score, msg = res
        return [] if score == 1 else [{"kind": "legacy", "message": msg}]
    return res

  def solve(self,
            max_iterations: int = 2000,
            time_limit: float = 12.0) -> Tuple[List[Tuple[float, float]], str]:
    """Run simulation until convergence or time limit."""
    firstStallTime = None

    pos = self._init_positions()
    vel = self._init_velocities()

    best_pos = [p[:] for p in pos]
    best_vel = [v[:] for v in vel]
    best_errors = self._evaluate(pos)
    best_count = len(best_errors)

    if best_count == 0:
      return self._to_tuples(pos), f"Solved in 0 iterations"

    stall_counter = 0

    revert_to_best_count = 0

    for it in range(max_iterations):
      if firstStallTime and time.time() - firstStallTime > time_limit:
        if revert_to_best_count < 5 and error_count > best_count:
          pos = [p[:] for p in best_pos]
          vel = [v[:] for v in best_vel]
          revert_to_best_count += 1
          firstStallTime = None
          print(f"- Reverted at {it} ({error_count} errors) back to {best_count}")

        else:
          break

      # Progress ramps from 0 to 1 over iterations (edge springs get stronger)
      progress = min(1.0, it / 1000.0)  # Ramp up over first 1000 iterations
      self._step(pos, vel, progress)

      # Periodically evaluate
      if it % 20 == 0 or it < 50:
        errors = self._evaluate(pos)
        error_count = len(errors)

        if error_count == 0:
          return self._to_tuples(pos), f"Solved in {it} iterations"

        if error_count < best_count:
          best_pos = [p[:] for p in pos]
          best_vel = [v[:] for v in vel]
          best_errors = errors
          best_count = error_count
          stall_counter = 0
          firstStallTime = None
          revert_to_best_count = 0
          print(f"- Iter {it}: {error_count} errors")

        else:
          stall_counter += 1

        # Progress logging
        if it in [10, 50, 100, 200, 500, 1000, 1500, 2000, 3000, 4000, 5000, 10000, 15000]:
          kinds = [e.get("kind", "?") for e in errors[:3]]
          print(f"- Iter {it}: {error_count} errors, types: {kinds}")

        # If stalled, add random perturbation
        if stall_counter > 20:
          for i in random.choices(range(self.n), k=5):
            vel[i][0] += (self.rng.random() - 0.5) * 5
            vel[i][1] += (self.rng.random() - 0.5) * 5
          stall_counter = 0
          if firstStallTime is None:
            firstStallTime = time.time()

    if len(vel) > 5:
      for i in range(5):
        print(f"  - {pos[i][0]:.1f} {pos[i][1]:.1f}. V = {vel[i][0]:.1f} {vel[i][1]:.1f}")

    kinds = [e.get("kind", "?") for e in errors[:3]]

    if "segment_length" in kinds:
      self.k_edge_min += 5
      self.k_edge_max += 50
      print(
        f"Next iteration - we're making the edge springs stronger! {self.k_edge_min} - {self.k_edge_max}"
      )
    elif "angle_range" in kinds:
      self.k_angle_min += 5
      self.k_angle_max += 50
      print(
        f"Next iteration - we're making the angle springs stronger! {self.k_angle_min} - {self.k_angle_max}"
      )
    return self._to_tuples(
      best_pos), f"Best had {best_count} errors ({kinds}) after {max_iterations} iterations"


def get_response(subPass: int):
  # Check cache first
  cached = _load_cached_solution(subPass)
  if cached is not None:
    return cached, "Solver: Loaded from cache"

  # Try multiple restarts with different seeds for robustness
  best_pts = None
  best_errors = float('inf')
  best_summary = ""

  print(f"Starting {subPass}")

  num_restarts = 50 + subPass * 2
  time_per_restart = 15.0 + subPass * 0.5  # They get harder

  lastSolver = None

  for restart in range(num_restarts):
    seed = int(time.time() * 1000) + restart * 12345
    solver = SpringSimulation(subPass, seed=seed, lastSolver=lastSolver)
    pts, summary = solver.solve(10000 + subPass * 1000, time_limit=time_per_restart)

    # Check result
    answer = {"points": [{"x": float(x), "y": float(y)} for x, y in pts]}
    errors = solver.gradeAnswer(answer, subPass, "solver", returnedStructuredErrors=True)
    error_count = len(errors) if isinstance(errors, list) else 1

    if error_count == 0:
      print(f"SOLVED! {subPass}")
      _save_cached_solution(subPass, answer)  # Cache the solution
      return answer, f"Solver: {summary}"

    if error_count < best_errors:
      best_pts = pts
      best_errors = error_count
      best_summary = summary
    lastSolver = solver

  answer = {"points": [{"x": float(x), "y": float(y)} for x, y in best_pts]}
  print(f"FAILED! {subPass} - {best_summary}")
  return answer, f"Solver: {best_summary}"


if __name__ == "__main__":
  # Test multiple subpasses

  r = range(40)
  if len(sys.argv) > 1:
    r = sys.argv[1:]
    r = [int(x) for x in r]

  solved = 0
  failed = []
  for sp in r:
    print(f"Testing subpass {sp}...", end=" ")
    result, msg = get_response(sp)
    if "Loaded from cache" in msg:
      solved += 1
    elif "Solved" in msg:
      print(f"SOLVED - {msg}")
      solved += 1
    else:
      print(f"FAILED - {msg}")
      failed.append(sp)
  print(f"\nSummary: {solved}/40 solved, failed: {failed}")
