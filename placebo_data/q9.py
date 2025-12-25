import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass < 4:  # Catch-all for any subpass
    gridSizes = [4, 8, 12, 16, 16, 16, 16, 16, 16]
    gridSize = gridSizes[subPass]

    steps = []
    for y in range(gridSize):
      if y % 2 == 0:
        for x in range(1, gridSize):
          steps.append({"xy": [x + 1, y + 1]})
      else:
        for x in range(gridSize - 1, 0, -1):
          steps.append({"xy": [x + 1, y + 1]})
    for y in range(gridSize - 1, -1, -1):
      steps.append({"xy": [1, y + 1]})

    return {"steps": steps}, "Placebo thinking... hmmm..."

  map = [
    "", "", "", "", """
................
................
................
................
...............
................
................
................
................
................
................
................
..X.............
..X.............
................
................  
  """, """
  ................
..X.........X...
........X......X
................
..X...X..X......
........X.......
................
............X...
.....X.....X..XX
................
............X...
......X.....X...
................
................
............X.X.
................
  """, """
................
................
...........X....
................
.....XX.........
................
................
......X.........
...X............
................
...X..X.....X...
......X.........
................
............X...
................
................
"""
  ]

  map = map[subPass]
  steps = []
  #TODO Insert algorithm to walk a hamilton loop around that map, syaying on
  #the .'s and avoiding the X's. Noting bottom left is 1,1 and top right is
  #16,16

  # Parse the map into a grid
  lines = [line for line in map.strip().split('\n') if line.strip()]
  gridSize = 16

  # Build set of walkable cells (convert to 1-indexed, bottom-left origin)
  walkable = set()
  for row_idx, line in enumerate(lines):
    y = gridSize - row_idx  # Flip y: top row = 16, bottom row = 1
    for x_idx, ch in enumerate(line):
      if x_idx < gridSize and ch == '.':
        walkable.add((x_idx + 1, y))  # 1-indexed

  if not walkable:
    return {"steps": []}, "No walkable cells"

  # Directions: right, up, left, down
  DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

  def get_neighbors(pos, unvisited):
    """Get walkable unvisited neighbors of a position."""
    x, y = pos
    neighbors = []
    for dx, dy in DIRS:
      np = (x + dx, y + dy)
      if np in unvisited:
        neighbors.append(np)
    return neighbors

  def count_neighbor_degrees(unvisited, exclude_pos=None):
    """Count neighbors for each unvisited cell, optionally excluding a position."""
    test_set = unvisited - {exclude_pos} if exclude_pos else unvisited
    degrees = {}
    for pos in test_set:
      degrees[pos] = len(get_neighbors(pos, test_set))
    return degrees

  def would_create_dead_end(current, next_pos, unvisited, start):
    """Check if moving to next_pos would create an unvisited cell with 0 or 1 neighbors."""
    # Simulate removing next_pos from unvisited
    remaining = unvisited - {next_pos}
    if not remaining:
      return False  # All visited, that's fine

    for pos in remaining:
      if pos == start and len(remaining) == 1:
        # Last cell is start, we need to be able to reach it
        continue
      neighbor_count = len(get_neighbors(pos, remaining))
      if neighbor_count == 0:
        return True  # Isolated cell
      if neighbor_count == 1 and pos != start:
        # Dead end - only acceptable if it's the start and we're about to complete
        if len(remaining) > 1:
          return True
    return False

  def get_straight_runs(pos, direction, unvisited, start):
    """Get all cells in a straight line from pos in given direction."""
    dx, dy = direction
    run = []
    x, y = pos
    while True:
      x, y = x + dx, y + dy
      if (x, y) in unvisited:
        run.append((x, y))
      else:
        break
    return run

  def solve_hamilton(start):
    """DFS solver prioritizing long straight runs."""
    total_cells = len(walkable)

    # Stack: (current_pos, path, unvisited, last_direction)
    stack = [(start, [start], walkable - {start}, None)]

    iterations = 0
    max_iterations = 50_000_000

    while stack:
      iterations += 1
      if iterations > max_iterations:
        return None, f"Exceeded {max_iterations} iterations"

      current, path, unvisited, last_dir = stack.pop()

      # Check if complete
      if not unvisited:
        # Check if we can return to start
        if start in [((current[0] + dx, current[1] + dy)) for dx, dy in DIRS]:
          return path, None
        continue

      # Generate moves prioritizing long straight runs
      moves = []  # (priority, next_pos, new_unvisited, new_dir)

      for dir_idx, (dx, dy) in enumerate(DIRS):
        # Get the straight run in this direction
        run = get_straight_runs(current, (dx, dy), unvisited, start)

        if not run:
          continue

        # Try different run lengths, longest first
        for run_len in range(len(run), 0, -1):
          partial_run = run[:run_len]
          end_pos = partial_run[-1]
          new_unvisited = unvisited - set(partial_run)

          # Check for dead ends
          if would_create_dead_end(current, end_pos, unvisited - set(partial_run[:-1]), start):
            continue

          # Priority: longer runs are better (lower priority number = processed later = better)
          # Negative run_len so longer runs have lower priority value
          priority = -run_len
          moves.append((priority, partial_run, new_unvisited, (dx, dy)))

      # Sort by priority (worst first, so best are popped last)
      moves.sort(key=lambda m: -m[0])

      for priority, partial_run, new_unvisited, new_dir in moves:
        new_path = path + list(partial_run)
        stack.append((partial_run[-1], new_path, new_unvisited, new_dir))

    return None, "No solution found"

  # Try to solve starting from first walkable cell
  start = min(walkable)  # Consistent starting point
  solution, error = solve_hamilton(start)

  if solution is None:
    return {"steps": [], "error": error}, f"Failed: {error}"

  # Convert path to steps (skip first cell as it's the starting position)
  for x, y in solution[1:]:
    steps.append({"xy": [x, y]})

  return {"steps": steps}, "Solved using DFS"
