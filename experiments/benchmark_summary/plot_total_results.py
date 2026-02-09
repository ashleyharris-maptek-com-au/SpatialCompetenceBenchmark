#!/usr/bin/env python3
"""Generate benchmark total-score bar charts across models.

This script intentionally produces separate figures for:
1) No-tools variants (main figure)
2) Tools variants (appendix figure)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Literal

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
    "gpt-5.1": "GPT-5.1",
    "gpt-5.2": "GPT-5.2",
}
_FAMILY_SHADES = {
    "anthropic": ("#F7B267", "#D67B00"),
    "gemini": ("#8FB8DE", "#3A75B7"),
    "gpt": ("#8DC891", "#3F8B43"),
    "other": ("#B3B3B3", "#6E6E6E"),
}

# Paper-facing tweaks: allow suppressing numeric labels / placeholder annotations for
# specific groups without changing the underlying results data.
_HIDE_VALUE_LABEL_GROUPS = {
    "base": {"gpt-5.1"},
    "tools": set(),
}
_PLACEHOLDER_VALUE_LABELS = {
    "base": {},
    "tools": {},
}
_EXCLUDE_GROUPS_BY_VARIANT = {
    "base": {"gpt-5.1"},
    "tools": set(),
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
    if name == "gpt-5.2-chat-azure":
        name = "gpt-5.2"
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


def plot_benchmark_results(json_path: Path, output_path: Path, *, variant: Literal["base", "tools"]) -> Path:
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
        if entry["group_name"] in _EXCLUDE_GROUPS_BY_VARIANT[variant]:
            continue
        base_variant = entry["base"]
        tools_variant = entry["tools"]
        chosen = base_variant if variant == "base" else tools_variant
        if chosen is None:
            continue
        max_score = float(chosen["max"])
        raw_score = float(chosen["score"])
        placeholder_label = _PLACEHOLDER_VALUE_LABELS[variant].get(entry["group_name"])
        is_placeholder = placeholder_label is not None
        final_score = 0.0 if is_placeholder else raw_score
        rows.append(
            {
                "group_name": entry["group_name"],
                "label": entry["label"],
                "family": entry["family"],
                "final_score": final_score,
                "sort_score": raw_score,
                "max_score": max_score,
                "placeholder_label": placeholder_label,
            }
        )

    # Sort by the underlying score even if we are rendering a placeholder bar.
    rows.sort(key=lambda row: row["sort_score"], reverse=True)
    labels = [row["label"] for row in rows]
    y = np.arange(len(rows))
    bar_height = 0.5

    fig, ax = plt.subplots(figsize=(10, max(2.5, len(labels) * 0.9 + 1)))

    maxes = [row["max_score"] for row in rows]
    ax.barh(y, maxes, bar_height, color="#E8E8E8", edgecolor="white", linewidth=0.5)

    for index, row in enumerate(rows):
        base_color, tools_color = _FAMILY_SHADES.get(row["family"], _FAMILY_SHADES["other"])
        color = base_color if variant == "base" else tools_color
        max_score = row["max_score"]

        final_score = row["final_score"]
        if final_score > 0:
            ax.barh(index, final_score, bar_height, color=color, edgecolor="white", linewidth=0.5)

        group_name = row["group_name"]
        placeholder = row["placeholder_label"]
        if placeholder is not None:
            ax.text(max_score * 0.02, index, f" {placeholder}", va="center", fontsize=9, fontweight="bold", color="#333")
            continue
        if group_name in _HIDE_VALUE_LABEL_GROUPS[variant]:
            continue

        final_pct = final_score / max_score * 100 if max_score > 0 else 0
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
    out_main = plot_benchmark_results(json_path, output_dir / "benchmark_results.png", variant="base")
    out_appendix = plot_benchmark_results(
        json_path, output_dir / "benchmark_results_tools.png", variant="tools"
    )
    print(f"Written to {out_main}")
    print(f"Written to {out_appendix}")


if __name__ == "__main__":
    main()
