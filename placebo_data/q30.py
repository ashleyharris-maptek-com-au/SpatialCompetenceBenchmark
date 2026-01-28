import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    result = []

    o = {
      "1": "flippedX",
      "2": "flat",
      "3": "flippedX",
      "4": "flat",
      "5": "flat",
      "6": "flat",
      "7": "flippedX",
      "8": "flat",
      "9": "rotate180Z",
    }

    # 888,999,996,969,699,696,669,666,333,377,777,711,111,171

    for i in str(8889999969696996966696663333777777111111):
      result.append({"digit": int(i), "orientation": o[i]})

    result.append({"digit": 7, "orientation": "rotate90Y"})

    result.append({"digit": 1, "orientation": "rotate90X"})

    return {
      "numberSequence": result
    }, """
Ash solved this by deducing order, and then, after 
getting 50 candidates, finding the largest prime.
The solver is in 30.py's main function.

The solution is all of these flat, rotating the 9's to fit on the 6's, then
flipping the 3's to fit on the 6's, then a stack of 7's flipped in X, then 
2 * 1 flat (flipped in X), then a 7 on it's side, and then a 1 stacked 
on top of it in a giant spike. Height is 86mm.
"""
