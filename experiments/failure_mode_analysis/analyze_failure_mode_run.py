#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from experiments.failure_mode_analysis.failure_mode_task_cards.paths import get_default_run_name
from experiments.failure_mode_analysis.judge import classify_rows
from experiments.failure_mode_analysis.run_summary_analysis import (build_evidence_rows, merge_decisions,
                                                                    select_candidate_rows,
                                                                    write_failure_mode_analysis_md,
                                                                    write_failure_mode_distribution_pie,
                                                                    write_failure_mode_task_csv,
                                                                    write_failure_modes_jsonl)
from experiments.failure_mode_analysis.schemas import (AnalysisConfig, JUDGE_STATUS_ERROR, JUDGE_STATUS_OK)

def _parse_model_names(value: str) -> list[str]:
  return [part.strip() for part in value.split(",") if part.strip()]


def _load_model_runs(model_names: list[str], results_models_dir: Path) -> list[dict]:
  runs: list[dict] = []
  for model_name in model_names:
    model_dir = results_models_dir / model_name
    summary_path = model_dir / "run_summary.json"
    if not summary_path.exists():
      raise FileNotFoundError(f"run_summary.json not found: {summary_path}")
    with summary_path.open("r", encoding="utf-8") as f:
      summary = json.load(f)
    runs.append({
      "model_name": model_name,
      "summary": summary,
    })
  runs.sort(key=lambda run: run["model_name"])
  return runs


def main() -> None:
  parser = argparse.ArgumentParser(description="Run failure-mode analysis using an online LLM judge.")
  parser.add_argument("--model-names",
                      required=True,
                      help="Comma-separated model names to analyze (must exist under results/models).")
  parser.add_argument("--results-models-dir",
                      default="results/models",
                      help="Base directory containing <model>/run_summary.json files.")
  parser.add_argument("--output-dir",
                      default="results/experiments/failure_mode_analysis",
                      help="Directory where outputs are written.")
  parser.add_argument("--judge-trace-dir",
                      default=None,
                      help="Optional directory for per-sub-batch judge traces (prompts/raw/cot). "
                      "Default: <output-dir>/judge_traces")
  parser.add_argument("--run-name",
                      default=None,
                      help="Task-card run name.")
  parser.add_argument("--low-score-threshold",
                      type=float,
                      default=0.6,
                      help="Also classify passes with 0 < score < threshold.")
  parser.add_argument("--judge-engine",
                      default="azure-openai",
                      choices=["azure-openai", "openai"],
                      help="Provider used for the online judge.")
  parser.add_argument("--judge-model",
                      default=os.environ.get("FAILURE_MODE_JUDGE_MODEL"),
                      help="Judge model/deployment name. Can also be set via FAILURE_MODE_JUDGE_MODEL.")
  parser.add_argument("--judge-reasoning",
                      type=int,
                      default=os.environ.get("FAILURE_MODE_JUDGE_REASONING", 5),
                      help="Judge reasoning level. 0 disables reasoning; higher values increase effort.")
  parser.add_argument("--judge-timeout-seconds", type=float, default=180.0)
  parser.add_argument("--judge-temperature", type=float, default=None)
  parser.add_argument("--judge-max-output-tokens", type=int, default=16384)
  parser.add_argument("--judge-retries", type=int, default=2)
  parser.add_argument("--judge-max-batch-subpasses", type=int, default=5,
                      help="Max subpasses per judge LLM call. Tasks with more subpasses are split into sub-batches.")
  parser.add_argument("--prompt-version", default="failure-mode-judge-v1")
  args = parser.parse_args()

  run_name = args.run_name or get_default_run_name()
  output_dir = Path(args.output_dir)
  judge_trace_dir = Path(args.judge_trace_dir) if args.judge_trace_dir else output_dir / "judge_traces"

  if not args.judge_model:
    raise ValueError("Judge model is required. Pass --judge-model or set FAILURE_MODE_JUDGE_MODEL.")

  config = AnalysisConfig(run_name=run_name,
                          low_score_threshold=float(args.low_score_threshold),
                          judge_engine=args.judge_engine,
                          judge_model=args.judge_model,
                          judge_reasoning=max(0, int(args.judge_reasoning)),
                          judge_timeout_seconds=float(args.judge_timeout_seconds),
                          judge_temperature=args.judge_temperature,
                          judge_max_output_tokens=int(args.judge_max_output_tokens),
                          judge_retries=max(0, int(args.judge_retries)),
                          prompt_version=args.prompt_version,
                          judge_max_batch_subpasses=max(1, int(args.judge_max_batch_subpasses)),
                          judge_trace_dir=str(judge_trace_dir))

  model_names = _parse_model_names(args.model_names)

  results_models_dir = Path(args.results_models_dir)
  model_runs = _load_model_runs(model_names, results_models_dir)
  if not model_runs:
    raise ValueError("No run_summary.json files found for the requested models.")

  evidence_rows = build_evidence_rows(model_runs, results_models_dir=results_models_dir)
  candidate_rows = select_candidate_rows(evidence_rows, config.low_score_threshold)
  decisions = classify_rows(candidate_rows, config)
  labeled_rows = merge_decisions(evidence_rows, decisions, config)

  output_dir.mkdir(parents=True, exist_ok=True)
  outputs = {
    "failure_modes_jsonl": write_failure_modes_jsonl(labeled_rows, output_dir),
    "failure_mode_task_csv": write_failure_mode_task_csv(labeled_rows, output_dir),
    "failure_mode_analysis_md": write_failure_mode_analysis_md(labeled_rows, output_dir),
    "failure_mode_distribution_pie": write_failure_mode_distribution_pie(labeled_rows, output_dir),
  }

  total_rows = len(labeled_rows)
  judged_rows = sum(1 for row in labeled_rows if row.judge_status == JUDGE_STATUS_OK)
  error_rows = sum(1 for row in labeled_rows if row.judge_status == JUDGE_STATUS_ERROR)
  print("Failure-mode analysis complete.")
  print(f"  rows_total: {total_rows}")
  print(f"  rows_judged: {judged_rows}")
  print(f"  rows_judge_error: {error_rows}")
  print("Generated artifacts:")
  for key, path in outputs.items():
    print(f"  {key}: {path}")
  if config.judge_trace_dir:
    print(f"  judge_traces (per-sub-batch): {config.judge_trace_dir}")


if __name__ == "__main__":
  main()
