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

from typing import Dict, Any

from LLMBenchCore import BenchmarkRunner, run_benchmark_main
from LLMBenchCore.AiEnginePlacebo import set_placebo_data_provider
import placebo_data


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
  set_placebo_data_provider(["always-wrong", "human-with-tools", "guessing"],
                            placebo_data.get_response)
  runner = MeshBenchmarkRunner()
  run_benchmark_main(runner, __file__)
