import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def _git_value(repo_dir: Path, *args: str) -> str | None:
  try:
    out = subprocess.run(["git", *args], cwd=str(repo_dir), check=True, capture_output=True, text=True)
    return out.stdout.strip()
  except Exception:
    return None


def collect_git_state(repo_root: Path) -> dict[str, Any]:
  llmbenchcore_dir = repo_root / "LLMBenchCore"
  return {
    "meshbenchmark": {
      "branch": _git_value(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
      "commit": _git_value(repo_root, "rev-parse", "HEAD"),
    },
    "llmbenchcore": {
      "branch": _git_value(llmbenchcore_dir, "rev-parse", "--abbrev-ref", "HEAD")
      if llmbenchcore_dir.exists() else None,
      "commit": _git_value(llmbenchcore_dir, "rev-parse", "HEAD") if llmbenchcore_dir.exists() else None,
    },
  }


def collect_env_flags() -> dict[str, bool]:
  keys = [
    "OPENAI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
  ]
  return {key: bool(os.environ.get(key)) for key in keys}


def build_manifest(*,
                   repo_root: Path,
                   model_configs: list[dict],
                   budgets: list[int],
                   test_ids: list[int],
                   experiment_name: str,
                   experiment_tag: str) -> dict[str, Any]:
  return {
    "experiment_name": experiment_name,
    "experiment_tag": experiment_tag,
    "generated_at": datetime.now().isoformat(),
    "budgets": budgets,
    "test_ids": test_ids,
    "model_configs": model_configs,
    "git": collect_git_state(repo_root),
    "environment": collect_env_flags(),
  }


def write_manifest(path: Path, manifest: dict[str, Any]) -> Path:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
  return path
