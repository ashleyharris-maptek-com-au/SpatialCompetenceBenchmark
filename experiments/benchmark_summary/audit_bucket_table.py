#!/usr/bin/env python3
"""Audit SCBench per-bucket score accounting from run_summary.json.

SCBench subtasks can be partial-credit, so the numerator is a float (sum of
per-subpass scores) while the denominator is the number of subtasks (subpasses).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from experiments.benchmark_summary.bucket_mapping import BUCKET_TO_TEST_INDICES, BUCKET_ORDER


def _safe_int(value) -> int:
  try:
    return int(value)
  except Exception:
    return 0


def _safe_float(value) -> float:
  try:
    return float(value)
  except Exception:
    return 0.0


def _accuracy_pct(total_score: float, max_score: float) -> float:
  return (total_score / max_score * 100.0) if max_score > 0 else 0.0


def _load_run_summary(path: Path) -> dict:
  return json.loads(path.read_text(encoding="utf-8"))


def _audit_test(test: dict, *, model: str, strict: bool) -> None:
  idx = _safe_int(test.get("test_index", -1))
  title = str(test.get("title") or "")
  subpass_count = _safe_int(test.get("subpass_count") or 0)
  subpasses = test.get("subpasses") or []

  max_score = _safe_float(test.get("max_score") or 0.0)
  total_score = _safe_float(test.get("score") or 0.0)

  if strict and subpass_count != len(subpasses):
    raise ValueError(
      f"{model}: Q{idx} subpass_count={subpass_count} but len(subpasses)={len(subpasses)} ({title})"
    )
  if strict and abs(max_score - float(subpass_count)) > 1e-6:
    raise ValueError(
      f"{model}: Q{idx} max_score={max_score} but subpass_count={subpass_count} ({title})"
    )
  if strict and (total_score < -1e-6 or total_score > max_score + 1e-6):
    raise ValueError(
      f"{model}: Q{idx} total_score={total_score} out of range for max_score={max_score} ({title})"
    )

  # Subpass scores are expected to be normalized to [0, 1].
  if strict:
    for sp in subpasses:
      if "score" not in sp:
        continue
      score = sp["score"]
      try:
        score_f = float(score)
      except Exception:
        raise ValueError(f"{model}: Q{idx} subpass has non-numeric score={score!r}")
      if score_f < -1e-6 or score_f > 1.0 + 1e-6:
        raise ValueError(f"{model}: Q{idx} subpass score out of range: {score_f}")


def _bucket_stats(summary: dict, test_indices: list[int], *, model: str, strict: bool) -> dict:
  selected = {int(i) for i in test_indices}
  by_idx = {int(t.get("test_index", -1)): t for t in summary.get("tests", [])}
  missing = sorted(i for i in selected if i not in by_idx)
  if missing:
    raise ValueError(f"{model}: missing tests in run_summary: {missing}")

  tests = [by_idx[i] for i in test_indices]
  for test in tests:
    _audit_test(test, model=model, strict=strict)

  subpasses = sum(_safe_int(t.get("subpass_count") or 0) for t in tests)
  max_score = sum(_safe_float(t.get("max_score") or 0.0) for t in tests)
  total_score = sum(_safe_float(t.get("score") or 0.0) for t in tests)
  return {
    "task_count": len(tests),
    "subpass_count": subpasses,
    "max_score": max_score,
    "total_score": total_score,
    "accuracy_pct": _accuracy_pct(total_score, max_score),
  }


def main() -> None:
  parser = argparse.ArgumentParser(description="Audit SCBench bucket accounting from run_summary.json.")
  parser.add_argument(
    "--models",
    required=True,
    help="Comma-separated model dirs under results/models (each must contain run_summary.json).",
  )
  parser.add_argument("--results-models-dir", default="results/models")
  parser.add_argument("--strict", action="store_true", help="Enforce invariants and fail fast.")
  args = parser.parse_args()

  models = [m.strip() for m in args.models.split(",") if m.strip()]
  if not models:
    raise ValueError("No models provided.")

  all_selected = sorted({i for idxs in BUCKET_TO_TEST_INDICES.values() for i in idxs})
  results_models_dir = Path(args.results_models_dir)

  for model in models:
    summary_path = results_models_dir / model / "run_summary.json"
    if not summary_path.exists():
      raise FileNotFoundError(f"run_summary.json not found: {summary_path}")
    summary = _load_run_summary(summary_path)

    print()
    print(f"== {model} ==")
    overall_subpasses = sum(_safe_int(t.get("subpass_count") or 0) for t in summary.get("tests", []))
    overall_max = _safe_float((summary.get("overall") or {}).get("max_score") or 0.0)
    overall_total = _safe_float((summary.get("overall") or {}).get("total_score") or 0.0)
    print(
      f"overall_subpasses={overall_subpasses} "
      f"overall_total_score={overall_total:.6f} overall_max_score={overall_max:.0f}"
    )

    # Sanity-check that the "active" tasks match the bucket mapping.
    active = sorted(
      int(t.get("test_index", -1))
      for t in summary.get("tests", [])
      if _safe_float(t.get("max_score") or 0.0) > 0
    )
    if active != all_selected:
      msg = f"{model}: active test_indices != selected bucket mapping\n  active={active}\n  selected={all_selected}"
      if args.strict:
        raise ValueError(msg)
      print(f"WARNING: {msg}")

    per_bucket = {}
    for bucket in BUCKET_ORDER:
      indices = BUCKET_TO_TEST_INDICES[bucket]
      stats = _bucket_stats(summary, indices, model=model, strict=bool(args.strict))
      per_bucket[bucket] = stats
      print(
        f"{bucket}: tasks={stats['task_count']} subtasks={stats['subpass_count']} "
        f"score={stats['total_score']:.6f}/{stats['max_score']:.0f} ({stats['accuracy_pct']:.3f}%)"
      )

    selected_total_score = sum(per_bucket[b]["total_score"] for b in per_bucket)
    selected_max_score = sum(per_bucket[b]["max_score"] for b in per_bucket)
    selected_subpasses = sum(per_bucket[b]["subpass_count"] for b in per_bucket)
    print(
      f"Selected overall: tasks={sum(per_bucket[b]['task_count'] for b in per_bucket)} "
      f"subtasks={selected_subpasses} "
      f"score={selected_total_score:.6f}/{selected_max_score:.0f} "
      f"({_accuracy_pct(selected_total_score, selected_max_score):.3f}%)"
    )


if __name__ == "__main__":
  main()
