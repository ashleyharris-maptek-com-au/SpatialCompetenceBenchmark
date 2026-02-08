from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

from .failure_mode_task_cards.paths import get_task_card_path
from .prompting import SYSTEM_PROMPT, build_task_batch_prompt
from .schemas import (AnalysisConfig, EvidenceRow, FAILURE_MODES, FAILURE_MODE_SET, JudgeDecision, JUDGE_STATUS_ERROR,
                      JUDGE_STATUS_OK, RowKey)

_BATCH_SCHEMA = {
  "type": "object",
  "additionalProperties": False,
  "required": ["decisions"],
  "properties": {
    "decisions": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["subpass", "failure_mode", "confidence", "justification", "evidence_tags"],
        "properties": {
          "subpass": {"type": "integer", "minimum": 0},
          "failure_mode": {"type": "string", "enum": list(FAILURE_MODES)},
          "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "justification": {"type": "string", "minLength": 1},
          "evidence_tags": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        },
      },
    }
  },
}

_TASK_GROUP_MAX_WORKERS = 4


def _make_llmbenchcore_engine(config: AnalysisConfig):
  timeout = max(1, int(config.judge_timeout_seconds))

  if config.judge_engine in {"azure-openai", "azure_openai"}:
    from LLMBenchCore.AiEngineAzureOpenAI import AzureOpenAIEngine

    return AzureOpenAIEngine(model=config.judge_model,
                             reasoning=config.judge_reasoning,
                             tools=False,
                             timeout=timeout,
                             max_output_tokens=config.judge_max_output_tokens,
                             temperature=config.judge_temperature,
                             emit_meta=True)

  if config.judge_engine == "openai":
    from LLMBenchCore.AiEngineOpenAiChatGPT import OpenAIEngine

    return OpenAIEngine(model=config.judge_model,
                        reasoning=config.judge_reasoning,
                        tools=False,
                        timeout=timeout,
                        max_output_tokens=config.judge_max_output_tokens,
                        temperature=config.judge_temperature,
                        emit_meta=True)

  raise ValueError(f"Unsupported judge engine: {config.judge_engine}")


@lru_cache(maxsize=256)
def _get_task_card_markdown(run_name: str, test_index: int) -> str:
  task_card_path = get_task_card_path(run_name, test_index)
  return task_card_path.read_text(encoding="utf-8")


def _extract_engine_output(result) -> tuple[object, str, dict]:
  if not isinstance(result, tuple):
    return result, "", {}
  if len(result) == 3:
    return result[0], result[1], result[2]
  if len(result) == 2:
    return result[0], result[1], {}
  return result[0] if result else {}, "", {}


def _validate_batch_payload(payload: dict, expected_subpasses: set[int]) -> dict[int, tuple[str, float, str, list[str]]]:
  if not isinstance(payload, dict):
    raise ValueError("payload must be an object")

  decisions = payload.get("decisions")
  if not isinstance(decisions, list) or not decisions:
    raise ValueError("payload.decisions must be a non-empty list")

  by_subpass: dict[int, tuple[str, float, str, list[str]]] = {}
  for item in decisions:
    if not isinstance(item, dict):
      raise ValueError("decision item must be an object")

    subpass = item.get("subpass")
    if not isinstance(subpass, int):
      raise ValueError("decision.subpass must be an integer")

    mode = item.get("failure_mode")
    if mode not in FAILURE_MODE_SET:
      raise ValueError(f"Invalid failure_mode: {mode}")

    confidence = item.get("confidence")
    if not isinstance(confidence, (int, float)):
      raise ValueError("confidence must be numeric")
    confidence_value = float(confidence)
    if confidence_value < 0.0 or confidence_value > 1.0:
      raise ValueError("confidence must be in [0,1]")

    justification = item.get("justification")
    if not isinstance(justification, str) or not justification.strip():
      raise ValueError("justification must be non-empty")

    evidence_tags = item.get("evidence_tags")
    if not isinstance(evidence_tags, list):
      raise ValueError("evidence_tags must be a list")
    normalized_tags = [str(tag).strip() for tag in evidence_tags if str(tag).strip()]

    if subpass in by_subpass:
      raise ValueError(f"Duplicate decision for subpass={subpass}")

    by_subpass[subpass] = (mode, confidence_value, justification.strip(), normalized_tags)

  missing = expected_subpasses - set(by_subpass.keys())
  extra = set(by_subpass.keys()) - expected_subpasses
  if missing:
    raise ValueError(f"Missing decisions for subpasses: {sorted(missing)}")
  if extra:
    raise ValueError(f"Unexpected decisions for subpasses: {sorted(extra)}")

  return by_subpass


def _trace_base_name(rows: list[EvidenceRow]) -> str:
  first = rows[0]
  subpasses = [row.subpass for row in rows]
  if len(subpasses) == 1:
    return f"{first.model_name}_{first.test_index}_sp{subpasses[0]}"

  contiguous = subpasses == list(range(subpasses[0], subpasses[-1] + 1))
  if contiguous:
    return f"{first.model_name}_{first.test_index}_sp{subpasses[0]}-{subpasses[-1]}"
  return f"{first.model_name}_{first.test_index}_sp{'_'.join(str(subpass) for subpass in subpasses)}"


