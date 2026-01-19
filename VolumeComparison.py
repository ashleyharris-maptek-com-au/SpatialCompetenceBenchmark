import scad_format
import tempfile
import StlVolume
import os
import hashlib
import json
import traceback
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import OpenScad
from OpenScad import openScadPath, formatConfig, run_openscad, render_stl_to_png, render_scadText_to_png, hit_tests, TimeoutError


def compareVolumeAgainstOpenScad(index: int, subPass: int, result, testGlobals: dict,
                                 aiEngineName: str) -> Dict[str, Any]:
  """
    Compare a test result against a reference OpenSCAD model by computing volumes.
    
    Returns a dictionary containing:
        - 'score': float (0.0 to 1.0)
        - 'output_image': path to PNG of output STL
        - 'reference_image': path to PNG of reference STL
    """
  resultToScad = testGlobals["resultToScad"]

  if "prepareSubpassReferenceScad" in testGlobals:
    referenceScad = testGlobals["prepareSubpassReferenceScad"](subPass)
  else:
    referenceScad = testGlobals["referenceScad"]

  if "earlyFailTest" in testGlobals:
    reason = testGlobals["earlyFailTest"](result, subPass)
    if reason:
      return {
        "score": 0,
        "output_image": None,
        "output_mouseover_image": None,
        "output_hyperlink": None,
        "reference_image": None,
        "temp_dir": None,
        "scoreExplanation": "Early failure: " + reason,
      }

  try:
    resultAsScad = resultToScad(result, aiEngineName)
  except Exception as e:
    print("Result to scad threw: " + str(e))
    traceback.print_exc()
    return {
      "score": 100000,  # Not an AI failure, framework failure.
      "output_image": None,
      "output_mouseover_image": None,
      "output_hyperlink": None,
      "reference_image": None,
      "temp_dir": None,
      "scoreExplanation": "Exception: " + str(e) + " in resultToScad",
    }

  if resultAsScad == "" or resultAsScad is None:
    return {
      "score": 0,
      "output_image": None,
      "output_mouseover_image": None,
      "output_hyperlink": resultAsScad,
      "reference_image": None,
      "temp_dir": None,
      "scoreExplanation": "Result was empty",
    }

  scadModules = testGlobals.get("scadModules", "")

  # Generate separate cache keys for reference (stable) and result (changes often)
  reference_cache_key = _compute_reference_cache_key(referenceScad, scadModules)
  result_cache_key = _compute_result_cache_key(resultAsScad, reference_cache_key)

  # Reference cache directory (for reference.stl, reference.png)
  reference_cache_dir = os.path.join(tempfile.gettempdir(), "mesh_benchmark_cache", "ref",
                                     reference_cache_key)

  # Result cache directory (for comparison results)
  result_cache_dir = os.path.join(tempfile.gettempdir(), "mesh_benchmark_cache", "res",
                                  result_cache_key)
  cache_meta_path = os.path.join(result_cache_dir, "cache_meta.json")

  # Check for result cache hit
  if os.path.exists(cache_meta_path):
    cached = _load_cache(cache_meta_path)
    if cached is not None:
      print(f"Cache hit for result {result_cache_key[:12]}...")
      if "scoreExplanation" not in cached:
        cached["scoreExplanation"] = ""
      cached["scoreExplanation"] += "Results were <a href='" + cache_meta_path + "'>cached</a>."
      return cached

  # Create cache directories
  os.makedirs(reference_cache_dir, exist_ok=True)
  os.makedirs(result_cache_dir, exist_ok=True)
  temp_dir = result_cache_dir

  # Define all file paths
  # Reference files go in reference cache (stable, reused across results)
  reference_scad_file = os.path.join(reference_cache_dir, "reference.scad")
  reference_stl = os.path.join(reference_cache_dir, "reference.stl")
  reference_png = os.path.join(reference_cache_dir, "reference.png")

  # Result/comparison files go in result cache (specific to this comparison)
  result_scad = os.path.join(temp_dir, "result.scad")
  resultWithReference_scad = os.path.join(temp_dir, "resultWithReference.scad")
  compare1_scad = os.path.join(temp_dir, "compare1.scad")
  compare2_scad = os.path.join(temp_dir, "compare2.scad")

  output_stl = os.path.join(temp_dir, "output.stl")
  intersection_stl = os.path.join(temp_dir, "intersection.stl")
  difference_stl = os.path.join(temp_dir, "difference.stl")

  output_png = os.path.join(temp_dir, "output.png")
  output2_png = os.path.join(temp_dir, "output2.png")

  # Write SCAD files
  if "minkowski" not in resultAsScad and "minkowski" not in testGlobals.get(
      "scadModules", "") and "noMinkowski" not in testGlobals:
    _write_scad_file(result_scad, resultAsScad, testGlobals.get("scadModules", ""),
                     "minkowski(){cube(0.001);result();}")
  else:
    _write_scad_file(result_scad, resultAsScad, testGlobals.get("scadModules", ""),
                     "cube(0.001);result();")

  if "noMinkowski" not in testGlobals:
    suffix = "minkowski(){cube(0.001);result();}\n" + """
color([1,0,0,0.8])
minkowski(){
    cube(0.001);
    difference() {
        union() {
            result();   
            reference();
        }   
        result();
    }
}"""
  else:
    suffix = "result();\n" + """
color([1,0,0,0.8])
{
    difference() {
        union() {
            result();   
            reference();
        }   
        result();
    }
}"""

  _write_scad_file(resultWithReference_scad, resultAsScad + "\n" + referenceScad,
                   testGlobals.get("scadModules"), suffix)

  # Write reference SCAD only if not already cached
  if not os.path.exists(reference_scad_file):
    _write_scad_file(reference_scad_file, referenceScad, testGlobals.get("scadModules"),
                     "minkowski(){cube(0.001);reference();}")

  # Write comparison SCAD files (use absolute path to reference since it's in different dir)
  reference_scad_abs = reference_scad_file.replace("\\", "/")

  with open(compare1_scad, "w", encoding="utf-8") as f:
    f.write(f"use <result.scad>;\n")
    f.write(f"use <{reference_scad_abs}>;\n")
    if "scadModules" in testGlobals:
      f.write(testGlobals["scadModules"])

    if "noMinkowski" not in testGlobals:
      f.write("  minkowski()")

    f.write("{")
    if "noMinkowski" not in testGlobals: f.write("    cube(0.001);")
    f.write("""
    intersection() {
        result();
        reference();
    }
}""")

  with open(compare2_scad, "w", encoding="utf-8") as f:
    f.write(f"use <result.scad>;\n")
    f.write(f"use <{reference_scad_abs}>;\n")
    if "scadModules" in testGlobals:
      f.write(testGlobals["scadModules"])

    if "noMinkowski" not in testGlobals:
      f.write("  minkowski()")

    f.write("{")
    if "noMinkowski" not in testGlobals: f.write("    cube(0.001);")
    f.write("""
    difference() {
        union() {
            result();   
            reference();
        }   
        intersection() {
            result();
            reference();
        }        
    }
}""")

  # Generate STL files
  print(f"Generating STL files in {temp_dir}...")
  openscad_errors = []

  # Generate reference STL only if not already cached
  if not os.path.exists(reference_stl):
    print(f"Building reference STL (not cached)...")
    try:
      err = _run_openscad(reference_scad_file, reference_stl, timeout=900)
    except:
      err = "Timeout generating reference stl"
    if err:
      openscad_errors.append(err)
  else:
    print(f"Using cached reference STL: {reference_cache_key[:12]}...")

  # Run result SCAD with 10min timeout - complex/infinite renders get aborted
  try:
    err = _run_openscad(result_scad, output_stl, timeout=600)
  except:
    err = "Timeout"
  if err:
    try:
      openscad_errors.append(
        f"Error {err}. Attempting to rendering without minkowski - this can create non-watertight"
        "meshes.")
      _write_scad_file(result_scad, resultAsScad, testGlobals.get("scadModules"),
                       "union(){result();}")

      err = _run_openscad(result_scad, output_stl, timeout=600)
      if err:
        openscad_errors.append("When running without minkowski:" + str(err))

    except TimeoutError as e:
      cache = {
        "score": 0,
        "output_image": None,
        "output_mouseover_image": None,
        "output_hyperlink": result_scad,
        "reference_image": reference_png if os.path.exists(reference_png) else None,
        "temp_dir": temp_dir,
        "scoreExplanation": f"<div style='color:red;'>Render timeout: {e}</div>",
      }
      _save_cache(cache_meta_path, cache)
      return cache

  # Generate PNG images with off-axis camera
  print(f"Rendering PNG images...")
  _render_stl_to_png(output_stl, output_png)

  if "lateFailTest" in testGlobals:
    failureReason = testGlobals["lateFailTest"](result, subPass)

    if failureReason:
      result_dict = {
        "score": 0,
        "output_image": output_png,
        "output_mouseover_image": "",
        "output_hyperlink": result_scad,
        "reference_image": reference_png,
        "temp_dir": temp_dir,
        "scoreExplanation": failureReason,
      }

      # Save to cache
      _save_cache(cache_meta_path, result_dict)

      return result_dict

  # Run the intersection and difference calculations in parallel with 20 minute timeouts.
  # If we've gotten here then the result and reference scads rendered successfully,
  # so all is good we just got to be patient.
  with ThreadPoolExecutor(max_workers=2) as executor:
    future_intersection = executor.submit(_run_openscad,
                                          compare1_scad,
                                          intersection_stl,
                                          timeout=1200)
    future_difference = executor.submit(_run_openscad, compare2_scad, difference_stl, timeout=1200)

    err = future_intersection.result()
    if err:
      openscad_errors.append(err)
    err = future_difference.result()
    if err:
      openscad_errors.append(err)

  render_scadText_to_png(f"include <{os.path.basename(resultWithReference_scad)}>;", output2_png)

  if not os.path.exists(reference_png):
    _render_stl_to_png(reference_stl, reference_png)

  # Calculate volumes
  resultVolume = StlVolume.calculate_stl_volume(output_stl)
  referenceVolume = StlVolume.calculate_stl_volume(reference_stl)
  intersectionVolume = StlVolume.calculate_stl_volume(intersection_stl)
  differenceVolume = StlVolume.calculate_stl_volume(difference_stl)

  print(f"Result Volume: {resultVolume}")
  print(f"Reference Volume: {referenceVolume}")
  print(f"Intersection Volume: {intersectionVolume}")
  print(f"Difference Volume: {differenceVolume}")

  scoreExplantion = f"""
    <table>
    <tr><td>Result Volume:</td><td>{resultVolume:.2f}</td></tr>
    <tr><td>Reference Volume:</td><td>{referenceVolume:.2f}</td></tr>
    <tr><td>Intersection Volume:</td><td>{intersectionVolume:.2f}</td></tr>
    <tr><td>Difference Volume:</td><td>{differenceVolume:.2f}</td></tr>
    </table>
    """

  if openscad_errors:
    scoreExplantion += "<div style='color:red;white-space:pre-wrap;'>" + "\n".join(
      openscad_errors).replace('<', '&lt;').replace('>', '&gt;') + "</div>"

  # Calculate score
  if referenceVolume == 0:
    score = 0.0
  else:
    score = min(intersectionVolume / referenceVolume, resultVolume / referenceVolume)

    if "validatePostVolume" in testGlobals:
      score, explanation = testGlobals["validatePostVolume"](result, score, resultVolume,
                                                             referenceVolume, intersectionVolume,
                                                             differenceVolume)

      if explanation:
        scoreExplantion += explanation

    score -= (differenceVolume / referenceVolume) * 0.5

    if "postProcessScore" in testGlobals:
      oldScore = score
      score = testGlobals["postProcessScore"](score, subPass)
      if oldScore != score:
        scoreExplantion += f"Score was renormalised: {oldScore:.2f} -> {score:.2f}\n"

    score = max(0, score)

  if openscad_errors:
    score = 0

  if score > 1:
    score = 1

  result_dict = {
    "score": score,
    "output_image": output_png,
    "output_mouseover_image": output2_png,
    "output_hyperlink": result_scad,
    "reference_image": reference_png,
    "temp_dir": temp_dir,
    "scoreExplanation": scoreExplantion,
    "resultVolume": resultVolume,
    "referenceVolume": referenceVolume,
    "intersectionVolume": intersectionVolume,
    "differenceVolume": differenceVolume
  }

  # Save to cache
  _save_cache(cache_meta_path, result_dict)

  return result_dict


