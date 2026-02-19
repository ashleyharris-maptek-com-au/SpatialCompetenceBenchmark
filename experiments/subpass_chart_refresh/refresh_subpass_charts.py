#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .spec import CANONICAL_MODEL_RUNS, PUBLISH_FILENAME_BY_TASK, TASK_SPECS, TaskSpec


_BAR_COLOR = "#E89C15"
_EDGE_COLOR = "#D78800"
_MEDIAN_COLOR = "#1F4E79"
_GRID_COLOR = "#DDDDDD"


def _sha256_file(path: Path) -> str:
  hasher = hashlib.sha256()
  with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
      hasher.update(chunk)
  return hasher.hexdigest()


def _safe_float(value, *, context: str) -> float:
  try:
    out = float(value)
  except (TypeError, ValueError) as exc:
    raise ValueError(f"{context}: expected numeric score, got {value!r}") from exc
  if math.isnan(out) or math.isinf(out):
    raise ValueError(f"{context}: score must be finite, got {out!r}")
  return out


def _git_commit(repo_root: Path) -> str | None:
  try:
    out = subprocess.run(["git", "rev-parse", "HEAD"],
                         cwd=str(repo_root),
                         check=True,
                         capture_output=True,
                         text=True)
  except (FileNotFoundError, subprocess.CalledProcessError):
    return None
  commit = out.stdout.strip()
  return commit or None


def _load_run_summary(path: Path) -> dict:
  with path.open("r", encoding="utf-8") as handle:
    return json.load(handle)


def _extract_task_scores(summary: dict, task: TaskSpec, *, model_run: str, strict: bool) -> list[float]:
  tests = summary.get("tests")
  if not isinstance(tests, list):
    raise ValueError(f"{model_run}: run_summary missing list field 'tests'")

  task_row = None
  for test in tests:
    if int(test.get("test_index", -1)) == task.task_index:
      task_row = test
      break

  if task_row is None:
    raise ValueError(f"{model_run}: missing task Q{task.task_index} in run_summary")

  subpasses = task_row.get("subpasses")
  if not isinstance(subpasses, list):
    raise ValueError(f"{model_run}: Q{task.task_index} missing list field 'subpasses'")

  seen_indices: set[int] = set()
  score_by_subpass: dict[int, float] = {}
  for idx, subpass in enumerate(subpasses):
    subpass_index = int(subpass.get("subpass", idx))
    if subpass_index in seen_indices:
      raise ValueError(f"{model_run}: Q{task.task_index} duplicate subpass index {subpass_index}")
    seen_indices.add(subpass_index)
    score = _safe_float(subpass.get("score", 0.0),
                        context=f"{model_run}: Q{task.task_index} S{subpass_index}")
    if strict and not (0.0 <= score <= 1.0):
      raise ValueError(
        f"{model_run}: Q{task.task_index} S{subpass_index} score out of [0,1]: {score}")
    score_by_subpass[subpass_index] = score

  expected_indices = set(range(task.expected_subpasses))
  got_indices = set(score_by_subpass.keys())
  if got_indices != expected_indices:
    missing = sorted(expected_indices - got_indices)
    extra = sorted(got_indices - expected_indices)
    raise ValueError(
      f"{model_run}: Q{task.task_index} subpass mismatch. expected=0..{task.expected_subpasses - 1}, "
      f"missing={missing}, extra={extra}")

  return [score_by_subpass[i] for i in range(task.expected_subpasses)]


def _format_score(value: float) -> str:
  return f"{value:.10f}"


def _build_dimension_groups(labels: tuple[str, ...]) -> list[tuple[str, int, int]]:
  groups: list[tuple[str, int, int]] = []
  start = 0
  current = labels[0]
  for idx in range(1, len(labels)):
    if labels[idx] != current:
      groups.append((current, start, idx - 1))
      current = labels[idx]
      start = idx
  groups.append((current, start, len(labels) - 1))
  return groups


