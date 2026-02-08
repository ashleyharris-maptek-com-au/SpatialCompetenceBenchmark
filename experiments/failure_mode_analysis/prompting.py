from __future__ import annotations

from .schemas import EvidenceRow, FAILURE_MODES


SYSTEM_PROMPT = (
  "You are a strict failure-mode judge for visual geometry benchmark tasks. "
  "Use only the provided task card and evidence. "
  "Return valid JSON that matches the requested schema."
)

def build_task_batch_prompt(task_card_markdown: str,
                            rows: list[EvidenceRow]) -> str:
  if not rows:
    raise ValueError("rows must be non-empty")

  attempts_lines = []
  for row in rows:
    raw_text = (row.raw_text or "").strip()
    cot_text = (row.cot_text or "").strip()
    attempts_lines.extend([
      f"### Subpass {row.subpass}",
      "",
      "Attempt Metadata:",
      f"- question_id: {row.test_index}",
      f"- subpass: {row.subpass}",
      f"- score: {row.score}",
      f"- status: {row.status}",
      f"- incomplete_reason: {row.incomplete_reason}",
      f"- output_text_chars: {row.output_text_chars}",
      "",
      "Verifier Signal:",
      row.score_explanation or "(none)",
      "",
      "Raw Output:",
      raw_text or "(none)",
      "",
      "Chain of Thought:",
      cot_text or "(none)",
      "",
    ])

  attempts_block = "\n".join(attempts_lines).rstrip()
  subpasses = ", ".join(str(r.subpass) for r in rows)
  labels_block = "\n".join(f"- {label}" for label in FAILURE_MODES)

  return (
    "Classify each attempt below into exactly one failure mode.\n\n"
    "Allowed labels:\n"
    f"{labels_block}\n\n"
    "Rules:\n"
    "- You must output one decision per listed subpass.\n"
    f"- Listed subpasses: {subpasses}\n"
    "- Base justification on verifier signals and model output/COT evidence.\n"
    "- Do not invent constraints absent from the task card.\n\n"
    "Task Card:\n"
    f"{task_card_markdown}\n\n"
    "Attempts:\n"
    f"{attempts_block}\n"
  )
