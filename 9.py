import itertools, random
import numpy as np
import VolumeComparison as vc

title = "Hamiltonian Loop on Grid"

prompt = """
You have a SIZE*SIZE grid of unit squares, with cell coordinates (x, y) where 1 <= x <= SIZE, 1 <= y <= SIZE.

TWIST

Draw a single closed path that:
- Moves from cell to cell using only side-adjacent moves.
- Visits every cell exactly once.
- Returns to its starting cell (so the path is a loop).
- The last cell in your list must be side-adjacent to the first.

Answer format:
Give an ordered list of the SQUARED cell coordinates for the loop, starting anywhere, for example:

1,1
1,2
1,3
...
2,1
"""

structure = {
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "xy": {
            "type": "array",
            "items": {
              "type": "number"
            }
          }
        },
        "propertyOrdering": ["xy"],
        "additionalProperties": False,
        "required": ["xy"]
      }
    }
  },
  "propertyOrdering": ["steps"],
  "additionalProperties": False,
  "required": ["steps"]
}

equation5 = "x * 19 + y * 23 + x * y + 10000000028"
equation6 = "x * 13 + y * 29 + x * y + 8000000000"
equation7 = "x * 73 + y * 37 + x * y + 500000002"

subpassParamSummary = [
  "4x4 grid",
  "8x8 grid",
  "12x12 grid",
  "16x16 grid",
  "16x16 grid with cells (3,3) and (3,4) removed",
  "16x16 grid with cells(x,y) where " + equation5 + " is prime, are removed",
  "16x16 grid with cells(x,y) where " + equation6 + " is prime, are removed",
  "16x16 grid with cells(x,y) where " + equation7 + " is prime, are removed",
]
promptChangeSummary = "Grid size increases across subpasses, with a missing chunk in the final subpasses"


def isPrime(n):
  if n <= 1:
    return False
  for i in range(2, int(n**0.5) + 1):
    if n % i == 0:
      return False
  return True


validSquaresForPass = [16 * 16] * 8
validGridForPass = np.array([[['.'] * 16] * 16] * 8, dtype=str)

for x in range(1, 17):
  for y in range(1, 17):
    if isPrime(eval(equation5)):
      validSquaresForPass[5] -= 1
      validGridForPass[5][x - 1][y - 1] = "X"
    if isPrime(eval(equation6)):
      validSquaresForPass[6] -= 1
      validGridForPass[6][x - 1][y - 1] = "X"
    if isPrime(eval(equation7)):
      validSquaresForPass[7] -= 1
      validGridForPass[7][x - 1][y - 1] = "X"

for p in range(5, 8):
  subpassParamSummary[p] += "<br>\n<pre>\n"
  for r in validGridForPass[p]:
    subpassParamSummary[p] += "".join(r) + "\n"
  subpassParamSummary[p] += "</pre>"
  subpassParamSummary[p] += "<br>\n"


def isHamiltonianLoopSolvable(subPass):
  grid = validGridForPass[subPass]

  # For a Hamiltonian loop to exist on a grid graph:
  # 1. All valid cells must be connected
  # 2. No cell can have degree < 2 (dead ends make loops impossible)
  # 3. The total number of valid cells must be even (for a loop on a grid)

  # Build set of valid cells using 1-indexed coords (matching problem definition)
  # grid[x-1][y-1] stores cell (x,y) where 1 <= x,y <= 16
  valid_cells = set()
  for x in range(1, 17):
    for y in range(1, 17):
      if grid[x - 1][y - 1] == '.':
        valid_cells.add((x, y))

  if len(valid_cells) == 0:
    return False, "No valid cells"

  # Check connectivity using BFS
  start = next(iter(valid_cells))
  visited = {start}
  queue = [start]
  while queue:
    cx, cy = queue.pop(0)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
      nx, ny = cx + dx, cy + dy
      if (nx, ny) in valid_cells and (nx, ny) not in visited:
        visited.add((nx, ny))
        queue.append((nx, ny))

  if len(visited) != len(valid_cells):
    return False, f"Graph not connected: {len(visited)}/{len(valid_cells)} cells reachable"

  # Check for dead ends (cells with degree < 2)
  dead_ends = []
  for x, y in valid_cells:
    degree = 0
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
      if (x + dx, y + dy) in valid_cells:
        degree += 1
    if degree < 2:
      dead_ends.append((x, y, degree))  # already 1-indexed

  if dead_ends:
    return False, f"Dead ends (degree < 2): {dead_ends}"

  # Check if total cells is even (necessary for loop on grid)
  if len(valid_cells) % 2 != 0:
    return False, f"Odd number of cells ({len(valid_cells)}) - no Hamiltonian loop possible on grid"

  return True, f"Potentially solvable: {len(valid_cells)} cells, all connected, no dead ends"


if __name__ == "__main__":
  for r, e2 in zip(range(5, 8), [equation5, equation6, equation7]):
    e = e2
    while True:

      validSquaresForPass[r] = 16 * 16
      validGridForPass[r] = np.array([['.'] * 16] * 16, dtype=str)

      for x in range(1, 17):
        for y in range(1, 17):
          if isPrime(eval(e)):
            validSquaresForPass[r] -= 1
            validGridForPass[r][x - 1][y - 1] = "X"

      print(subpassParamSummary[r])
      solvable, reason = isHamiltonianLoopSolvable(r)
      print(f"Solvable: {solvable}")
      print(f"Reason: {reason}")

      if solvable:
        break

      if r == 5:
        equation5 += str(random.randint(0, 10))
        e = equation5
        print(equation5)
      elif r == 6:
        equation6 += str(random.randint(0, 10))
        e = equation6
        print(equation6)
      elif r == 7:
        equation7 += str(random.randint(0, 10))
        e = equation7
        print(equation7)


