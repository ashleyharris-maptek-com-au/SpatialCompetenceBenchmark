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
  return {"labels": ground_truth}, "Placebo: returning ground truth from dataset"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"labels": []}, "Random guess"
  gt = data[subPass].get("ground_truth", [])
  choices = ["known behaviour", "three domains meeting", "ambiguous"]
  labels = [rng.choice(choices) for _ in range(len(gt))]
  return {"labels": labels}, "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  data = _get_data()
  if subPass >= len(data):
    return {"labels": []}, "Always-wrong placeholder"
  # Return wrong classification labels while staying schema-valid
  gt = data[subPass].get("ground_truth", [])
  if gt and isinstance(gt, list):
    label_map = {
      "known behaviour": "ambiguous",
      "ambiguous": "three domains meeting",
      "three domains meeting": "known behaviour",
    }
    wrong = [label_map.get(label, "ambiguous") for label in gt]
    return {"labels": wrong}, "Always-wrong placeholder"
  return {"labels": ["ambiguous"]}, "Always-wrong placeholder"
