from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .schemas import (AnalysisConfig, EvidenceRow, FAILURE_MODE_EVASION, FAILURE_MODE_LOCAL_ONLY,
                      FAILURE_MODE_NEAR_MISS, FAILURE_MODE_RUNAWAY, FAILURE_MODE_TRIVIALIZED,
                      FAILURE_MODES, JudgeDecision, JUDGE_STATUS_ERROR,
                      JUDGE_STATUS_NOT_SELECTED, JUDGE_STATUS_OK, LabeledRow)


def _safe_float(value):
  try:
    if value is None:
      return None
    return float(value)
  except Exception:
    return None


def _strip_html(value: str | None) -> str:
  if not value:
    return ""
  return re.sub(r"<[^>]+>", " ", value).strip()


def _read_optional_text(path: Path) -> str | None:
  if not path.exists():
    return None
  try:
    return path.read_text(encoding="utf-8")
  except Exception:
    return None


_IMAGE_TAG_RE = re.compile(r'<image[^>]*>.*?</image>', re.DOTALL)


def _strip_prompt_for_judge(text: str | None) -> str | None:
  if not text:
    return None
  cleaned = _IMAGE_TAG_RE.sub("[image omitted]", text).strip()
  if not cleaned:
    return None
  return cleaned


def is_candidate_for_judge(row: EvidenceRow, low_score_threshold: float) -> bool:
  if row.score <= 0:
    return True
  return row.score < low_score_threshold


def build_evidence_rows(model_runs: Iterable[dict],
                        results_models_dir: Path | str = Path("results/models")) -> list[EvidenceRow]:
  results_models_dir = Path(results_models_dir)
  rows: list[EvidenceRow] = []

  for run in model_runs:
    model_name = str(run["model_name"])
    summary = run["summary"]

    for test in summary.get("tests", []):
      test_index = int(test.get("test_index", -1))
      test_title = str(test.get("title") or f"Test {test_index}")
      for subpass in test.get("subpasses", []):
        subpass_idx = int(subpass.get("subpass", 0))

        prompt_path = results_models_dir / model_name / "prompts" / f"{model_name}_{test_index}_{subpass_idx}.txt"
        raw_path = results_models_dir / model_name / "raw" / f"{model_name}_{test_index}_{subpass_idx}.txt"
        cot_path = results_models_dir / model_name / "cot" / f"{model_name}_{test_index}_{subpass_idx}.txt"
        raw_text = _read_optional_text(raw_path)
        cot_text = _read_optional_text(cot_path)

        score_raw = _safe_float(subpass.get("score"))
        score = score_raw if score_raw is not None else 0.0
        score_explanation = _strip_html(str(subpass.get("scoreExplanation") or ""))

        meta = subpass.get("meta")
        if not isinstance(meta, dict):
          meta = {}
        usage = subpass.get("usage")
        if not isinstance(usage, dict):
          usage = {}
        if not usage and isinstance(meta.get("usage"), dict):
          usage = meta["usage"]

        output_tokens = _safe_float(usage.get("output_tokens")) if usage else None
        status = str(meta.get("status")).strip() if meta.get("status") is not None else None
        incomplete_reason = str(meta.get("incomplete_reason")).strip() if meta.get(
          "incomplete_reason") is not None else None
        if meta.get("output_text_chars") is not None:
          output_text_chars = int(meta.get("output_text_chars") or 0)
        else:
          output_text_chars = len(raw_text) if raw_text is not None else 0

        rows.append(
          EvidenceRow(model_name=model_name,
                      test_index=test_index,
                      test_title=test_title,
                      subpass=subpass_idx,
                      score=score,
                      status=status,
                      incomplete_reason=incomplete_reason,
                      output_tokens=output_tokens,
                      output_text_chars=output_text_chars,
                      score_explanation=score_explanation,
                      raw_path=str(raw_path) if raw_text is not None else None,
                      cot_path=str(cot_path) if cot_text is not None else None,
                      prompt_path=str(prompt_path) if prompt_path.exists() else None,
                      raw_text=raw_text,
                      cot_text=cot_text,
                      prompt_text=_strip_prompt_for_judge(_read_optional_text(prompt_path))))

  rows.sort(key=lambda row: (row.model_name, row.test_index, row.subpass))
  return rows


