import csv
import math
from pathlib import Path
from statistics import mean
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .constants import RESULTS_DIR
from .io import iter_subpasses, load_run_summary, model_run_summary_path, safe_float



def _parse_budget_from_model_name(model_name: str) -> int | None:
  marker = "-B"
  informed = "-informed"
  if marker not in model_name or informed not in model_name:
    return None
  try:
    start = model_name.index(marker) + len(marker)
    end = model_name.index(informed, start)
    return int(model_name[start:end])
  except Exception:
    return None


def _resolve_budget(config: dict, summary: dict) -> int | None:
  budget = config.get("max_output_tokens")
  if budget is None:
    budget = (summary.get("run_context") or {}).get("max_output_tokens")
  if budget is None:
    budget = _parse_budget_from_model_name(config["name"])
  return int(budget) if budget is not None else None


def _load_model_runs(model_configs: Iterable[dict]) -> list[dict]:
  runs: list[dict] = []
  for config in model_configs:
    model_name = config["name"]
    summary_path = model_run_summary_path(model_name)
    if not summary_path.exists():
      print(f"Skipping missing run summary: {summary_path}")
      continue
    summary = load_run_summary(model_name)
    runs.append({
      "model_name": model_name,
      "budget": _resolve_budget(config, summary),
      "summary": summary,
    })
  return runs


def compute_metrics(model_configs: Iterable[dict]) -> list[dict]:
  metrics: list[dict] = []
  model_runs = _load_model_runs(model_configs)

  for run in model_runs:
    model_name = run["model_name"]
    summary = run["summary"]
    budget_value = run["budget"]

    overall = summary.get("overall", {})
    total_score = safe_float(overall.get("total_score")) or 0.0
    max_score = safe_float(overall.get("max_score")) or 0.0
    accuracy = (total_score / max_score) if max_score > 0 else 0.0

    # Collect output token values for mean calculation (not stored in summary).
    output_tokens = []
    for subpass in iter_subpasses(summary):
      meta = subpass.get("meta")
      usage = subpass.get("usage") or (meta.get("usage") if isinstance(meta, dict) else None)
      if isinstance(usage, dict):
        token_value = safe_float(usage.get("output_tokens"))
        if token_value is not None:
          output_tokens.append(token_value)

    mean_output_tokens = mean(output_tokens) if output_tokens else None
    subpass_total = int(max_score)

    # Read diagnostics computed at sweep time from run_summary.
    diag = summary.get("diagnostics", {})

    def _diag_int(key: str) -> int:
      return int(safe_float(diag.get(key)) or 0)

    def _diag_rate(key: str) -> float:
      val = safe_float(diag.get(key))
      return val if val is not None else 0.0

    metrics.append({
      "model_name": model_name,
      "budget": budget_value,
      "accuracy": accuracy,
      "invalid_rate": 1.0 - accuracy,
      "mean_output_tokens": mean_output_tokens,
      "total_score": total_score,
      "total_subpasses": subpass_total,
      "token_observations": len(output_tokens),
      "empty_output_count": _diag_int("empty_output_count"),
      "empty_output_rate": _diag_rate("empty_output_rate"),
      "api_error_count": _diag_int("api_error_count"),
      "api_error_rate": _diag_rate("api_error_rate"),
      "non_completed_count": _diag_int("non_completed_count"),
      "non_completed_rate": _diag_rate("non_completed_rate"),
      "incomplete_response_count": _diag_int("incomplete_response_count"),
      "incomplete_response_rate": _diag_rate("incomplete_response_rate"),
      "budget_cap_hit_count": _diag_int("budget_cap_hit_count"),
      "budget_cap_hit_rate": _diag_rate("budget_cap_hit_rate"),
      "reasoning_equals_output_count": _diag_int("reasoning_equals_output_count"),
      "reasoning_equals_output_rate": _diag_rate("reasoning_equals_output_rate"),
      "missing_meta_count": _diag_int("missing_meta_count"),
      "missing_meta_rate": _diag_rate("missing_meta_rate"),
    })

  metrics.sort(key=lambda m: (m["budget"] if m["budget"] is not None else math.inf, m["model_name"]))
  return metrics


