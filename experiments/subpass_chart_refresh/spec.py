from __future__ import annotations

from dataclasses import dataclass


CANONICAL_MODEL_RUNS: tuple[str, ...] = (
  "claude-sonnet-4-5-HighReasoning",
  "claude-sonnet-4-5-Reasoning-Tools",
  "gemini-3-pro-preview-HighReasoning",
  "gemini-3-pro-preview-Reasoning-Tools",
  "gpt-5.2-HighReasoning",
  "gpt-5.2-Reasoning-Tools",
)

Q11_DIMENSION_LABELS: tuple[str, ...] = (
  "2D",
  "2D",
  "3D",
  "3D",
  "4D",
  "4D",
  "5D",
  "6D",
  "6D",
  "7D",
  "8D",
  "9D",
  "10D",
)


@dataclass(frozen=True)
class TaskSpec:
  task_index: int
  short_name: str
  expected_subpasses: int
  chart_filename: str
  chart_title: str
  include_median_overlay: bool = False
  dimension_labels: tuple[str, ...] | None = None


TASK_SPECS: tuple[TaskSpec, ...] = (
  TaskSpec(task_index=11,
           short_name="q11_hypersnake",
           expected_subpasses=13,
           chart_filename="q11_hypersnake_mean_subpass_6runs.png",
           chart_title="Hyper-Snake: Mean score by subpass (6 runs)",
           include_median_overlay=False,
           dimension_labels=Q11_DIMENSION_LABELS),
  TaskSpec(task_index=12,
           short_name="q12_pipe_loop",
           expected_subpasses=40,
           chart_filename="q12_pipe_loop_mean_subpass_6runs.png",
           chart_title="Pipe Loop Fitting: Mean score by subpass (6 runs)",
           include_median_overlay=False),
  TaskSpec(task_index=16,
           short_name="q16_pack_prisms",
           expected_subpasses=9,
           chart_filename="q16_pack_prisms_mean_subpass_6runs.png",
           chart_title="Pack Rectangular Prisms: Mean score by subpass (6 runs)",
           include_median_overlay=False),
)


PUBLISH_FILENAME_BY_TASK: dict[int, str] = {
  11: "q11_mean_subpass_6runs.png",
  12: "q12_mean_subpass_6runs.png",
  16: "q16_mean_subpass_6runs.png",
}
