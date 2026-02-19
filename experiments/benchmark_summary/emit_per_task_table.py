#!/usr/bin/env python3
"""Emit a LaTeX per-task accuracy table for the SCBench paper appendix.

This intentionally matches the paper's preferred formatting exactly (no derived
columns like averages).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from experiments.benchmark_summary.bucket_mapping import BUCKET_ORDER, PAPER_TASKS_BY_BUCKET


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


def _load_summary(path: Path) -> dict:
  return json.loads(path.read_text(encoding="utf-8"))


def _escape_latex(text: str) -> str:
  return (text.replace("\\", "\\textbackslash{}")
          .replace("&", "\\&")
          .replace("%", "\\%")
          .replace("#", "\\#")
          .replace("_", "\\_"))


def _display_name(model_name: str) -> str:
  if model_name.startswith("claude-sonnet-4-5"):
    return "Claude"
  if model_name.startswith("gemini-3-pro-preview"):
    return "Gemini"
  return model_name


def _collect(summary: dict, test_indices: list[int]) -> dict[int, dict]:
  by_idx = {int(t.get("test_index", -1)): t for t in summary.get("tests", [])}
  out: dict[int, dict] = {}
  for idx in test_indices:
    test = by_idx[idx]
    max_score = _safe_float(test.get("max_score") or 0.0)
    score = _safe_float(test.get("score") or 0.0)
    pct = (score / max_score * 100.0) if max_score > 0 else 0.0
    out[idx] = {
      "title": str(test.get("title") or f"Task {idx}"),
      "subpasses": _safe_int(test.get("subpass_count") or 0),
      "score": score,
      "max": max_score,
      "pct": pct,
    }
  return out


def main() -> None:
  parser = argparse.ArgumentParser(description="Emit per-task LaTeX table for SCBench.")
  parser.add_argument("--models", required=True, help="Comma-separated model dirs under results/models.")
  parser.add_argument("--results-models-dir", default="results/models")
  parser.add_argument("--caption",
                      default="Per-task accuracy (\\%) for the 22 SCBench tasks under no-tools evaluation.")
  parser.add_argument("--label", default="tab:per-task-scores")
  args = parser.parse_args()

  models = [m.strip() for m in args.models.split(",") if m.strip()]
  if not models:
    raise ValueError("No models provided.")
  if len(models) != 2:
    raise ValueError("Expected exactly 2 models (Claude and Gemini).")

  results_models_dir = Path(args.results_models_dir)
  test_indices = [idx for bucket in BUCKET_ORDER for idx, _label in PAPER_TASKS_BY_BUCKET[bucket]]

  per_model: dict[str, dict[int, dict]] = {}
  for model in models:
    summary_path = results_models_dir / model / "run_summary.json"
    if not summary_path.exists():
      raise FileNotFoundError(f"run_summary.json not found: {summary_path}")
    per_model[model] = _collect(_load_summary(summary_path), test_indices)

  model_headers = [_escape_latex(_display_name(m)) for m in models]
  if model_headers != ["Claude", "Gemini"]:
    raise ValueError(f"Expected models to resolve to Claude,Gemini. Got: {model_headers}")

  print("\\begin{table}[ht]")
  print("\\centering")
  print("\\small")
  print(f"\\caption{{{args.caption}}}")
  print(f"\\label{{{args.label}}}")
  print("\\vspace{2pt}")
  print("\\setlength{\\tabcolsep}{4pt}")
  print("\\begin{tabular}{@{}llrrr@{}}")
  print("\\hline")
  print("\\textbf{Bucket} & \\textbf{Task} & \\textbf{$N$} & \\textbf{Claude} & \\textbf{Gemini} \\\\")
  print("\\hline")

  for bucket in BUCKET_ORDER:
    print(f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{{bucket}}}}} \\\\")
    for idx, short_label in PAPER_TASKS_BY_BUCKET[bucket]:
      subpasses = per_model[models[0]][idx]["subpasses"]
      claude = float(f"{per_model[models[0]][idx]['pct']:.1f}")
      gemini = float(f"{per_model[models[1]][idx]['pct']:.1f}")
      print(
        f" & {short_label:<27} & {subpasses:2d} & "
        f"{claude:.1f} & {gemini:.1f} \\\\"
      )
    print("\\hline")

  print("\\end{tabular}")
  print("\\end{table}")


if __name__ == "__main__":
  main()
