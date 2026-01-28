import ast
import json
import sys
from pathlib import Path

VGB_ROOT = Path(__file__).resolve().parent / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
    sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.topology_enumeration import verify_topology_enumeration

DATA_PATH = Path(__file__).resolve().parent / "data" / "vgb" / "topology_enumeration_curated.jsonl"
DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
PARSER = PythonLiteralParser()


title = "VGB1 — Topology Enumeration"
structure = None


def prepareSubpassPrompt(index):
    if index >= len(DATA):
        raise StopIteration
    return DATA[index]["prompt"]


def gradeAnswer(result, subPass, aiEngineName):
    raw = result if isinstance(result, str) else repr(result)
    extracted = PARSER.parse_answer(raw) or raw
    try:
        parsed = ast.literal_eval(extracted.strip())
        if (
            isinstance(parsed, list)
            and all(isinstance(item, list) and len(item) == 4 for item in parsed)
        ):
            extracted = repr([tuple(item) for item in parsed])
    except (ValueError, SyntaxError):
        pass
    record = DATA[subPass]
    gt = record.get("ground_truth")
    if isinstance(gt, list):
        record = dict(record)
        record["ground_truth"] = [tuple(cfg) for cfg in gt]
    diff = verify_topology_enumeration(extracted, record, return_diff=True)
    return (1 if diff.get("passed") else 0), str(diff)
