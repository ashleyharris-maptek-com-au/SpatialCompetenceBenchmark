import copy
from typing import Iterable

from LLMBenchCore import get_default_model_configs

from .constants import (BUDGETS, DEFAULT_BASE_MODEL_CONFIG_NAME, EXPERIMENT_TAG,
                        MODEL_NAME_ALIASES)


def resolve_model_config_name(model_name: str) -> str:
  return MODEL_NAME_ALIASES.get(model_name, model_name)


def get_base_model_config(model_config_name: str = DEFAULT_BASE_MODEL_CONFIG_NAME) -> dict:
  resolved = resolve_model_config_name(model_config_name)
  for cfg in get_default_model_configs():
    if cfg.get("name") == resolved:
      return copy.deepcopy(cfg)
  raise ValueError(f"Model config '{model_config_name}' not found (resolved to '{resolved}').")


def build_budget_model_configs(model_config_name: str = DEFAULT_BASE_MODEL_CONFIG_NAME,
                               budgets: Iterable[int] = BUDGETS,
                               temperature: float | None = None,
                               include_tools: bool = True,
                               include_no_tools: bool = True,
                               experiment_tag: str = EXPERIMENT_TAG) -> list[dict]:
  if not include_tools and not include_no_tools:
    raise ValueError("At least one variant must be enabled: tools or no-tools.")

  base_cfg = get_base_model_config(model_config_name)
  base_name = base_cfg["name"]

  configs: list[dict] = []
  for budget in budgets:
    if include_no_tools:
      base_variant = copy.deepcopy(base_cfg)
      base_variant["name"] = f"{base_name}-B{int(budget)}-informed"
      base_variant["tools"] = False
      base_variant["max_output_tokens"] = int(budget)
      base_variant["budget_informed_tokens"] = int(budget)
      if temperature is not None:
        base_variant["temperature"] = float(temperature)
      else:
        base_variant.pop("temperature", None)
      base_variant["experiment_tag"] = experiment_tag
      configs.append(base_variant)

    if include_tools:
      tools_variant = copy.deepcopy(base_cfg)
      tools_variant["name"] = f"{base_name}-B{int(budget)}-informed-tools"
      tools_variant["tools"] = True
      tools_variant["max_output_tokens"] = int(budget)
      tools_variant["budget_informed_tokens"] = int(budget)
      if temperature is not None:
        tools_variant["temperature"] = float(temperature)
      else:
        tools_variant.pop("temperature", None)
      tools_variant["experiment_tag"] = experiment_tag
      configs.append(tools_variant)

  return configs