def _compute_reference_cache_key(referenceScad: str, scadModules: str) -> str:
  """Compute a hash key for reference data only (changes infrequently)."""
  combined = f"{referenceScad}\n---MODULES---\n{scadModules or ''}"
  return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def _compute_result_cache_key(resultAsScad: str, reference_cache_key: str) -> str:
  """Compute a hash key for comparison results (depends on both result and reference)."""
  combined = f"{resultAsScad}\n---REF_KEY---\n{reference_cache_key}"
  return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def _load_cache(cache_meta_path: str) -> Optional[Dict[str, Any]]:
  """Load cached result if all files still exist."""
  try:
    with open(cache_meta_path, 'r', encoding='utf-8') as f:
      cached = json.load(f)
    # Verify all referenced files still exist
    for key in ['output_image', 'reference_image']:
      if key in cached and cached[key] and not os.path.exists(cached[key]):
        return None
    return cached
  except (json.JSONDecodeError, IOError):
    return None


def _save_cache(cache_meta_path: str, result: Dict[str, Any]) -> None:
  """Save result to cache."""
  try:
    with open(cache_meta_path, 'w', encoding='utf-8') as f:
      json.dump(result, f, indent=2)
  except IOError as e:
    print(f"Warning: Failed to save cache: {e}")


def _write_scad_file(filepath: str, content: str, modules: Optional[str], suffix: str) -> None:
  """Write a SCAD file with optional modules and suffix."""
  with open(filepath, "w", encoding="utf-8") as f:
    if modules:
      f.write(modules)
    f.write(content)
    f.write(suffix)
  scad_format.format_file(filepath, formatConfig)


# Use private alias for internal use
_run_openscad = run_openscad
_render_stl_to_png = render_stl_to_png
