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

  # Brick half-dimensions
  hx, hy, hz = 16, 8, 4.8

  for x0 in range(-tp[1] * 2, tp[1] * 2, 32):
    for y0 in range(-tp[1] * 2, tp[1] * 2, 16):
      for zBy10 in range(48, 1800, 96):
        if (zBy10 // 48) % 4 == 1:
          cx = x0
          cy = y0
        else:
          cx = x0 + 16
          cy = y0 + 8
        cz = zBy10 / 10

        # Check all 8 corner points
        corners_in_shell = 0
        for dx in (-hx, hx):
          for dy in (-hy, hy):
            for dz in (-hz, hz):
              px, py, pz = cx + dx, cy + dy, cz + dz
              dist = math.sqrt(px * px + py * py + pz * pz)
              if dist > tp[0] and dist < tp[1]:
                corners_in_shell += 1

        if corners_in_shell >= 3:
          bricks.append({"Centroid": [cx, cy, cz], "RotationDegrees": 0})

  return {
    "bricks": bricks,
  }, "30 lines of python - building one giant structure, overlapping to hold together like bricks do."


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  tp = list(problem2.testParams[subPass])
  tp[0] *= 10
  tp[1] *= 10
  outer = tp[1]
  brick_count = rng.randint(10, 40)
  bricks = []
  for _ in range(brick_count):
    cx = rng.uniform(-outer, outer)
    cy = rng.uniform(-outer, outer)
    cz = rng.uniform(0, outer)
    rot = rng.choice([0, 90, 180, 270])
    bricks.append({"Centroid": [cx, cy, cz], "RotationDegrees": rot})
  return {"reasoning": "Random guess", "bricks": bricks}, "Random guess"
