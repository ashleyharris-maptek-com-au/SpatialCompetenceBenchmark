import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    # Question 1
    return {
      "pipes": [{
        "xCentre": 0,
        "yCentre": 0,
        "rotationDegrees": 0
      }, {
        "xCentre": -2.55,
        "yCentre": 2.5,
        "rotationDegrees": 90
      }, {
        "xCentre": 2.55,
        "yCentre": 2.5,
        "rotationDegrees": 90
      }, {
        "xCentre": -2.55,
        "yCentre": -2.5,
        "rotationDegrees": 90
      }, {
        "xCentre": 2.55,
        "yCentre": -2.5,
        "rotationDegrees": 90
      }],
      "Reasoning":
      "This was manually calculated. Half of 10cm is 5cm, so the 10cm wide pipes center is offset by 5cm."
    }, "Placebo thinking... hmmm..."

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  pipes = [{"xCentre": 0.0, "yCentre": 0.0, "rotationDegrees": 0.0}]
  for side in (-1.0, 1.0):
    y_top = rng.uniform(1.0, 4.0)
    y_bottom = rng.uniform(-4.0, -1.0)
    pipes.append({
      "xCentre": 2.55 * side,
      "yCentre": y_top,
      "rotationDegrees": 90.0,
    })
    pipes.append({
      "xCentre": 2.55 * side,
      "yCentre": y_bottom,
      "rotationDegrees": 90.0,
    })
  pipes.append({
    "xCentre": 0.0,
    "yCentre": rng.uniform(-0.5, 0.5),
    "rotationDegrees": 0.0,
  })
  return {
    "reasoning": "Random guess",
    "pipes": pipes[:5],
  }, "Random guess"
