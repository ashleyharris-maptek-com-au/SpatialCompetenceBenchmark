#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from experiments.axiomatic_budget_efficiency.constants import (BUDGETS,
                                                               DEFAULT_BASE_MODEL_CONFIG_NAME)
from experiments.axiomatic_budget_efficiency.sweep import run_axiomatic_budget_sweep


def _parse_budgets(value: str) -> list[int]:
  return [int(part.strip()) for part in value.split(",") if part.strip()]


def _parse_tests(value: str | None) -> list[int] | None:
  if value is None or not value.strip():
    return None
  return [int(part.strip()) for part in value.split(",") if part.strip()]


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Run axiomatic spatial reasoning benchmark under output-token budgets.")
  parser.add_argument("--model-config-name",
                      default=DEFAULT_BASE_MODEL_CONFIG_NAME,
                      help="Base LLMBenchCore model config name (default: gpt-5.2-chat-azure)")
  parser.add_argument("--budgets",
                      default=",".join(str(b) for b in BUDGETS),
                      help="Comma-separated output token budgets")
  parser.add_argument("--temperature",
                      type=float,
                      default=None,
                      help="Optional sampling temperature. Omit to use provider defaults.")
  parser.add_argument("--variant",
                      choices=("all", "tools", "no-tools"),
                      default="all",
                      help="Which model variants to run.")
  parser.add_argument("--tests",
                      default=None,
                      help="Optional comma-separated test IDs (e.g. 54,57).")
  parser.add_argument("--anthropic-thinking-budget",
                      type=int,
                      default=None,
                      help=("Optional override for Anthropic thinking budget_tokens. "
                            "Applied as-is (no local clamping/adjustment)."))
  parser.add_argument("--reuse-cache",
                      action="store_true",
                      help="Use cached responses instead of forcing fresh API calls.")
  parser.add_argument("--dry-run",
                      action="store_true",
                      help="Write manifest and print planned configs without running models")
  args = parser.parse_args()

  include_tools = args.variant in ("all", "tools")
  include_no_tools = args.variant in ("all", "no-tools")

  result = run_axiomatic_budget_sweep(model_config_name=args.model_config_name,
                                      budgets=_parse_budgets(args.budgets),
                                      test_ids=_parse_tests(args.tests),
                                      temperature=args.temperature,
                                      include_tools=include_tools,
                                      include_no_tools=include_no_tools,
                                      anthropic_thinking_budget=args.anthropic_thinking_budget,
                                      force=not args.reuse_cache,
                                      dry_run=args.dry_run)

  print(f"Manifest: {result['manifest']}")
  print(f"Results dir: {result['results_dir']}")
  print("Model configs:")
  for cfg in result["model_configs"]:
    print(f"  - {cfg['name']}")


if __name__ == "__main__":
  main()
