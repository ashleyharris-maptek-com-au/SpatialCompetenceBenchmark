from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from .schemas import (FAILURE_MODE_EVASION, FAILURE_MODE_LOCAL_ONLY, FAILURE_MODE_NEAR_MISS,
                      FAILURE_MODE_RUNAWAY, FAILURE_MODE_TRIVIALIZED, FAILURE_MODES, JUDGE_STATUS_OK)

FAILURE_MODE_INFRA = "Infrastructure / Engine Failure"

_SHORT_LABELS = {
  FAILURE_MODE_EVASION: "Evasion",
  FAILURE_MODE_TRIVIALIZED: "Trivialized",
  FAILURE_MODE_RUNAWAY: "Overthinking",
  FAILURE_MODE_LOCAL_ONLY: "Local-Only",
  FAILURE_MODE_NEAR_MISS: "Near-Miss",
  FAILURE_MODE_INFRA: "Infra/Engine",
}

_PALETTE = {
  FAILURE_MODE_EVASION: "#4E79A7",
  FAILURE_MODE_TRIVIALIZED: "#F28E2B",
  FAILURE_MODE_RUNAWAY: "#E15759",
  FAILURE_MODE_LOCAL_ONLY: "#76B7B2",
  FAILURE_MODE_NEAR_MISS: "#59A14F",
  FAILURE_MODE_INFRA: "#9C755F",
}

_VISUAL_MODES = FAILURE_MODES + (FAILURE_MODE_INFRA,)


def _is_infra_failure_row(row: dict) -> bool:
  raw_text = str(row.get("raw_text") or "")
  cot_text = str(row.get("cot_text") or "")
  return "Forced failure" in raw_text or "Forced failure" in cot_text


def _load_mode_counts(jsonl_path: Path) -> dict[str, int]:
  counts = {mode: 0 for mode in _VISUAL_MODES}
  with jsonl_path.open("r", encoding="utf-8") as f:
    for line in f:
      if not line.strip():
        continue
      row = json.loads(line)
      if row.get("judge_status") != JUDGE_STATUS_OK:
        continue
      if _is_infra_failure_row(row):
        counts[FAILURE_MODE_INFRA] += 1
        continue
      mode = row.get("failure_mode")
      if mode in counts:
        counts[mode] += 1
  return counts


def _plot_pie_no_legend(mode_counts: dict[str, int], output_path: Path) -> None:
  non_zero = [(mode, mode_counts[mode]) for mode in _VISUAL_MODES if mode_counts[mode] > 0]
  output_path.parent.mkdir(parents=True, exist_ok=True)

  if not non_zero:
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.text(0.5, 0.5, "No judged rows", ha="center", va="center", fontsize=14)
    ax.set_axis_off()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return

  modes, counts = zip(*non_zero)
  colors = [_PALETTE[mode] for mode in modes]
  total = int(sum(counts))

  fig, ax = plt.subplots(figsize=(4.8, 4.2))
  wedges, _ = ax.pie(counts,
                     startangle=90,
                     counterclock=False,
                     colors=colors,
                     wedgeprops={"linewidth": 2.5, "edgecolor": "white", "width": 0.42},
                     radius=1.0)

  import math
  for wedge, count in zip(wedges, counts):
    pct = count * 100.0 / total
    if pct < 4:
      continue
    angle = math.radians((wedge.theta1 + wedge.theta2) / 2.0)
    label_r = 1.0 - 0.42 / 2.0
    ax.text(label_r * math.cos(angle),
            label_r * math.sin(angle),
            f"{pct:.0f}%",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="semibold",
            color="white")

  ax.text(0, 0.02, f"{total}", ha="center", va="center", fontsize=20, fontweight="bold", color="#333")
  ax.text(0, -0.13, "judged", ha="center", va="center", fontsize=9, color="#777")
  ax.axis("equal")
  fig.savefig(output_path, dpi=200, bbox_inches="tight")
  plt.close(fig)