def _render_chart(task: TaskSpec, aggregate_rows: list[dict], output_path: Path) -> None:
  x = np.arange(task.expected_subpasses)
  means = np.array([row["mean_score"] for row in aggregate_rows], dtype=float)

  fig_h = 4.2 if task.task_index != 12 else 4.6
  fig, ax = plt.subplots(figsize=(8.8, fig_h))
  ax.bar(x, means, color=_BAR_COLOR, edgecolor=_EDGE_COLOR, linewidth=0.7, width=0.82, label="Mean")
  ax.set_ylim(0, 1.0)
  ax.set_xlabel("Subpass")
  ax.set_ylabel("Score")
  ax.set_title(task.chart_title)
  ax.set_xticks(x)
  ax.set_xticklabels([str(i) for i in range(task.expected_subpasses)], fontsize=8)
  ax.grid(axis="y", color=_GRID_COLOR, linewidth=0.8)
  ax.set_axisbelow(True)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)

  if task.include_median_overlay:
    medians = np.array([row["median_score"] for row in aggregate_rows], dtype=float)
    ax.plot(x,
            medians,
            color=_MEDIAN_COLOR,
            linewidth=2.0,
            marker="o",
            markersize=4.5,
            markerfacecolor="white",
            markeredgecolor=_MEDIAN_COLOR,
            label="Median")
    ax.legend(frameon=False, fontsize=9, loc="upper right")

  if task.dimension_labels:
    groups = _build_dimension_groups(task.dimension_labels)
    for label, start, end in groups:
      center = (start + end) / 2.0
      ax.text(center,
              -0.18,
              label,
              ha="center",
              va="top",
              fontsize=10,
              fontweight="semibold",
              transform=ax.get_xaxis_transform())
      if end < task.expected_subpasses - 1:
        ax.axvline(end + 0.5, color="#EEEEEE", linewidth=0.8)
    ax.text(-0.9,
            -0.18,
            "Dimension",
            ha="left",
            va="top",
            fontsize=9,
            color="#444444",
            transform=ax.get_xaxis_transform())
    fig.tight_layout(rect=(0, 0.09, 1, 1))
  else:
    fig.tight_layout()

  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(output_path, dpi=220, bbox_inches="tight")
  plt.close(fig)


def _render_aggregate_csv_bytes(task: TaskSpec, aggregate_rows: list[dict]) -> bytes:
  header = ["task_index", "subpass", "mean_score"]
  if task.include_median_overlay:
    header.append("median_score")

  lines = [",".join(header)]
  for row in aggregate_rows:
    parts = [str(task.task_index), str(row["subpass"]), _format_score(row["mean_score"])]
    if task.include_median_overlay:
      parts.append(_format_score(row["median_score"]))
    lines.append(",".join(parts))
  return ("\n".join(lines) + "\n").encode("utf-8")


def _write_long_csv(path: Path, task: TaskSpec, long_rows: list[dict]) -> None:
  fieldnames = ["task_index", "subpass", "model_run", "score"]
  with path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for row in long_rows:
      writer.writerow({
        "task_index": task.task_index,
        "subpass": row["subpass"],
        "model_run": row["model_run"],
        "score": _format_score(row["score"]),
      })


def _write_aggregate_csv(path: Path, task: TaskSpec, aggregate_rows: list[dict]) -> str:
  payload = _render_aggregate_csv_bytes(task, aggregate_rows)
  path.write_bytes(payload)
  return hashlib.sha256(payload).hexdigest()


def _replace_once_or_verify(text: str, *, old: str, new: str, strict: bool, label: str) -> tuple[str, int]:
  if old in text:
    count = text.count(old)
    if strict and count != 1:
      raise ValueError(f"{label}: expected exactly 1 occurrence of old text, found {count}")
    return text.replace(old, new), count

  if new in text:
    return text, 0

  if strict:
    raise ValueError(f"{label}: neither old nor new text found")
  return text, 0


