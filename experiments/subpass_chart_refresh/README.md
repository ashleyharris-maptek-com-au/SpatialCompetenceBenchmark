# Subpass chart refresh (Q11/Q12/Q16)

This experiment rebuilds appendix score-by-subpass charts for:

- `Q11` Hyper-Snake
- `Q12` Pipe Loop Fitting
- `Q16` Pack Rectangular Prisms

It uses only `run_summary.json` from the six canonical runs:

- `claude-sonnet-4-5-HighReasoning`
- `claude-sonnet-4-5-Reasoning-Tools`
- `gemini-3-pro-preview-HighReasoning`
- `gemini-3-pro-preview-Reasoning-Tools`
- `gpt-5.2-HighReasoning`
- `gpt-5.2-Reasoning-Tools`

## Command

```bash
python -m experiments.subpass_chart_refresh.refresh_subpass_charts \
  --results-models-dir results/models \
  --output-dir results/experiments/subpass_chart_refresh \
  --publish-figures-dir /path/to/scbench/figures/appendix \
  --patch-appendix-tex /path/to/scbench/appendix_content.tex \
  --strict
```

If omitted, `--results-models-dir` and `--output-dir` default to repo-relative paths:

- `results/models`
- `results/experiments/subpass_chart_refresh`

## Outputs

Each run writes:

- `q11_scores_long.csv`, `q12_scores_long.csv`, `q16_scores_long.csv`
- `q11_aggregates.csv`, `q12_aggregates.csv`, `q16_aggregates.csv`
- `q11_hypersnake_mean_subpass_6runs.png`
- `q12_pipe_loop_mean_subpass_6runs.png`
- `q16_pack_prisms_mean_subpass_6runs_with_median.png`
- `calculation_manifest.json`
- `verification_report.md`

under:

- `results/experiments/subpass_chart_refresh/<timestamp>/`

and updates:

- `results/experiments/subpass_chart_refresh/latest`

as a symlink (or fallback copied directory) to the latest run.

Determinism checks compare aggregate CSV hashes against the previous `latest` run when input
`run_summary.json` hashes are identical.

When `--publish-figures-dir` is provided, the script copies:

- `q11_mean_subpass_6runs.png`
- `q12_mean_subpass_6runs.png`
- `q16_mean_subpass_6runs_median_overlay.png`

When `--patch-appendix-tex` is provided, the script patches image references and captions in the target TeX file deterministically.
