from pathlib import Path
import runpy

_QUESTION_FILE = Path(__file__).resolve().parent.parent / "36.py"
_QUESTION_CACHE = None


def _load_question_data():
  global _QUESTION_CACHE
  if _QUESTION_CACHE is None:
    namespace = runpy.run_path(str(_QUESTION_FILE))
    _QUESTION_CACHE = {
      "problems": namespace.get("problems", []),
      "structure": namespace.get("structure")
    }
  return _QUESTION_CACHE


def _shape_enum():
  data = _load_question_data()
  structure = data.get("structure") or {}
  shape_prop = (structure.get("properties") or {}).get("shapeType") or {}
  enum_vals = shape_prop.get("enum") or []
  return [val for val in enum_vals if isinstance(val, str) and val]


def _blank_response(reasoning_text: str):
  shapes = _shape_enum()
  default_shape = shapes[0] if shapes else "circle"
  return {
    "reasoning": reasoning_text,
    "shapeType": default_shape,
    "shapeDescription": f"Baseline response: {default_shape}."
  }


def get_response(subPass: int):
  data = _load_question_data()
  problems = data["problems"]
  if subPass < 0 or subPass >= len(problems):
    raise IndexError(f"Subpass {subPass} out of range for question 36")

  problem = problems[subPass]
  shape_type = problem["expected_type"].strip()
  object_desc = " ".join(problem["object"].strip().split())
  plane_desc = " ".join(problem["plane"].strip().split())

  reasoning = (f"Given {object_desc} and the described plane ({plane_desc}), "
               f"the cross-section is a {shape_type} as enumerated when the test was built.")

  response = {
    "reasoning":
    reasoning,
    "shapeType":
    shape_type,
    "shapeDescription":
    (f"Intersecting the object with the plane results in a {shape_type} cross-section.")
  }
  return response, "Reference answer from human-with-tools"


def get_guess(subPass: int, rng):
  shapes = _shape_enum()
  if not shapes:
    return _blank_response("Random guess"), "Random guess"

  guess_shape = rng.choice(shapes)
  response = {
    "reasoning": "Random guess",
    "shapeType": guess_shape,
    "shapeDescription": f"Pure guess: calling it a {guess_shape}."
  }
  return response, "Random guess"


def get_always_wrong(subPass: int):
  data = _load_question_data()
  problems = data["problems"]
  shapes = _shape_enum()
  if subPass < 0 or subPass >= len(problems) or not shapes:
    return _blank_response("Always wrong"), "Always-wrong placeholder"

  expected = problems[subPass]["expected_type"].strip().lower()
  wrong_choices = [shape for shape in shapes if shape.lower() != expected]
  wrong_shape = wrong_choices[0] if wrong_choices else shapes[0]
  response = {
    "reasoning": "Deliberately incorrect placeholder",
    "shapeType": wrong_shape,
    "shapeDescription": f"Asserting the section is a {wrong_shape}, intentionally incorrect."
  }
  return response, "Always-wrong placeholder"
