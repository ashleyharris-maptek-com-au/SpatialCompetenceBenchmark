import math, sys, os
from textwrap import dedent

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

problem2 = importlib.import_module("2")


def get_response(subPass: int):
  """Get the placebo response for this question."""

  bricks = []

  tp = list(problem2.testParams[subPass])

  tp[0] *= 10
  tp[1] *= 10

  for x0 in range(-tp[1] * 2, tp[1] * 2, 32):
    for y0 in range(-tp[1] * 2, tp[1] * 2, 16):
      for zBy10 in range(48, 1800, 96):
        if (zBy10 // 48) % 4 == 1:
          x = x0
          y = y0
        else:
          x = x0 + 16
          y = y0 + 8
        z = zBy10 / 10
        dist = math.sqrt(x * x + y * y + z * z)
        if dist > tp[0] * 0.92 - 4 and dist < tp[1] * 1.1 + 4:
          bricks.append({"Centroid": [x, y, z], "RotationDegrees": 0})

  return {
    "bricks": bricks,
  }, "10 lines of python - building one giant aligned structure."
