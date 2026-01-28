"""Placebo data for VGB5 - Two Segments."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

DATA_PATH = REPO_ROOT / "data" / "vgb" / "two_segments_curated.jsonl"
_DATA = None


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
  ground_truth = data[subPass].get("ground_truth", [])
  # For two_segments, ground_truth is shape counts, but the answer should be segments
  # We need to return a valid segment pair - use diagonal segments as placebo
  return [((0.0, 0.0), (1.0, 1.0)), ((0.0, 1.0), (1.0, 0.0))], "Placebo: X-shape segments"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  segs = []
  for _ in range(2):
    segs.append(((rng.random(), rng.random()), (rng.random(), rng.random())))
  return segs, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  # Return segments that don't partition correctly
  return [((0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0))], "Always-wrong placeholder"
