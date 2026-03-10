import itertools, random
import numpy as np
import OpenScad as vc
from LLMBenchCore.ResultPaths import result_path, report_relpath

tags = ["2D", "Packing", "NP Hard"]

title = "Hamiltonian Loop on Grid"


def _parse_grid_to_blocked(grid_str: str) -> set:
  """Parse a grid string into a set of blocked (x, y) coordinates."""
  blocked = set()
  lines = grid_str.strip().split("\n")
  for row_idx, line in enumerate(lines):
    y = len(lines) - row_idx  # Top line is highest y
    for x_idx, ch in enumerate(line):
      if ch == 'X':
        blocked.add((x_idx + 1, y))
  return blocked


# =============================================================================
# Unified Test Parameters
# =============================================================================
# Each entry: (grid_size, blocked_cells, summary, twist_text)
# blocked_cells can be a set or a grid string (will be parsed)

testParams = [
  # 0: 4x4 grid, no obstacles
  (4, set(), "4x4 grid", ""),
  (4, """
....
.X..
.X..
....
""".strip(), "4x4 grid with 2 cells blocked", None),

  # 1: 8x8 grid, no obstacles
  (8, set(), "8x8 grid", ""),

  # 2: 12x12 grid, no obstacles
  (12, set(), "12x12 grid", ""),

  # 3: 16x16 grid, no obstacles
  (16, set(), "16x16 grid", ""),

  # 4: 16x16 with 2 blocked cells
  (16, {(3, 3), (3, 4)}, "16x16 grid with cells (3,3) and (3,4) removed",
   "Cells 3,3 and 3,4 have been removed from the grid and must be skipped."),

  # 5: 16x16 with 6 blocked cells
  (16, {(12, 3), (12, 4), (5, 3), (5, 4), (7, 10), (8, 10)
        }, "16x16 grid with cells (12, 6), (12, 6), (5, 6), (5, 5), (7, 10), (8, 10) are removed.",
   "(12, 5), (12, 6), (5, 5), (5, 6), (7, 10), (8, 10) are removed from the grid and must be skipped."
   ),

  # 6: 16x16 with grid pattern
  (16, """
................
.X............X.
................
................
.X............X.
................
................
................
................
................
................
.X............X.
................
................
.X............X.
................
""", "16x16 grid where various holes exist.", None),  # twist_text = grid

  # 7: 16x16 with grid pattern including center block
  (16, """
................
.X............X.
................
................
.X............X.
................
................
.......XX.......
.......XX.......
................
................
.X............X.
................
................
.X............X.
................
""", "16x16 grid where various holes exist.", None),  # twist_text = grid
  (16, """
XX..............
XX............X.
XX............X.
XX............X.
XX............X.
................
................
.......XX.......
.......XX.......
................
................
XXXX..........X.
................
.XX.............
.XX...........X.
................
""", "16x16 grid where various holes exist.", None),
]

# Process testParams to normalize blocked cells and generate derived data
for i, (grid_size, blocked, summary, twist) in enumerate(testParams):
  if isinstance(blocked, str):
    blocked = _parse_grid_to_blocked(blocked)
    testParams[i] = (grid_size, blocked, summary, twist)


def get_blocked_cells(subPass: int) -> set:
  """Get blocked cells for a subpass."""
  if subPass < len(testParams):
    return testParams[subPass][1]
  return set()


def get_grid_size(subPass: int) -> int:
  """Get grid size for a subpass."""
  if subPass < len(testParams):
    return testParams[subPass][0]
  return 16


def get_valid_cell_count(subPass: int) -> int:
  """Get number of valid (non-blocked) cells for a subpass."""
  size = get_grid_size(subPass)
  blocked = get_blocked_cells(subPass)
  return size * size - len(blocked)


def _blocked_to_grid(blocked: set, size: int) -> list:
  """Convert blocked set to grid array for visualization."""
  grid = [['.' for _ in range(size)] for _ in range(size)]
  for x, y in blocked:
    if 1 <= x <= size and 1 <= y <= size:
      grid[y - 1][x - 1] = 'X'
  return grid


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

earlyFail = True
earlyFailSubpassSampleCount = 3

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

# Generate subpassParamSummary from testParams
subpassParamSummary = []
for i, (grid_size, blocked, summary, twist) in enumerate(testParams):
  param_summary = summary
  if blocked:
    param_summary += "<br>\n<pre>\n"
    grid = _blocked_to_grid(blocked, grid_size)
    for row in grid:
      param_summary += "".join(row) + "\n"
    param_summary += "</pre><br>\n"
  subpassParamSummary.append(param_summary)