def select_candidate_rows(rows: list[EvidenceRow], low_score_threshold: float) -> list[EvidenceRow]:
  return [row for row in rows if is_candidate_for_judge(row, low_score_threshold)]


def _build_labeled_row(row: EvidenceRow,
                       candidate_for_judge: bool,
                       judge_status: str,
                       judge_model: str,
                       judge_engine: str,
                       prompt_version: str,
                       failure_mode: str | None = None,
                       confidence: float | None = None,
                       justification: str | None = None,
                       evidence_tags: list[str] | None = None,
                       judge_error: str | None = None) -> LabeledRow:
  return LabeledRow(model_name=row.model_name,
                    test_index=row.test_index,
                    test_title=row.test_title,
                    subpass=row.subpass,
                    score=row.score,
                    status=row.status,
                    incomplete_reason=row.incomplete_reason,
                    output_tokens=row.output_tokens,
                    output_text_chars=row.output_text_chars,
                    score_explanation=row.score_explanation,
                    raw_path=row.raw_path,
                    cot_path=row.cot_path,
                    prompt_path=row.prompt_path,
                    raw_text=row.raw_text,
                    cot_text=row.cot_text,
                    prompt_text=row.prompt_text,
                    candidate_for_judge=candidate_for_judge,
                    judge_status=judge_status,
                    failure_mode=failure_mode,
                    confidence=confidence,
                    justification=justification,
                    evidence_tags=evidence_tags or [],
                    judge_error=judge_error,
                    judge_model=judge_model,
                    judge_engine=judge_engine,
                    prompt_version=prompt_version)


def merge_decisions(rows: list[EvidenceRow], decisions: dict, config: AnalysisConfig) -> list[LabeledRow]:
  labeled: list[LabeledRow] = []
  for row in rows:
    candidate = is_candidate_for_judge(row, config.low_score_threshold)

    if not candidate:
      labeled.append(
        _build_labeled_row(row,
                           candidate_for_judge=False,
                           judge_status=JUDGE_STATUS_NOT_SELECTED,
                           judge_model=config.judge_model,
                           judge_engine=config.judge_engine,
                           prompt_version=config.prompt_version))
      continue

    decision: JudgeDecision | None = decisions.get(row.key)
    if decision is None:
      decision = JudgeDecision(key=row.key,
                               judge_status=JUDGE_STATUS_ERROR,
                               failure_mode=None,
                               confidence=None,
                               justification=None,
                               evidence_tags=[],
                               judge_error="missing_judge_decision",
                               judge_model=config.judge_model,
                               judge_engine=config.judge_engine,
                               prompt_version=config.prompt_version)

    labeled.append(
      _build_labeled_row(row,
                         candidate_for_judge=True,
                         judge_status=decision.judge_status,
                         judge_model=decision.judge_model,
                         judge_engine=decision.judge_engine,
                         prompt_version=decision.prompt_version,
                         failure_mode=decision.failure_mode,
                         confidence=decision.confidence,
                         justification=decision.justification,
                         evidence_tags=decision.evidence_tags,
                         judge_error=decision.judge_error))

  labeled.sort(key=lambda row: (row.model_name, row.test_index, row.subpass))
  return labeled


def write_failure_modes_jsonl(rows: list[LabeledRow], output_dir: Path) -> Path:
  path = output_dir / "failure_modes.jsonl"
  with path.open("w", encoding="utf-8") as f:
    for row in rows:
      f.write(json.dumps(asdict(row), ensure_ascii=True) + "\n")
  return path


