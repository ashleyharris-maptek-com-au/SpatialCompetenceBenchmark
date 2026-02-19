#!/usr/bin/env python3
"""
MeshBenchmark - Spatial/Geometry LLM Benchmark

This is the main entry point for the Mesh Benchmark suite, which tests
LLM capabilities in spatial reasoning, geometry, and 3D visualization.

This extends the abstract TestRunner framework with spatial-specific:
- OpenSCAD volume comparison scoring
- 3D model reference building
- Spatial benchmark metadata
"""

# IMPORTANT: Set up sys.path BEFORE any other imports so submodules can be found
import atexit
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if VGB_ROOT.is_dir() and str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from typing import Dict, Any

from LLMBenchCore import BenchmarkRunner, run_benchmark_main
from LLMBenchCore.AiEnginePlacebo import set_placebo_data_provider
import placebo_data

_RUNTIME_TASK_SHIM_PREFIX = "# Auto-generated runtime task shim. Do not commit."


def _ensure_runtime_task_shims() -> list[Path]:
  created: list[Path] = []
  for task_index in range(1, 58):
    shim_path = REPO_ROOT / f"{task_index}.py"
    if shim_path.exists():
      continue
    shim_path.write_text(
      _RUNTIME_TASK_SHIM_PREFIX + "\n"
      "from _task_loader import load_task\n\n"
      f'load_task("{task_index}.py", globals())\n',
      encoding="utf-8",
    )
    created.append(shim_path)
  return created


def _cleanup_runtime_task_shims(paths: list[Path]) -> None:
  for path in paths:
    path.unlink(missing_ok=True)


class MeshBenchmarkRunner(BenchmarkRunner):
  """
  Mesh Benchmark runner for spatial/geometry LLM testing.
  
  Implements OpenSCAD-based volume comparison scoring and
  spatial-specific benchmark metadata.
  """

  def get_benchmark_title(self) -> str:
    return "Mesh Benchmark Results"

  def get_benchmark_subtitle(self) -> str:
    return "Model Evaluation of Spatial Heuristics."

  def get_benchmark_description(self) -> str:
    return "<p>Can LLMs use internal visualisation or spatial reasoning to solve problems?</p>"

  def can_handle_custom_scoring(self, test_globals: dict) -> bool:
    """Check if test uses OpenSCAD reference comparison."""
    return "referenceScad" in test_globals or "prepareSubpassReferenceScad" in test_globals

  def process_custom_scoring(self, index: int, subPass: int, result: Any, test_globals: dict,
                             aiEngineName: str) -> Dict[str, Any]:
    """
    Process OpenSCAD volume comparison scoring.
    
    Compares the AI's generated shape against reference OpenSCAD models
    by computing volume intersection/difference.
    """
    # Import lazily so OpenSCAD isn't required for non-geometry tests.
    import VolumeComparison
    return VolumeComparison.compareVolumeAgainstOpenScad(index, subPass, result, test_globals,
                                                         aiEngineName)

  def run_setup_for_test(self, test_index: int, test_globals: dict) -> None:
    """Build OpenSCAD reference models during setup."""
    if "prepareSubpassReferenceScad" in test_globals:
      print(f"    Building OpenSCAD reference models...")
      subpass = 0
      while True:
        try:
          out = test_globals["prepareSubpassReferenceScad"](subpass)
          subpass += 1
          if out is None or out == "":
            break
        except StopIteration:
          break
        except Exception as e:
          print(f"    Warning: Reference build for subpass {subpass} failed: {e}")
          break

      print(f"    Built {subpass} reference models")
    placebo_data.cache_solutions(test_index)


if __name__ == "__main__":
  generated_shims = _ensure_runtime_task_shims()
  atexit.register(_cleanup_runtime_task_shims, generated_shims)
  set_placebo_data_provider(["always-wrong", "human-with-tools", "guessing"],
                            placebo_data.get_response)
  runner = MeshBenchmarkRunner()
  run_benchmark_main(runner, __file__)