promptChangeSummary = "Grid size increases across subpasses, with a missing chunk in the final subpasses"


def isPrime(n):
  if n <= 1:
    return False
  for i in range(2, int(n**0.5) + 1):
    if n % i == 0:
      return False
  return True


def prepareSubpassPrompt(index):
  if index >= len(testParams):
    raise StopIteration

  grid_size, blocked, summary, twist_text = testParams[index]
  valid_cells = get_valid_cell_count(index)

  # Build twist text if not provided (use grid visualization)
  if twist_text is None and blocked:
    grid = _blocked_to_grid(blocked, grid_size)
    grid_str = "\n".join("".join(row) for row in grid)
    twist_text = grid_str + "\n\nX represents a cell to be skipped. Top Left is 1,1"

  return prompt.replace("SIZE", str(grid_size)).replace("SQUARED", str(valid_cells)).replace(
    "TWIST", twist_text or "")


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if not isinstance(answer, dict):
    return 0, "Invalid answer format"

  if "steps" not in answer or len(answer["steps"]) == 0:
    return 0, "No steps provided"

  expected_steps = get_valid_cell_count(subPass)
  if len(answer["steps"]) != expected_steps:
    return 0, f"Expected {expected_steps} steps, got {len(answer['steps'])}"

  size = get_grid_size(subPass)
  blocked = get_blocked_cells(subPass)

  # since the path is supposed to be a loop, we start at the end to check that the start
  # and end are adjacent.
  location = answer["steps"][-1]["xy"]

  visited = set()

  for step in answer["steps"]:

    if step["xy"][0] <= 0 or step["xy"][0] > size or step["xy"][1] <= 0 or step["xy"][1] > size:
      return 0, "Out of bounds!"

    cell = (int(step["xy"][0]), int(step["xy"][1]))
    if cell in blocked:
      return 0, f"You visited an invalid cell {step['xy']}!"

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
    translate([{a['xy'][0]* 0.9 + xMid*0.1}, {a['xy'][1]* 0.9 + yMid*0.1}, 0]) cube([0.1, 0.1, 0.1], center=true);
    translate([{b['xy'][0]* 0.9 + xMid*0.1}, {b['xy'][1]* 0.9 + yMid*0.1}, 0]) cube([0.1, 0.1, 0.1], center=true);
}}

"""

  size = get_grid_size(subPass)
  blocked = get_blocked_cells(subPass)

  for i, a in enumerate(answer["steps"]):
    scadOutput += f"""
translate([{a['xy'][0]}, {a['xy'][1]}, 0.5]) color([0,0,1]) linear_extrude(0.01) text("{i}",size=0.35, halign="center", valign="center");
"""

  for x, y in blocked:
    scadOutput += f"""
translate([{x}, {y}, 0]) color([1,0,0])linear_extrude(0.01) text("X",size=0.5, halign="center", valign="center");
"""

  import os
  output_path = result_path("9_Visualization_" + aiEngineName + "_" + str(subPass) + ".png",
                            aiEngineName)

  extraArgs = ["--projection=p"]
  if blocked: extraArgs.append("--no-autocenter")

  vc.render_scadText_to_png(scadOutput, output_path,
                            f"--camera=8,-5,{10 + size*2},{size/2},{size/2},0", extraArgs)
  print(f"Saved visualization to {output_path}")

  return f'<img src="{report_relpath(output_path, aiEngineName)}" alt="Hamiltonian Path Visualization" style="max-width: 100%;">'


highLevelSummary = """
This is a known simple problem and I'd expect even a 5 year old to solve the simplest case.
<br><br>
Observing the Chain-Of-Thought for the simple models even shows them trying to find
existing solutions on the web to copy paste. It's that well known.
<br><br>
As we crank it up, things get harder. LLMs may truncate or lose focus on the longer
paths, and some of the complex paths, especially with holes, require novel solutions, as without
any spatial reasoning, this becomes NP-Complete, while a child can solve it with a crayon and a 
minutes.
<br><br>
Using Claude Opus 4.5, Windsurf, $40 of API credits and a day of my life explaining algorithms
for an AI to implement, I was able to build a solver for this that can solve simple sparse grids in a few minutes
 (placebo_data/q9.py), this is probably the peak of what I'd expect an AI could do.
"""
