import ast
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs, urlparse

import LLMBenchCore.ResultPaths as rp
import LLMBenchCore.TestRunner as tr
from LLMBenchCore import PromptImageTagging as pit
from LLMBenchCore._openai_usage_utils import extract_openai_usage_meta

from .configs import build_budget_model_configs
from .io import model_run_summary_path, safe_float
from .constants import (AXIOMATIC_TEST_IDS, BUDGETS, DEFAULT_BASE_MODEL_CONFIG_NAME,
                        EXPERIMENT_NAME, EXPERIMENT_TAG, RESULTS_DIR)
from .manifest import build_manifest, write_manifest
from .prompting import apply_budget_informed_prefix


def build_axiomatic_test_filter(test_ids: Iterable[int] = AXIOMATIC_TEST_IDS) -> dict[int, None]:
  return {int(test_id): None for test_id in test_ids}


def _manifest_model_config_snapshot(configs: list[dict]) -> list[dict]:
  keys = [
    "name",
    "engine",
    "base_model",
    "reasoning",
    "tools",
    "max_output_tokens",
    "budget_informed_tokens",
    "temperature",
    "experiment_tag",
  ]
  snapshots = []
  for cfg in configs:
    snapshot = {}
    for key in keys:
      value = cfg.get(key)
      if value is not None:
        snapshot[key] = value
    snapshots.append(snapshot)
  return snapshots


def _read_field(obj, key: str):
  if obj is None:
    return None
  if isinstance(obj, dict):
    return obj.get(key)
  return getattr(obj, key, None)


def _coerce_int(value):
  if value is None:
    return None
  try:
    return int(value)
  except Exception:
    return None


def _extract_usage(response_obj) -> dict | None:
  if _read_field(response_obj, "usage") is None:
    return None
  return extract_openai_usage_meta(response_obj, "")["usage"]


def _extract_incomplete_reason(response_obj) -> str | None:
  incomplete_details = _read_field(response_obj, "incomplete_details")
  if incomplete_details is None:
    return None
  return _read_field(incomplete_details, "reason")


def _normalize_azure_endpoint(endpoint: str | None) -> str:
  endpoint = (endpoint or "").strip()
  if not endpoint:
    return endpoint

  parsed = urlparse(endpoint)
  if parsed.scheme and parsed.netloc:
    return f"{parsed.scheme}://{parsed.netloc}"

  return endpoint.rstrip("/")


def _normalize_azure_api_version(endpoint: str | None, api_version: str | None) -> str | None:
  if api_version:
    return api_version
  parsed = urlparse((endpoint or "").strip())
  if parsed.scheme and parsed.netloc:
    query = parse_qs(parsed.query)
    if "api-version" in query and query["api-version"]:
      return query["api-version"][0]
  return None


def _build_openai_input(prompt: str):
  prompt_parts = pit.parse_prompt_parts(prompt)
  has_images = any(part_type == "image" for part_type, _ in prompt_parts)
  if not has_images:
    return prompt

  content: list[dict] = []
  for part_type, part_value in prompt_parts:
    if part_type == "text":
      if part_value:
        content.append({"type": "input_text", "text": part_value})
    elif part_type == "image":
      if pit.is_url(part_value) or pit.is_data_uri(part_value):
        image_url = part_value
      else:
        image_url = pit.file_to_data_uri(pit.resolve_local_path(part_value))
      content.append({"type": "input_image", "image_url": image_url, "detail": "high"})

  return [{"role": "user", "content": content}]


def _map_reasoning_effort(reasoning) -> str | None:
  if isinstance(reasoning, int) and reasoning > 0:
    if reasoning <= 3:
      return "low"
    if reasoning <= 7:
      return "medium"
    return "high"
  if isinstance(reasoning, str) and reasoning in {"minimal", "low", "medium", "high"}:
    return reasoning
  return None


def _resolve_tools_param(engine: str, model_name: str, tools) -> list[dict] | None:
  if not tools or tools is False:
    return None

  if tools is True:
    if engine in ("azure_openai", "azure-openai"):
      if "5.2-pro" in model_name:
        return None
      return [{"type": "code_interpreter", "container": {"type": "auto"}}]

    built_in = [{"type": "web_search"}]
    if "5.2-pro" not in model_name:
      built_in.append({"type": "code_interpreter", "container": {"type": "auto"}})
    return built_in

  if isinstance(tools, list):
    return tools
  if isinstance(tools, dict):
    return [tools]
  return None


def _extract_output_text(response_obj) -> str:
  output_text = _read_field(response_obj, "output_text")
  if isinstance(output_text, str):
    return output_text

  pieces: list[str] = []
  for item in (_read_field(response_obj, "output") or []):
    item_type = _read_field(item, "type")
    if item_type != "message":
      continue
    for content_item in (_read_field(item, "content") or []):
      content_type = _read_field(content_item, "type")
      if content_type in ("text", "output_text"):
        text = _read_field(content_item, "text")
        if isinstance(text, str):
          pieces.append(text)
  return "".join(pieces)


