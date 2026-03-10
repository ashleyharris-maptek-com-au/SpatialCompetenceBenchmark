import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from LLMBenchCore.ResultPaths import model_artifact_dir, report_relpath

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.topology_enumeration import verify_topology_enumeration
from visualisations import visualise_record

DATA_PATH = REPO_ROOT / "data" / "vgb" / "topology_enumeration_curated.jsonl"
_DATA = None
PARSER = PythonLiteralParser()

FIGURES_DIR = VGB_ROOT / "data" / "figures" / "topology_enumeration"
GENERATOR_SCRIPT = VGB_ROOT / "scripts" / "generate_topology_enumeration_figures.py"

tags = ["2D", "Fundamental Geometry"]
earlyFail=True
title = "VGB1 — Topology Enumeration"
structure = {
  "type": "object",
  "additionalProperties": False,
  "required": ["configs"],
  "properties": {
    "configs": {
      "type": "array",
      "items": {
        "type": "array",
        "minItems": 4,
        "maxItems": 4,
        "items": {
          "type": "integer"
        },
      },
    },
  },
}


def _parse_structured_payload(raw: str):
  if not isinstance(raw, str):
    return None
  payload = raw.strip()
  if not payload:
    return None
  for parser in (json.loads, ast.literal_eval):
    try:
      return parser(payload)
    except (ValueError, SyntaxError, json.JSONDecodeError):
      continue
  return None


def _coerce_configs(configs):
  if not isinstance(configs, list):
    return None
  try:
    return [tuple(item) for item in configs]
  except TypeError:
    return None


def _extract_configs(result):
  if isinstance(result, dict):
    configs = _coerce_configs(result.get("configs"))
    if configs is not None:
      return configs

  if isinstance(result, str):
    parsed = _parse_structured_payload(result)
    if parsed is None:
      extracted = PARSER.parse_answer(result)
      if extracted:
        parsed = _parse_structured_payload(extracted)

    if isinstance(parsed, dict):
      configs = _coerce_configs(parsed.get("configs"))
      if configs is not None:
        return configs
    if isinstance(parsed, list):
      configs = _coerce_configs(parsed)
      if configs is not None:
        return configs

  return None


def _get_data():
  global _DATA
  if _DATA is None:
    _DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
  return _DATA


def _build_subpass_summary():
  data = _get_data()
  items = []
  for rec in data:
    meta = rec.get("metadata", {}) if isinstance(rec, dict) else {}
    dg = rec.get("datagen_args", {}) if isinstance(rec, dict) else {}
    corner_order = tuple(
      dg.get("corner_order", ("bottom-left", "bottom-right", "top-right", "top-left")))
    n_classes = dg.get("n_classes", "?")
    tags = meta.get("tags", [])
    tag_text = ", ".join(tags[:3]) if tags else "curated"
    items.append(f"corner_order={corner_order} • n_classes={n_classes} • tags={tag_text}")
  return items


subpassParamSummary = _build_subpass_summary()
promptChangeSummary = "Corner orders and class counts vary per curated topology-enumeration case; list label tuples that force class intersections."
highLevelSummary = (
  "Each record shows a unit square with corner labels. Ground-truth configurations (green) are the label tuples that guarantee class interfaces; "
  "model answers (blue) are overlaid for comparison. Edge markers E0–E3 follow the prompt's corner ordering."
)


def _format_diff(diff):
  if not isinstance(diff, dict):
    return str(diff)

  lines = []

  def add_line(key, value):
    lines.append(f"<b>{key}:</b> {value}")

  add_line("passed", diff.get("passed"))
  if "missing" in diff:
    add_line("missing", diff.get("missing"))
  if "extra" in diff:
    add_line("extra", diff.get("extra"))
  if "errors" in diff:
    add_line("errors", diff.get("errors"))

  details = diff.get("details")
  if isinstance(details, dict):
    for k, v in sorted(details.items()):
      add_line(f"details.{k}", v)

  return "<br>".join(lines)


def prepareSubpassPrompt(index):
  data = _get_data()
  if index >= len(data):
    raise StopIteration
  return data[index]["prompt"]


def gradeAnswer(result, subPass, aiEngineName):
  data = _get_data()
  configs = _extract_configs(result)
  if configs is not None:
    extracted = repr(configs)
  else:
    raw = result if isinstance(result, str) else repr(result)
    extracted = PARSER.parse_answer(raw) or raw
  record = data[subPass]
  gt = record.get("ground_truth")
  if isinstance(gt, list):
    record = dict(record)
    record["ground_truth"] = [tuple(cfg) for cfg in gt]
  diff = verify_topology_enumeration(extracted, record, return_diff=True)
  pretty = _format_diff(diff)
  return (1 if diff.get("passed") else 0), pretty


def resultToNiceReport(result, subPass, aiEngineName: str):
  data = _get_data()
  if subPass >= len(data):
    raise StopIteration

  record = data[subPass]
  configs = _extract_configs(result)
  if configs is not None:
    answer = configs
  else:
    raw = result if isinstance(result, str) else repr(result)
    parsed = PARSER.parse_answer(raw)
    answer = parsed if parsed is not None else raw

  output_dir = Path(model_artifact_dir(aiEngineName))
  output_dir.mkdir(parents=True, exist_ok=True)
  stub_base = Path(__file__).stem if "__file__" in globals() else Path(DATA_PATH).stem
  stub = f"{stub_base}_{aiEngineName}_{subPass}"

  vis_result = visualise_record(
    record,
    answer,
    detail=True,
    save_dir=output_dir,
    fmt="png",
    output_stub=stub,
    answer_label=aiEngineName,
  )

  if isinstance(vis_result, dict):
    file_paths = [output_dir / f"{stub}_{name}.png" for name in vis_result.keys()]
  else:
    file_paths = [output_dir / f"{stub}.png"]

  img_tags = [
    f'<img src="{report_relpath(str(path), aiEngineName)}" alt="Topology enumeration visualization" style="max-width: 100%;">'
    for path in file_paths
  ]

  legend_html = (
    "<div style='margin-top:6px;font-size:13px;line-height:1.4;'>"
    "<b>Legend:</b> Green = ground truth label tuples; Blue = model answers. "
    "Corner labels follow the prompt order; edge markers E0–E3 show boundary positions. "
    "Dashed lines indicate inferred class interfaces in multi-class cases.</div>")

  return "".join(img_tags + [legend_html])


def setup():
  if DATA_PATH.exists():
    return

  fallback = VGB_ROOT / "data" / "vgb" / DATA_PATH.name
  if fallback.exists():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fallback, DATA_PATH)
  else:
    raise RuntimeError(f"Missing dataset file: {DATA_PATH}. "
                       f"Expected it under MeshBenchmark/data/vgb. "
                       f"If you have VisGeomBench, try generating or copying {fallback}.")

  # If figures are missing, run the generator script from VisGeomBench
  if not FIGURES_DIR.exists() or not any(FIGURES_DIR.iterdir()):
    if not GENERATOR_SCRIPT.exists():
      raise RuntimeError(f"Generator script not found: {GENERATOR_SCRIPT}. "
                         f"Ensure VisGeomBench submodule is populated.")
    subprocess.run(
      [sys.executable, str(GENERATOR_SCRIPT)],
      cwd=VGB_ROOT,
      check=True,
    )