def prepareSubpassPrompt(index):
  if index == 0:
    return prompt.replace("SIZE", "4").replace("SQUARED", "16").replace("TWIST", "")
  if index == 1:
    return prompt.replace("SIZE", "8").replace("SQUARED", "64").replace("TWIST", "")
  if index == 2:
    return prompt.replace("SIZE", "12").replace("SQUARED", "144").replace("TWIST", "")
  if index == 3:
    return prompt.replace("SIZE", "16").replace("SQUARED", "256").replace("TWIST", "")
  if index == 4:
    return prompt.replace("SIZE", "16").replace("SQUARED", "254").replace(
      "TWIST", "Cells 3,3 and 3,4 have been removed from the grid and must be skipped.")
  if index == 5:
    return prompt.replace("SIZE", "16").replace("SQUARED", str(validSquaresForPass[5])).replace(
      "TWIST", f"Cells where {equation5} is prime must be skipped.")
  if index == 6:
    return prompt.replace("SIZE", "16").replace("SQUARED", str(validSquaresForPass[6])).replace(
      "TWIST", f"Cells where {equation6} is prime must be skipped.")
  if index == 7:
    return prompt.replace("SIZE", "16").replace("SQUARED", str(validSquaresForPass[7])).replace(
      "TWIST", f"Cells where {equation7} is prime must be skipped.")
  raise StopIteration


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if "steps" not in answer or len(answer["steps"]) == 0:
    return 0, "No steps provided"

  expected_steps = [
    16, 64, 144, 256, 254, validSquaresForPass[5], validSquaresForPass[6], validSquaresForPass[7]
  ]
  if subPass < len(expected_steps) and len(answer["steps"]) != expected_steps[subPass]:
    return 0, f"Expected {expected_steps[subPass]} steps, got {len(answer['steps'])}"

  size = 4 if subPass == 0 else 8 if subPass == 1 else 12 if subPass == 2 else 16

  # since the path is supposed to be a loop, we start at the end to check that the start
  # and end are adjacent.
  location = answer["steps"][-1]["xy"]

  visited = set()

  for step in answer["steps"]:

    if step["xy"][0] <= 0 or step["xy"][0] > size or step["xy"][1] <= 0 or step["xy"][1] > size:
      return 0, "Out of bounds!"

    if subPass == 4 and (step["xy"][0] == 3 and step["xy"][1] == 3
                         or step["xy"][0] == 3 and step["xy"][1] == 4):
      return 0, "You forgot to skip cell 3,3 or 3,4!"

    if subPass == 5:
      x = step["xy"][0]
      y = step["xy"][1]
      if isPrime(eval(equation5)):
        return 0, f"You visited an prime numbered cell {step['xy']}, {equation5} = {eval(equation5)}!"

    # check that the step is side-adjacent to the previous step
    xDiff = abs(step["xy"][0] - location[0])
    yDiff = abs(step["xy"][1] - location[1])
    if xDiff + yDiff != 1:
      return 0, f"didn't step side-adjacent {step['xy']} from {location}"
    location = tuple(step["xy"])
    if location in visited:
      return 0, f"visited {location} more than once!"
    visited.add(location)

  return 1, f"Valid Hamiltonian path with {len(answer['steps'])} steps"


def resultToNiceReport(answer, subPass, aiEngineName):
  scadOutput = ""
  for a, b in itertools.pairwise(answer["steps"]):
    xMid = (a['xy'][0] + b['xy'][0]) / 2
    yMid = (a['xy'][1] + b['xy'][1]) / 2

    scadOutput += f"""
hull() {{
    translate([{a['xy'][0]* 0.9 + xMid*0.1}, {a['xy'][1]* 0.9 + yMid*0.1}, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([{b['xy'][0]* 0.9 + xMid*0.1}, {b['xy'][1]* 0.9 + yMid*0.1}, 0]) cube([0.01, 0.01, 0.01], center=true);
}}

"""

  for i, a in enumerate(answer["steps"]):
    scadOutput += f"""
translate([{a['xy'][0]}, {a['xy'][1]}, 0]) linear_extrude(0.01) text("{i}",size=0.15, halign="center", valign="center");
"""

  if subPass in [5, 6, 7]:
    for x in range(1, 17):
      for y in range(1, 17):
        try:
          if validGridForPass[subPass][x - 1][y - 1] == "X":
            scadOutput += f"""
translate([{x}, {y}, 0]) color([1,0,0])linear_extrude(0.01) text("X",size=0.5, halign="center", valign="center");
"""
        except:
          pass

  import os
  os.makedirs("results", exist_ok=True)
  output_path = "results/9_Visualization_" + aiEngineName + "_" + str(subPass) + ".png"
  vc.render_scadText_to_png(scadOutput, output_path)
  print(f"Saved visualization to {output_path}")

  return f'<img src="{os.path.basename(output_path)}" alt="Hamiltonian Path Visualization" style="max-width: 100%;">'


highLevelSummary = """
This is a known simple problem and I'd expect even a 5 year old to solve the simplest case.
<br><br>
Observing the Chain-Of-Thought for the simple models even shows them trying to find
existing solutions on the web to copy paste. It's that well known.
<br><br>
As we crank it up, things get harder. LLMs may truncate or lose focus on the longer
paths, and some of the complex paths, especially with holes, require novel solutions.
"""
