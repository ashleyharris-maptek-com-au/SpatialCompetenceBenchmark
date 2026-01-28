import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    # L-pieces tile a 2-column strip. We need to fill ALL columns in a row
    # before it clears. So we interleave positions across the full width.
    #
    # Rotation 3: vertical L pointing up  [(0,0), (1,0), (0,-1), (0,-2)]
    # Rotation 1: vertical L pointing down [(0,0), (-1,0), (0,1), (0,2)]
    #
    # Two pieces (rot 3 at x, rot 1 at x+1) tile a 2x4 area.
    # For width W, we need W/2 pairs per layer.

    widths = [10, 16, 20, 40]
    targets = [10, 15, 20, 30]
    W = widths[subPass] if subPass < len(widths) else 10
    target = targets[subPass] if subPass < len(targets) else 10

    def one_layer(width):
      """Generate one full layer of pieces across the width (clears 2 rows)."""
      layer = []
      for x in range(0, width, 2):
        layer.append({"translationCount": x, "rotationCount": 3})
        layer.append({"translationCount": x + 1, "rotationCount": 1})
      return layer

    # Each layer clears 2 rows (the 2x4 tiles stack to fill 2 complete rows)
    # Need target rows cleared, so need target/2 layers (plus some buffer)
    layers_needed = (target // 2) + 2

    basicBlocks = []
    for _ in range(layers_needed):
      basicBlocks.extend(one_layer(W))

    return {"moves": basicBlocks}, "Placebo thinking... hmmm..."

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  widths = [10, 16, 20, 40]
  targets = [10, 15, 20, 30]
  width = widths[subPass] if subPass < len(widths) else 10
  target = targets[subPass] if subPass < len(targets) else 10
  move_count = target * 2
  moves = []
  for _ in range(move_count):
    moves.append({
      "translationCount": rng.randint(0, width - 1),
      "rotationCount": rng.randint(0, 3),
    })
  return {"moves": moves}, "Random guess"