def _write_metrics_csv(metrics: list[dict], output_dir: Path) -> Path:
  path = output_dir / "metrics.csv"
  output_dir.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
      f,
      fieldnames=[
        "model_name",
        "budget",
        "accuracy",
        "invalid_rate",
        "mean_output_tokens",
        "total_score",
        "total_subpasses",
        "token_observations",
        "empty_output_count",
        "empty_output_rate",
        "api_error_count",
        "api_error_rate",
        "non_completed_count",
        "non_completed_rate",
        "incomplete_response_count",
        "incomplete_response_rate",
        "budget_cap_hit_count",
        "budget_cap_hit_rate",
        "reasoning_equals_output_count",
        "reasoning_equals_output_rate",
        "missing_meta_count",
        "missing_meta_rate",
      ],
    )
    writer.writeheader()
    for row in metrics:
      writer.writerow(row)
  return path


def _plot_metric(metrics: list[dict], *, y_key: str, y_label: str,
                 output_path: Path) -> None:
  _LINE_COLOR = "#4E79A7"
  _MARKER_COLOR = "#4E79A7"
  _LABEL_COLOR = "#333333"

  x_vals = []
  y_vals = []
  labels = []

  for row in metrics:
    x = row.get("mean_output_tokens")
    y = row.get(y_key)
    if x is None or y is None:
      continue
    x_vals.append(float(x))
    y_vals.append(float(y))
    labels.append(f"B={row.get('budget')}")

  fig, ax = plt.subplots(figsize=(6, 5))
  if x_vals:
    ax.plot(x_vals, y_vals, marker="o", markersize=8, linestyle="-", linewidth=2,
            color=_LINE_COLOR, markerfacecolor=_MARKER_COLOR, markeredgecolor="white", markeredgewidth=1.5)
    fig.canvas.draw()
    tr = ax.transData
    placed_screen: list[tuple[float, float]] = []
    for x, y, label in zip(x_vals, y_vals, labels):
      sx, sy = tr.transform((x, y))
      ox, oy = 0, 14
      target_sx, target_sy = sx + ox, sy + oy
      for psx, psy in placed_screen:
        if abs(target_sx - psx) < 55 and abs(target_sy - psy) < 18:
          oy = -16
          target_sy = sy + oy
          break
      placed_screen.append((target_sx, target_sy))
      va = "bottom" if oy > 0 else "top"
      ax.annotate(label, (x, y), textcoords="offset points", xytext=(ox, oy),
                  fontsize=9, fontweight="bold", color=_LABEL_COLOR, ha="center", va=va)

  ax.set_xlabel("Mean Realized Output Tokens", fontsize=10, labelpad=8)
  ax.set_ylabel(y_label, fontsize=10, labelpad=8)
  ax.grid(True, alpha=0.15, linewidth=0.8)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.tick_params(labelsize=9)
  if y_vals:
    y_lo, y_hi = min(y_vals), max(y_vals)
    margin = (y_hi - y_lo) * 0.12 or 0.05
    ax.set_ylim(y_lo - margin, y_hi + margin)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(output_path, dpi=150, bbox_inches="tight")
  plt.close(fig)


def _model_series(model_name: str) -> tuple[str, str] | None:
  if model_name.startswith("gpt-5.2"):
    return "GPT-5.2", "#4D9A67"
  if model_name.startswith("claude-sonnet-4-5"):
    return "Claude Sonnet 4.5", "#E39435"
  return None


