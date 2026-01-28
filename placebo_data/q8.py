import os
import sys
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
problem8 = importlib.import_module("8")


def _build_polynomial_from_grid(grid: str) -> str:
  dot_points = []
  for y, row in enumerate(grid):
    for x, cell in enumerate(row):
      if cell == ".":
        dot_points.append((x, y))

  if not dot_points:
    return "x**2 + y**2 + 1"

  terms = [f"((x-{x})**2+(y-{y})**2)" for x, y in dot_points]
  return f"{' * '.join(terms)} - 1"


def get_response(subPass: int):
  """Get the placebo response for this question."""
  try:
    grid = problem8._get_grid_for_subpass(subPass)
  except (IndexError, TypeError):
    return None

  function_body = _build_polynomial_from_grid(grid)
  return {
    "function": f"def f(x, y):\n    return {function_body}"
  }, """
There's no limit on the polynomial order, so we can abuse the Intermediate Value 
Theorem / Rational Root Theorum from high school maths and add a factor for every 
value we need and submit the answer in factored form rather than standard form. 
The polynomial is large but simplification wasn't requested nor required."""


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  a = rng.uniform(-3.0, 3.0)
  b = rng.uniform(-3.0, 3.0)
  c = rng.uniform(-10.0, 10.0)
  function_body = f"({a:.3f})*x + ({b:.3f})*y + ({c:.3f})"
  return {
    "reasoning": "Random guess",
    "function": f"def f(x, y):\n    return {function_body}",
  }, "Random guess"