def _render_stacked_bar(
    labeled_counts: list[tuple[str, dict[str, int]]], output_path: Path
) -> None:
  """Render a 100% stacked horizontal bar chart for failure-mode distributions.

  Parameters
  ----------
  labeled_counts : list of (display_label, mode_counts) tuples, one per bar.
  output_path : where to save the PNG.
  """
  import numpy as np

  n_bars = len(labeled_counts)
  labels = [lbl for lbl, _ in labeled_counts]
  totals = [sum(mc.values()) for _, mc in labeled_counts]

  # Convert counts to percentages per bar.
  pct_data = {}  # mode -> list of pct values per bar
  for mode in _VISUAL_MODES:
    pct_data[mode] = []
    for _, mc in labeled_counts:
      total = sum(mc.values())
      pct_data[mode].append(mc.get(mode, 0) / total * 100 if total > 0 else 0)

  # Use only the 5 core failure modes (exclude Infra/Engine).
  bar_modes = FAILURE_MODES

  fig, ax = plt.subplots(figsize=(5.5, max(2.4, n_bars * 0.48 + 0.9)))
  y = np.arange(n_bars)
  bar_height = 0.55

  lefts = np.zeros(n_bars)
  for mode in bar_modes:
    widths = np.array(pct_data[mode])
    ax.barh(y, widths, bar_height, left=lefts,
            color=_PALETTE[mode], edgecolor="white", linewidth=0.5, zorder=2)
    # Label segments >= 8%.
    for i, (w, l) in enumerate(zip(widths, lefts)):
      if w >= 8:
        ax.text(l + w / 2, i, f"{w:.0f}%",
                ha="center", va="center", fontsize=7,
                fontweight="medium", color="white")
    lefts += widths

  # N-judged at bar end.
  for i, total in enumerate(totals):
    ax.text(101.5, i, f"n={total}", ha="left", va="center",
            fontsize=7, color="#555555")

  ax.set_yticks(y)
  ax.set_yticklabels(labels, fontsize=8, color="#2B2B2B")
  ax.invert_yaxis()
  ax.set_xlim(0, 115)
  ax.set_xlabel("Failure-mode share (%)", fontsize=8, color="#2B2B2B", labelpad=6)
  ax.tick_params(axis="x", labelsize=7)
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.spines["left"].set_linewidth(0.6)
  ax.spines["bottom"].set_linewidth(0.6)
  ax.tick_params(axis="both", which="both", length=3, width=0.6)
  ax.set_axisbelow(True)

  # Legend.
  legend_handles = [
    Patch(facecolor=_PALETTE[mode], edgecolor="none", label=_SHORT_LABELS[mode])
    for mode in bar_modes
  ]
  ax.legend(handles=legend_handles, loc="upper center",
            bbox_to_anchor=(0.45, -0.18), ncol=5, frameon=False,
            fontsize=7, handlelength=1.0, handletextpad=0.3, columnspacing=0.8)

  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
  plt.close(fig)


def _plot_standalone_legend(output_path: Path) -> None:
  handles = [
    Patch(facecolor=_PALETTE[mode], edgecolor="none", label=_SHORT_LABELS[mode])
    for mode in _VISUAL_MODES
  ]
  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig, ax = plt.subplots(figsize=(9.2, 0.9))
  ax.axis("off")
  ax.legend(handles=handles,
            loc="center",
            ncol=6,
            frameon=False,
            fontsize=9,
            handlelength=1.3,
            handletextpad=0.4,
            columnspacing=1.2)
  fig.savefig(output_path, dpi=200, bbox_inches="tight", transparent=True)
  plt.close(fig)


def main() -> None:
  parser = argparse.ArgumentParser(description="Render failure-mode pie charts without legends plus standalone legend.")
  parser.add_argument("--claude-jsonl", required=True, type=Path)
  parser.add_argument("--gemini-jsonl", required=True, type=Path)
  parser.add_argument("--gpt-jsonl", required=False, type=Path)
  parser.add_argument("--claude-tools-jsonl", required=False, type=Path)
  parser.add_argument("--gemini-tools-jsonl", required=False, type=Path)
  parser.add_argument("--gpt-tools-jsonl", required=False, type=Path)
  parser.add_argument("--out-dir", required=True, type=Path)
  args = parser.parse_args()

  claude_counts = _load_mode_counts(args.claude_jsonl)
  gemini_counts = _load_mode_counts(args.gemini_jsonl)
  gpt_counts = _load_mode_counts(args.gpt_jsonl) if args.gpt_jsonl else None

  _plot_pie_no_legend(claude_counts, args.out_dir / "failure_mode_distribution_pie_claude.png")
  _plot_pie_no_legend(gemini_counts, args.out_dir / "failure_mode_distribution_pie_gemini.png")
  if gpt_counts is not None:
    _plot_pie_no_legend(gpt_counts, args.out_dir / "failure_mode_distribution_pie_gpt52.png")
  _plot_standalone_legend(args.out_dir / "failure_mode_distribution_legend.png")

  # Stacked bar chart (requires all 6 JSONL files).
  claude_tools = _load_mode_counts(args.claude_tools_jsonl) if args.claude_tools_jsonl else None
  gemini_tools = _load_mode_counts(args.gemini_tools_jsonl) if args.gemini_tools_jsonl else None
  gpt_tools = _load_mode_counts(args.gpt_tools_jsonl) if args.gpt_tools_jsonl else None

  bar_rows: list[tuple[str, dict[str, int]]] = []
  if gpt_counts is not None:
    bar_rows.append(("GPT-5.2 (No tools)", gpt_counts))
  if gpt_tools is not None:
    bar_rows.append(("GPT-5.2 (Tools)", gpt_tools))
  bar_rows.append(("Gemini 3 Pro (No tools)", gemini_counts))
  if gemini_tools is not None:
    bar_rows.append(("Gemini 3 Pro (Tools)", gemini_tools))
  bar_rows.append(("Claude Sonnet 4.5 (No tools)", claude_counts))
  if claude_tools is not None:
    bar_rows.append(("Claude Sonnet 4.5 (Tools)", claude_tools))

  if len(bar_rows) >= 4:
    _render_stacked_bar(bar_rows, args.out_dir / "failure_mode_stacked_bar.png")


if __name__ == "__main__":
  main()