def _parse_structured_output(output_text: str) -> Any:
  if not output_text:
    return {}
  for parser in (json.loads, ast.literal_eval):
    try:
      return parser(output_text)
    except Exception:
      continue
  # Keep the raw text so per-test graders can attempt extraction.
  return output_text


def _load_test_globals(test_index: int) -> dict[str, Any]:
  test_file = Path(f"{test_index}.py")
  if not test_file.exists():
    raise FileNotFoundError(f"Missing test file: {test_file}")
  g: dict[str, Any] = {"__file__": str(test_file)}
  exec(compile(test_file.read_text(encoding="utf-8"), str(test_file), "exec"), g)
  return g


def _inspect_test(test_index: int) -> tuple[str, list[int]]:
  g = _load_test_globals(test_index)
  title = str(g.get("title", f"Test {test_index}"))

  if "prepareSubpassPrompt" in g:
    subpass_indices: list[int] = []
    subpass = 0
    while True:
      try:
        g["prepareSubpassPrompt"](subpass)
        subpass_indices.append(subpass)
        subpass += 1
      except StopIteration:
        break
  else:
    subpass_indices = [0]

  return title, subpass_indices


def _model_meta_path(model_name: str, test_index: int, subpass: int) -> Path:
  return Path("results") / "models" / model_name / "meta" / f"{model_name}_{test_index}_{subpass}.json"



def _write_json(path: Path, data: dict) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)


def _make_hook(client, provider: str, model_name: str, reasoning_effort: str | None,
               temperature: float | None, tools_param: list[dict] | None,
               budget: int, usage_log: dict[tuple[int, int], dict],
               prompt_log: dict[tuple[int, int], str]):

  def hook(prompt: str, structure: dict | None, test_index: int, subpass: int):
    key = (test_index, subpass)
    started_at = time.time()
    effective_prompt = apply_budget_informed_prefix(prompt, budget)
    prompt_log[key] = effective_prompt

    params = {
      "model": model_name,
      "input": _build_openai_input(effective_prompt),
      "max_output_tokens": int(budget),
    }

    if reasoning_effort:
      params["reasoning"] = {"effort": reasoning_effort, "summary": "auto"}

    if temperature is not None:
      params["temperature"] = temperature

    if structure is not None:
      params["text"] = {
        "format": {
          "type": "json_schema",
          "name": "structured_response",
          "schema": structure,
          "strict": True,
        }
      }

    if tools_param:
      params["tools"] = tools_param

    try:
      response = client.responses.create(**params)
    except Exception as exc:
      usage_log[key] = {
        "provider": provider,
        "budget": int(budget),
        "status": "error",
        "error": str(exc),
        "usage": None,
        "elapsed_ms": int((time.time() - started_at) * 1000),
        "output_text_chars": 0,
      }
      raise

    output_text = _extract_output_text(response)
    usage_log[key] = {
      "provider": provider,
      "budget": int(budget),
      "status": _read_field(response, "status") or "completed",
      "incomplete_reason": _extract_incomplete_reason(response),
      "response_id": _read_field(response, "id"),
      "usage": _extract_usage(response),
      "elapsed_ms": int((time.time() - started_at) * 1000),
      "output_text_chars": len(output_text),
    }

    if structure is not None:
      return _parse_structured_output(output_text), ""
    return output_text or "", ""

  return hook


def _build_azure_hook(config: dict, budget: int, usage_log: dict[tuple[int, int], dict],
                      prompt_log: dict[tuple[int, int], str]):
  from openai import AzureOpenAI

  endpoint = config.get("endpoint") or os.environ.get("AZURE_OPENAI_ENDPOINT")
  endpoint = _normalize_azure_endpoint(endpoint)
  if not endpoint:
    raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")

  api_version = _normalize_azure_api_version(config.get("endpoint"), config.get("api_version"))
  api_version = api_version or os.environ.get("AZURE_OPENAI_API_VERSION") or "2025-04-01-preview"

  api_key = os.environ.get("AZURE_OPENAI_API_KEY")
  if not api_key:
    raise RuntimeError("AZURE_OPENAI_API_KEY is not set")

  timeout = config.get("timeout") or 3600
  client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version,
                       timeout=timeout)

  model_name = config["base_model"]
  reasoning_effort = _map_reasoning_effort(config.get("reasoning"))
  temperature = config.get("temperature")
  tools_param = _resolve_tools_param("azure_openai", model_name, config.get("tools"))

  return _make_hook(client, "azure_openai", model_name, reasoning_effort,
                    temperature, tools_param, budget, usage_log, prompt_log)


