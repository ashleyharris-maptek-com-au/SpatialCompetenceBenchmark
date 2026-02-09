#!/usr/bin/env python3
"""Generate a grouped bar chart of benchmark scores per question across models."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_SKIP_MODELS = {"always-wrong"}
_KNOWN_SUFFIXES = (
    "-Reasoning-Tools",
    "-HighReasoning",
    "-Reasoning",
    "-Tools",
    "-informed-tools",
    "-informed",
)
_GROUP_LABELS = {
    "claude-sonnet-4-5": "Claude Sonnet 4.5",
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gpt-5.2": "GPT-5.2",
}
_FAMILY_SHADES = {
    "anthropic": ("#F7B267", "#D67B00"),
    "gemini": ("#8FB8DE", "#3A75B7"),
    "gpt": ("#8DC891", "#3F8B43"),
    "other": ("#B3B3B3", "#6E6E6E"),
}


def _is_tools_variant(model_name: str) -> bool:
    lowered = model_name.lower()
    return "-tools" in lowered or lowered.endswith("tools")


def _canonical_group_name(model_name: str) -> str:
    name = re.sub(r"-Reasoning-\d+$", "", model_name)
    changed = True
    while changed:
        changed = False
        for suffix in _KNOWN_SUFFIXES:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                changed = True
    return name


def _family_for_group(group_name: str) -> str:
    if group_name.startswith("claude-"):
        return "anthropic"
    if group_name.startswith("gemini-"):
        return "gemini"
    if group_name.startswith("gpt-"):
        return "gpt"
    return "other"


def _display_label(group_name: str) -> str:
    return _GROUP_LABELS.get(group_name, group_name)


def plot_benchmark_results(json_path: Path, output_path: Path) -> Path:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = [m for m in data if m not in _SKIP_MODELS]

    # Compute total score and total max per model (only questions with max > 0).
    model_totals: list[tuple[str, float, float, bool]] = []
    for model in models:
        total_score = 0.0
        total_max = 0.0
        for qid, info in data[model].items():
            mx = info.get("max", 0)
            if mx > 0:
                score = min(info.get("score", 0), mx)
                total_score += score
                total_max += mx
        model_totals.append((model, total_score, total_max, _is_tools_variant(model)))

    grouped: dict[str, dict] = {}
    for model_name, score, max_score, is_tools in model_totals:
        group_name = _canonical_group_name(model_name)
        entry = grouped.setdefault(
            group_name,
            {
                "group_name": group_name,
                "label": _display_label(group_name),
                "family": _family_for_group(group_name),
                "base": None,
                "tools": None,
            },
        )
        variant_key = "tools" if is_tools else "base"
        current = entry[variant_key]
        if current is None or score > current["score"]:
            entry[variant_key] = {"model_name": model_name, "score": score, "max": max_score}

    rows = []
    for entry in grouped.values():
        base_variant = entry["base"]
        tools_variant = entry["tools"]
        max_score = 0.0
        if base_variant is not None:
            max_score = max(max_score, float(base_variant["max"]))
        if tools_variant is not None:
            max_score = max(max_score, float(tools_variant["max"]))
        base_score = float(base_variant["score"]) if base_variant is not None else 0.0
        tools_score = float(tools_variant["score"]) if tools_variant is not None else None
        final_score = tools_score if tools_score is not None else base_score
        rows.append(
            {
                "label": entry["label"],
                "family": entry["family"],
                "base_score": base_score,
                "tools_score": tools_score,
                "final_score": final_score,
                "max_score": max_score,
            }
        )

    rows.sort(key=lambda row: row["final_score"], reverse=True)
    labels = [row["label"] for row in rows]
    y = np.arange(len(rows))
    bar_height = 0.5

    fig, ax = plt.subplots(figsize=(10, max(2.5, len(labels) * 0.9 + 1)))

    maxes = [row["max_score"] for row in rows]
    ax.barh(y, maxes, bar_height, color="#E8E8E8", edgecolor="white", linewidth=0.5)

    for index, row in enumerate(rows):
        base_color, tools_color = _FAMILY_SHADES.get(row["family"], _FAMILY_SHADES["other"])
        base_score = row["base_score"]
        tools_score = row["tools_score"]
        max_score = row["max_score"]

        if base_score > 0:
            ax.barh(index, base_score, bar_height, color=base_color, edgecolor="white", linewidth=0.5)

        if tools_score is not None:
            if base_score > 0:
                low = min(base_score, tools_score)
                high = max(base_score, tools_score)
                ax.barh(index, high - low, bar_height, left=low, color=tools_color, edgecolor="white", linewidth=0.5)
            else:
                ax.barh(index, tools_score, bar_height, color=tools_color, edgecolor="white", linewidth=0.5)

        final_score = tools_score if tools_score is not None else base_score
        final_pct = final_score / max_score * 100 if max_score > 0 else 0
        if tools_score is not None and base_score > 0:
            label = f" {base_score:.1f}->{tools_score:.1f}/{max_score:.0f}  ({final_pct:.1f}%)"
        else:
            label = f" {final_score:.1f}/{max_score:.0f}  ({final_pct:.1f}%)"
        ax.text(final_score + max_score * 0.01, index, label, va="center", fontsize=9, fontweight="bold", color="#333")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Total Score", fontsize=10, labelpad=8)
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
