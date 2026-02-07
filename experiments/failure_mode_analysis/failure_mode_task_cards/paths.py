from __future__ import annotations

from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent


def get_default_run_name() -> str:
  cards_dir = _BASE_DIR / "cards"
  if not cards_dir.is_dir():
    raise FileNotFoundError(f"Missing cards directory: {cards_dir}")

  run_dirs = sorted([p.name for p in cards_dir.iterdir() if p.is_dir() and not p.name.startswith(".")])
  if not run_dirs:
    raise ValueError(f"No run directories found under {cards_dir}")
  if len(run_dirs) > 1:
    raise ValueError(f"Multiple run directories found under {cards_dir}: {run_dirs}")
  return run_dirs[0]


def get_task_card_path(run_name: str, question_id: int) -> Path:
  run_dir = _BASE_DIR / "cards" / run_name
  if not run_dir.is_dir():
    raise FileNotFoundError(f"Unknown run_name '{run_name}' (missing dir: {run_dir})")

  prefix = f"q{int(question_id):02d}_"
  matches = sorted(run_dir.glob(f"{prefix}*.md"))
  if len(matches) != 1:
    raise FileNotFoundError(
      f"Expected exactly 1 card for question_id={question_id} under {run_dir}, found {len(matches)}"
    )
  return matches[0]
