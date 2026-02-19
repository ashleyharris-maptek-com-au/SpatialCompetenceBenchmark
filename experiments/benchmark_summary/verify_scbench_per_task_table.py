#!/usr/bin/env python3
"""Verify the SCBench appendix per-task table matches run_summary.json.

This is strict about *numbers* (and task ordering), but tolerant to whitespace.
It parses the LaTeX table and compares against run_summary-derived values after
rounding to 1 decimal (the paper's displayed precision).
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


def _find_table_block(tex_text: str) -> str:
  label = r"\label{tab:per-task-scores}"
  label_pos = tex_text.find(label)
  if label_pos < 0:
    raise ValueError("Could not find tab:per-task-scores label.")

  tabular_begin = tex_text.find(r"\begin{tabular}", label_pos)
  if tabular_begin < 0:
    raise ValueError("Could not find \\begin{tabular} after label.")

  tabular_end = tex_text.find(r"\end{tabular}", tabular_begin)
  if tabular_end < 0:
    raise ValueError("Could not find \\end{tabular}.")

  return tex_text[tabular_begin:tabular_end + len(r"\end{tabular}")]


def _parse_rows(tabular_block: str) -> list[tuple[str, str, int, float, float]]:
  rows = []
  for line in tabular_block.splitlines():
    stripped = line.strip()
    if not stripped.startswith("&"):
      continue
    if not stripped.endswith(r"\\"):
      continue
    parts = [p.strip() for p in stripped[:-2].split("&")]
    if len(parts) != 5:
      continue
    _bucket_cell, task, n, claude, gemini = parts
    try:
      n_i = int(n)
      claude_f = float(claude)
      gemini_f = float(gemini)
    except Exception:
      continue
    rows.append(("", task, n_i, claude_f, gemini_f))
  return rows


def main() -> None:
  parser = argparse.ArgumentParser(description="Verify appendix per-task score table.")
  parser.add_argument("--tex-path", required=True, help="Path to appendix_content.tex (or the file containing the table).")
  parser.add_argument("--models", required=True, help="Comma-separated model dirs under results/models.")
  parser.add_argument("--results-models-dir", default="results/models")
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

  model_headers = [_display_name(m) for m in models]
  if model_headers != ["Claude", "Gemini"]:
    raise ValueError(f"Expected models to resolve to Claude,Gemini. Got: {model_headers}")

  tex_text = Path(args.tex_path).read_text(encoding="utf-8")
  tabular = _find_table_block(tex_text)
  parsed = _parse_rows(tabular)

  expected_rows = []
  for bucket in BUCKET_ORDER:
    for idx, short_label in PAPER_TASKS_BY_BUCKET[bucket]:
      n = int(per_model[models[0]][idx]["subpasses"])
      claude = float(f"{per_model[models[0]][idx]['pct']:.1f}")
      gemini = float(f"{per_model[models[1]][idx]['pct']:.1f}")
      expected_rows.append((bucket, short_label, n, claude, gemini))

  if len(parsed) != len(expected_rows):
    print(f"ERROR: parsed {len(parsed)} data rows, expected {len(expected_rows)}.")
    sys.exit(2)

  # Compare row-by-row against expected order and displayed numbers.
  errors = 0
  for (bucket, short_label, n, claude, gemini), (_blank, task, n_i, claude_f, gemini_f) in zip(expected_rows, parsed):
    if task != short_label:
      print(f"ERROR: task label mismatch. expected={short_label!r} got={task!r}")
      errors += 1
      continue
    if n_i != n:
      print(f"ERROR: N mismatch for {task}. expected={n} got={n_i}")
      errors += 1
    if abs(claude_f - claude) > 1e-9:
      print(f"ERROR: Claude value mismatch for {task}. expected={claude:.1f} got={claude_f:.1f}")
      errors += 1
    if abs(gemini_f - gemini) > 1e-9:
      print(f"ERROR: Gemini value mismatch for {task}. expected={gemini:.1f} got={gemini_f:.1f}")
      errors += 1

  if errors:
    sys.exit(2)
  print("OK: appendix per-task table matches run_summary-derived values (rounded to 0.1).")


if __name__ == "__main__":
  main()
