from collections import defaultdict
import OpenScad as vc
import os
import random
from math import isqrt
from LLMBenchCore.ResultPaths import result_path, report_relpath

title = "Pack rectangular prisms"


def get_divisors(n):
  """Get all divisors of n."""
  divisors = []
  for i in range(1, isqrt(n) + 1):
    if n % i == 0:
      divisors.append(i)
      if i != n // i:
        divisors.append(n // i)
  return sorted(divisors)


def get_3factor_decompositions(n):
  """Get all ways to write n as x*y*z where x <= y <= z and all > 1."""
  decompositions = []
  divisors = [d for d in get_divisors(n) if d > 1]

  for x in divisors:
    if x * x * x > n:
      break
    if n % x != 0:
      continue
    remainder = n // x
    for y in divisors:
      if y < x:
        continue
      if y * y > remainder:
        break
      if remainder % y != 0:
        continue
      z = remainder // y
      if z >= y:
        decompositions.append((x, y, z))

  return decompositions


def isTheoreticallySolvablePerfectly(subPassIndex):
  """
  Determine if a subpass is theoretically solvable with 100% packing efficiency.
  Returns (is_possible, reason_string).
  
  Checks:
  1. Volume must have a valid 3-factor decomposition (x*y*z where all > 1)
  2. Each bounding box dimension must be >= the minimum dimension of every box
  3. For each axis, box dimensions must be able to tile/sum to the bounding box dimension
  """

  # if subPassIndex == 2:
  # Observed solved in the wild.

  if subPassIndex == 3:
    return False, """
Factorises only into (7, 12, 283)
Prism (13, 11, 7) has only 1 valid rotation(s) that fit in the container: [(7, 11, 13)].
This wastes a strip of 1 in Y, which no other prism can fit into.
"""

  if subPassIndex == 8:
    return False, "Factorises only into one size (91, 109, 647), And there aren't enough prism "\
    "combinations that add up to 647 to fill a 91*109 area."

  boxes = []
  for count, x, y, z in prismList[0:subPassIndex + 1]:
    for _ in range(count):
      boxes.append(sorted([x, y, z]))  # sorted smallest to largest

  total_volume = sum(x * y * z for x, y, z in boxes)

  # Check 1: Can volume be factored into x*y*z where all > 1?
  decompositions = get_3factor_decompositions(total_volume)

  if not decompositions:
    divisors = get_divisors(total_volume)
    return False, f"Volume {total_volume} cannot be written as x*y*z (x,y,z > 1). Divisors: {divisors}"

  # Check 2: For each decomposition, check if bounding box dims are >= all box dims
  # Since boxes can rotate, min bounding box dim must be >= min dim of largest box's smallest side
  min_box_dim = max(box[0] for box in boxes)  # largest "smallest dimension"
  mid_box_dim = max(box[1] for box in boxes)  # largest "middle dimension"
  max_box_dim = max(box[2] for box in boxes)  # largest "largest dimension"

  valid_decompositions = []
  for x, y, z in decompositions:
    # x <= y <= z from our decomposition
    # We need x >= min_box_dim, y >= mid_box_dim, z >= max_box_dim
    # But boxes can rotate, so we just need sorted bbox dims to dominate sorted box dims
    if x >= min_box_dim and y >= mid_box_dim and z >= max_box_dim:
      valid_decompositions.append((x, y, z))

  if not valid_decompositions:
    reason = f"Volume {total_volume} has decompositions {decompositions}, "
    reason += f"but none can fit boxes requiring dims >= ({min_box_dim}, {mid_box_dim}, {max_box_dim})"
    return False, reason

  # Check 3: For each valid decomposition, check if dimensions can plausibly tile
  # This is a heuristic - we check if box dimensions along each axis can sum to bbox dim
  # using a greedy divisibility check

  # Collect all unique box dimensions
  all_box_dims = set()
  for box in boxes:
    all_box_dims.update(box)

  plausible_decompositions = []
  for bx, by, bz in valid_decompositions:
    bbox = [bx, by, bz]

    # For a dimension D of bbox, boxes aligned along that axis must have their
    # corresponding dimension sum to D. Check if each bbox dim is achievable.
    plausible = True
    for dim in bbox:
      achievable = can_sum_to(dim, all_box_dims)
      if not achievable:
        plausible = False
        break

    if plausible:
      plausible_decompositions.append((bx, by, bz))

  if not plausible_decompositions:
    reason = f"Volume {total_volume} has geometrically valid decompositions {valid_decompositions}, "
    reason += f"but box dimensions {sorted(all_box_dims)} cannot tile to those sizes"
    return False, reason

  return True, f"Potentially solvable with bounding boxes: {plausible_decompositions}"


def can_sum_to(target, available_dims):
  """
  Check if target can be expressed as a sum of values from available_dims.
  Each value can be used multiple times (since we have multiple boxes).
  This is the unbounded subset sum / coin change problem.
  """
  if target in available_dims:
    return True

  # DP approach for small targets
  if target > 10000:
    # For large targets, use GCD heuristic
    from math import gcd
    from functools import reduce
    g = reduce(gcd, available_dims)
    return target % g == 0

  reachable = [False] * (target + 1)
  reachable[0] = True

  for i in range(1, target + 1):
    for d in available_dims:
      if d <= i and reachable[i - d]:
        reachable[i] = True
        break

  return reachable[target]


prompt = """
You are given the following rectangular prisms:

PRISM_LIST

and have to pack them as efficiently as possible into the smallest volume possible.
You can rotate the prisms orthogonally. Return a list of min/max xyz coordinates, one
per box that you've successfully packed.

A perfect answer is one in which the volume of the enclosing bounding box is the same as
the sum of the volumes of the prisms.

Every bit of unused space is a point of failure, effort should be taken to elimiate
unused space.
"""

structure = {
  "type": "object",
  "properties": {
    "boxes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "XyzMin": {
            "type": "array",
            "items": {
              "type": "integer"
            }
          },
          "XyzMax": {
            "type": "array",
            "items": {
              "type": "integer"
            }
          }
        },
        "propertyOrdering": ["XyzMin", "XyzMax"],
        "required": ["XyzMin", "XyzMax"],
        "additionalProperties": False
      }
    }
  },
  "propertyOrdering": ["boxes"],
  "required": ["boxes"],
  "additionalProperties": False
}

