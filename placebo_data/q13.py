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
        for i in np.arange(-xDiff, xDiff, 0.6):
            for j in np.arange(-yDiff, yDiff, 0.6):
                people.append({"xy": [i - 12, j - 12]})
                if len(people) == peopleCount:
                    break
            if len(people) == peopleCount:
                break
        return {"people": people}, "Placebo thinking... hmmm..."


    return None
