# Placebo data package - contains reference responses for each question
# Each module exports a get_response(subPass) function that returns (response, reasoning) tuple
import hashlib
import importlib
import random
import copy

_module_names = {
  1: "q1",
  2: "q2",
  3: "q3",
  4: "q4",
  5: "q5",
  6: "q6",
  7: "q7",
  8: "q8",
  9: "q9",
  10: "q10",
  11: "q11",
  12: "q12",
  13: "q13",
  14: "q14",
  15: "q15",
  16: "q16",
  17: "q17",
  18: "q18",
  19: "q19",
  20: "q20",
  21: "q21",
  22: "q22",
  23: "q23",
  24: "q24",
  25: "q25",
  26: "q26",
  27: "q27",
  28: "q28",
  29: "q29",
  30: "q30",
  31: "q31",
  32: "q32",
  35: "q35",
  36: "q36",
  37: "q37",
  38: "q38",
  41: "q41",
  42: "q42",
  43: "q43",
  45: "q45",
  48: "q48",
  49: "q49",
  50: "q50",
  51: "q51",
  52: "q52",
  53: "q53",
  54: "q54",
  55: "q55",
  56: "q56",
  57: "q57"
}

_module_cache = {}


def _load_module(questionNum: int):
  if questionNum in _module_cache:
    return _module_cache[questionNum]

  module_name = _module_names.get(questionNum)
  if not module_name:
    return None

  module = importlib.import_module(f"{__name__}.{module_name}")
  _module_cache[questionNum] = module
  return module


def _get_placebo_response(questionNum: int, subPass: int):
  module = _load_module(questionNum)
  if module and hasattr(module, "get_response"):
    res, cot = module.get_response(subPass)
    if isinstance(res, dict) and "reasoning" not in res:
      res["reasoning"] = cot
    return res, cot
  print(f"No response defined in placebo_data for question {questionNum} subpass {subPass}")
  return None, "Not yet implemented"


def cache_solutions(questionNum: int):
  print(f"Caching reference solution to question {questionNum}")
  if questionNum == 9:
    module = _load_module(9)
    if module:
      module.cache_solutions()
  elif questionNum == 11:
    module = _load_module(11)
    if module:
      module.cache_solutions()
  elif questionNum == 12:
    module = _load_module(12)
    if module:
      module.cache_solutions()
  elif questionNum == 16:
    module = _load_module(16)
    if module:
      module.cache_solutions()
  elif questionNum == 28:
    module = _load_module(28)
    if module:
      module.cache_solutions()
  elif questionNum == 45:
    module = _load_module(45)
    if module:
      module.cache_solutions()


def _build_from_schema(schema):
  if not isinstance(schema, dict):
    return None

  if "enum" in schema and schema["enum"]:
    return schema["enum"][0]

  schema_type = schema.get("type")
  if schema_type == "object":
    result = {}
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
      result[key] = _build_from_schema(properties.get(key, {}))
    return result

  if schema_type == "array":
    min_items = schema.get("minItems", 1)
    max_items = schema.get("maxItems")
    length = min_items if min_items is not None else 1
    if max_items is not None:
      length = min(length, max_items)
    items_schema = schema.get("items", {})
    if isinstance(items_schema, list):
      items_schema = items_schema[0] if items_schema else {}
    return [_build_from_schema(items_schema) for _ in range(max(1, length))]

  if schema_type == "string":
    return ""

  if schema_type == "boolean":
    return False

  if schema_type == "integer":
    return 0

  if schema_type == "number":
    return 0

  return None


def _make_rng(model_name: str, questionNum: int, subPass: int) -> random.Random:
  seed_text = f"{model_name}:{questionNum}:{subPass}"
  seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16) % (2**32)
  return random.Random(seed)


def _get_always_wrong_response(questionNum: int, subPass: int):
  module = _load_module(questionNum)
  if module and hasattr(module, "get_always_wrong"):
    return module.get_always_wrong(subPass)

  try:
    question_module = importlib.import_module(str(questionNum))
  except Exception:
    question_module = None

  if question_module is None:
    return "", "Always-wrong placeholder"

  response = _build_from_schema(question_module.structure)
  if isinstance(response, dict) and "reasoning" not in response:
    response["reasoning"] = "Always-wrong placeholder"
  return response, "Always-wrong placeholder"


def get_response(*args):
  if len(args) == 3:
    model_name, questionNum, subPass = args
  else:
    model_name = None
    questionNum, subPass = args

  normalized_name = str(model_name or "human-with-tools").strip().lower().replace(" ", "-")
  if normalized_name == "always-wrong":
    return _get_always_wrong_response(questionNum, subPass)

  if normalized_name == "guessing":
    module = _load_module(questionNum)
    rng = _make_rng(normalized_name, questionNum, subPass)
    if module and hasattr(module, "get_guess"):
      return module.get_guess(subPass, rng)
    try:
      question_module = importlib.import_module(str(questionNum))
      schema = getattr(question_module, "structure", None)
    except Exception:
      schema = None
    response = _build_from_schema(schema)
    if isinstance(response, dict) and "reasoning" not in response:
      response["reasoning"] = "Random guess"
    return response, "Random guess"

  return _get_placebo_response(questionNum, subPass)