# Count, x, y, z. Largest dimension first.
prismList = [
  [7, 5, 3, 2],
  [11, 7, 5, 3],
  [14, 11, 7, 5],
  [17, 13, 11, 7],
  [19, 17, 13, 11],
  [23, 19, 17, 13],
  [15, 5, 5, 1],
  [2, 17, 10, 2],
  [50, 50, 50, 50],
]


def preparePrismListString(index):
  return "\n".join([
    str(a) + " prisms of " + str(b) + "x" + str(c) + "x" + str(d)
    for a, b, c, d in prismList[0:index + 1]
  ])


def prepareSubpassPrompt(index):
  if index == 9: raise StopIteration
  return prompt.replace("PRISM_LIST", preparePrismListString(index))


promptChangeSummary = "Adds additional prisms for each run"

subpassParamSummary = [
  preparePrismListString(0).replace("\n", "<br>"),
  preparePrismListString(1).replace("\n", "<br>"),
  preparePrismListString(2).replace("\n", "<br>"),
  preparePrismListString(3).replace("\n", "<br>"),
  preparePrismListString(4).replace("\n", "<br>"),
  preparePrismListString(5).replace("\n", "<br>"),
  preparePrismListString(6).replace("\n", "<br>"),
  preparePrismListString(7).replace("\n", "<br>"),
  preparePrismListString(8).replace("\n", "<br>"),
]


