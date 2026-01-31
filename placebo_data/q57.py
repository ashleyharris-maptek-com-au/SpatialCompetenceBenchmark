"""Placebo data for VGB5 - Two Segments."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.verification.two_segments import verify_two_segments

DATA_PATH = REPO_ROOT / "data" / "vgb" / "two_segments_curated.jsonl"
_DATA = None

def _map_point(point, corners):
  c0, c1, _, c3 = corners
  axis_u = (c1[0] - c0[0], c1[1] - c0[1])
  axis_v = (c3[0] - c0[0], c3[1] - c0[1])
  return (
    c0[0] + point[0] * axis_u[0] + point[1] * axis_v[0],
    c0[1] + point[0] * axis_u[1] + point[1] * axis_v[1],
  )


def _map_segments(segments, corners):
  if not corners:
    return segments
  return [(_map_point(p0, corners), _map_point(p1, corners)) for p0, p1 in segments]


def _boundary_points(values):
  pts = []
  for v in values:
    v = float(v)
    pts.append((v, 0.0))
    pts.append((v, 1.0))
    pts.append((0.0, v))
    pts.append((1.0, v))
  uniq = []
  for p in pts:
    if p not in uniq:
      uniq.append(p)
  return uniq


def _segment_on_boundary_edge(p0, p1):
  if p0[0] == p1[0] and p0[0] in (0.0, 1.0):
    return True
  if p0[1] == p1[1] and p0[1] in (0.0, 1.0):
    return True
  return False


def _candidate_values(datagen_args):
  grid = datagen_args.get("coordinate_grid")
  if grid:
    return sorted(set(float(v) for v in grid))
  snap_decimals = int(datagen_args.get("snap_decimals", 2))
  values = {0.0, 1.0}
  max_den = 6
  for den in range(2, max_den + 1):
    for num in range(1, den):
      values.add(round(num / den, snap_decimals))
  return sorted(values)


def _get_data():
  global _DATA
  if _DATA is None:
    if DATA_PATH.exists():
      _DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
    else:
      _DATA = []
  return _DATA


def get_response(subPass: int):
  """Get the placebo response for this question."""
  data = _get_data()
  if subPass >= len(data):
    return None, "Not yet implemented"
  record = data[subPass]
  datagen_args = record.get("datagen_args", {})
  corners = datagen_args.get("corners")
  grid = datagen_args.get("coordinate_grid")

  values = _candidate_values(datagen_args)
  pts = _boundary_points(values)
  segs = []
  for i in range(len(pts)):
    for j in range(i + 1, len(pts)):
      p0, p1 = pts[i], pts[j]
      if _segment_on_boundary_edge(p0, p1):
        continue
      segs.append((p0, p1))

  map_corners = corners if not grid else None
  for i in range(len(segs)):
    for j in range(i + 1, len(segs)):
      segments = [segs[i], segs[j]]
      candidate = _map_segments(segments, map_corners)
      if verify_two_segments(repr(candidate), record):
        return {"segments": candidate}, "Placebo: derived segments"

  return None, "Not yet implemented"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  segs = []
  for _ in range(2):
    segs.append(((rng.random(), rng.random()), (rng.random(), rng.random())))
  return {"segments": segs}, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  # Return segments that don't partition correctly
  return {"segments": [((0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0))]}, "Always-wrong placeholder"
