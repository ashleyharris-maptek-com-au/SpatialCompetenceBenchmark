# Placebo data package - contains reference responses for each question
# Each module exports a get_response(subPass) function that returns (response, reasoning) tuple

from . import q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15
from . import q16, q17, q18, q19, q20, q23, q24, q25, q26, q27, q28, q29, q30, q31
from . import q41, q42, q43, q21, q22, q49, q35, q45, q32, q37, q48
from . import q50
from . import q51, q52, q53, q54, q55, q56, q57
import hashlib
import importlib
import random
import copy

_modules = {
  1: q1,
  2: q2,
  3: q3,
  4: q4,
  5: q5,
  6: q6,
  7: q7,
  8: q8,
  9: q9,
  10: q10,
  11: q11,
  12: q12,
  13: q13,
  14: q14,
  15: q15,
  16: q16,
  17: q17,
  18: q18,
  19: q19,
  20: q20,
  21: q21,
  22: q22,
  23: q23,
  24: q24,
  25: q25,
  26: q26,
  27: q27,
  28: q28,
  29: q29,
  30: q30,
  31: q31,
  32: q32,
  35: q35,
  37: q37,
  41: q41,
  42: q42,
  43: q43,
  45: q45,
  48: q48,
  49: q49,
  50: q50,
  51: q51,
  52: q52,
  53: q53,
  54: q54,
  55: q55,
  56: q56,
  57: q57
}


def _get_placebo_response(questionNum: int, subPass: int):
  module = _modules.get(questionNum)
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
    q9.cache_solutions()
  elif questionNum == 11:
    q11.cache_solutions()
  elif questionNum == 12:
    q12.cache_solutions()
  elif questionNum == 16:
    q16.cache_solutions()
  elif questionNum == 28:
    q28.cache_solutions()
  elif questionNum == 45:
    q45.cache_solutions()


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
  module = _modules.get(questionNum)
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
    module = _modules.get(questionNum)
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
