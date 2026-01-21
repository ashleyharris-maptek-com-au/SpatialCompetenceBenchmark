import OpenScad as vc
import itertools
import math
from typing import Dict, List, Tuple

title = "Fit a loop into a square that's perimeter is smaller than the total length"

basePrompt = """
You have {pipes} 1m lengths of pipe, and a square area of side length {boundary} to play with.

Lay the pipe out to form a closed loop, using all the pipe, and returning to the starting point.

You can not re-use vertices, and you can not cross the boundary of the area. You do not need to
stick to axis aligned paths.

Return the loop as a list of the pipe endpoints. Note that N pipes requires N+1 verticies to describe a path, but since the
first and last vertices are the same, you only need to return N points.
""".strip()


# ---------------------------------------------------------------------------
# Complication helpers (kept in one place so every consumer uses the same truth)
# ---------------------------------------------------------------------------
def comp_max_crossings(max_crossings: int):
  return {"type": "max_crossings", "max": max_crossings}


def comp_exact_crossings(count: int):
  return {"type": "exact_crossings", "count": count}


def comp_angle_range(min_deg: float, max_deg: float):
  return {"type": "angle_range", "min_deg": min_deg, "max_deg": max_deg}


def comp_centroid_box(xmin_ratio: float, xmax_ratio: float, ymin_ratio: float, ymax_ratio: float):
  return {
    "type": "centroid_box",
    "xmin_ratio": xmin_ratio,
    "xmax_ratio": xmax_ratio,
    "ymin_ratio": ymin_ratio,
    "ymax_ratio": ymax_ratio
  }


def comp_must_touch_boundary(edges_needed: int = 1):
  return {"type": "must_touch_boundary", "edges_needed": edges_needed}


def comp_min_turns(min_turns: int):
  return {"type": "min_turns", "min_turns": min_turns}


def comp_max_straight_run(max_run: int):
  return {"type": "max_straight_run", "max_run": max_run}


def comp_coverage_quadrants():
  return {"type": "coverage_quadrants"}


def comp_avoid_margin(margin_ratio: float):
  return {"type": "avoid_margin", "margin_ratio": margin_ratio}


def comp_min_convex_hull_area(min_area_ratio: float):
  return {"type": "min_convex_hull_area", "min_area_ratio": min_area_ratio}


def comp_fixed_start(x_ratio: float, y_ratio: float, tolerance: float = 0.25):
  return {"type": "fixed_start", "x_ratio": x_ratio, "y_ratio": y_ratio, "tolerance": tolerance}


def comp_min_point_separation(min_dist: float):
  return {"type": "min_point_separation", "min_dist": min_dist}


