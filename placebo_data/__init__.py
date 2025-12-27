# Placebo data package - contains reference responses for each question
# Each module exports a get_response(subPass) function that returns (response, reasoning) tuple

from . import q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15
from . import q16, q17, q18, q19, q20, q23, q24, q25, q26, q27, q28, q29, q30, q31
from . import q41, q42, q43, q21

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
  23: q23,
  24: q24,
  25: q25,
  26: q26,
  27: q27,
  28: q28,
  29: q29,
  30: q30,
  31: q31,
  41: q41,
  42: q42,
  43: q43,
}


def get_response(questionNum: int, subPass: int):
  """Get the placebo response for a given question and subpass.
    Returns (response, reasoning) tuple or None if no response defined."""
  module = _modules.get(questionNum)
  if module and hasattr(module, 'get_response'):
    return module.get_response(subPass)
  print(f"No response defined in placebo_data for question {questionNum} subpass {subPass}")
  return None, "Not yet implemented"
