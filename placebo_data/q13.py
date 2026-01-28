import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    import numpy as np
    peopleCounts = [4, 20, 40, 80, 150, 200]
    peopleCount = peopleCounts[subPass]

    xDiff = math.sqrt(peopleCount) / 3
    yDiff = math.sqrt(peopleCount) / 3
    people = []

    if subPass == 5:
      xDiff -= 1
      yDiff -= 1

    for i in np.arange(-xDiff, xDiff, 0.6):
      for j in np.arange(-yDiff, yDiff, 0.6):
        people.append({"xy": [i - 12, j - 12]})
        if len(people) == peopleCount:
          break
      if len(people) == peopleCount:
        break

    if len(people) != peopleCount:
      xDiff /= 2
      yDiff /= 2
      for i in np.arange(-xDiff, xDiff, 0.6):
        for j in np.arange(-yDiff, yDiff, 0.6):
          people.append({"xy": [i - 6, j - 6]})
          if len(people) == peopleCount:
            break
        if len(people) == peopleCount:
          break

    return {"people": people}, "Placebo thinking... hmmm..."

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  peopleCounts = [4, 20, 40, 80, 150, 200]
  peopleCount = peopleCounts[subPass]
  people = []
  for _ in range(peopleCount):
    x = rng.uniform(-15.0, 15.0)
    y = rng.uniform(-15.0, 15.0)
    people.append({"xy": [x, y]})
  return {"people": people}, "Random guess"