def gradeAnswer(answer, subPass, aiEngineName):
  if isinstance(answer, list):
    answer = max(
      [item for item in answer if isinstance(item, dict) and isinstance(item.get("boxes"), list)],
      key=lambda item: len(item["boxes"]),
      default={"boxes": []})

  # calcualte the expected volume from the prismList and subpass
  expectedVolume = sum([a * b * c * d for a, b, c, d in prismList[0:subPass + 1]])

  # See if any boxes do not have xyx coordinates, and if so instantly fail
  if "boxes" not in answer or not isinstance(answer["boxes"], list):
    return 0, "Invalid answer format: missing boxes list"

  for box in answer["boxes"]:
    if len(box["XyzMin"]) != 3 or len(box["XyzMax"]) != 3:
      return 0, "Invalid box coordinates"

  # calculate the volume of all the boxes in the answer
  answerVolume = 0
  for box in answer["boxes"]:
    volume = (box["XyzMax"][0] - box["XyzMin"][0]) * (box["XyzMax"][1] - box["XyzMin"][1]) * (
      box["XyzMax"][2] - box["XyzMin"][2])
    answerVolume += volume

  reasoning = f"Answer volume: {answerVolume}, Expected volume: {expectedVolume}"
  if answerVolume != expectedVolume:
    return 0, reasoning + f"\nBoxes are overlapping: Sum of prisms volume: "\
        f"{expectedVolume}, Union of answer prisms volume: {answerVolume}"

  # count the number of boxes of each size
  boxCountBySize = defaultdict(int)
  for box in answer["boxes"]:
    span = [
      box["XyzMax"][0] - box["XyzMin"][0], box["XyzMax"][1] - box["XyzMin"][1],
      box["XyzMax"][2] - box["XyzMin"][2]
    ]
    span.sort(reverse=True)
    boxCountBySize[tuple(span)] += 1

  for size, count in boxCountBySize.items():
    print(f"Subpass {subPass}. Box size {size} count: {count}")

  # check to make sure that the number of boxes of each size is correct
  for boxCount, x, y, z in prismList[0:subPass + 1]:
    if boxCountBySize[(x, y, z)] != boxCount:
      return 0, reasoning + f"\nBox count mismatch for {x}x{y}x{z}:"\
        f" expected {boxCount}, got {boxCountBySize[(x,y,z)]}"

  # check to see if any boxes overlap (compare by index, not value, to catch identical boxes)
  boxes = answer["boxes"]
  for i, box in enumerate(boxes):
    for j, otherBox in enumerate(boxes):
      if i != j:
        if box["XyzMin"][0] < otherBox["XyzMax"][0] and box["XyzMax"][0] > otherBox["XyzMin"][
            0] and box["XyzMin"][1] < otherBox["XyzMax"][1] and box["XyzMax"][1] > otherBox[
              "XyzMin"][1] and box["XyzMin"][2] < otherBox["XyzMax"][2] and box["XyzMax"][
                2] > otherBox["XyzMin"][2]:
          return 0, reasoning + "\nBox overlap detected"

  # check to see if all coordinates are positive
  for box in answer["boxes"]:
    if box["XyzMin"][0] < 0 or box["XyzMin"][1] < 0 or box["XyzMin"][2] < 0:
      return 0, reasoning + "\nBox with negative coordinates detected"

  maxPoint = [0, 0, 0]
  for box in answer["boxes"]:
    maxPoint[0] = max(maxPoint[0], box["XyzMax"][0])
    maxPoint[1] = max(maxPoint[1], box["XyzMax"][1])
    maxPoint[2] = max(maxPoint[2], box["XyzMax"][2])

  enclosingVolume = maxPoint[0] * maxPoint[1] * maxPoint[2]
  score = answerVolume / enclosingVolume

  tsp = isTheoreticallySolvablePerfectly(subPass)
  if not tsp[0]:
    score = min(1, score / 0.95)

  return score, reasoning + f"\nPacking efficiency: {answerVolume / enclosingVolume*100:.1f}% (enclosing volume: {enclosingVolume})"


def resultToNiceReport(result, subPass, aiEngineName: str):
  if isinstance(result, list):
    result = max(
      [item for item in result if isinstance(item, dict) and isinstance(item.get("boxes"), list)],
      key=lambda item: len(item["boxes"]),
      default={"boxes": []})

  openScadData = ""

  for box in result["boxes"]:
    if len(box["XyzMin"]) != 3 or len(box["XyzMax"]) != 3:
      return "Invalid box coordinates: " + str(box)

    span = [
      box["XyzMax"][0] - box["XyzMin"][0], box["XyzMax"][1] - box["XyzMin"][1],
      box["XyzMax"][2] - box["XyzMin"][2]
    ]
    pos = [(box["XyzMax"][0] + box["XyzMin"][0]) / 2, (box["XyzMax"][1] + box["XyzMin"][1]) / 2,
           (box["XyzMax"][2] + box["XyzMin"][2]) / 2]

    randomColour = [random.random(), random.random(), random.random()]

    openScadData += f"translate([{pos[0]}, {pos[1]}, {pos[2]}]) color({randomColour}) cube([{span[0]}, {span[1]}, {span[2]}], center=true);\n"

  output_path = result_path(f"16_Visualization_{aiEngineName}_subpass{subPass}.png", aiEngineName)
  vc.render_scadText_to_png(openScadData, output_path)
  print(f"Saved visualization to {output_path}")

  tsp = isTheoreticallySolvablePerfectly(subPass)

  perfectText = ""
  if tsp[0]:
    perfectText = "<br><br>Perfect packing possible! " + tsp[1]
  else:
    perfectText = "<br><br>Perfect packing not possible! " + tsp[1]

  return "<img src=\"" + report_relpath(output_path, aiEngineName) + "\" />" + perfectText


earlyFail = False

highLevelSummary = """
Packing prisms into the smallest possible volume 
is NP Hard. However because we're adding multiples of the same prisms, some clever maths
becomes available. With a few insights, factorisation of the target volume 
and some simultaneous equations, a solver can be written to do this in a few 
seconds perfectly when a perfect solution is possible, or to get a 95%+ packing
efficient solution when it's not.
"""
