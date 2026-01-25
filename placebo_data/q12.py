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
import html
import math
import os
import random
import sys
import tempfile
import threading
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

DIAG_DIR = Path(tempfile.gettempdir()) / "q12_spring_diag"


def _copy_2d(v: List[List[float]]) -> List[List[float]]:
  return [row[:] for row in v]


def _diag_path(subPass: int, tag: str) -> Path:
  ts = time.strftime("%Y%m%d_%H%M%S")
  pid = os.getpid()
  DIAG_DIR.mkdir(parents=True, exist_ok=True)
  safe_tag = "".join([c for c in tag if c.isalnum() or c in "_-."])
  return DIAG_DIR / f"q12_subpass{subPass}_{safe_tag}_{ts}_{pid}.html"


def _fmt_float(v: float, nd: int = 3) -> str:
  try:
    return f"{float(v):.{nd}f}"
  except Exception:
    return str(v)


def _svg_map_y(boundary: float, y: float) -> float:
  return boundary - y


def _svg_point(boundary: float, p: Tuple[float, float]) -> Tuple[float, float]:
  return (p[0], _svg_map_y(boundary, p[1]))


def _segment_intersection_point(a1, a2, b1, b2) -> Optional[Tuple[float, float]]:
  x1, y1 = a1
  x2, y2 = a2
  x3, y3 = b1
  x4, y4 = b2
  den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
  if abs(den) < 1e-12:
    return None
  px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
  py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
  return (px, py)


