"""Compatibility loader for task shims.

LLMBenchCore expects numbered task files (1.py..57.py) at repository root.
This loader keeps that interface stable while real task implementations live in
`tasks/`.
"""

from __future__ import annotations

from pathlib import Path


def load_task(stub_name: str, target_globals: dict) -> None:
  """Execute the real task file from `tasks/` into target globals."""
  repo_root = Path(__file__).resolve().parent
  task_path = repo_root / "tasks" / stub_name
  if not task_path.exists():
    task_path = repo_root / "tasks" / "deprecated" / stub_name
  if not task_path.exists():
    raise FileNotFoundError(f"Missing task file: {task_path}")

  # Preserve LLMBenchCore semantics where __file__ is the numbered root script.
  target_globals.setdefault("__file__", stub_name)

  code = task_path.read_text(encoding="utf-8")
  compiled = compile(code, str(task_path), "exec")
  exec(compiled, target_globals)
