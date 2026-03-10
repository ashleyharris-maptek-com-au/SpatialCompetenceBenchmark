import json
import shutil
import sys
from pathlib import Path
from LLMBenchCore.ResultPaths import model_artifact_dir, report_relpath

REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.two_segments import verify_two_segments
from visualisations import visualise_record

DATA_PATH = REPO_ROOT / "data" / "vgb" / "two_segments_curated.jsonl"
_DATA = None
PARSER = PythonLiteralParser()

tags = ["2D", "Constructive"]
earlyFail=True

title = "VGB5 — Two Segments"
structure = {
  "type": "object",
  "additionalProperties": False,
  "required": ["segments"],
  "properties": {
    "segments": {
      "type": "array",
      "minItems": 2,
      "maxItems": 2,
      "items": {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "items": {
            "type": "number"
          },
        },
      },
    },
  },
}


def _get_data():
  global _DATA
  if _DATA is None:
    _DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
  return _DATA


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
  extracted = None
  if isinstance(result, dict) and "segments" in result:
    segments = result.get("segments")
    if isinstance(segments, list):
      extracted = json.dumps(segments)
  if extracted is None:
    raw = result if isinstance(result, str) else repr(result)
    extracted = PARSER.parse_answer(raw) or raw
  diff = verify_two_segments(extracted, data[subPass], return_diff=True)
  pretty = _format_diff(diff)
  return (1 if diff.get("passed") else 0), pretty


def resultToNiceReport(result, subPass, aiEngineName: str):
  data = _get_data()
  if subPass >= len(data):
    raise StopIteration

  record = data[subPass]
  if isinstance(result, dict) and "segments" in result:
    answer = result.get("segments")
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
    f'<img src="{report_relpath(str(path), aiEngineName)}" alt="Two segments visualization" style="max-width: 100%;">'
    for path in file_paths
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
