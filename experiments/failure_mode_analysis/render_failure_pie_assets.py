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


if __name__ == "__main__":
  main()