def _write_task_trace(rows: list[EvidenceRow],
                      prompt: str,
                      output: object,
                      chain_of_thought: str,
                      config: AnalysisConfig) -> None:
  if not rows or not config.judge_trace_dir:
    return

  trace_dir = Path(config.judge_trace_dir)
  prompt_dir = trace_dir / "prompts"
  raw_dir = trace_dir / "raw"
  cot_dir = trace_dir / "cot"
  prompt_dir.mkdir(parents=True, exist_ok=True)
  raw_dir.mkdir(parents=True, exist_ok=True)
  cot_dir.mkdir(parents=True, exist_ok=True)

  if isinstance(output, str):
    raw_text = output
  else:
    try:
      raw_text = json.dumps(output, ensure_ascii=False, indent=2)
    except Exception:
      raw_text = str(output)

  cot_text = str(chain_of_thought or "")
  prompt_text = str(prompt)

  base_name = _trace_base_name(rows)
  (prompt_dir / f"{base_name}.txt").write_text(prompt_text, encoding="utf-8")
  (raw_dir / f"{base_name}.txt").write_text(raw_text, encoding="utf-8")
  (cot_dir / f"{base_name}.txt").write_text(cot_text, encoding="utf-8")


def _judge_task_rows(engine, rows: list[EvidenceRow], config: AnalysisConfig) -> dict[RowKey, JudgeDecision]:
  if not rows:
    return {}

  task_card_markdown = _get_task_card_markdown(config.run_name, rows[0].test_index)
  user_prompt = build_task_batch_prompt(task_card_markdown=task_card_markdown, rows=rows)
  prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

  expected_subpasses = {r.subpass for r in rows}
  last_error: str | None = None
  last_output: object = {}
  last_chain_of_thought = ""
  for _ in range(max(1, int(config.judge_retries) + 1)):
    try:
      output, chain_of_thought, _meta = _extract_engine_output(engine.AIHook(prompt, _BATCH_SCHEMA))
      last_output = output
      last_chain_of_thought = chain_of_thought
      if not isinstance(output, dict):
        raise ValueError("Engine returned non-object structured output")
      by_subpass = _validate_batch_payload(output, expected_subpasses)
      _write_task_trace(rows, prompt, output, chain_of_thought, config)

      out: dict[RowKey, JudgeDecision] = {}
      for row in rows:
        mode, confidence, justification, evidence_tags = by_subpass[row.subpass]
        out[row.key] = JudgeDecision(key=row.key,
                                     judge_status=JUDGE_STATUS_OK,
                                     failure_mode=mode,
                                     confidence=confidence,
                                     justification=justification,
                                     evidence_tags=evidence_tags,
                                     judge_error=None,
                                     judge_model=config.judge_model,
                                     judge_engine=config.judge_engine,
                                     prompt_version=config.prompt_version)
      return out
    except Exception as exc:
      last_error = str(exc)

  _write_task_trace(rows,
                    prompt,
                    {"error": last_error or "judge_call_failed", "output": last_output},
                    last_chain_of_thought,
                    config)

  out: dict[RowKey, JudgeDecision] = {}
  for row in rows:
    out[row.key] = JudgeDecision(key=row.key,
                                 judge_status=JUDGE_STATUS_ERROR,
                                 failure_mode=None,
                                 confidence=None,
                                 justification=None,
                                 evidence_tags=[],
                                 judge_error=last_error or "judge_call_failed",
                                 judge_model=config.judge_model,
                                 judge_engine=config.judge_engine,
                                 prompt_version=config.prompt_version)
  return out


def _judge_task_group(rows: list[EvidenceRow], config: AnalysisConfig) -> dict[RowKey, JudgeDecision]:
  max_batch = config.judge_max_batch_subpasses
  decisions: dict[RowKey, JudgeDecision] = {}
  for i in range(0, len(rows), max_batch):
    sub_batch = rows[i:i + max_batch]
    decisions.update(_judge_task_rows(_make_llmbenchcore_engine(config), sub_batch, config))
  return decisions


def classify_rows(rows: list[EvidenceRow], config: AnalysisConfig) -> dict[RowKey, JudgeDecision]:
  if not rows:
    return {}

  rows_by_task: dict[tuple[str, int], list[EvidenceRow]] = {}
  for row in rows:
    rows_by_task.setdefault((row.model_name, row.test_index), []).append(row)

  task_groups = [sorted(rows_by_task[key], key=lambda row: row.subpass) for key in sorted(rows_by_task)]

  def _judge_group(task_rows: list[EvidenceRow]) -> dict[RowKey, JudgeDecision]:
    return _judge_task_group(task_rows, config)

  with ThreadPoolExecutor(max_workers=_TASK_GROUP_MAX_WORKERS) as pool:
    task_results = list(pool.map(_judge_group, task_groups))

  decisions: dict[RowKey, JudgeDecision] = {}
  for task_decisions in task_results:
    decisions.update(task_decisions)

  return decisions
