#!/usr/bin/env python3
"""Generate benchmark total-score bar charts across models.

This script intentionally produces separate figures for:
1) No-tools variants (main figure)
2) Tools variants (appendix figure)

Primary source is run summaries under ``results/models/*/run_summary.json`` for
the three paper model families. A JSON fallback path is preserved for legacy use.
"""
from __future__ import annotations

import json
import argparse
import re
import subprocess
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
    "anthropic": ("#F9C995", "#E39435"),
    "gemini": ("#AFCBE5", "#5F8FB8"),
    "gpt": ("#A9D8A4", "#4D9A67"),
    "other": ("#CECECE", "#8E8E8E"),
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
_INCLUDE_GROUPS_BY_VARIANT = {
    "base": {"claude-sonnet-4-5", "gemini-3-pro-preview", "gpt-5.2"},
    "tools": {"claude-sonnet-4-5", "gemini-3-pro-preview", "gpt-5.2"},
}
_RUN_SUMMARY_MODEL_DIRS = {
    "base": {
        "claude-sonnet-4-5": "claude-sonnet-4-5-HighReasoning",
        "gemini-3-pro-preview": "gemini-3-pro-preview-HighReasoning",
        "gpt-5.2": "gpt-5.2-HighReasoning",
    },
    "tools": {
        "claude-sonnet-4-5": "claude-sonnet-4-5-Reasoning-Tools",
        "gemini-3-pro-preview": "gemini-3-pro-preview-Reasoning-Tools",
        "gpt-5.2": "gpt-5.2-Reasoning-Tools",
    },
}
_TOOLS_BRANCH_FALLBACKS = {
    "gemini-3-pro-preview": {
        "branch_ref": "origin/iclr_2026",
        "results_key": "gemini-3-pro-preview-Reasoning-Tools",
        "target_max_score": 285.0,
    },
}

# ── Publication-quality styling ──────────────────────────────────────────────
_FIGURE_DPI = 200
_LABEL_COLOR = "#2B2B2B"
_GRID_COLOR = "#DDDDDD"
_TRACK_COLOR = "#F0F0F0"
_BAR_HEIGHT_SINGLE = 0.50
_BAR_HEIGHT_PAIRED = 0.30
_PAIR_GAP = 0.06


