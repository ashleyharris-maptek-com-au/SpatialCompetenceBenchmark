from __future__ import annotations

from dataclasses import dataclass


FAILURE_MODE_EVASION = "Evasion / Forfeit"
FAILURE_MODE_TRIVIALIZED = "Trivialized / Misframed"
FAILURE_MODE_RUNAWAY = "Runaway Overthinking"
FAILURE_MODE_LOCAL_ONLY = "Local-Only (Global Constraint Integration Failure)"
FAILURE_MODE_NEAR_MISS = "Near-Miss Edge Case"

FAILURE_MODES = (
  FAILURE_MODE_EVASION,
  FAILURE_MODE_TRIVIALIZED,
  FAILURE_MODE_RUNAWAY,
  FAILURE_MODE_LOCAL_ONLY,
  FAILURE_MODE_NEAR_MISS,
)

FAILURE_MODE_SET = set(FAILURE_MODES)
JUDGE_STATUS_OK = "ok"
JUDGE_STATUS_ERROR = "error"
JUDGE_STATUS_NOT_SELECTED = "not_selected"

RowKey = tuple[str, int, int]


@dataclass(frozen=True)
class AnalysisConfig:
  run_name: str
  low_score_threshold: float = 0.6
  judge_engine: str = "azure-openai"
  judge_model: str = ""
  judge_reasoning: int = 5
  judge_timeout_seconds: float = 180.0
  judge_temperature: float | None = None
  judge_max_output_tokens: int = 16384
  judge_retries: int = 2
  prompt_version: str = "failure-mode-judge-v1"
  judge_max_batch_subpasses: int = 5
  judge_trace_dir: str | None = None


@dataclass(frozen=True)
class EvidenceRow:
  model_name: str
  test_index: int
  test_title: str
  subpass: int
  score: float
  status: str | None
  incomplete_reason: str | None
  output_tokens: float | None
  output_text_chars: int
  score_explanation: str
  raw_path: str | None
  cot_path: str | None
  prompt_path: str | None
  raw_text: str | None
  cot_text: str | None

  @property
  def key(self) -> RowKey:
    return (self.model_name, self.test_index, self.subpass)


@dataclass(frozen=True)
class JudgeDecision:
  key: RowKey
  judge_status: str
  failure_mode: str | None
  confidence: float | None
  justification: str | None
  evidence_tags: list[str]
  judge_error: str | None
  judge_model: str
  judge_engine: str
  prompt_version: str


@dataclass(frozen=True)
class LabeledRow(EvidenceRow):
  candidate_for_judge: bool
  judge_status: str
  failure_mode: str | None
  confidence: float | None
  justification: str | None
  evidence_tags: list[str]
  judge_error: str | None
  judge_model: str
  judge_engine: str
  prompt_version: str