def _patch_appendix_tex(tex_path: Path, strict: bool) -> dict:
  text = tex_path.read_text(encoding="utf-8")
  replacements_applied = 0

  image_replacements = (
    ("figures/appendix/appendix_image30.png", "figures/appendix/q11_mean_subpass_6runs.png", "Q11 image"),
    ("figures/appendix/appendix_image33.png", "figures/appendix/q12_mean_subpass_6runs.png", "Q12 image"),
    ("figures/appendix/appendix_image40.png", "figures/appendix/q16_mean_subpass_6runs.png",
     "Q16 image"),
  )
  for old, new, label in image_replacements:
    text, count = _replace_once_or_verify(text, old=old, new=new, strict=strict, label=label)
    replacements_applied += count

  caption_replacements = (
    ("\\caption{Hyper-Snake (2). Score by subpass and dimensionality.}",
     "\\caption{Hyper-Snake (2). Mean score by subpass across six model runs, with dimensionality progression from 2D to 10D.}",
     "Q11 caption"),
    ("\\caption{Pipe Loop Fitting (2, 3). (Left) 390 pipes in 35 x 35, solved with spring solver (subpass 37). (Right) Mean score of all 39 subpasses under models.}",
     "\\caption{Pipe Loop Fitting (2, 3). (Left) 390 pipes in 35 x 35, solved with spring solver (subpass 37). (Right) Mean score across all 40 subpasses under six model runs.}",
     "Q12 caption"),
    ("\\caption{Pack Rectangular Prisms (2, 3). (Left) Median score by subtask. (Right) A model's perfect packing for subtask 1.}",
     "\\caption{Pack Rectangular Prisms (2, 3). (Left) Mean score by subtask across six model runs; median overlay shown. (Right) A model's perfect packing for subtask 1.}",
     "Q16 caption"),
  )
  for old, new, label in caption_replacements:
    text, count = _replace_once_or_verify(text, old=old, new=new, strict=strict, label=label)
    replacements_applied += count

  tex_path.write_text(text, encoding="utf-8")
  return {"tex_path": str(tex_path.resolve()), "replacements_applied": replacements_applied}


def _copy_published_figures(chart_paths: dict[int, Path], publish_dir: Path) -> list[dict]:
  publish_dir.mkdir(parents=True, exist_ok=True)
  mappings = []
  for task_index, src in sorted(chart_paths.items()):
    target_name = PUBLISH_FILENAME_BY_TASK[task_index]
    dst = publish_dir / target_name
    shutil.copy2(src, dst)
    mappings.append({
      "task_index": task_index,
      "source": str(src.resolve()),
      "target": str(dst.resolve()),
      "target_name": target_name,
    })
  return mappings


def _update_latest_pointer(base_output_dir: Path, run_dir: Path) -> None:
  latest_path = base_output_dir / "latest"
  if latest_path.exists() or latest_path.is_symlink():
    if latest_path.is_dir() and not latest_path.is_symlink():
      shutil.rmtree(latest_path)
    else:
      latest_path.unlink()
  latest_path.symlink_to(run_dir.name)


def _find_previous_latest_run(base_output_dir: Path) -> Path | None:
  latest_path = base_output_dir / "latest"
  if not (latest_path.exists() or latest_path.is_symlink()):
    return None
  resolved = latest_path.resolve(strict=False)
  if not resolved.exists() or not resolved.is_dir():
    return None
  return resolved


def _build_input_hash_map(run_summary_metadata: list[dict]) -> dict[str, str]:
  return {row["model_run"]: row["run_summary_sha256"] for row in run_summary_metadata}


def _load_previous_manifest(path: Path) -> dict | None:
  manifest_path = path / "calculation_manifest.json"
  if not manifest_path.exists():
    return None
  return json.loads(manifest_path.read_text(encoding="utf-8"))