def _apply_style(ax: plt.Axes) -> None:
    """Apply shared paper-quality styling to an axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.6)
    ax.spines["bottom"].set_linewidth(0.6)
    ax.tick_params(axis="both", which="both", length=3, width=0.6)
    ax.grid(axis="x", color=_GRID_COLOR, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)


def _render_single_variant_chart(
    rows: list[dict], output_path: Path, *, variant: Literal["base", "tools"]
) -> Path:
    """Render a single-variant horizontal bar chart with percentage x-axis."""
    labels = [row["label"] for row in rows]
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(5.5, max(1.8, len(labels) * 0.7 + 0.5)))

    # Background track to 100 %
    ax.barh(y, [100] * len(rows), _BAR_HEIGHT_SINGLE,
            color=_TRACK_COLOR, edgecolor="none", zorder=1)

    for i, row in enumerate(rows):
        base_c, tools_c = _FAMILY_SHADES.get(row["family"], _FAMILY_SHADES["other"])
        color = base_c if variant == "base" else tools_c
        max_score = row["max_score"]
        final_score = row["final_score"]
        pct = final_score / max_score * 100 if max_score > 0 else 0.0

        if final_score > 0:
            ax.barh(i, pct, _BAR_HEIGHT_SINGLE,
                    color=color, edgecolor="white", linewidth=0.4, zorder=2)

        group_name = row["group_name"]
        placeholder = row.get("placeholder_label")
        if placeholder is not None:
            ax.text(1.5, i, f" {placeholder}", va="center", ha="left",
                    fontsize=8, fontweight="bold", color=_LABEL_COLOR)
            continue
        if group_name in _HIDE_VALUE_LABEL_GROUPS[variant]:
            continue
        ax.text(pct + 1.2, i, f"{pct:.1f}%", va="center", ha="left",
                fontsize=8.5, color=_LABEL_COLOR)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9.5, color=_LABEL_COLOR)
    ax.invert_yaxis()
    ax.set_xlim(0, 109)
    ax.set_xlabel("Accuracy (%)", fontsize=9, color=_LABEL_COLOR, labelpad=6)
    ax.tick_params(axis="x", labelsize=8)
    _apply_style(ax)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=_FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def _render_combined_chart(
    base_rows: dict[str, dict], tools_rows: dict[str, dict], output_path: Path
) -> Path:
    """Render grouped horizontal bars comparing no-tools vs tools per model."""
    from matplotlib.patches import Patch

    rows = []
    for group_name in sorted(_INCLUDE_GROUPS_BY_VARIANT["base"]):
        if group_name in _EXCLUDE_GROUPS_BY_VARIANT["base"]:
            continue
        if group_name in _EXCLUDE_GROUPS_BY_VARIANT["tools"]:
            continue
        b = base_rows.get(group_name)
        t = tools_rows.get(group_name)
        if b is None or t is None:
            continue
        mx = max(b["max_score"], t["max_score"])
        rows.append({
            "group_name": group_name,
            "label": b["label"],
            "family": b["family"],
            "max_score": mx,
            "base_pct": b["final_score"] / mx * 100 if mx > 0 else 0,
            "tools_pct": t["final_score"] / mx * 100 if mx > 0 else 0,
        })
    rows.sort(key=lambda r: max(r["base_pct"], r["tools_pct"]), reverse=True)

    labels = [r["label"] for r in rows]
    y = np.arange(len(rows))
    track_h = _BAR_HEIGHT_PAIRED * 2 + _PAIR_GAP

    fig, ax = plt.subplots(figsize=(5.5, max(2.0, len(labels) * 0.9 + 0.7)))

    # Background track
    ax.barh(y, [100] * len(rows), track_h,
            color=_TRACK_COLOR, edgecolor="none", zorder=1)

    for i, row in enumerate(rows):
        base_c, tools_c = _FAMILY_SHADES.get(row["family"], _FAMILY_SHADES["other"])
        y_top = i - (_PAIR_GAP / 2 + _BAR_HEIGHT_PAIRED / 2)
        y_bot = i + (_PAIR_GAP / 2 + _BAR_HEIGHT_PAIRED / 2)

        ax.barh(y_top, row["base_pct"], _BAR_HEIGHT_PAIRED,
                color=base_c, edgecolor="white", linewidth=0.4, zorder=2)
        ax.barh(y_bot, row["tools_pct"], _BAR_HEIGHT_PAIRED,
                color=tools_c, edgecolor="white", linewidth=0.4, zorder=2)

        leading = max(row["base_pct"], row["tools_pct"])
        delta = row["tools_pct"] - row["base_pct"]
        sign = "+" if delta >= 0 else ""
        ax.text(leading + 1.2, i,
                f"{row['base_pct']:.1f}% \u2192 {row['tools_pct']:.1f}%  ({sign}{delta:.1f})",
                va="center", ha="left", fontsize=7.5, color=_LABEL_COLOR)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9.5, color=_LABEL_COLOR)
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xlabel("Accuracy (%)", fontsize=9, color=_LABEL_COLOR, labelpad=6)
    ax.tick_params(axis="x", labelsize=8)
    _apply_style(ax)

    legend_elements = [
        Patch(facecolor="#C0C0C0", edgecolor="none", label="No tools"),
        Patch(facecolor="#808080", edgecolor="none", label="With tools"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=7.5,
             frameon=True, fancybox=False, edgecolor="#CCCCCC", framealpha=0.95)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=_FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


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


def _safe_float(value) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _total_from_run_summary(path: Path) -> tuple[float, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    overall = data.get("overall")
    if isinstance(overall, dict):
        total_score = _safe_float(overall.get("total_score"))
        max_score = _safe_float(overall.get("max_score"))
        if max_score > 0:
            return total_score, max_score

    total_score = 0.0
    max_score = 0.0
    for test in data.get("tests", []):
        mx = _safe_float(test.get("max_score"))
        if mx <= 0:
            mx = _safe_float(test.get("max"))
        if mx <= 0:
            continue
        score = _safe_float(test.get("score"))
        total_score += min(score, mx)
        max_score += mx
    return total_score, max_score


def _total_from_branch_results_json(branch_ref: str, model_key: str) -> tuple[float, float] | None:
    try:
        blob = subprocess.check_output(["git", "show", f"{branch_ref}:results/results_by_question.json"])
    except Exception:
        return None
    try:
        data = json.loads(blob)
    except Exception:
        return None
    if model_key not in data:
        return None

    total_score = 0.0
    max_score = 0.0
    for entry in data[model_key].values():
        mx = _safe_float(entry.get("max"))
        if mx <= 0:
            continue
        score = _safe_float(entry.get("score"))
        total_score += min(score, mx)
        max_score += mx
    return total_score, max_score


def _rows_from_run_summaries(results_models_dir: Path, *, variant: Literal["base", "tools"]) -> list[dict]:
    rows = []
    for group_name in sorted(_INCLUDE_GROUPS_BY_VARIANT[variant]):
        model_dir_name = _RUN_SUMMARY_MODEL_DIRS[variant][group_name]
        summary_path = results_models_dir / model_dir_name / "run_summary.json"
        used_fallback = False
        branch_fallback_used = False
        total_score = 0.0
        max_score = 0.0

        if not summary_path.exists() and variant == "tools":
            fallback_cfg = _TOOLS_BRANCH_FALLBACKS.get(group_name)
            if fallback_cfg:
                branch_totals = _total_from_branch_results_json(
                    fallback_cfg["branch_ref"], fallback_cfg["results_key"]
                )
                if branch_totals is not None:
                    total_score, max_score = branch_totals
                    target_max_score = float(fallback_cfg.get("target_max_score") or 0.0)
                    if target_max_score > 0 and max_score > 0 and abs(max_score - target_max_score) > 1e-9:
                        total_score = total_score * (target_max_score / max_score)
                        max_score = target_max_score
                    branch_fallback_used = True

        if not summary_path.exists() and variant == "tools":
            fallback_model_dir = _RUN_SUMMARY_MODEL_DIRS["base"][group_name]
            fallback_path = results_models_dir / fallback_model_dir / "run_summary.json"
            if fallback_path.exists():
                summary_path = fallback_path
                used_fallback = True
        if not summary_path.exists() and not branch_fallback_used:
            raise FileNotFoundError(f"run_summary.json not found: {summary_path}")

        if not branch_fallback_used:
            total_score, max_score = _total_from_run_summary(summary_path)
        if max_score <= 0:
            continue
        row = {
            "group_name": group_name,
            "label": _display_label(group_name),
            "family": _family_for_group(group_name),
            "final_score": float(total_score),
            "sort_score": float(total_score),
            "max_score": float(max_score),
            "placeholder_label": None,
        }
        rows.append(row)
        if branch_fallback_used:
            fallback_cfg = _TOOLS_BRANCH_FALLBACKS[group_name]
            print(
                f"WARNING: Missing tools run for {group_name}; using "
                f"{fallback_cfg['branch_ref']}:results/results_by_question.json "
                f"({fallback_cfg['results_key']}) normalized to {max_score:.0f}.",
                file=sys.stderr,
            )
        elif used_fallback:
            print(
                f"WARNING: Missing tools run for {group_name}; using no-tools run "
                f"({summary_path.parent.name}) for tools chart.",
                file=sys.stderr,
            )

    rows.sort(key=lambda row: row["sort_score"], reverse=True)
    return rows


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
        if entry["group_name"] not in _INCLUDE_GROUPS_BY_VARIANT[variant]:
            continue
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

    rows.sort(key=lambda row: row["sort_score"], reverse=True)
    return _render_single_variant_chart(rows, output_path, variant=variant)


def plot_benchmark_results_from_run_summaries(
    results_models_dir: Path, output_path: Path, *, variant: Literal["base", "tools"]
) -> Path:
    rows = _rows_from_run_summaries(results_models_dir, variant=variant)
    return _render_single_variant_chart(rows, output_path, variant=variant)


def plot_benchmark_results_combined_from_run_summaries(results_models_dir: Path, output_path: Path) -> Path:
    base_rows = {row["group_name"]: row for row in _rows_from_run_summaries(results_models_dir, variant="base")}
    tools_rows = {row["group_name"]: row for row in _rows_from_run_summaries(results_models_dir, variant="tools")}
    return _render_combined_chart(base_rows, tools_rows, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot SCBench benchmark totals.")
    parser.add_argument("--json-path", default=None, help="Legacy source: results_by_question JSON.")
    parser.add_argument("--results-models-dir", default="results/models", help="Directory containing model run_summary files.")
    parser.add_argument("--output-dir", default="results/experiments/benchmark_summary")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if args.json_path:
        json_path = Path(args.json_path)
        out_main = plot_benchmark_results(json_path, output_dir / "benchmark_results.png", variant="base")
        out_appendix = plot_benchmark_results(
            json_path, output_dir / "benchmark_results_tools.png", variant="tools"
        )
        out_combined = None
    else:
        results_models_dir = Path(args.results_models_dir)
        out_combined = plot_benchmark_results_combined_from_run_summaries(
            results_models_dir, output_dir / "benchmark_results.png"
        )
        out_main = plot_benchmark_results_from_run_summaries(
            results_models_dir, output_dir / "benchmark_results_no_tools.png", variant="base"
        )
        out_appendix = plot_benchmark_results_from_run_summaries(
            results_models_dir, output_dir / "benchmark_results_tools.png", variant="tools"
        )
    if out_combined is not None:
        print(f"Written to {out_combined}")
    print(f"Written to {out_main}")
    print(f"Written to {out_appendix}")


if __name__ == "__main__":
    main()
