import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.topology_edge_tasks import verify_topology_edge_tasks
from visualisations import visualise_record

DATA_PATH = REPO_ROOT / "data" / "vgb" / "topology_edge_enumerate_curated.jsonl"
_DATA = None
PARSER = PythonLiteralParser()

title = "VGB2 — Topology Edge Tasks: Enumerate Edges"
structure = None


def _get_data():
  global _DATA
  if _DATA is None:
    _DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
  return _DATA


def _build_subpass_summary():
  data = _get_data()
  rows = []
  for rec in data:
    meta = rec.get("metadata", {}) if isinstance(rec, dict) else {}
    dg = rec.get("datagen_args", {}) if isinstance(rec, dict) else {}
    corner_order = tuple(
      dg.get("corner_order", ("bottom-left", "bottom-right", "top-right", "top-left")))
    edge_order = tuple(dg.get("edge_order", ("bottom", "right", "top", "left")))
    subtask = dg.get("subtask", "enumerate_edges")
    cases = dg.get("cases")
    case_desc = f"cases={len(cases)}" if isinstance(cases, (list, tuple)) else "cases=curated"
    tags = meta.get("tags", [])
    tag_text = ", ".join(tags[:3]) if tags else "curated"
    rows.append(
      f"subtask={subtask} • corner_order={corner_order} • edge_order={edge_order} • {case_desc} • tags={tag_text}"
    )
  return rows


subpassParamSummary = _build_subpass_summary()
promptChangeSummary = "Corner/edge ordering and curated edge cases vary per record; enumerate all edges guaranteed to exist."
highLevelSummary = (
  "Each panel shows a labeled unit square. Ground truth (green) marks guaranteed edge connections; model answers (blue) overlay predicted edges. "
  "Corner labels follow the prompt order; edge markers E0–E3 label boundaries. Curved arcs visualise connections without crossing the square."
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
  raw = result if isinstance(result, str) else repr(result)
  extracted = PARSER.parse_answer(raw) or raw
  diff = verify_topology_edge_tasks(extracted, data[subPass], return_diff=True)
  pretty = _format_diff(diff)
  return (1 if diff.get("passed") else 0), pretty


def resultToNiceReport(result, subPass, aiEngineName: str):
  data = _get_data()
  if subPass >= len(data):
    raise StopIteration

  record = data[subPass]
  raw = result if isinstance(result, str) else repr(result)
  parsed = PARSER.parse_answer(raw)
  answer = parsed if parsed is not None else raw

  output_dir = Path("results")
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
    file_names = [f"{stub}_{name}.png" for name in vis_result.keys()]
  else:
    file_names = [f"{stub}.png"]

  img_tags = [
    f'<img src="{fname}" alt="Topology edge visualization" style="max-width: 100%;">'
    for fname in file_names
  ]
  return "".join(img_tags)


def setup():
  if DATA_PATH.exists():
    return

  fallback = VGB_ROOT / "data" / "vgb" / DATA_PATH.name
  if fallback.exists():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fallback, DATA_PATH)
    return

  raise RuntimeError(f"Missing dataset file: {DATA_PATH}. "
                     f"Expected it under MeshBenchmark/data/vgb. "
                     f"If you have VisGeomBench, try generating or copying {fallback}.")