def main() -> None:
  repo_root = Path(__file__).resolve().parents[2]
  default_results_models_dir = repo_root / "results" / "models"
  default_output_dir = repo_root / "results" / "experiments" / "subpass_chart_refresh"

  parser = argparse.ArgumentParser(description="Recompute Q11/Q12/Q16 subpass charts from run_summary artifacts.")
  parser.add_argument("--results-models-dir",
                      default=default_results_models_dir,
                      type=Path,
                      help="Directory containing model run_summary.json files.")
  parser.add_argument("--output-dir",
                      default=default_output_dir,
                      type=Path,
                      help="Base output directory for refresh artifacts.")
  parser.add_argument("--publish-figures-dir",
                      default=None,
                      type=Path,
                      help="Optional directory to copy final paper figure assets.")
  parser.add_argument("--patch-appendix-tex",
                      default=None,
                      type=Path,
                      help="Optional path to patch appendix figure references and captions.")
  parser.add_argument("--strict",
                      action=argparse.BooleanOptionalAction,
                      default=True,
                      help="When true, enforce strict schema/range/count checks.")
  args = parser.parse_args()

  results_models_dir = args.results_models_dir.resolve()
  base_output_dir = args.output_dir.resolve()
  previous_latest_run = _find_previous_latest_run(base_output_dir)
  timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
  run_dir = base_output_dir / timestamp
  run_dir.mkdir(parents=True, exist_ok=False)

  run_summaries: dict[str, dict] = {}
  run_summary_metadata: list[dict] = []
  for model_run in CANONICAL_MODEL_RUNS:
    summary_path = results_models_dir / model_run / "run_summary.json"
    if not summary_path.exists():
      raise FileNotFoundError(f"Missing run_summary.json for model '{model_run}': {summary_path}")
    summary = _load_run_summary(summary_path)
    run_summaries[model_run] = summary
    run_summary_metadata.append({
      "model_run": model_run,
      "run_summary_path": str(summary_path.resolve()),
      "run_summary_sha256": _sha256_file(summary_path),
    })

  chart_paths: dict[int, Path] = {}
  aggregate_hashes: dict[int, str] = {}
  verification_lines = [
    "# Verification Report",
    "",
    f"- Generated at (UTC): {datetime.now(timezone.utc).isoformat()}",
    f"- Strict mode: {args.strict}",
    f"- Source models: {len(CANONICAL_MODEL_RUNS)}",
    "",
    "## Task-level checks",
    "",
  ]

  for task in TASK_SPECS:
    long_rows: list[dict] = []
    scores_by_subpass: dict[int, list[float]] = {subpass: [] for subpass in range(task.expected_subpasses)}

    for model_run in CANONICAL_MODEL_RUNS:
      scores = _extract_task_scores(run_summaries[model_run], task, model_run=model_run, strict=args.strict)
      for subpass, score in enumerate(scores):
        long_rows.append({
          "subpass": subpass,
          "model_run": model_run,
          "score": score,
        })
        scores_by_subpass[subpass].append(score)

    aggregate_rows: list[dict] = []
    for subpass in range(task.expected_subpasses):
      values = scores_by_subpass[subpass]
      if len(values) != len(CANONICAL_MODEL_RUNS):
        raise ValueError(
          f"Q{task.task_index} S{subpass}: expected {len(CANONICAL_MODEL_RUNS)} values, got {len(values)}")
      aggregate_row = {
        "subpass": subpass,
        "mean_score": float(mean(values)),
      }
      if task.include_median_overlay:
        aggregate_row["median_score"] = float(median(values))
      aggregate_rows.append(aggregate_row)

    long_csv_path = run_dir / f"q{task.task_index}_scores_long.csv"
    agg_csv_path = run_dir / f"q{task.task_index}_aggregates.csv"
    _write_long_csv(long_csv_path, task, long_rows)
    aggregate_hashes[task.task_index] = _write_aggregate_csv(agg_csv_path, task, aggregate_rows)

    chart_path = run_dir / task.chart_filename
    _render_chart(task, aggregate_rows, chart_path)
    chart_paths[task.task_index] = chart_path

    scores_only = [row["score"] for row in long_rows]
    expected_rows = task.expected_subpasses * len(CANONICAL_MODEL_RUNS)
    verification_lines.extend([
      f"### Q{task.task_index}",
      f"- Expected rows: {expected_rows}",
      f"- Actual rows: {len(long_rows)}",
      f"- Score min/max: {min(scores_only):.6f} / {max(scores_only):.6f}",
      f"- Subpass coverage: 0..{task.expected_subpasses - 1}",
      f"- Aggregate CSV hash: `{aggregate_hashes[task.task_index]}`",
      "",
    ])

  publish_mappings: list[dict] = []
  if args.publish_figures_dir is not None:
    publish_mappings = _copy_published_figures(chart_paths, args.publish_figures_dir.resolve())

  tex_patch_result = None
  if args.patch_appendix_tex is not None:
    tex_patch_result = _patch_appendix_tex(args.patch_appendix_tex.resolve(), strict=args.strict)

  determinism_result = {
    "previous_run_dir": str(previous_latest_run) if previous_latest_run else None,
    "checked": False,
    "same_inputs": False,
    "per_task": {},
  }

  previous_manifest = _load_previous_manifest(previous_latest_run) if previous_latest_run else None
  current_input_hashes = _build_input_hash_map(run_summary_metadata)
  previous_input_hashes = {}
  if previous_manifest:
    previous_input_hashes = {
      row.get("model_run"): row.get("run_summary_sha256")
      for row in previous_manifest.get("model_runs", [])
      if isinstance(row, dict)
    }

  verification_lines.extend(["## Determinism checks", ""])
  current_task_specs = [asdict(task) for task in TASK_SPECS]
  previous_task_specs = previous_manifest.get("tasks") if isinstance(previous_manifest, dict) else None
  same_task_specs = previous_task_specs == current_task_specs

  if previous_manifest and previous_input_hashes == current_input_hashes and same_task_specs:
    determinism_result["checked"] = True
    determinism_result["same_inputs"] = True
    previous_hashes = previous_manifest.get("aggregate_hashes", {})
    for task in TASK_SPECS:
      key = f"q{task.task_index}"
      current_hash = aggregate_hashes[task.task_index]
      previous_hash = previous_hashes.get(key)
      match = previous_hash == current_hash
      determinism_result["per_task"][key] = {
        "current_hash": current_hash,
        "previous_hash": previous_hash,
        "match": match,
      }
      verification_lines.append(
        f"- Q{task.task_index}: current={current_hash}, previous={previous_hash}, match={match}")
      if args.strict and not match:
        raise ValueError(f"Determinism check failed for Q{task.task_index}: aggregate hash changed for same inputs")
  else:
    if previous_manifest and previous_input_hashes == current_input_hashes and not same_task_specs:
      verification_lines.append("- Skipped (inputs identical, but task/chart spec changed since previous run).")
    else:
      verification_lines.append("- Skipped (no previous comparable run with identical input hashes).")
  verification_lines.append("")

  if publish_mappings:
    verification_lines.extend(["## Publish mappings", ""])
    for mapping in publish_mappings:
      verification_lines.append(f"- Q{mapping['task_index']}: `{mapping['target_name']}`")
    verification_lines.append("")

  if tex_patch_result:
    verification_lines.extend([
      "## TeX patch",
      "",
      f"- Target file: `{tex_patch_result['tex_path']}`",
      f"- Replacements applied in this run: {tex_patch_result['replacements_applied']}",
      "",
    ])

  verification_report_path = run_dir / "verification_report.md"
  verification_report_path.write_text("\n".join(verification_lines), encoding="utf-8")

  manifest = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "script_module": "experiments.subpass_chart_refresh.refresh_subpass_charts",
    "script_path": str(Path(__file__).resolve()),
    "script_sha256": _sha256_file(Path(__file__).resolve()),
    "git_commit": _git_commit(repo_root),
    "strict": args.strict,
    "results_models_dir": str(results_models_dir),
    "model_runs": run_summary_metadata,
    "tasks": [asdict(task) for task in TASK_SPECS],
    "aggregate_hashes": {
      f"q{task_index}": value
      for task_index, value in sorted(aggregate_hashes.items())
    },
    "determinism_check": determinism_result,
    "publish_mappings": publish_mappings,
    "tex_patch_result": tex_patch_result,
    "output_run_dir": str(run_dir),
  }
  manifest_path = run_dir / "calculation_manifest.json"
  manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

  _update_latest_pointer(base_output_dir, run_dir)

  print("Subpass chart refresh complete.")
  print(f"  run_dir: {run_dir}")
  print(f"  verification_report: {verification_report_path}")
  print(f"  calculation_manifest: {manifest_path}")
  for task in TASK_SPECS:
    print(f"  chart_q{task.task_index}: {chart_paths[task.task_index]}")
  if publish_mappings:
    print(f"  published_figures_dir: {Path(publish_mappings[0]['target']).parent}")
  if tex_patch_result:
    print(f"  patched_tex: {tex_patch_result['tex_path']}")


if __name__ == "__main__":
  main()