def _build_openai_hook(config: dict, budget: int, usage_log: dict[tuple[int, int], dict],
                       prompt_log: dict[tuple[int, int], str]):
  from openai import OpenAI

  api_key = os.environ.get("OPENAI_API_KEY")
  if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

  timeout = config.get("timeout") or 3600
  client = OpenAI(timeout=timeout)
  model_name = config["base_model"]
  reasoning_effort = _map_reasoning_effort(config.get("reasoning"))
  temperature = config.get("temperature")
  tools_param = _resolve_tools_param("openai", model_name, config.get("tools"))

  return _make_hook(client, "openai", model_name, reasoning_effort,
                    temperature, tools_param, budget, usage_log, prompt_log)


def _build_ai_hook(config: dict, budget: int, usage_log: dict[tuple[int, int], dict],
                   prompt_log: dict[tuple[int, int], str]) -> Callable:
  engine = config.get("engine")
  if engine in ("azure_openai", "azure-openai"):
    return _build_azure_hook(config, budget, usage_log, prompt_log)
  if engine == "openai":
    return _build_openai_hook(config, budget, usage_log, prompt_log)
  raise ValueError(f"Unsupported engine for this experiment runner: {engine}")


def _rate(count: int, total: int) -> float:
  if total <= 0:
    return 0.0
  return count / total



def _update_diagnostics(diagnostics: dict[str, int], meta: dict | None, budget: int) -> None:
  diagnostics["subpasses_total"] += 1
  if not isinstance(meta, dict):
    diagnostics["missing_meta_count"] += 1
    return

  diagnostics["subpasses_with_meta"] += 1

  if int(meta.get("output_text_chars", 0) or 0) == 0:
    diagnostics["empty_output_count"] += 1

  status = str(meta.get("status", ""))
  if status == "error" or meta.get("error"):
    diagnostics["api_error_count"] += 1

  if status and status != "completed":
    diagnostics["non_completed_count"] += 1

  if status == "incomplete" or meta.get("incomplete_reason"):
    diagnostics["incomplete_response_count"] += 1

  usage = meta.get("usage")
  if not isinstance(usage, dict):
    return

  output_tokens = _coerce_int(usage.get("output_tokens"))
  reasoning_tokens = _coerce_int(usage.get("reasoning_tokens"))

  if output_tokens is not None and output_tokens >= int(budget):
    diagnostics["budget_cap_hit_count"] += 1

  if output_tokens is not None and reasoning_tokens is not None and output_tokens == reasoning_tokens:
    diagnostics["reasoning_equals_output_count"] += 1


