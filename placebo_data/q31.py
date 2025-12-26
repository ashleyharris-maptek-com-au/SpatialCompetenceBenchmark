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
