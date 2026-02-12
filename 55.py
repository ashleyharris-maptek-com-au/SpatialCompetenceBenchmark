import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from LLMBenchCore.ResultPaths import model_artifact_dir, report_relpath

_cache_dir = os.path.join(tempfile.gettempdir(), "55_delaunay_cache")
os.makedirs(_cache_dir, exist_ok=True)


def _get_cache_key(answer: dict, subPass: int, aiEngineName: str) -> str:
  """Generate a cache key from the answer, subPass, and engine name."""
  data = json.dumps(answer, sort_keys=True) + str(subPass) + aiEngineName + "v1"
  return hashlib.sha256(data.encode()).hexdigest()


def _load_from_cache(cache_key: str):
  """Load result from cache if available. Thread/process safe."""
  cache_file = os.path.join(_cache_dir, f"grade_{cache_key}.json")
  if os.path.exists(cache_file):
    try:
      with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
      pass
  return None


def _save_to_cache(cache_key: str, result):
  """Save result to cache. Thread/process safe using atomic write."""
  cache_file = os.path.join(_cache_dir, f"grade_{cache_key}.json")
  tmp_file = cache_file + f".{os.getpid()}.tmp"
  try:
    with open(tmp_file, 'w', encoding='utf-8') as f:
      json.dump(result, f)
    os.replace(tmp_file, cache_file)
  except (IOError, OSError):
    try:
      os.remove(tmp_file)
    except OSError:
      pass


def _load_vis_from_cache(cache_key: str):
  """Load cached visualization HTML if available and underlying files still exist."""
  cache_file = os.path.join(_cache_dir, f"vis_{cache_key}.json")
  if not os.path.exists(cache_file):
    return None
  try:
    with open(cache_file, 'r', encoding='utf-8') as f:
      data = json.load(f)
    html = data.get("html")
    files = data.get("files", [])
    if not html:
      return None
    # Ensure all referenced files still exist
    for p in files:
      if not os.path.exists(p):
        return None
    return html
  except (json.JSONDecodeError, IOError, OSError):
    return None


def _save_vis_to_cache(cache_key: str, html: str, files):
  """Save visualization HTML and file list to cache with atomic write."""
  cache_file = os.path.join(_cache_dir, f"vis_{cache_key}.json")
  tmp_file = cache_file + f".{os.getpid()}.tmp"
  payload = {"html": html, "files": [str(p) for p in files]}
  try:
    with open(tmp_file, 'w', encoding='utf-8') as f:
      json.dump(payload, f)
    os.replace(tmp_file, cache_file)
  except (IOError, OSError):
    try:
      os.remove(tmp_file)
    except OSError:
      pass


REPO_ROOT = Path(".").resolve()
VGB_ROOT = REPO_ROOT / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
  sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.delaunay_tasks import verify_delaunay_triangulation
from visualisations import visualise_record

DATA_PATH = REPO_ROOT / "data" / "vgb" / "delaunay_dataset.jsonl"
_DATA = None
PARSER = PythonLiteralParser()

title = "VGB6 — Delaunay Triangulation"
structure = {
  "type": "object",
  "additionalProperties": False,
  "required": ["triangles"],
  "properties": {
    "triangles": {
      "type": "array",
      "items": {
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "items": {
          "type": "integer",
          "minimum": 0
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


def _build_subpass_summary():
  data = _get_data()
  rows = []
  for rec in data:
    meta = rec.get("metadata", {}) if isinstance(rec, dict) else {}
    dg = rec.get("datagen_args", {}) if isinstance(rec, dict) else {}
    num_points = dg.get("num_points", "?")
    seed = dg.get("seed", meta.get("seed", "?"))
    tags = meta.get("tags", [])
    tag_text = ", ".join(tags[:3]) if tags else "curated"
    rows.append(f"num_points={num_points} • seed={seed} • tags={tag_text}")
  return rows


subpassParamSummary = _build_subpass_summary()
promptChangeSummary = "Point sets vary per record (count/seed); triangulations must match the dataset ordering of indices."
highLevelSummary = (
  "Black dots show input points. Ground truth triangulation edges are green; model answers are blue. Points are labelled by index; "
  "plots include both ground truth and model panels when available.")


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
  cache_key = _get_cache_key(result if isinstance(result, dict) else {"raw": repr(result)}, subPass,
                             aiEngineName)
  cached = _load_from_cache(cache_key)
  if cached is not None:
    print(f"Cache hit grading 55 - {cache_key}")
    return tuple(cached)

  data = _get_data()
  extracted = None
  if isinstance(result, dict) and "triangles" in result:
    triangles = result.get("triangles")
    if isinstance(triangles, list):
      extracted = json.dumps(triangles)
  if extracted is None:
    raw = result if isinstance(result, str) else repr(result)
    extracted = PARSER.parse_answer(raw) or raw
  diff = verify_delaunay_triangulation(extracted, data[subPass], return_diff=True)
  pretty = _format_diff(diff)
  score = 1 if diff.get("passed") else 0

  _save_to_cache(cache_key, [score, pretty])
  return score, pretty


def resultToNiceReport(result, subPass, aiEngineName: str):
  data = _get_data()
  if subPass >= len(data):
    raise StopIteration

  cache_key = _get_cache_key(result if isinstance(result, dict) else {"raw": repr(result)}, subPass,
                             aiEngineName)
  cached_html = _load_vis_from_cache(cache_key)
  if cached_html is not None:
    return cached_html

  record = data[subPass]
  if isinstance(result, dict) and "triangles" in result:
    answer = result.get("triangles")
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
    f'<img src="{report_relpath(str(path), aiEngineName)}" alt="Delaunay triangulation visualization" style="max-width: 100%;">'
    for path in file_paths
  ]
  html = "".join(img_tags)
  _save_vis_to_cache(cache_key, html, file_paths)
  return html


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
