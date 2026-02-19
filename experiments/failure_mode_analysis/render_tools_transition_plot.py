#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_PAPER_RC = {
  "font.family": "DejaVu Sans",
  "font.size": 10,
  "axes.titlesize": 11,
  "axes.labelsize": 10,
  "xtick.labelsize": 9,
  "ytick.labelsize": 9,
  "figure.facecolor": "white",
  "axes.facecolor": "white",
  "savefig.facecolor": "white",
  "axes.edgecolor": "#333333",
  "text.color": "#111111",
  "axes.labelcolor": "#111111",
  "xtick.color": "#111111",
  "ytick.color": "#111111",
}

FAILURE_MODE_EVASION = "Evasion / Forfeit"
FAILURE_MODE_TRIVIALIZED = "Trivialized / Misframed"
FAILURE_MODE_RUNAWAY = "Runaway Overthinking"
FAILURE_MODE_LOCAL_ONLY = "Local-Only (Global Constraint Integration Failure)"
FAILURE_MODE_NEAR_MISS = "Near-Miss Edge Case"

FAILURE_MODES = (
  FAILURE_MODE_EVASION,
  FAILURE_MODE_TRIVIALIZED,
  FAILURE_MODE_RUNAWAY,
  FAILURE_MODE_LOCAL_ONLY,
  FAILURE_MODE_NEAR_MISS,
)

STATE_PASS = "Pass"
STATE_ORDER = (
  STATE_PASS,
  FAILURE_MODE_EVASION,
  FAILURE_MODE_LOCAL_ONLY,
  FAILURE_MODE_NEAR_MISS,
  FAILURE_MODE_TRIVIALIZED,
  FAILURE_MODE_RUNAWAY,
)

SHORT_LABELS = {
  STATE_PASS: "Pass",
  FAILURE_MODE_EVASION: "Evasion",
  FAILURE_MODE_LOCAL_ONLY: "Local-Only",
  FAILURE_MODE_NEAR_MISS: "Near-Miss",
  FAILURE_MODE_TRIVIALIZED: "Trivialized",
  FAILURE_MODE_RUNAWAY: "Overthinking",
}

STATE_COLORS = {
  STATE_PASS: "#2E7D32",
  FAILURE_MODE_EVASION: "#4E79A7",
  FAILURE_MODE_TRIVIALIZED: "#F28E2B",
  FAILURE_MODE_RUNAWAY: "#E15759",
  FAILURE_MODE_LOCAL_ONLY: "#76B7B2",
  FAILURE_MODE_NEAR_MISS: "#59A14F",
}


def _load_rows(path: Path) -> list[dict]:
  rows: list[dict] = []
  with path.open("r", encoding="utf-8") as f:
    for line in f:
      if line.strip():
        rows.append(json.loads(line))
  return rows


def _state(row: dict) -> str | None:
  if row.get("candidate_for_judge"):
    if row.get("judge_status") == "ok":
      mode = row.get("failure_mode")
      if mode in FAILURE_MODES:
        return mode
    return None
  return STATE_PASS


def _count_states(rows: list[dict]) -> tuple[Counter, int]:
  counts = Counter()
  dropped = 0
  for row in rows:
    state = _state(row)
    if state is None:
      dropped += 1
      continue
    counts[state] += 1
  return counts, dropped


