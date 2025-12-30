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