def _collect_error_index_sets(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
  point_idxs = set()
  vertex_idxs = set()
  seg_idxs = set()
  seg_pairs = []
  min_sep_pairs = []
  for e in errors:
    kind = e.get("kind", "")
    where = e.get("where") or {}
    if kind in ("boundary", "avoid_margin"):
      if "point_index" in where:
        point_idxs.add(where["point_index"])
    if kind == "angle_range":
      if "vertex_index" in where:
        vertex_idxs.add(where["vertex_index"])
    if kind in ("segment_length", "closure", "backtrack"):
      if "segment_index" in where:
        seg_idxs.add(where["segment_index"])
        if kind == "backtrack":
          seg_idxs.add((where["segment_index"] + 1))
    if kind in ("crossings", "exact_crossings"):
      pairs = where.get("pairs")
      if isinstance(pairs, list):
        for p in pairs:
          if isinstance(p, (list, tuple)) and len(p) == 2:
            seg_pairs.append((int(p[0]), int(p[1])))
    if kind == "min_point_separation":
      pair = where.get("point_indices")
      if isinstance(pair, (list, tuple)) and len(pair) == 2:
        min_sep_pairs.append((int(pair[0]), int(pair[1])))
  return {
    "point_idxs": point_idxs,
    "vertex_idxs": vertex_idxs,
    "seg_idxs": seg_idxs,
    "seg_pairs": seg_pairs,
    "min_sep_pairs": min_sep_pairs,
  }


def _snapshot_svg(snapshot: Dict[str, Any]) -> str:
  boundary = float(snapshot["boundary"])
  n = int(snapshot["n"])
  pos = snapshot["pos"]
  vel = snapshot["vel"]
  forces = snapshot.get("forces")
  errors = snapshot.get("errors") or []
  constraints = snapshot.get("constraints") or {}

  idxs = _collect_error_index_sets(errors)
  point_err = idxs["point_idxs"]
  vertex_err = idxs["vertex_idxs"]
  seg_err = idxs["seg_idxs"]
  seg_pairs = idxs["seg_pairs"]
  min_sep_pairs = idxs["min_sep_pairs"]

  stroke = max(0.002 * boundary, 0.02)
  pt_r = max(0.008 * boundary, 0.06)
  font_sz = max(0.02 * boundary, 0.18)

  vel_mag_max = max(1e-9, max(math.hypot(v[0], v[1]) for v in vel))
  vel_scale = max(0.3, boundary * 0.03) / vel_mag_max

  force_scale = 0.0
  if forces:
    force_mag_max = max(1e-9, max(math.hypot(f[0], f[1]) for f in forces))
    force_scale = max(0.25, boundary * 0.025) / force_mag_max

  vb = f"0 0 {boundary} {boundary}"
  wpx = 1600
  hpx = 1600

  parts = []
  parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{wpx}" height="{hpx}">')
  parts.append("<defs>")
  parts.append(
    "<marker id=\"arrowVel\" markerWidth=\"6\" markerHeight=\"6\" refX=\"5\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L6,3 L0,6 z\" fill=\"#4fd1c5\"/></marker>"
  )
  parts.append(
    "<marker id=\"arrowF\" markerWidth=\"6\" markerHeight=\"6\" refX=\"5\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L6,3 L0,6 z\" fill=\"#f56565\"/></marker>"
  )
  parts.append("</defs>")

  parts.append(
    f'<rect x="0" y="0" width="{boundary}" height="{boundary}" fill="#0b1220" stroke="#3b82f6" stroke-width="{stroke}"/>'
  )

  mid = boundary / 2.0
  parts.append(
    f'<line x1="{mid}" y1="0" x2="{mid}" y2="{boundary}" stroke="#1f2937" stroke-width="{stroke}"/>'
  )
  parts.append(
    f'<line x1="0" y1="{mid}" x2="{boundary}" y2="{mid}" stroke="#1f2937" stroke-width="{stroke}"/>'
  )

  if constraints.get("avoid_margin"):
    m = float(constraints["avoid_margin"])
    parts.append(
      f'<rect x="{m}" y="{m}" width="{boundary-2*m}" height="{boundary-2*m}" fill="none" stroke="#f59e0b" stroke-dasharray="{stroke*4} {stroke*3}" stroke-width="{stroke}"/>'
    )

  if constraints.get("centroid_box"):
    xmin, xmax, ymin, ymax = constraints["centroid_box"]
    y_svg = boundary - ymax
    parts.append(
      f'<rect x="{xmin}" y="{y_svg}" width="{xmax-xmin}" height="{ymax-ymin}" fill="none" stroke="#22c55e" stroke-dasharray="{stroke*4} {stroke*3}" stroke-width="{stroke}"/>'
    )

  if constraints.get("must_touch_boundary"):
    tol_edge = max(1e-3, boundary * 0.001)
    edges_hit = set()
    for i in range(n):
      x0, y0 = pos[i][0], pos[i][1]
      if abs(x0) <= tol_edge:
        edges_hit.add("left")
      if abs(x0 - boundary) <= tol_edge:
        edges_hit.add("right")
      if abs(y0) <= tol_edge:
        edges_hit.add("bottom")
      if abs(y0 - boundary) <= tol_edge:
        edges_hit.add("top")
    need = int(constraints.get("must_touch_boundary") or 0)
    ok = (len(edges_hit) >= need)
    col_ok = "#22c55e" if ok else "#f59e0b"

    def edge_color(name: str) -> str:
      return "#22c55e" if name in edges_hit else col_ok

    parts.append(
      f'<line x1="0" y1="0" x2="{boundary}" y2="0" stroke="{edge_color("top")}" stroke-width="{stroke*3}" opacity="0.8"/>'
    )
    parts.append(
      f'<line x1="0" y1="{boundary}" x2="{boundary}" y2="{boundary}" stroke="{edge_color("bottom")}" stroke-width="{stroke*3}" opacity="0.8"/>'
    )
    parts.append(
      f'<line x1="0" y1="0" x2="0" y2="{boundary}" stroke="{edge_color("left")}" stroke-width="{stroke*3}" opacity="0.8"/>'
    )
    parts.append(
      f'<line x1="{boundary}" y1="0" x2="{boundary}" y2="{boundary}" stroke="{edge_color("right")}" stroke-width="{stroke*3}" opacity="0.8"/>'
    )

  if constraints.get("fixed_start"):
    fx, fy, tol = constraints["fixed_start"]
    fxs, fys = _svg_point(boundary, (fx, fy))
    parts.append(
      f'<circle cx="{fxs}" cy="{fys}" r="{max(tol, pt_r*1.2)}" fill="none" stroke="#a78bfa" stroke-width="{stroke*1.4}" opacity="0.85"/>'
    )
    parts.append(f'<circle cx="{fxs}" cy="{fys}" r="{pt_r*0.9}" fill="#a78bfa" opacity="0.9"/>')

  pts_svg = [_svg_point(boundary, (p[0], p[1])) for p in pos]
  poly_pts = " ".join([f"{_fmt_float(x,4)},{_fmt_float(y,4)}" for x, y in pts_svg])
  parts.append(
    f'<polyline points="{poly_pts} {_fmt_float(pts_svg[0][0],4)},{_fmt_float(pts_svg[0][1],4)}" fill="none" stroke="#94a3b8" stroke-width="{stroke}"/>'
  )

  if snapshot.get("hull"):
    hull = snapshot["hull"]
    hull_svg = [_svg_point(boundary, (p[0], p[1])) for p in hull]
    hull_pts = " ".join([f"{_fmt_float(x,4)},{_fmt_float(y,4)}" for x, y in hull_svg])
    parts.append(
      f'<polygon points="{hull_pts}" fill="rgba(34,197,94,0.06)" stroke="#22c55e" stroke-width="{stroke}"/>'
    )

  if min_sep_pairs:
    for a, b in min_sep_pairs:
      if 0 <= a < n and 0 <= b < n:
        x1, y1 = pts_svg[a]
        x2, y2 = pts_svg[b]
        parts.append(
          f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fb7185" stroke-width="{stroke*1.5}"/>'
        )

  if seg_pairs:
    for si, sj in seg_pairs:
      si = si % n
      sj = sj % n
      a1 = (pos[si][0], pos[si][1])
      a2 = (pos[(si + 1) % n][0], pos[(si + 1) % n][1])
      b1 = (pos[sj][0], pos[sj][1])
      b2 = (pos[(sj + 1) % n][0], pos[(sj + 1) % n][1])
      ip = _segment_intersection_point(a1, a2, b1, b2)
      if ip is not None:
        ix, iy = _svg_point(boundary, ip)
        parts.append(
          f'<circle cx="{ix}" cy="{iy}" r="{pt_r*0.7}" fill="none" stroke="#ef4444" stroke-width="{stroke*1.5}"/>'
        )

  for i in range(n):
    j = (i + 1) % n
    x1, y1 = pts_svg[i]
    x2, y2 = pts_svg[j]
    if i in seg_err:
      parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ef4444" stroke-width="{stroke*2.2}" opacity="0.9"/>'
      )
    for pair in seg_pairs:
      if i == (pair[0] % n) or i == (pair[1] % n):
        parts.append(
          f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ef4444" stroke-width="{stroke*1.6}" opacity="0.6"/>'
        )

  for i in range(n):
    x, y = pts_svg[i]
    fill = "#e2e8f0"
    if i in point_err or i in vertex_err:
      fill = "#fb7185"
    if i == 0 and constraints.get("fixed_start"):
      parts.append(
        f'<circle cx="{x}" cy="{y}" r="{pt_r*1.6}" fill="none" stroke="#a78bfa" stroke-width="{stroke*1.4}" opacity="0.9"/>'
      )
    parts.append(
      f'<circle cx="{x}" cy="{y}" r="{pt_r}" fill="{fill}" stroke="#0f172a" stroke-width="{stroke}"/>'
    )
    parts.append(
      f'<text x="{x+pt_r*1.2}" y="{y-pt_r*1.2}" font-size="{font_sz}" fill="#e5e7eb">{i}</text>')

  if constraints.get("coverage_quadrants"):
    mid = boundary / 2.0
    quadrants = set()
    for (x0, y0) in pos:
      if x0 <= mid and y0 <= mid:
        quadrants.add("bottom_left")
      if x0 <= mid and y0 >= mid:
        quadrants.add("top_left")
      if x0 >= mid and y0 <= mid:
        quadrants.add("bottom_right")
      if x0 >= mid and y0 >= mid:
        quadrants.add("top_right")
    all_q = ["top_left", "top_right", "bottom_left", "bottom_right"]
    q_pos = {
      "top_left": (boundary * 0.15, boundary * 0.15),
      "top_right": (boundary * 0.85, boundary * 0.15),
      "bottom_left": (boundary * 0.15, boundary * 0.85),
      "bottom_right": (boundary * 0.85, boundary * 0.85),
    }
    for q in all_q:
      px, py = q_pos[q]
      col = "#22c55e" if q in quadrants else "#ef4444"
      parts.append(
        f'<text x="{px}" y="{py}" text-anchor="middle" font-size="{font_sz*1.2}" fill="{col}" opacity="0.9">{q}</text>'
      )

  for i in range(n):
    x, y = pts_svg[i]
    vx, vy = vel[i]
    ex = pos[i][0] + vx * vel_scale
    ey = pos[i][1] + vy * vel_scale
    exs, eys = _svg_point(boundary, (ex, ey))
    parts.append(
      f'<line x1="{x}" y1="{y}" x2="{exs}" y2="{eys}" stroke="#4fd1c5" stroke-width="{stroke*1.2}" marker-end="url(#arrowVel)" opacity="0.9"/>'
    )

  if forces:
    for i in range(n):
      x, y = pts_svg[i]
      fx, fy = forces[i]
      ex = pos[i][0] + fx * force_scale
      ey = pos[i][1] + fy * force_scale
      exs, eys = _svg_point(boundary, (ex, ey))
      parts.append(
        f'<line x1="{x}" y1="{y}" x2="{exs}" y2="{eys}" stroke="#f56565" stroke-width="{stroke*1.1}" marker-end="url(#arrowF)" opacity="0.75"/>'
      )

  cx, cy = snapshot.get("centroid", (None, None))
  if cx is not None and cy is not None:
    cxs, cys = _svg_point(boundary, (cx, cy))
    parts.append(
      f'<line x1="{cxs-pt_r*1.5}" y1="{cys}" x2="{cxs+pt_r*1.5}" y2="{cys}" stroke="#22c55e" stroke-width="{stroke*1.2}"/>'
    )
    parts.append(
      f'<line x1="{cxs}" y1="{cys-pt_r*1.5}" x2="{cxs}" y2="{cys+pt_r*1.5}" stroke="#22c55e" stroke-width="{stroke*1.2}"/>'
    )

  parts.append("</svg>")
  return "".join(parts)


