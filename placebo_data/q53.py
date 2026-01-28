"""Placebo data for VGB3 - Topology Edge Tasks: Classify Behaviour."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

DATA_PATH = REPO_ROOT / "data" / "vgb" / "topology_edge_classify_curated.jsonl"
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
  return ground_truth, "Placebo: returning ground truth from dataset"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  data = _get_data()
  if subPass >= len(data):
    return [], "Random guess"
  count = rng.randint(1, 4)
  labels = []
  for _ in range(count):
    labels.append([rng.randint(0, 3), rng.randint(0, 3)])
  return labels, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  data = _get_data()
  if subPass >= len(data):
    return [], "Always-wrong placeholder"
  # Return wrong classification - shift behaviours
  gt = data[subPass].get("ground_truth", [])
  if gt and isinstance(gt, list) and len(gt) > 0:
    wrong = [[3 - i for i in pair] if isinstance(pair, list) else pair for pair in gt]
    return wrong, "Always-wrong placeholder"
  return [[0, 0]], "Always-wrong placeholder"
