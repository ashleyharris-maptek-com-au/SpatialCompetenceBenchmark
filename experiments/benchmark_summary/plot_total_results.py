#!/usr/bin/env python3
"""Generate a grouped bar chart of benchmark scores per question across models."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Aesthetic constants (matching pie / Pareto charts) ---
_MODEL_COLORS = {
    "gpt-5.2-chat-azure-Reasoning": "#4E79A7",
    "gpt-5.1": "#F28E2B",
    "gpt-5.2-chat-azure-Reasoning-7": "#59A14F",
}
_MODEL_SHORT = {
    "gpt-5.2-chat-azure-Reasoning": "GPT-5.2 Reasoning",
    "gpt-5.1": "GPT-5.1",
    "gpt-5.2-chat-azure-Reasoning-7": "GPT-5.2 R-7",
}
_SKIP_MODELS = {"always-wrong"}


def _short_title(qid: str, title: str, max_len: int = 28) -> str:
    prefix = f"Q{qid} "
    remaining = max_len - len(prefix)
    if len(title) > remaining:
        title = title[:remaining - 1] + "\u2026"
    return prefix + title


def plot_benchmark_results(json_path: Path, output_path: Path) -> Path:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = [m for m in data if m not in _SKIP_MODELS]

    # Compute total score and total max per model (only questions with max > 0)
    model_totals: list[tuple[str, float, float]] = []
    for model in models:
        total_score = 0.0
        total_max = 0.0
        for qid, info in data[model].items():
            mx = info.get("max", 0)
            if mx > 0:
                score = min(info.get("score", 0), mx)
                total_score += score
                total_max += mx
        model_totals.append((model, total_score, total_max))

    # Sort by total score descending
    model_totals.sort(key=lambda t: t[1], reverse=True)

    labels = [_MODEL_SHORT.get(m, m) for m, _, _ in model_totals]
    scores = [s for _, s, _ in model_totals]
    maxes = [mx for _, _, mx in model_totals]
    colors = [_MODEL_COLORS.get(m, "#999999") for m, _, _ in model_totals]

    y = np.arange(len(labels))
    bar_height = 0.5

    fig, ax = plt.subplots(figsize=(10, max(2.5, len(labels) * 0.9 + 1)))

    # Max capacity bars (light grey background)
    ax.barh(y, maxes, bar_height, color="#E8E8E8", edgecolor="white", linewidth=0.5, label="Max possible")
    # Score bars
    ax.barh(y, scores, bar_height, color=colors, edgecolor="white", linewidth=0.5)

    # Score labels on bars
    for i, (s, mx) in enumerate(zip(scores, maxes)):
        pct = s / mx * 100 if mx > 0 else 0
        ax.text(s + mx * 0.01, i, f" {s:.1f}/{mx:.0f}  ({pct:.1f}%)",
                va="center", fontsize=9, fontweight="bold", color="#333")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Total Score", fontsize=10, labelpad=8)
    ax.set_title("Total Benchmark Scores", fontsize=13, fontweight="bold", pad=14)
    ax.grid(axis="x", alpha=0.15, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/results_by_question.json")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results/experiments/benchmark_summary")
    out = plot_benchmark_results(json_path, output_dir / "benchmark_results.png")
    print(f"Written to {out}")


if __name__ == "__main__":
    main()
