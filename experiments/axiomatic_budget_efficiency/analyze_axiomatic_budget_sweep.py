#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from experiments.axiomatic_budget_efficiency.analysis import analyze_budget_sweep
from experiments.axiomatic_budget_efficiency.configs import build_budget_model_configs
from experiments.axiomatic_budget_efficiency.constants import (BUDGETS,
                                                               DEFAULT_BASE_MODEL_CONFIG_NAME,
                                                               RESULTS_DIR)


def _parse_budgets(value: str) -> list[int]:
  return [int(part.strip()) for part in value.split(",") if part.strip()]


def _load_model_configs_from_manifest(manifest_path: Path) -> list[dict]:
  if not manifest_path.exists():
    raise FileNotFoundError(f"Manifest not found: {manifest_path}")
  with manifest_path.open("r", encoding="utf-8") as f:
    manifest = json.load(f)
  model_configs = manifest.get("model_configs")
  if not isinstance(model_configs, list) or not model_configs:
    raise ValueError(f"Manifest has no model_configs: {manifest_path}")
  return model_configs


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Analyze axiomatic budget sweep and generate Pareto artifacts.")
  parser.add_argument("--model-config-name",
                      default=DEFAULT_BASE_MODEL_CONFIG_NAME,
                      help="Base LLMBenchCore model config name (default: gpt-5.2-chat-azure)")
  parser.add_argument("--budgets",
                      default=None,
                      help="Comma-separated budgets to analyze")
  parser.add_argument("--manifest",
                      default=str(RESULTS_DIR / "manifest.json"),
                      help="Sweep manifest path (used when --budgets is omitted)")
  parser.add_argument("--temperature",
                      type=float,
                      default=None,
                      help="Expected sweep temperature (used only for config reconstruction)")
  parser.add_argument("--output-dir",
                      default=str(RESULTS_DIR),
                      help="Output directory for metrics and plots")
  args = parser.parse_args()

  if args.budgets:
    budgets = _parse_budgets(args.budgets)
    model_configs = build_budget_model_configs(model_config_name=args.model_config_name,
                                               budgets=budgets,
                                               temperature=args.temperature)
  else:
    model_configs = _load_model_configs_from_manifest(Path(args.manifest))

  outputs = analyze_budget_sweep(model_configs=model_configs, output_dir=Path(args.output_dir))
  print("Generated artifacts:")
  for key, path in outputs.items():
    print(f"  {key}: {path}")


if __name__ == "__main__":
  main()