def _run_single_model_config(config: dict, test_ids: list[int]) -> Path:
  model_name = config["name"]
  budget = int(config["max_output_tokens"])

  env_key = config.get("env_key")
  if env_key and not os.environ.get(env_key):
    raise RuntimeError(f"Required env var not set for {model_name}: {env_key}")

  rp.ensure_global_result_dirs()
  rp.ensure_model_dirs(model_name)

  usage_log: dict[tuple[int, int], dict] = {}
  prompt_log: dict[tuple[int, int], str] = {}
  ai_hook = _build_ai_hook(config, budget, usage_log, prompt_log)

  previous_force = tr.FORCE_ARG
  tr.FORCE_ARG = True

  tests_summary: list[dict] = []
  overall_total_score = 0.0
  overall_max_score = 0
  diagnostics = {
    "subpasses_total": 0,
    "subpasses_with_meta": 0,
    "missing_meta_count": 0,
    "empty_output_count": 0,
    "api_error_count": 0,
    "non_completed_count": 0,
    "incomplete_response_count": 0,
    "budget_cap_hit_count": 0,
    "reasoning_equals_output_count": 0,
  }

  print(f"[{model_name}] Starting budget run with max_output_tokens={budget}")

  try:
    for test_id in test_ids:
      test_title, expected_subpass_indices = _inspect_test(test_id)
      print(
        f"[{model_name}] Test {test_id}: {test_title} "
        f"(expected subpasses={len(expected_subpass_indices)})"
      )

      test_result = tr.runTest(test_id, ai_hook, model_name)
      subpass_results = list(test_result.get("subpass_results", []))
      subpass_results.sort(key=lambda subpass: int(subpass.get("subpass", 0)))

      subpasses_summary = []
      for subpass in subpass_results:
        subpass_idx = int(subpass.get("subpass", 0))
        key = (test_id, subpass_idx)
        score_value = safe_float(subpass.get("score"), default=0.0)

        effective_prompt = prompt_log.get(key)
        if effective_prompt is not None:
          prompt_path = Path(rp.model_prompt_path(model_name, test_id, subpass_idx))
          prompt_path.parent.mkdir(parents=True, exist_ok=True)
          prompt_path.write_text(effective_prompt, encoding="utf-8")

        subpass_entry = {
          "subpass": subpass_idx,
          "score": subpass.get("score"),
          "scoreExplanation": subpass.get("scoreExplanation"),
        }

        meta = usage_log.get(key)
        if meta is not None:
          subpass_entry["meta"] = meta
          if isinstance(meta.get("usage"), dict):
            subpass_entry["usage"] = meta.get("usage")
          _write_json(_model_meta_path(model_name, test_id, subpass_idx), meta)

        _update_diagnostics(diagnostics, meta, budget)
        status = meta.get("status") if isinstance(meta, dict) else "missing-meta"
        usage = meta.get("usage") if isinstance(meta, dict) else None
        output_tokens = usage.get("output_tokens") if isinstance(usage, dict) else None
        elapsed_ms = meta.get("elapsed_ms") if isinstance(meta, dict) else None
        print(
          f"[{model_name}] Q{test_id} subpass #{subpass_idx} done "
          f"score={score_value:.2f} status={status} output_tokens={output_tokens} elapsed_ms={elapsed_ms}"
        )

        subpasses_summary.append(subpass_entry)

      test_score = safe_float(test_result.get("total_score"), default=0.0)
      max_score = int(test_result.get("subpass_count", len(subpass_results)))
      overall_total_score += test_score
      overall_max_score += max_score

      tests_summary.append({
        "test_index": test_id,
        "title": test_title,
        "score": test_score,
        "max_score": max_score,
        "subpass_count": max_score,
        "subpasses": subpasses_summary,
      })
  finally:
    tr.FORCE_ARG = previous_force

  run_context = {
    "engine": config.get("engine"),
    "base_model": config.get("base_model"),
    "reasoning": config.get("reasoning"),
    "tools": config.get("tools"),
    "max_output_tokens": config.get("max_output_tokens"),
    "budget_informed_tokens": config.get("budget_informed_tokens"),
    "temperature": config.get("temperature"),
    "experiment_tag": config.get("experiment_tag"),
  }

  total_subpasses = diagnostics["subpasses_total"]
  diagnostics_summary = {
    **diagnostics,
    "empty_output_rate": _rate(diagnostics["empty_output_count"], total_subpasses),
    "api_error_rate": _rate(diagnostics["api_error_count"], total_subpasses),
    "non_completed_rate": _rate(diagnostics["non_completed_count"], total_subpasses),
    "incomplete_response_rate": _rate(diagnostics["incomplete_response_count"], total_subpasses),
    "budget_cap_hit_rate": _rate(diagnostics["budget_cap_hit_count"], total_subpasses),
    "reasoning_equals_output_rate": _rate(diagnostics["reasoning_equals_output_count"], total_subpasses),
    "missing_meta_rate": _rate(diagnostics["missing_meta_count"], total_subpasses),
  }

  run_summary = {
    "model_name": model_name,
    "run_context": run_context,
    "overall": {
      "total_score": overall_total_score,
      "max_score": overall_max_score,
      "accuracy": overall_total_score / overall_max_score if overall_max_score > 0 else 0.0,
      "percentage": (overall_total_score / overall_max_score * 100.0)
      if overall_max_score > 0 else 0.0,
    },
    "diagnostics": diagnostics_summary,
    "tests": tests_summary,
  }

  summary_path = model_run_summary_path(model_name)
  _write_json(summary_path, run_summary)
  return summary_path


def run_axiomatic_budget_sweep(model_config_name: str = DEFAULT_BASE_MODEL_CONFIG_NAME,
                               budgets: Iterable[int] = BUDGETS,
                               temperature: float | None = None,
                               include_tools: bool = True,
                               include_no_tools: bool = True,
                               dry_run: bool = False) -> dict[str, Path | list[dict]]:
  budget_list = [int(b) for b in budgets]
  model_configs = build_budget_model_configs(model_config_name=model_config_name,
                                             budgets=budget_list,
                                             temperature=temperature,
                                             include_tools=include_tools,
                                             include_no_tools=include_no_tools,
                                             experiment_tag=EXPERIMENT_TAG)
  test_filter = build_axiomatic_test_filter()
  test_ids = sorted(int(test_id) for test_id in test_filter.keys())

  repo_root = Path(__file__).resolve().parents[2]
  manifest = build_manifest(repo_root=repo_root,
                            model_configs=_manifest_model_config_snapshot(model_configs),
                            budgets=budget_list,
                            test_ids=test_ids,
                            experiment_name=EXPERIMENT_NAME,
                            experiment_tag=EXPERIMENT_TAG)
  manifest_path = write_manifest(RESULTS_DIR / "manifest.json", manifest)

  if not dry_run:
    for cfg in model_configs:
      _run_single_model_config(cfg, test_ids)

  return {
    "manifest": manifest_path,
    "model_configs": model_configs,
    "results_dir": RESULTS_DIR,
  }