complication_presets = [
  {
    "name":
    "no_cross_tight_angles",
    "description":
    "No crossings, angles must stay between 45° and 135°, centroid stays near the middle half.",
    "complications":
    [comp_max_crossings(0),
     comp_angle_range(45, 135),
     comp_centroid_box(0.25, 0.75, 0.25, 0.75)]
  },
  {
    "name": "edge_runner",
    "description": "No crossings, touch at least three edges and keep turning regularly.",
    "complications": [comp_max_crossings(0),
                      comp_must_touch_boundary(3),
                      comp_min_turns(5)]
  },
  {
    "name": "curvy_and_short_runs",
    "description": "No crossings, avoid long straight lines and keep angles gentle.",
    "complications": [comp_max_crossings(0),
                      comp_max_straight_run(2),
                      comp_angle_range(60, 150)]
  },
  {
    "name": "balanced_quadrants",
    "description": "No crossings, visit all quadrants of the square at least once.",
    "complications": [comp_max_crossings(0), comp_coverage_quadrants()]
  },
  {
    "name": "stay_off_walls",
    "description":
    "Stay a small margin away from the walls and still keep a reasonably large hull.",
    "complications":
    [comp_avoid_margin(0.05),
     comp_min_convex_hull_area(0.15),
     comp_max_crossings(0)]
  },
  {
    "name":
    "dense_center",
    "description":
    "Keep centroid close to the center and avoid clustering points too tightly.",
    "complications": [
      comp_centroid_box(0.45, 0.55, 0.45, 0.55),
      comp_min_point_separation(0.25),
      comp_max_crossings(0)
    ]
  },
  {
    "name": "one_forced_cross",
    "description": "Exactly one crossing is allowed and required, with broad angle flexibility.",
    "complications": [comp_exact_crossings(1), comp_angle_range(30, 150)]
  },
  {
    "name": "two_forced_crosses",
    "description": "Two crossings are allowed and required, keep angles between 45° and 135°.",
    "complications": [comp_exact_crossings(2), comp_angle_range(45, 135)]
  },
  {
    "name": "corner_start",
    "description": "Start at the lower-left corner, avoid crossings, and keep turning.",
    "complications": [comp_fixed_start(0.0, 0.0),
                      comp_min_turns(6),
                      comp_max_crossings(0)]
  },
  {
    "name": "center_start",
    "description": "Start near the center, avoid crossings, and keep angles moderate.",
    "complications": [comp_fixed_start(0.5, 0.5),
                      comp_angle_range(40, 140),
                      comp_max_crossings(0)]
  },
  {
    "name": "hull_spreader",
    "description": "No crossings and the convex hull must occupy at least 25% of the board.",
    "complications": [comp_max_crossings(0), comp_min_convex_hull_area(0.25)]
  },
  {
    "name": "wall_kisser",
    "description": "Must touch all four edges while keeping crossings at zero.",
    "complications": [comp_must_touch_boundary(4),
                      comp_max_crossings(0)]
  },
]

# Generate ~40 varied cases, cycling through complication presets so everything
# pulls from a single ground-truth source.
_base_specs: List[Tuple[int, int]] = [(3, 1), (6, 2), (8, 2), (10, 3), (12, 3), (14, 3), (16, 3),
                                      (18, 4), (20, 4), (22, 4), (24, 4), (26, 5), (28, 5), (30, 5),
                                      (32, 5), (36, 6), (40, 6), (44, 6), (48, 7), (52, 7), (56, 7),
                                      (60, 8), (64, 8), (72, 9), (80, 10), (90, 12), (100, 14),
                                      (110, 15), (120, 16), (140, 18), (160, 20), (180, 22),
                                      (200, 24), (240, 26), (280, 28), (320, 30), (360, 32),
                                      (420, 34), (500, 36), (600, 40)]


def _describe_complication(comp: Dict) -> str:
  ctype = comp["type"]
  if ctype == "max_crossings":
    return f"Crossings allowed: {comp['max']}."
  if ctype == "exact_crossings":
    if comp['count'] == 1:
      return "Exactly one crossing is required."
    return f"Exactly {comp['count']} crossings are required."
  if ctype == "angle_range":
    return f"Angles must stay between {comp['min_deg']}° and {comp['max_deg']}°."
  if ctype == "centroid_box":
    return ("Center of gravity must stay within "
            f"{int(comp['xmin_ratio'] * 100)}%-{int(comp['xmax_ratio'] * 100)}% X and "
            f"{int(comp['ymin_ratio'] * 100)}%-{int(comp['ymax_ratio'] * 100)}% Y of the square.")
  if ctype == "must_touch_boundary":
    return f"Touch at least {comp['edges_needed']} distinct edges of the square."
  if ctype == "min_turns":
    return f"Make at least {comp['min_turns']} genuine turns."
  if ctype == "max_straight_run":
    return f"No more than {comp['max_run']} straight segments in a row."
  if ctype == "coverage_quadrants":
    return "Visit all four quadrants divided by the square's midlines."
  if ctype == "avoid_margin":
    return f"Stay at least {int(comp['margin_ratio'] * 100)}% inside from every wall."
  if ctype == "min_convex_hull_area":
    return f"Convex hull area must be at least {int(comp['min_area_ratio'] * 100)}% of the board."
  if ctype == "fixed_start":
    return ("Start the loop near "
            f"({int(comp['x_ratio'] * 100)}% * side, {int(comp['y_ratio'] * 100)}% * side).")
  if ctype == "min_point_separation":
    return f"Non-adjacent vertices must be at least {comp['min_dist']} apart."
  return ctype