def write_failure_mode_task_csv(rows: list[LabeledRow], output_dir: Path) -> Path:
  path = output_dir / "failure_mode_by_task.csv"

  grouped: dict[tuple[str, int, str], dict] = {}
  for row in rows:
    key = (row.model_name, row.test_index, row.test_title)
    if key not in grouped:
      grouped[key] = {
        "model_name": row.model_name,
        "test_index": row.test_index,
        "test_title": row.test_title,
        "subpasses_total": 0,
        "candidates": 0,
        "judged": 0,
        "judge_errors": 0,
      }
      for mode in FAILURE_MODES:
        grouped[key][f"{mode}__count"] = 0

    grouped[key]["subpasses_total"] += 1
    if row.candidate_for_judge:
      grouped[key]["candidates"] += 1
    if row.judge_status == JUDGE_STATUS_OK:
      grouped[key]["judged"] += 1
      if row.failure_mode in FAILURE_MODES:
        grouped[key][f"{row.failure_mode}__count"] += 1
    elif row.judge_status == JUDGE_STATUS_ERROR:
      grouped[key]["judge_errors"] += 1

  output_rows = []
  for _, group in sorted(grouped.items(), key=lambda item: (
      item[1]["model_name"],
      item[1]["test_index"],
  )):
    candidates = int(group["candidates"])
    judged = int(group["judged"])
    out = dict(group)
    out["candidate_rate"] = (candidates / group["subpasses_total"]) if group["subpasses_total"] > 0 else 0.0
    out["judge_coverage_rate"] = (judged / candidates) if candidates > 0 else 0.0
    output_rows.append(out)

  fieldnames = [
    "model_name",
    "test_index",
    "test_title",
    "subpasses_total",
    "candidates",
    "judged",
    "judge_errors",
    "candidate_rate",
    "judge_coverage_rate",
  ]
  for mode in FAILURE_MODES:
    fieldnames.append(f"{mode}__count")

  with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in output_rows:
      writer.writerow(row)

  return path


def write_failure_mode_analysis_md(rows: list[LabeledRow], output_dir: Path) -> Path:
  path = output_dir / "failure_mode_analysis.md"

  candidates = [row for row in rows if row.candidate_for_judge]
  judged = [row for row in candidates if row.judge_status == JUDGE_STATUS_OK and row.failure_mode in FAILURE_MODES]
  judge_errors = [row for row in candidates if row.judge_status == JUDGE_STATUS_ERROR]

  mode_counts = {mode: 0 for mode in FAILURE_MODES}
  for row in judged:
    mode_counts[row.failure_mode] += 1

  task_counts: dict[tuple[int, str], dict[str, int]] = {}
  for row in candidates:
    key = (row.test_index, row.test_title)
    if key not in task_counts:
      task_counts[key] = {"candidates": 0, "judged": 0, "judge_errors": 0}
    task_counts[key]["candidates"] += 1
    if row.judge_status == JUDGE_STATUS_OK:
      task_counts[key]["judged"] += 1
    elif row.judge_status == JUDGE_STATUS_ERROR:
      task_counts[key]["judge_errors"] += 1

  def _excerpt(text: str | None, limit: int = 220) -> str:
    if not text:
      return ""
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= limit else one_line[:limit - 3] + "..."

  lines = [
    "# Failure-Mode Analysis",
    "",
    f"- Total subpasses: {len(rows)}",
    f"- Candidate rows (failed + low-score pass): {len(candidates)}",
    f"- Judged rows: {len(judged)}",
    f"- Judge errors: {len(judge_errors)}",
    "",
    "## Mode Distribution (Judged Rows)",
    "",
    "| Mode | Count | Share |",
    "|---|---:|---:|",
  ]

  judged_total = len(judged)
  for mode in FAILURE_MODES:
    count = mode_counts[mode]
    share = (count / judged_total) if judged_total > 0 else 0.0
    lines.append(f"| {mode} | {count} | {share:.2%} |")

  lines.extend([
    "",
    "## Task Hotspots",
    "",
    "| Task | Candidates | Judged | Judge Errors | Coverage |",
    "|---|---:|---:|---:|---:|",
  ])

  sorted_tasks = sorted(
    task_counts.items(),
    key=lambda item: item[1]["candidates"],
    reverse=True,
  )
  for (test_index, test_title), counts in sorted_tasks[:15]:
    coverage = (counts["judged"] / counts["candidates"]) if counts["candidates"] > 0 else 0.0
    lines.append(
      f"| Q{test_index} - {test_title} | {counts['candidates']} | {counts['judged']} | {counts['judge_errors']} | {coverage:.2%} |"
    )

  lines.extend(["", "## Evidence Samples", ""])
  for mode in FAILURE_MODES:
    sample = next((row for row in judged if row.failure_mode == mode), None)
    if sample is None:
      continue
    lines.append(f"### {mode}")
    lines.append(f"- Task: Q{sample.test_index} - {sample.test_title} (subpass {sample.subpass})")
    lines.append(f"- Score: {sample.score}")
    lines.append(f"- Confidence: {sample.confidence}")
    lines.append(f"- Verifier signal: {_excerpt(sample.score_explanation) or '(none)'}")
    lines.append(f"- Judge justification: {_excerpt(sample.justification) or '(none)'}")
    lines.append("")

  if judge_errors:
    lines.extend(["## Judge Errors", ""])
    for row in judge_errors[:20]:
      lines.append(
        f"- Q{row.test_index} subpass {row.subpass}: {_excerpt(row.judge_error) or 'unknown_judge_error'}"
      )
    lines.append("")

  path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
  return path


