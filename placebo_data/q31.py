import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    return {
      'hole': {
        'transform': [1.0, 0.0, 0.0, 0.0]
      },
      'solid': {
        'transform': [math.sqrt(0.5), math.sqrt(0.5), 0.0, 0.0]
      }
    }, "Placebo thinking... hmmm..."

  if subPass == 2:
    return {
      'hole': {
        'transform': [0.7071, 0.0, 0.7071, 0.0]
      },
      'solid': {
        'transform': [0.7071, 0.0, 0.7071, 0.0, 0.0, 0.0, -0.1]
      }
    }, ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""

  def random_quat():
    q = [rng.uniform(-1.0, 1.0) for _ in range(4)]
    norm = math.sqrt(sum(v * v for v in q)) or 1.0
    return [v / norm for v in q]

  def maybe_offset(q):
    if rng.random() < 0.4:
      return q + [rng.uniform(-0.2, 0.2) for _ in range(3)]
    return q

  return {
    "hole": {
      "transform": maybe_offset(random_quat())
    },
    "solid": {
      "transform": maybe_offset(random_quat())
    },
  }, "Random guess"
