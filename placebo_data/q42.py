import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    return "eseeneesessseesseeeseessseeessseesssssssssssssssswwwwwnnnnnnnnnnnnw", ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  steps = []
  for _ in range(80):
    steps.append(rng.choice(["n", "s", "e", "w"]))
  return "".join(steps), "Random guess"


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  return "nn", "Always-wrong placeholder"
