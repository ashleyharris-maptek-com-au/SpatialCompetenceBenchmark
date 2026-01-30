"""Placebo data for VGB6 - Delaunay Triangulation."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

DATA_PATH = REPO_ROOT / "data" / "vgb" / "delaunay_dataset.jsonl"
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
  return {"triangles": ground_truth}, "Placebo: returning ground truth from dataset"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"triangles": [[0, 0, 0]]}, "Random guess"
  triangles = []
  for _ in range(3):
    triangles.append([rng.randint(0, 10), rng.randint(0, 10), rng.randint(0, 10)])
  return {"triangles": triangles}, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"triangles": []}, "Always-wrong placeholder"
  # Return a single degenerate triangle
  return {"triangles": [[0, 0, 0]]}, "Always-wrong placeholder"