def write_failure_mode_distribution_pie(rows: list[LabeledRow], output_dir: Path) -> Path:
  path = output_dir / "failure_mode_distribution_pie.png"

  judged = [row for row in rows if row.judge_status == JUDGE_STATUS_OK and row.failure_mode in FAILURE_MODES]
  mode_counts = {mode: 0 for mode in FAILURE_MODES}
  for row in judged:
    mode_counts[row.failure_mode] += 1

  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt

  _SHORT_LABELS = {
    FAILURE_MODE_EVASION: "Evasion",
    FAILURE_MODE_TRIVIALIZED: "Trivialized",
    FAILURE_MODE_RUNAWAY: "Overthinking",
    FAILURE_MODE_LOCAL_ONLY: "Local-Only",
    FAILURE_MODE_NEAR_MISS: "Near-Miss",
  }
  _PALETTE = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F"]

  counts = [mode_counts[mode] for mode in FAILURE_MODES]
  labels = [_SHORT_LABELS.get(mode, mode) for mode in FAILURE_MODES]

  non_zero = [(l, c, col) for l, c, col in zip(labels, counts, _PALETTE) if c > 0]
  if not non_zero:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.text(0.5, 0.5, "No judged rows", ha="center", va="center", fontsize=14)
    ax.set_axis_off()
  else:
    nz_labels, nz_counts, nz_colors = zip(*non_zero)
    total = sum(nz_counts)

    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, _ = ax.pie(nz_counts,
                        startangle=90,
                        counterclock=False,
                        colors=nz_colors,
                        wedgeprops={"linewidth": 2.5, "edgecolor": "white", "width": 0.42},
                        radius=1.0)

    import math
    for wedge, count in zip(wedges, nz_counts):
      angle = math.radians((wedge.theta2 + wedge.theta1) / 2)
      mid_r = 1.0 - 0.42 / 2
      pct = count * 100 / total
      ax.text(mid_r * math.cos(angle), mid_r * math.sin(angle),
              f"{pct:.0f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white")

    ax.text(0, 0, f"{total}", ha="center", va="center", fontsize=22, fontweight="bold", color="#333")
    ax.text(0, -0.12, "judged", ha="center", va="center", fontsize=9, color="#888")

    legend_labels = [f"{label}  ({count})"
                     for label, count in zip(nz_labels, nz_counts)]
    ax.legend(wedges, legend_labels, loc="upper center", bbox_to_anchor=(0.5, -0.02),
              fontsize=9, frameon=False, ncol=min(len(nz_labels), 3), title="Class Counts",
              title_fontproperties={"weight": "bold", "size": 10})

    ax.set_title("Failure Mode Distribution", fontsize=13, fontweight="bold", pad=14)
    ax.axis("equal")

  fig.savefig(path, dpi=150, bbox_inches="tight")
  plt.close(fig)
  return path
