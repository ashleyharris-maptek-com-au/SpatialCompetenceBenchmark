import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    g = {}
    exec(open("18.py").read(), g)
    code = g["prepareSubpassReferenceScad"](subPass)
    code = code.replace("module reference", "union")
    return code, "I had to solve this for the reference implementation."

  return None


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  return "cube([1,1,1]);", "Always-wrong placeholder"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  size = rng.randint(1, 6)
  code = f"cube([{size},{size},{size}]);"
  return code, "Random guess"
