import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    # Question 14 _ 0
    return {"lines": [{"a": -0.5, "b": 4}, {"a": 0, "b": 7}]}, "Placebo thinking... hmmm..."

  if subPass == 1:
    return {
      'lines': [{
        'a': 0,
        'b': 2.5
      }, {
        'a': 1,
        'b': -11.5
      }, {
        'a': -1,
        'b': 21.5
      }]
    }, "Placebo thinking... hmmm..."

  if subPass == 2:
    return {
      'lines': [{
        'a': 1,
        'b': -36.0
      }, {
        'a': 1,
        'b': -30.0
      }, {
        'a': 1,
        'b': -23.5
      }, {
        'a': 1,
        'b': -21.5
      }, {
        'a': 1,
        'b': -19.5
      }, {
        'a': 1,
        'b': -15.5
      }, {
        'a': 1,
        'b': -9.5
      }, {
        'a': 1,
        'b': -4.0
      }, {
        'a': 1,
        'b': -0.5
      }, {
        'a': 1,
        'b': 3.5
      }, {
        'a': 1,
        'b': 7.5
      }, {
        'a': 1,
        'b': 12.0
      }, {
        'a': 1,
        'b': 19.0
      }, {
        'a': 1,
        'b': 28.0
      }]
    }, ""

  if subPass == 3:
    return {
      'lines': [{
        'a': 0.125,
        'b': 1.0625
      }, {
        'a': 0.125,
        'b': 3.6875
      }, {
        'a': 0.125,
        'b': 9.0625
      }, {
        'a': 0.125,
        'b': 14.0
      }, {
        'a': 0.125,
        'b': 18.0
      }, {
        'a': 0.125,
        'b': 23.5625
      }, {
        'a': 0.125,
        'b': 31.9375
      }, {
        'a': 0.125,
        'b': 37.5
      }, {
        'a': 0.125,
        'b': 38.75
      }, {
        'a': 0.125,
        'b': 42.1875
      }, {
        'a': 0.125,
        'b': 46.125
      }, {
        'a': 0.125,
        'b': 48.875
      }, {
        'a': 0.125,
        'b': 50.6875
      }, {
        'a': 0.125,
        'b': 52.625
      }, {
        'a': 0.125,
        'b': 54.875
      }, {
        'a': 0.125,
        'b': 57.75
      }, {
        'a': 0.125,
        'b': 59.75
      }, {
        'a': 0.125,
        'b': 61.1875
      }, {
        'a': 0.125,
        'b': 63.5
      }, {
        'a': 0.125,
        'b': 65.4375
      }, {
        'a': 0.125,
        'b': 66.6875
      }, {
        'a': 0.125,
        'b': 69.8125
      }, {
        'a': 0.125,
        'b': 72.8125
      }, {
        'a': 0.125,
        'b': 74.9375
      }, {
        'a': 0.125,
        'b': 77.75
      }, {
        'a': 0.125,
        'b': 81.25
      }, {
        'a': 0.125,
        'b': 85.75
      }, {
        'a': 0.125,
        'b': 90.75
      }, {
        'a': 0.125,
        'b': 96.25
      }]
    }, ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  line_counts = [2, 3, 6, 10]
  count = line_counts[subPass] if subPass < len(line_counts) else 3
  lines = []
  for _ in range(count):
    if rng.random() < 0.15:
      a = float("inf") if rng.random() < 0.5 else float("-inf")
      b = rng.uniform(0.0, 100.0)
    else:
      a = rng.uniform(-2.0, 2.0)
      b = rng.uniform(-50.0, 50.0)
    lines.append({"a": a, "b": b})
  return {"lines": lines}, "Random guess"