def _plot_deltas(no_tools_counts: Counter,
                 tools_counts: Counter,
                 *,
                 no_tools_total: int,
                 tools_total: int,
                 out_path: Path,
                 title: str,
                 footnote: str | None = None) -> np.ndarray:
  states = list(STATE_ORDER)
  no_tools_rates = np.array([no_tools_counts.get(state, 0) / no_tools_total for state in states])
  tools_rates = np.array([tools_counts.get(state, 0) / tools_total for state in states])
  deltas_pp = (tools_rates - no_tools_rates) * 100.0
  y = np.arange(len(states))
  colors = [STATE_COLORS[state] for state in states]

  plt.rcParams.update(_PAPER_RC)
  state_count = len(states)
  fig_w = 6.0
  fig_h = max(3.8, 0.72 * state_count + 0.9)
  fig, ax = plt.subplots(figsize=(fig_w, fig_h))
  ax.set_axisbelow(True)
  ax.grid(axis="x", color="#E6E6E6", linewidth=0.9, linestyle="-")
  ax.barh(y,
          deltas_pp,
          color=colors,
          alpha=0.95,
          height=0.56,
          edgecolor="white",
          linewidth=1.2)
  ax.axvline(0.0, color="#333333", linewidth=1.1)
  ax.set_yticks(y)
  ax.set_yticklabels([SHORT_LABELS[s] for s in states])
  ax.set_xlabel("Tools - No tools (percentage points)")
  ax.set_title(title, pad=10)
  ax.invert_yaxis()

  max_abs = float(np.max(np.abs(deltas_pp))) if deltas_pp.size else 1.0
  xlim = max(2.0, max_abs * 1.18)
  ax.set_xlim(-xlim, xlim)
  ax.tick_params(axis="y", pad=6)

  inside_threshold = max(1.8, 0.18 * xlim)
  for yi, value in enumerate(deltas_pp):
    abs_value = abs(value)
    label_text = f"{value:+.1f}"
    if abs_value >= inside_threshold:
      ax.text(value / 2.0,
              yi,
              label_text,
              va="center",
              ha="center",
              fontsize=9,
              color="white",
              fontweight="semibold")
    else:
      pad = 0.32
      x = value + (pad if value >= 0 else -pad)
      ha = "left" if value >= 0 else "right"
      ax.text(x,
              yi,
              label_text,
              va="center",
              ha=ha,
              fontsize=9,
              color="#111111",
              clip_on=False)

  for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
  ax.spines["left"].set_color("#444444")
  ax.spines["bottom"].set_color("#444444")

  if footnote:
    fig.text(0.01, 0.01, footnote, ha="left", va="bottom", fontsize=8.5, color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
  else:
    fig.tight_layout()
  out_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(out_path, dpi=220, bbox_inches="tight")
  plt.close(fig)
  return deltas_pp


def _write_summary_json(no_tools_counts: Counter,
                        tools_counts: Counter,
                        *,
                        no_tools_total: int,
                        tools_total: int,
                        no_tools_dropped: int,
                        tools_dropped: int,
                        deltas_pp: np.ndarray,
                        output_path: Path) -> None:
  states = list(STATE_ORDER)
  data = {
    "states": states,
    "no_tools_total_rows": no_tools_total,
    "tools_total_rows": tools_total,
    "no_tools_dropped_unlabeled_rows": no_tools_dropped,
    "tools_dropped_unlabeled_rows": tools_dropped,
    "no_tools_counts": dict(no_tools_counts),
    "tools_counts": dict(tools_counts),
    "deltas_pp": {
      state: float(delta) for state, delta in zip(states, deltas_pp)
    },
  }
  output_path.parent.mkdir(parents=True, exist_ok=True)
  with output_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Render state-rate deltas from no-tools and tools failure_modes.jsonl files.")
  parser.add_argument("--no-tools-jsonl", required=True, type=Path)
  parser.add_argument("--tools-jsonl", required=True, type=Path)
  parser.add_argument("--out", required=True, type=Path, help="PNG output path.")
  parser.add_argument("--summary-out",
                      default=None,
                      type=Path,
                      help="Optional JSON summary path. Defaults to <out>.json.")
  parser.add_argument("--title", default="State-rate deltas (Tools - No tools)")
  args = parser.parse_args()

  no_tools_rows = _load_rows(args.no_tools_jsonl)
  tools_rows = _load_rows(args.tools_jsonl)
  no_tools_counts, no_tools_dropped = _count_states(no_tools_rows)
  tools_counts, tools_dropped = _count_states(tools_rows)

  footnote = None
  if no_tools_dropped or tools_dropped:
    footnote = (
      f"Excluded unlabeled rows (judge errors / missing labels): no-tools={no_tools_dropped}, tools={tools_dropped}"
    )

  deltas_pp = _plot_deltas(no_tools_counts,
                           tools_counts,
                           no_tools_total=len(no_tools_rows),
                           tools_total=len(tools_rows),
                           out_path=args.out,
                           title=args.title,
                           footnote=footnote)

  summary_out = args.summary_out or args.out.with_suffix(".json")
  _write_summary_json(no_tools_counts,
                      tools_counts,
                      no_tools_total=len(no_tools_rows),
                      tools_total=len(tools_rows),
                      no_tools_dropped=no_tools_dropped,
                      tools_dropped=tools_dropped,
                      deltas_pp=deltas_pp,
                      output_path=summary_out)


if __name__ == "__main__":
  main()
