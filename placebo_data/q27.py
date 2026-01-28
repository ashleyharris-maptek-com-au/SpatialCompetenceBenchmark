import math, random
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    moves = []
    gridSize = [[32, 8], [48, 12], [56, 16], [64, 24], [72, 32]]

    for i in range(1000):
      moves.append({
        "cellX": random.randint(1, gridSize[subPass][0] - 2),
        "cellY": random.randint(1, gridSize[subPass][1] // 2),
        "direction": random.choice(["up", "down", "left", "right"])
      })
    return {"moves": moves}, "Placebo thinking... hmmm..."

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  gridSize = [[32, 8], [48, 12], [56, 16], [64, 24], [72, 32]]
  width, height = gridSize[subPass]
  moves = []
  for _ in range(100):
    moves.append({
      "cellX": rng.randint(1, width - 2),
      "cellY": rng.randint(1, height - 2),
      "direction": rng.choice(["up", "down", "left", "right"]),
    })
  return {"moves": moves}, "Random guess"
