import json
import sys
from pathlib import Path

VGB_ROOT = Path(__file__).resolve().parent / "VisGeomBench"
if str(VGB_ROOT) not in sys.path:
    sys.path.insert(0, str(VGB_ROOT))

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser
from visual_geometry_bench.verification.topology_edge_tasks import verify_topology_edge_tasks

DATA_PATH = Path(__file__).resolve().parent / "data" / "vgb" / "topology_edge_enumerate_curated.jsonl"
DATA = [json.loads(line) for line in open(DATA_PATH, "r", encoding="utf-8") if line.strip()]
PARSER = PythonLiteralParser()


title = "VGB2 — Topology Edge Tasks: Enumerate Edges"
structure = None


def prepareSubpassPrompt(index):
    if index >= len(DATA):
        raise StopIteration
    return DATA[index]["prompt"]


def gradeAnswer(result, subPass, aiEngineName):
    raw = result if isinstance(result, str) else repr(result)
    extracted = PARSER.parse_answer(raw) or raw
    diff = verify_topology_edge_tasks(extracted, DATA[subPass], return_diff=True)
    return (1 if diff.get("passed") else 0), str(diff)
