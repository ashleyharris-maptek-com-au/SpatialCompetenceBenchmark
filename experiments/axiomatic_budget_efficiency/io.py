import json
from pathlib import Path
from typing import Any, Iterator


def safe_float(value: Any, default: float | None = None) -> float | None:
  try:
    if value is None:
      return default
    return float(value)
  except Exception:
    return default


def model_run_summary_path(model_name: str) -> Path:
  return Path("results") / "models" / model_name / "run_summary.json"


def load_run_summary(model_name: str) -> dict:
  path = model_run_summary_path(model_name)
  if not path.exists():
    raise FileNotFoundError(f"Run summary not found: {path}")
  with path.open("r", encoding="utf-8") as f:
    return json.load(f)


def iter_subpasses(summary: dict) -> Iterator[dict]:
  for test in summary.get("tests", []):
    for subpass in test.get("subpasses", []):
      yield subpass