def _write_stuck_diagnostics_html(subPass: int, snapshots: List[Dict[str, Any]],
                                  tag: str) -> Optional[Path]:
  if not snapshots:
    return None
  path = _diag_path(subPass, tag)

  title = f"q12 spring diagnostics - subpass {subPass} - {tag}"
  head = f"""<!doctype html>
<html><head><meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
<title>{html.escape(title)}</title>
<style>
body {{ background:#0b1220; color:#e5e7eb; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 0; }}
.wrap {{ padding: 18px; }}
.meta {{ font-size: 14px; line-height: 1.35; color: #cbd5e1; }}
.grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; }}
.card {{ background: rgba(15,23,42,0.75); border: 1px solid rgba(148,163,184,0.15); border-radius: 12px; padding: 14px; overflow: auto; }}
.h {{ font-size: 18px; margin: 0 0 8px 0; }}
.kvs {{ display: grid; grid-template-columns: 240px 1fr; gap: 4px 12px; font-size: 13px; }}
.k {{ color: #93c5fd; }}
.v {{ color: #e5e7eb; white-space: pre-wrap; }}
.svgwrap {{ overflow: auto; border-radius: 10px; border: 1px solid rgba(148,163,184,0.12); }}
.legend {{ font-size: 12px; color: #cbd5e1; margin-top: 6px; }}
code {{ color: #fde68a; }}
</style>
</head><body><div class=\"wrap\">"""

  body = [head]
  body.append(f"<h1 style=\"margin:0 0 10px 0; font-size:22px\">{html.escape(title)}</h1>")
  body.append("<div class=\"meta\">")
  body.append(f"<div>Saved to: <code>{html.escape(str(path))}</code></div>")
  body.append(f"<div>Snapshots: {len(snapshots)}</div>")
  body.append(
    "<div>Legend: cyan arrows = velocity, red arrows = force (acceleration proxy), red segments/points = constraint violations per grader.</div>"
  )
  body.append("</div>")

  body.append("<div class=\"grid\">")
  for s in snapshots:
    it = s.get("it")
    t = s.get("t")
    note = s.get("note", "")
    error_count = s.get("error_count")
    best_count = s.get("best_count")
    k_edge = s.get("k_edge")
    k_angle = s.get("k_angle")
    kinds = s.get("kinds")
    body.append("<div class=\"card\">")
    body.append(
      f"<h2 class=\"h\">Iter {it}  |  t={_fmt_float(t,2)}  |  errors={error_count} (best {best_count})  |  {html.escape(str(note))}</h2>"
    )
    body.append("<div class=\"kvs\">")
    body.append(
      f"<div class=\"k\">k_edge</div><div class=\"v\">{html.escape(str(_fmt_float(k_edge,4)))}</div>"
    )
    body.append(
      f"<div class=\"k\">k_angle</div><div class=\"v\">{html.escape(str(_fmt_float(k_angle,4)))}</div>"
    )
    body.append(
      f"<div class=\"k\">error kinds</div><div class=\"v\">{html.escape(str(kinds))}</div>")
    body.append(
      f"<div class=\"k\">constraints</div><div class=\"v\">{html.escape(str(s.get('constraints')))}</div>"
    )
    body.append("</div>")
    body.append("<div class=\"svgwrap\">")
    body.append(_snapshot_svg(s))
    body.append("</div>")
    errs = s.get("errors") or []
    if errs:
      body.append(
        "<div class=\"legend\"><div style=\"margin-top:8px; font-weight:600\">Structured errors (first 5)</div><pre style=\"white-space:pre-wrap; margin:6px 0 0 0;\">"
        + html.escape(json.dumps(errs[:5], indent=2)) + "</pre></div>")
    body.append("</div>")
  body.append("</div>")

  body.append("</div></body></html>")

  try:
    with open(path, "w", encoding="utf-8") as f:
      f.write("".join(body))
    print(f"Spring diagnostics written: {path}")
    return path
  except Exception:
    return None


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
    self.seed = seed
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
    for comp in self.complications or []:
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
    """Initialize positions by randomly selecting from a set of shapes."""
    # Build list of candidate initializers based on constraints
    candidates = []

    exact_cross = self.constraints["exact_crossings"]
    max_cross = self.constraints["max_crossings"]

    # Figure-8 patterns work well when we need exactly 1 crossing
    if exact_cross == 1:
      candidates.append(self._init_figure_eight)

    # Lissajous patterns can create multiple crossings
    if exact_cross and exact_cross > 1:
      candidates.append(self._init_lissajous)

    # No-crossing shapes: good when max_crossings=0 or no crossing constraint
    if not exact_cross or exact_cross == 0:
      if self.n < 150:
        candidates.append(self._init_circle)
      if self.n >= 20:  # Need enough points for complex shapes
        candidates.append(self._init_double_helix)
        candidates.append(self._init_railway_tracks)
      if self.n >= 40:
        candidates.append(self._init_triple_helix)

    # Always have at least circle as fallback
    if not candidates:
      candidates.append(self._init_circle)

    # Randomly select one
    init_fn = self.rng.choice(candidates)
    print("Using generator: " + init_fn.__name__)
    pts = init_fn()

    # Apply fixed_start shift if needed (skip for shapes that handle it internally)
    #if self.constraints["fixed_start"] and init_fn != self._init_circle:
    #  pts = self._apply_fixed_start_shift(pts)

    return pts

  def _apply_fixed_start_shift(self, pts: List[List[float]]) -> List[List[float]]:
    """Move shape so point 0 lands on fixed_start, scaling down if needed to fit in bounds.
    
    This preserves topology by:
    1. Translating the entire shape so point 0 is at the target
    2. If any points go out of bounds, scale the shape toward point 0 until it fits
    3. Ensure minimum point spacing is maintained (don't over-scale)
    """
    fx, fy, tolerance = self.constraints["fixed_start"]
    margin = 0.1

    # Compute original average spacing between adjacent points
    n = len(pts)
    total_spacing = 0.0
    for i in range(n):
      j = (i + 1) % n
      total_spacing += math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
    orig_avg_spacing = total_spacing / n if n > 0 else 1.0

    # Minimum spacing we need to maintain (at least 0.3 to avoid coincident points)
    min_spacing = 0.3
    min_scale_for_spacing = min_spacing / orig_avg_spacing if orig_avg_spacing > 1e-6 else 1.0

    # Step 1: Translate so point 0 is at the target
    p0x, p0y = pts[0]
    dx = fx - p0x
    dy = fy - p0y

    translated = [[px + dx, py + dy] for px, py in pts]

    # Step 2: Check if any points are out of bounds
    # If so, scale the shape toward point 0 (which is now at fx, fy)
    max_scale = 1.0
    for px, py in translated:
      rel_x = px - fx
      rel_y = py - fy

      # X bounds
      if rel_x > 0:
        s = (self.boundary - margin - fx) / rel_x if rel_x > 1e-6 else 1.0
        max_scale = min(max_scale, s)
      elif rel_x < 0:
        s = (margin - fx) / rel_x if rel_x < -1e-6 else 1.0
        max_scale = min(max_scale, s)

      # Y bounds
      if rel_y > 0:
        s = (self.boundary - margin - fy) / rel_y if rel_y > 1e-6 else 1.0
        max_scale = min(max_scale, s)
      elif rel_y < 0:
        s = (margin - fy) / rel_y if rel_y < -1e-6 else 1.0
        max_scale = min(max_scale, s)

    # Apply scaling: use max_scale but don't go below min_scale_for_spacing
    # If we can't fit, let the solver's boundary forces push points back in
    scale = max(min_scale_for_spacing, min(1.0, max_scale))

    result = []
    for px, py in translated:
      x = fx + scale * (px - fx)
      y = fy + scale * (py - fy)
      # Don't clamp here - let solver's boundary forces handle it
      # Clamping causes coincident points when multiple points hit the same boundary
      result.append([x, y])

    return result

  def _init_circle(self) -> List[List[float]]:
    """Initialize as a regular polygon (circle of points).
    
    If fixed_start is set, position the circle so point 0 is at fixed_start
    and the circle fits within bounds.
    """
    margin = 0.2

    # Determine center based on fixed_start constraint
    if self.constraints["fixed_start"]:
      fx, fy, _ = self.constraints["fixed_start"]
      # Point 0 will be at angle 0 (rightmost point of circle)
      # So center should be to the left of fx
      # But we need to fit the whole circle in bounds

      # Calculate max radius that fits given point 0 at (fx, fy)
      # Point 0 is at center + (r, 0), so center_x = fx - r
      # Circle must fit: center_x - r >= margin, center_x + r <= boundary - margin
      #                  center_y - r >= margin, center_y + r <= boundary - margin
      # With center_x = fx - r: fx - 2r >= margin, fx <= boundary - margin
      # So r <= (fx - margin) / 2
      # Also r <= fx - margin (for right side: center_x + r = fx <= boundary - margin)
      # And center_y = fy, so: fy - r >= margin, fy + r <= boundary - margin
      # So r <= fy - margin, r <= boundary - margin - fy

      max_r_x = (fx - margin) if fx > margin else (self.boundary - margin - fx)
      max_r_y = min(fy - margin, self.boundary - margin - fy)
      max_r_fixed = min(max_r_x, max_r_y)

      # Also limit by ideal radius for chord length = 1
      if self.n >= 3:
        ideal_r = 1.0 / (2 * math.sin(math.pi / self.n))
      else:
        ideal_r = 1.0

      r = min(ideal_r, max(0.5, max_r_fixed))  # At least 0.5 radius

      # Center so that point 0 (at angle 0) lands on (fx, fy)
      center_x = fx - r
      center_y = fy

      # If center would put circle out of bounds, adjust
      if center_x - r < margin:
        center_x = margin + r
      if center_x + r > self.boundary - margin:
        center_x = self.boundary - margin - r
      if center_y - r < margin:
        center_y = margin + r
      if center_y + r > self.boundary - margin:
        center_y = self.boundary - margin - r
    else:
      center_x = self.boundary / 2
      center_y = self.boundary / 2

      if self.n >= 3:
        ideal_r = 1.0 / (2 * math.sin(math.pi / self.n))
      else:
        ideal_r = 1.0
      max_r = (self.boundary - 2 * margin) / 2
      r = min(ideal_r, max_r)

    pts = []
    for i in range(self.n):
      ang = 2 * math.pi * i / self.n
      x = center_x + r * math.cos(ang)
      y = center_y + r * math.sin(ang)
      pts.append([x, y])
    return pts

  def _init_figure_eight(self) -> List[List[float]]:
    """Initialize as a figure-8 pattern (Lissajous with freq=2) for 1 crossing."""
    center = self.boundary / 2
    scale = min(self.boundary * 0.35, self.n / (2 * math.pi) * 0.5)

    pts = []
    for i in range(self.n):
      t = 2 * math.pi * i / self.n
      x = center + scale * math.sin(t)
      y = center + scale * math.sin(2 * t) * 0.8
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])
    return pts

  def _init_lissajous(self) -> List[List[float]]:
    """Initialize as a Lissajous curve for multiple crossings."""
    center = self.boundary / 2
    scale = min(self.boundary * 0.35, self.n / (2 * math.pi) * 0.5)

    crossings_needed = self.constraints["exact_crossings"] or 2
    # Lissajous: x = sin(t), y = sin(freq*t) creates (freq-1) crossings approximately
    freq = crossings_needed + 1

    pts = []
    for i in range(self.n):
      t = 2 * math.pi * i / self.n
      x = center + scale * math.sin(t)
      y = center + scale * math.sin(freq * t) * 0.8
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])
    return pts

  def _init_double_helix(self) -> List[List[float]]:
    """Initialize as two concentric circles going opposite directions.
    
    Creates a shape like: outer circle CW from top, then short link down,
    inner circle CCW back to near start, then short link back up.
    No crossings if done right.
    """
    center = self.boundary / 2

    # Allocate points: ~half on outer, ~half on inner, with a few for links
    link_pts = 2  # points for each link
    circle_pts = (self.n - 2 * link_pts) // 2
    outer_pts = circle_pts
    inner_pts = self.n - outer_pts - 2 * link_pts

    # Radii
    outer_r = min(self.boundary * 0.4, self.n / (4 * math.pi) * 0.8)
    inner_r = outer_r * 0.6

    # Gap angle where we DON'T place points (for the link slots)
    gap_angle = 0.15  # radians, small gap at bottom

    pts = []

    # Outer circle: CW from just past the gap, almost all the way around
    arc_outer = 2 * math.pi - gap_angle
    for i in range(outer_pts):
      # Start at bottom-right of gap, go CW (negative angle)
      t = -math.pi / 2 + gap_angle / 2 - (arc_outer * i / outer_pts)
      x = center + outer_r * math.cos(t)
      y = center + outer_r * math.sin(t) * 2
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Link from outer to inner (at bottom-left of gap)
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      r = outer_r + (inner_r - outer_r) * frac
      t = -math.pi / 2 - gap_angle / 2
      x = center + r * math.cos(t)
      y = center + r * math.sin(t) * 2
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Inner circle: CCW from bottom-left of gap, almost all the way around
    arc_inner = 2 * math.pi - gap_angle
    for i in range(inner_pts):
      # Start at bottom-left of gap, go CCW (positive angle)
      t = -math.pi / 2 - gap_angle / 2 + (arc_inner * i / inner_pts)
      x = center + inner_r * math.cos(t)
      y = center + inner_r * math.sin(t) * 2
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Link from inner back to outer (at bottom-right of gap)
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      r = inner_r + (outer_r - inner_r) * frac
      t = -math.pi / 2 + gap_angle / 2
      x = center + r * math.cos(t)
      y = center + r * math.sin(t) * 2
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    return pts

  def _init_triple_helix(self) -> List[List[float]]:
    """Initialize as three concentric circles forming a spiral pattern.
    
    Links are positioned 120° apart to avoid crossings:
    - Outer circle: angle A to B (CW)
    - Link at B: outer to middle
    - Middle circle: angle B to C (CCW)  
    - Link at C: middle to inner
    - Inner circle: angle C to A (CW)
    - Link at A: inner back to outer
    """
    center = self.boundary / 2

    # Allocate points across three circles plus links
    link_pts = 2
    total_links = 3
    circle_budget = self.n - total_links * link_pts
    pts_per_circle = circle_budget // 3
    outer_pts = pts_per_circle
    middle_pts = pts_per_circle
    inner_pts = self.n - outer_pts - middle_pts - total_links * link_pts

    # Calculate radii based on chord length ≈ 1.0
    # For n points around 2/3 of a circle, chord = 2*r*sin(pi*2/3 / n)
    # For chord = 1, r = 1 / (2 * sin(2*pi / (3*n)))
    arc_fraction = 2.0 / 3.0  # each circle covers 2/3 of full circle

    if outer_pts >= 3:
      outer_r = 1.0 / (2 * math.sin(math.pi * arc_fraction / outer_pts))
    else:
      outer_r = 2.0

    # Limit to fit in boundary, but keep reasonable size
    max_r = (self.boundary - 0.4) / 2
    outer_r = min(outer_r, max_r)
    outer_r = max(outer_r, self.boundary * 0.35)  # at least 35% of boundary

    # Space rings evenly - each ring separated by ~2 units for link length
    ring_spacing = 2.0
    middle_r = outer_r - ring_spacing
    inner_r = middle_r - ring_spacing

    # Ensure inner radius is positive
    if inner_r < 1.0:
      # Rescale all radii
      scale = (outer_r - 2.0) / (outer_r - inner_r) if outer_r > inner_r else 0.5
      inner_r = 1.0
      middle_r = inner_r + ring_spacing * scale
      outer_r = middle_r + ring_spacing * scale

    pts = []

    # Three link positions, 120° apart
    angle_A = 0  # 0° (right)
    angle_B = 2 * math.pi / 3  # 120° (upper left)
    angle_C = 4 * math.pi / 3  # 240° (lower left)

    # Each circle arc covers ~240° (2/3 of circle)
    arc_angle = 2 * math.pi * arc_fraction

    # Outer circle: CW from angle A to angle B
    for i in range(outer_pts):
      frac = i / outer_pts if outer_pts > 0 else 0
      t = angle_A - frac * arc_angle  # CW = negative direction
      x = center + outer_r * math.cos(t)
      y = center + outer_r * math.sin(t)
      pts.append([x, y])

    # Link at angle B: outer to middle (radial, no crossing)
    link_angle_1 = angle_A - arc_angle  # where outer circle ended
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      r = outer_r + (middle_r - outer_r) * frac
      x = center + r * math.cos(link_angle_1)
      y = center + r * math.sin(link_angle_1)
      pts.append([x, y])

    # Middle circle: CCW from link_angle_1 for arc_angle
    for i in range(middle_pts):
      frac = i / middle_pts if middle_pts > 0 else 0
      t = link_angle_1 + frac * arc_angle  # CCW = positive direction
      x = center + middle_r * math.cos(t)
      y = center + middle_r * math.sin(t)
      pts.append([x, y])

    # Link at end of middle: middle to inner
    link_angle_2 = link_angle_1 + arc_angle  # where middle circle ended
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      r = middle_r + (inner_r - middle_r) * frac
      x = center + r * math.cos(link_angle_2)
      y = center + r * math.sin(link_angle_2)
      pts.append([x, y])

    # Inner circle: CW from link_angle_2 for arc_angle
    for i in range(inner_pts):
      frac = i / inner_pts if inner_pts > 0 else 0
      t = link_angle_2 - frac * arc_angle  # CW = negative direction
      x = center + inner_r * math.cos(t)
      y = center + inner_r * math.sin(t)
      pts.append([x, y])

    # Link back to start: inner to outer
    link_angle_3 = link_angle_2 - arc_angle  # where inner circle ended (should be ~angle_A)
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      r = inner_r + (outer_r - inner_r) * frac
      x = center + r * math.cos(link_angle_3)
      y = center + r * math.sin(link_angle_3)
      pts.append([x, y])

    return pts

  def _init_railway_tracks(self) -> List[List[float]]:
    """Initialize as two parallel sin waves (like railway tracks).
    
    Goes left-to-right on top wave, then right-to-left on bottom wave,
    connected at the ends. No crossings.
    """
    center = self.boundary / 2

    # Half the points on each "track"
    half_n = self.n // 2
    link_pts = 2
    track_pts = (self.n - 2 * link_pts) // 2
    track1_pts = track_pts
    track2_pts = self.n - track1_pts - 2 * link_pts

    # Wave parameters
    amplitude = self.boundary * 0.15
    separation = self.boundary * 0.1  # vertical separation between tracks
    wave_periods = max(2, self.n // 30)  # more points = more waves

    x_start = self.boundary * 0.1
    x_end = self.boundary * 0.9

    pts = []

    # Top track: left to right
    for i in range(track1_pts):
      frac = i / (track1_pts - 1) if track1_pts > 1 else 0
      x = x_start + (x_end - x_start) * frac
      t = frac * wave_periods * 2 * math.pi
      y = center + separation / 2 + amplitude * math.sin(t)
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Right link: top to bottom
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      x = x_end
      y_top = center + separation / 2 + amplitude * math.sin(wave_periods * 2 * math.pi)
      y_bot = center - separation / 2 + amplitude * math.sin(wave_periods * 2 * math.pi + 0.3)
      y = y_top + (y_bot - y_top) * frac
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Bottom track: right to left (slightly phase-shifted)
    phase_shift = 0.3  # slight offset so tracks don't perfectly align
    for i in range(track2_pts):
      frac = i / (track2_pts - 1) if track2_pts > 1 else 0
      x = x_end - (x_end - x_start) * frac
      t = (1 - frac) * wave_periods * 2 * math.pi + phase_shift
      y = center - separation / 2 + amplitude * math.sin(t)
      pts.append([_clamp(x, 0.1, self.boundary - 0.1), _clamp(y, 0.1, self.boundary - 0.1)])

    # Left link: bottom to top
    for i in range(link_pts):
      frac = (i + 1) / (link_pts + 1)
      x = x_start
      y_bot = center - separation / 2 + amplitude * math.sin(phase_shift)
      y_top = center + separation / 2
      y = y_bot + (y_top - y_bot) * frac
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

        if dist > 0.95 and dist < 1.05:
          continue  # Close enough for the grader.

        fx = k_edge * stretch * dx / dist
        fy = k_edge * stretch * dy / dist

        forces[i][0] += fx
        forces[i][1] += fy
        forces[j][0] -= fx
        forces[j][1] -= fy

        if n > 100:
          dropOff = 0.5
          count = 4

          if progress > 0.2: continue

          if progress < 0.025:
            dropOff = 0.5
            count = 10

          for k in range(1, count):
            i2 = i - k
            j2 = j + k
            if j2 >= n: j2 -= n
            fx *= dropOff
            fy *= dropOff
            forces[i2][0] += fx
            forces[i2][1] += fy
            forces[j2][0] -= fx
            forces[j2][1] -= fy

      else:
        # If they intersect - spray them randomly.
        print(f"    Points {i} and {j} are coincident")
        forces[i][0] += random.random() * 2
        forces[i][1] += random.random() * 2
        forces[j][0] -= random.random() * 2
        forces[j][1] -= random.random() * 2

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

    diag_snapshots: List[Dict[str, Any]] = []
    last_diag_it = -10**9
    last_diag_error_count: Optional[int] = None

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

    def record_diag(it: int, note: str, errors: List[Dict[str, Any]], error_count: int,
                    best_count: int, progress: float) -> None:
      nonlocal last_diag_it, last_diag_error_count
      if it - last_diag_it < 20 and last_diag_error_count == error_count:
        return
      last_diag_it = it
      last_diag_error_count = error_count

      forces = self._compute_forces(pos, progress)
      k_edge = self.k_edge_min + (self.k_edge_max - self.k_edge_min) * min(
        0, math.sin(progress * .013))
      k_angle = self.k_angle_min + (self.k_angle_max - self.k_angle_min) * min(
        0, math.sin(progress * .037))
      pts = [(p[0], p[1]) for p in pos]
      centroid = (sum(p[0] for p in pts) / len(pts),
                  sum(p[1] for p in pts) / len(pts)) if pts else (0.0, 0.0)
      hull = _convex_hull(pts)

      kinds = sorted(list(set([e.get("kind", "?") for e in (errors[:25] if errors else [])])))
      diag_snapshots.append({
        "subPass": self.subPass,
        "seed": self.seed,
        "it": it,
        "t": it * self.dt,
        "note": note,
        "boundary": self.boundary,
        "tolerance": self.tolerance,
        "dt": self.dt,
        "damping": self.damping,
        "max_velocity": self.max_velocity,
        "n": self.n,
        "progress": progress,
        "k_edge": k_edge,
        "k_angle": k_angle,
        "constraints": self.constraints,
        "pos": _copy_2d(pos),
        "vel": _copy_2d(vel),
        "forces": forces,
        "errors": errors,
        "kinds": kinds,
        "error_count": error_count,
        "best_count": best_count,
        "centroid": centroid,
        "hull": hull,
      })

    record_diag(self.subPass, "initial", best_errors, best_count, best_count, 0.0)

    for it in range(max_iterations):
      if firstStallTime and time.time() - firstStallTime > time_limit:
        if revert_to_best_count < 5 and error_count > best_count:
          pos = [p[:] for p in best_pos]
          vel = [v[:] for v in best_vel]
          revert_to_best_count += 1
          print(f"- Reverted at {it} ({error_count} errors) back to {best_count}."
                f" As have been stuck for {time.time() - firstStallTime:.1f} seconds. "
                f"This was reversion #{revert_to_best_count}/5")
          firstStallTime = None

        else:
          try:
            if diag_snapshots:
              _write_stuck_diagnostics_html(self.subPass, diag_snapshots, "gave_up_time_limit")
          except Exception:
            pass
          break

      # Progress ramps from 0 to 1 over iterations (edge springs get stronger)
      progress = min(1.0, it / 1000.0)  # Ramp up over first 1000 iterations
      self._step(pos, vel, progress)

      # Periodically evaluate
      errors = self._evaluate(pos)
      error_count = len(errors)

      if firstStallTime is not None:
        record_diag(it, "stuck", errors, error_count, best_count, progress)

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
        kinds = list(set([e.get("kind", "?") for e in errors[:3]]))

        print(f"- Iter {it}: {error_count} errors, types: {kinds}")

      else:
        stall_counter += 1

      # Progress logging
      if it in [10, 50, 100, 200, 500, 1000, 1500, 2000, 3000, 4000, 5000, 10000, 15000]:
        kinds = [e.get("kind", "?") for e in errors[:3]]
        print(f"- Iter {it}: {error_count} errors, types: {kinds}")

      # If stalled, add random perturbation
      if stall_counter > 20:
        error = random.choice(errors)
        if error["kind"] == "segment_length":
          #print(f"    Jiggling {i},{(i + 1) % self.n}")
          i = error["where"]["segment_index"]
          vel[i][0] += (self.rng.random() - 0.5)
          vel[i][1] += (self.rng.random() - 0.5)
          vel[(i + 1) % self.n][0] += (self.rng.random() - 0.5)
          vel[(i + 1) % self.n][1] += (self.rng.random() - 0.5)

        stall_counter = 0
        if firstStallTime is None:
          firstStallTime = time.time()
          record_diag(it, "stall_started", errors, error_count, best_count, progress)

    if len(vel) > 5:
      for i in range(5):
        print(f"  - {pos[i][0]:.1f} {pos[i][1]:.1f}. V = {vel[i][0]:.1f} {vel[i][1]:.1f}")

    kinds = [e.get("kind", "?") for e in errors[:3]]

    try:
      if diag_snapshots:
        record_diag(max_iterations, "final", errors, error_count, best_count, 1.0)
        _write_stuck_diagnostics_html(self.subPass, diag_snapshots, "gave_up")
    except Exception:
      pass

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


mutexLock = threading.Lock()


def get_response(subPass: int):
  # Check cache first
  cached = _load_cached_solution(subPass)
  if cached is not None:
    print("Cached: " + str(CACHE_DIR))
    return cached, "Solver: Loaded from cache"

  # There is no benefit to running the solver in parallel.
  with mutexLock:
    # Try multiple restarts with different seeds for robustness
    best_pts = None
    best_errors = float('inf')
    best_summary = ""

    print(f"Starting {subPass}")

    num_restarts = 10
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


def cache_solutions():
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