def _plot_accuracy_two_model_lines(metrics: list[dict], output_path: Path) -> None:
  series: dict[str, dict] = {}
  for row in metrics:
    model_name = row.get("model_name") or ""
    resolved = _model_series(model_name)
    if resolved is None:
      continue
    label, color = resolved
    x = row.get("mean_output_tokens")
    y = row.get("accuracy")
    if x is None or y is None:
      continue
    if label not in series:
      series[label] = {"x": [], "y": [], "color": color}
    series[label]["x"].append(float(x))
    series[label]["y"].append(float(y))

  fig, ax = plt.subplots(figsize=(6.3, 4.8))
  for label, payload in series.items():
    points = sorted(zip(payload["x"], payload["y"]), key=lambda item: item[0])
    xs = [item[0] for item in points]
    ys = [item[1] for item in points]
    ax.plot(xs, ys, marker="o", markersize=7, linewidth=2, label=label, color=payload["color"])

  ax.set_xlabel("Mean Realized Output Tokens", fontsize=10, labelpad=8)
  ax.set_ylabel("Accuracy", fontsize=10, labelpad=8)
  ax.grid(True, alpha=0.15, linewidth=0.8)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.tick_params(labelsize=9)
  ax.legend(frameon=False, fontsize=9)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(output_path, dpi=150, bbox_inches="tight")
  plt.close(fig)


def _write_summary_md(metrics: list[dict], output_dir: Path) -> Path:
  path = output_dir / "summary.md"
  lines = [
    "# Axiomatic Budget Sweep Summary",
    "",
    "Accuracy and invalid-rate are reported against mean realized output tokens.",
    "Invalid-rate is defined as `1 - accuracy`.",
    "Anthropic runs do not expose reasoning-token counts in usage metadata; this field is recorded as NA.",
    "",
    "| Budget | Accuracy | Invalid Rate | Mean Output Tokens | Cap-Hit Rate | Empty Rate | API Error Rate | Token Obs |",
    "|---:|---:|---:|---:|---:|---:|---:|---:|",
  ]

  for row in metrics:
    budget = row.get("budget")
    acc = row.get("accuracy")
    inv = row.get("invalid_rate")
    mean_tok = row.get("mean_output_tokens")
    cap_hit = row.get("budget_cap_hit_rate")
    empty_rate = row.get("empty_output_rate")
    api_error_rate = row.get("api_error_rate")
    tok_obs = row.get("token_observations")
    lines.append(
      f"| {budget} | {acc:.4f} | {inv:.4f} | {mean_tok if mean_tok is not None else 'NA'} | "
      f"{cap_hit:.4f} | {empty_rate:.4f} | {api_error_rate:.4f} | {tok_obs} |"
    )

  output_dir.mkdir(parents=True, exist_ok=True)
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")
  return path


def analyze_budget_sweep(model_configs: Iterable[dict], output_dir: Path = RESULTS_DIR) -> dict[str, Path]:
  metrics = compute_metrics(model_configs)
  if not metrics:
    raise ValueError("No run summaries found for the requested model configs.")

  metrics_csv = _write_metrics_csv(metrics, output_dir)
  acc_plot = output_dir / "pareto_accuracy_vs_tokens.png"
  invalid_plot = output_dir / "pareto_invalid_vs_tokens.png"
  _plot_metric(metrics,
               y_key="accuracy",
               y_label="Accuracy",
               output_path=acc_plot)
  _plot_metric(metrics,
               y_key="invalid_rate",
               y_label="Invalid Rate (1 - Accuracy)",
               output_path=invalid_plot)
  model_line_plot = output_dir / "accuracy_two_model_lines.png"
  _plot_accuracy_two_model_lines(metrics, model_line_plot)
  summary_md = _write_summary_md(metrics, output_dir)

  return {
    "metrics_csv": metrics_csv,
    "accuracy_plot": acc_plot,
    "invalid_plot": invalid_plot,
    "accuracy_two_model_lines_plot": model_line_plot,
    "summary_md": summary_md,
  }