def _build_test_params():
  params = []
  for idx, (pipes, boundary) in enumerate(_base_specs):
    preset = complication_presets[idx % len(complication_presets)]
    params.append({
      "pipes": pipes,
      "boundary": boundary,
      "tolerance": 0.05,
      "summary":
      f"{pipes} pipes in {boundary}x{boundary} with {preset['name']}: {preset['description']}",
      "complications": preset["complications"],
      "preset": preset["name"],
    })
  return params


testParams = _build_test_params()
subpassParamSummary = [tp["summary"] for tp in testParams]
promptChangeSummary = "Increasing pipe length, square size, and layered complication presets."
earlyFail = True

structure = {
  "type": "object",
  "properties": {
    "points": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "x": {
            "type": "number"
          },
          "y": {
            "type": "number"
          }
        },
        "propertyOrdering": ["x", "y"],
        "additionalProperties": False,
        "required": ["x", "y"]
      }
    }
  },
  "propertyOrdering": ["points"],
  "additionalProperties": False,
  "required": ["points"]
}


def prepareSubpassPrompt(index: int):
  if index < 0 or index >= len(testParams):
    raise StopIteration
  params = testParams[index]
  header = basePrompt.format(pipes=params["pipes"], boundary=params["boundary"])
  comp_lines = "\n".join([f"- {_describe_complication(c)}" for c in params["complications"]])
  if comp_lines:
    header += "\n\nAdditional constraints:\n" + comp_lines

  if "crossings are required" not in comp_lines and "crossing is required" not in comp_lines:
    header += "\n- The loop must not cross itself or touch itself."

  return header


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
  return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def _segments(
    points: List[Tuple[float, float]]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
  return list(zip(points, points[1:] + points[:1]))


def _segments_intersect(p1, p2, p3, p4):
  eps = 1e-9
  if (abs(p1[0] - p3[0]) < eps and abs(p1[1] - p3[1]) < eps) or \
     (abs(p1[0] - p4[0]) < eps and abs(p1[1] - p4[1]) < eps) or \
     (abs(p2[0] - p3[0]) < eps and abs(p2[1] - p3[1]) < eps) or \
     (abs(p2[0] - p4[0]) < eps and abs(p2[1] - p4[1]) < eps):
    return False

  def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

  return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def _crossing_pairs(
    segments: List[Tuple[Tuple[float, float], Tuple[float, float]]]) -> List[Tuple[int, int]]:
  crossings = []
  for i in range(len(segments)):
    for j in range(i + 2, len(segments)):
      if i == 0 and j == len(segments) - 1:
        continue
      if _segments_intersect(segments[i][0], segments[i][1], segments[j][0], segments[j][1]):
        crossings.append((i, j))
  return crossings


def _angle_deg(a, b, c) -> float:
  v1x, v1y = a[0] - b[0], a[1] - b[1]
  v2x, v2y = c[0] - b[0], c[1] - b[1]
  len1 = math.sqrt(v1x**2 + v1y**2)
  len2 = math.sqrt(v2x**2 + v2y**2)
  if len1 == 0 or len2 == 0:
    return 0.0
  dot = (v1x * v2x + v1y * v2y) / (len1 * len2)
  dot = max(-1.0, min(1.0, dot))
  return math.degrees(math.acos(dot))


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


def gradeAnswer(answer: dict, subPassIndex: int, aiEngineName: str, returnedStructuredErrors=False):
  if subPassIndex < 0 or subPassIndex >= len(testParams):
    if returnedStructuredErrors:
      return [{"kind": "fundamental", "message": "Invalid subPassIndex"}]
    return 0, "Invalid subPassIndex"

  params = testParams[subPassIndex]
  expected_pipes = params["pipes"]
  boundary = params["boundary"]
  tolerance = params.get("tolerance", 0.05)
  complications = params.get("complications", [])

  points = answer.get("points") if isinstance(answer, dict) else None
  if not isinstance(points, list):
    if returnedStructuredErrors:
      return [{"kind": "fundamental", "message": "Invalid answer format"}]
    return 0, "Answer must contain a 'points' array"

  parsed_points: List[Tuple[float, float]] = []
  for idx, pt in enumerate(points):
    if not isinstance(pt, dict):
      if returnedStructuredErrors:
        return [{"kind": "fundamental", "message": "Invalid point format"}]
      return 0, f"Point {idx} is not an object"
    try:
      parsed_points.append((float(pt["x"]), float(pt["y"])))
    except (TypeError, ValueError, KeyError):
      if returnedStructuredErrors:
        return [{"kind": "fundamental", "message": "Invalid point format"}]
      return 0, f"Point {idx} is missing numeric x/y"

  if len(parsed_points) < 3:
    if returnedStructuredErrors:
      return [{"kind": "count_mismatch", "message": "Answer must contain at least 3 points"}]

    return 0, "Answer must contain at least 3 points"

  errors = []

  def add_error(kind: str, message: str, location: Dict = None):
    entry = {"kind": kind, "message": message}
    if location:
      entry["where"] = location
    errors.append(entry)

  if len(parsed_points) != expected_pipes:
    add_error(
      "count_mismatch",
      f"Expected {expected_pipes} points (for {expected_pipes} pipe segments), got {len(parsed_points)}",
      {
        "expected": expected_pipes,
        "actual": len(parsed_points)
      })

  for i, (x, y) in enumerate(parsed_points):
    if x < 0 or x > boundary or y < 0 or y > boundary:
      add_error("boundary", f"Point {i} ({x:.3f}, {y:.3f}) is outside [0, {boundary}]",
                {"point_index": i})

  segments = _segments(parsed_points)

  for i, (p1, p2) in enumerate(segments[:-1]):  # closure check handled later
    dist = _distance(p1, p2)
    if abs(dist - 1.0) > tolerance:
      add_error("segment_length", f"Segment {i} length {dist:.4f}, expected 1.0 ± {tolerance}", {
        "segment_index": i,
        "start": p1,
        "end": p2
      })

  close_dist = _distance(parsed_points[-1], parsed_points[0])
  if abs(close_dist - 1.0) > tolerance:
    add_error("closure", f"Closing segment length {close_dist:.4f}, expected 1.0 ± {tolerance}",
              {"segment_index": len(parsed_points) - 1})

  seen_vertices = {}
  for idx, pt in enumerate(parsed_points):
    key = (round(pt[0], 6), round(pt[1], 6))
    if key in seen_vertices:
      add_error("duplicate_vertex", f"Vertex {idx} reuses point {key}", {
        "point_index": idx,
        "duplicate_of": seen_vertices[key]
      })
    else:
      seen_vertices[key] = idx

  crossings = _crossing_pairs(segments)
  max_crossing_limit = None
  exact_crossing_required = None
  for comp in complications:
    if comp["type"] == "max_crossings":
      max_crossing_limit = comp["max"]
    elif comp["type"] == "exact_crossings":
      exact_crossing_required = comp["count"]

  if exact_crossing_required is None:
    crossing_limit = max_crossing_limit if max_crossing_limit is not None else 0
    if len(crossings) > crossing_limit:
      add_error("crossings", f"Found {len(crossings)} crossings, allowed {crossing_limit}",
                {"pairs": crossings})

  for i in range(len(segments)):
    p0, p1 = segments[i]
    p2 = segments[(i + 1) % len(segments)][1]
    len1 = _distance(p0, p1)
    len2 = _distance(p1, p2)
    if len1 > 0 and len2 > 0:
      v1x, v1y = (p1[0] - p0[0]) / len1, (p1[1] - p0[1]) / len1
      v2x, v2y = (p2[0] - p1[0]) / len2, (p2[1] - p1[1]) / len2
      if v1x * v2x + v1y * v2y < -0.99:
        add_error("backtrack", f"Segment {i} backtracks on segment {(i + 1) % len(segments)}",
                  {"segment_index": i})

  # Complication-specific validators
  def angle_values():
    angles = []
    for i in range(len(parsed_points)):
      prev_pt = parsed_points[i - 1]
      curr_pt = parsed_points[i]
      next_pt = parsed_points[(i + 1) % len(parsed_points)]
      angles.append(_angle_deg(prev_pt, curr_pt, next_pt))
    return angles

  angles = angle_values()
  centroid = (sum(p[0] for p in parsed_points) / len(parsed_points),
              sum(p[1] for p in parsed_points) / len(parsed_points)) if parsed_points else (0, 0)

  hull = _convex_hull(parsed_points)
  hull_area = _polygon_area(hull)

  def run_complication_checks():
    for comp in complications:
      ctype = comp["type"]
      if ctype == "exact_crossings":
        if len(crossings) != comp["count"]:
          add_error("exact_crossings",
                    f"Crossings found {len(crossings)}; expected exactly {comp['count']}",
                    {"pairs": crossings})
      elif ctype == "angle_range":
        for i, ang in enumerate(angles):
          if ang < comp["min_deg"] or ang > comp["max_deg"]:
            add_error(
              "angle_range",
              f"Angle at vertex {i} is {ang:.1f}° (expected {comp['min_deg']}°-{comp['max_deg']}°)",
              {"vertex_index": i})
      elif ctype == "centroid_box":
        xmin = boundary * comp["xmin_ratio"]
        xmax = boundary * comp["xmax_ratio"]
        ymin = boundary * comp["ymin_ratio"]
        ymax = boundary * comp["ymax_ratio"]
        if not (xmin <= centroid[0] <= xmax and ymin <= centroid[1] <= ymax):
          add_error(
            "centroid",
            f"Centroid at ({centroid[0]:.2f}, {centroid[1]:.2f}) is outside required box "
            f"[{xmin:.2f}, {xmax:.2f}] x [{ymin:.2f}, {ymax:.2f}]")
      elif ctype == "must_touch_boundary":
        tolerance_edge = max(1e-3, boundary * 0.001)
        edges_hit = set()
        for i, (x, y) in enumerate(parsed_points):
          if abs(x) <= tolerance_edge:
            edges_hit.add("left")
          if abs(x - boundary) <= tolerance_edge:
            edges_hit.add("right")
          if abs(y) <= tolerance_edge:
            edges_hit.add("bottom")
          if abs(y - boundary) <= tolerance_edge:
            edges_hit.add("top")
        if len(edges_hit) < comp["edges_needed"]:
          add_error(
            "boundary_touch",
            f"Touched {len(edges_hit)} edges {sorted(edges_hit)}, need {comp['edges_needed']} edges"
          )
      elif ctype == "min_turns":
        turns = sum(1 for a in angles if a < 175)  # filter out almost straight
        if turns < comp["min_turns"]:
          add_error("min_turns", f"Only {turns} turns detected; need at least {comp['min_turns']}")
      elif ctype == "max_straight_run":
        straight_run = 0
        max_run_seen = 0
        for ang in angles:
          if ang > 175:
            straight_run += 1
          else:
            max_run_seen = max(max_run_seen, straight_run)
            straight_run = 0
        max_run_seen = max(max_run_seen, straight_run)
        if max_run_seen > comp["max_run"]:
          add_error(
            "max_straight_run",
            f"Detected straight run of {max_run_seen} segments, limit is {comp['max_run']}")
      elif ctype == "coverage_quadrants":
        mid = boundary / 2
        quadrants = set()
        for (x, y) in parsed_points:
          if x <= mid and y <= mid:
            quadrants.add("bottom_left")
          if x <= mid and y >= mid:
            quadrants.add("top_left")
          if x >= mid and y <= mid:
            quadrants.add("bottom_right")
          if x >= mid and y >= mid:
            quadrants.add("top_right")
        if len(quadrants) < 4:
          add_error(
            "coverage_quadrants",
            f"Missing quadrants: {sorted({'bottom_left','top_left','bottom_right','top_right'} - quadrants)}"
          )
      elif ctype == "avoid_margin":
        margin = boundary * comp["margin_ratio"]
        for i, (x, y) in enumerate(parsed_points):
          if x < margin or x > boundary - margin or y < margin or y > boundary - margin:
            add_error("avoid_margin",
                      f"Point {i} ({x:.2f},{y:.2f}) violates margin {margin:.2f} away from walls",
                      {"point_index": i})
            break
      elif ctype == "min_convex_hull_area":
        required = (boundary * boundary) * comp["min_area_ratio"]
        if hull_area < required:
          add_error(
            "min_convex_hull_area",
            f"Hull area {hull_area:.2f} < required {required:.2f} ({comp['min_area_ratio']*100:.0f}% of board)"
          )
      elif ctype == "fixed_start":
        expected = (boundary * comp["x_ratio"], boundary * comp["y_ratio"])
        dist = _distance(parsed_points[0], expected)
        if dist > comp.get("tolerance", 0.25):
          add_error(
            "fixed_start",
            f"First point {parsed_points[0]} should start near {expected} within {comp.get('tolerance',0.25)}"
          )
      elif ctype == "min_point_separation":
        for i in range(len(parsed_points)):
          for j in range(i + 2, len(parsed_points)):  # skip adjacent to avoid built-in length
            if _distance(parsed_points[i], parsed_points[j]) < comp["min_dist"]:
              add_error("min_point_separation",
                        f"Points {i} and {j} are closer than {comp['min_dist']}",
                        {"point_indices": (i, j)})
              return

  run_complication_checks()

  if errors:
    if returnedStructuredErrors:
      return errors

    error_lines = [
      f"{idx+1}. {err['kind']}: {err['message']}" +
      (f" @ {err.get('where')}" if err.get("where") else "") for idx, err in enumerate(errors)
    ]
    if len(error_lines) > 5:
      error_lines = error_lines[:5] + [f"... (truncated, {len(error_lines)} errors in total)"]

    return 0, "Validation failed:\n" + "\n".join(error_lines)

  if returnedStructuredErrors:
    return []

  return 1, f"Valid loop for preset '{params['preset']}' with {len(parsed_points)} points and {len(crossings)} crossings"


def resultToNiceReport(result: dict, subPass, aiEngineName: str):
  points = result.get("points", [])
  if len(points) < 3:
    return "LLM did not complete."

  if subPass < 0 or subPass >= len(testParams):
    raise StopIteration

  squareSize = testParams[subPass]["boundary"]

  scad_content = ""
  loop_points = points + [points[0]]

  for a, b in itertools.pairwise(loop_points):
    if round(math.sqrt((b['x'] - a['x'])**2 + (b['y'] - a['y'])**2)) == 1:
      scad_content += "hull(){\n"
      scad_content += f"    translate([{a['x']}, {a['y']}]) sphere(0.01);\n"
      scad_content += f"    translate([{b['x']}, {b['y']}]) sphere(0.01);\n"
      scad_content += "}\n"

  scad_content += f"translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([{squareSize},{squareSize},0.01]);"

  import os
  os.makedirs("results", exist_ok=True)
  output_path = "results/12_Visualization_" + aiEngineName + "_" + str(squareSize) + ".png"
  vc.render_scadText_to_png(scad_content, output_path)
  print(f"Saved visualization to {output_path}")

  return f'<img src="{os.path.basename(output_path)}" alt="Pipe Loop Visualization" style="max-width: 100%;">'


highLevelSummary = """
This tests laying out paths in a closed loop within a constrained square, with 40 parameterised subpasses.

<br><br>

Each subpass draws from a single source of truth (testParams) that drives prompts, summaries,
validators, and visualisations. Complication presets cover angles, crossings, centroid targets,
edge touches, hull size, start positions, and more to provide richer feedback.
"""
