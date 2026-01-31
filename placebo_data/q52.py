"""Placebo data for VGB2 - Topology Edge Tasks: Enumerate Edges."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

DATA_PATH = REPO_ROOT / "data" / "vgb" / "topology_edge_enumerate_curated.jsonl"
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
  return {"edges": ground_truth}, "Placebo: returning ground truth from dataset"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"edges": []}, "Random guess"
  gt = data[subPass].get("ground_truth", [])
  guess = []
  for _ in range(len(gt)):
    count = rng.randint(0, 2)
    pairs = []
    for _ in range(count):
      a = rng.randint(0, 3)
      b = rng.randint(0, 3)
      if a == b:
        b = (b + 1) % 4
      pairs.append([min(a, b), max(a, b)])
    guess.append(pairs)
  return {"edges": guess}, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"edges": []}, "Always-wrong placeholder"
  # Return incorrect edge pairs - use inverted indices
  gt = data[subPass].get("ground_truth", [])
  if gt and isinstance(gt, list) and len(gt) > 0:
    wrong = []
    for case in gt:
      if isinstance(case, list):
        pairs = []
        for pair in case:
          if isinstance(pair, list) and len(pair) == 2:
            a, b = pair
            pairs.append([3 - a, 3 - b])
        wrong.append(pairs)
      else:
        wrong.append([])
    return {"edges": wrong}, "Always-wrong placeholder"
  return {"edges": [[]]}, "Always-wrong placeholder"
