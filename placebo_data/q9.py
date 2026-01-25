"""
Expanding Barrage Hamilton loop solver for sparse grids.

Algorithm:
1. Split grid into 2x2 chunks, mark solvable (all 4 empty) or unsolvable (has obstacles)
2. Unsolvable chunks grow by absorbing neighbors until solvable
3. Track longest path from failed DFS to prioritize neighbors near unreachable cells
4. Chunks are non-rectangular - DFS handles arbitrary shapes
5. Chunks merge when they collide during growth
6. Once obstacle chunks solved, merge open space into similar-sized chunks
7. Create adjacency graph of chunks, find Hamilton loop through chunks
8. If no loop possible, subdivide open space and retry
9. Stitch chunks by cutting parallel edges along boundaries
"""

from typing import Optional
import random
import re
import os
import json
import hashlib
import tempfile
import sys
from filelock import FileLock

# Import problem definitions from parent module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

_q9_main = importlib.import_module("9")
get_blocked_cells = _q9_main.get_blocked_cells
get_grid_size = _q9_main.get_grid_size
get_valid_cell_count = _q9_main.get_valid_cell_count

# =============================================================================
# Subproblem Cache System
# =============================================================================
# Format: Each cell is '.' (traversable), 'X' (obstacle), or '?' (not relevant)
# Subproblems are normalized to origin and stored by hash of their pattern.

CACHE_DIR = os.path.join(tempfile.gettempdir(), "hamilton_subproblem_cache")


def _ensure_cache_dir():
  """Ensure cache directory exists."""
  os.makedirs(CACHE_DIR, exist_ok=True)


def _subproblem_to_pattern(cells: set, blocked: set, bbox: tuple = None) -> tuple:
  """
  Convert a subproblem to a normalized pattern.
  Returns (pattern_str, offset) where offset is (min_x, min_y) used for normalization.
  Pattern format: rows separated by newlines, '.' = traversable, 'X' = blocked, '?' = not relevant
  """
  if not cells:
    return "", (0, 0)

  # Get bounding box
  all_relevant = cells | blocked
  if bbox:
    min_x, min_y, max_x, max_y = bbox
  else:
    xs = [c[0] for c in all_relevant]
    ys = [c[1] for c in all_relevant]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

  # Build pattern (normalized to origin)
  rows = []
  for y in range(max_y, min_y - 1, -1):  # Top to bottom
    row = ""
    for x in range(min_x, max_x + 1):
      if (x, y) in cells:
        row += "."
      elif (x, y) in blocked:
        row += "X"
      else:
        row += "?"
    rows.append(row)

  pattern = "\n".join(rows)
  return pattern, (min_x, min_y)


def _pattern_to_hash(pattern: str) -> str:
  """Get hash of a pattern for cache lookup."""
  return hashlib.md5(pattern.encode()).hexdigest()


def _get_cache_path(pattern_hash: str) -> str:
  """Get the cache file path for a pattern hash."""
  return os.path.join(CACHE_DIR, f"{pattern_hash}.json")


def _get_lock_path(pattern_hash: str) -> str:
  """Get the lock file path for a pattern hash."""
  return os.path.join(CACHE_DIR, f"{pattern_hash}.lock")


def cache_subproblem_solution(cells: set, blocked: set, solution: list, bbox: tuple = None):
  """
  Cache a solved subproblem.
  solution: list of (x, y) tuples forming the Hamilton path/loop
  """
  _ensure_cache_dir()

  pattern, offset = _subproblem_to_pattern(cells, blocked, bbox)
  if not pattern:
    return

  pattern_hash = _pattern_to_hash(pattern)
  cache_path = _get_cache_path(pattern_hash)
  lock_path = _get_lock_path(pattern_hash)

  # Normalize solution coordinates
  min_x, min_y = offset
  normalized_solution = [(x - min_x, y - min_y) for x, y in solution]

  data = {
    "pattern": pattern,
    "solution": normalized_solution,
  }

  with FileLock(lock_path):
    with open(cache_path, 'w') as f:
      json.dump(data, f)


def lookup_subproblem_solution(cells: set, blocked: set, bbox: tuple = None) -> Optional[list]:
  """
  Look up a cached solution for a subproblem.
  Returns denormalized solution list or None if not cached.
  """
  _ensure_cache_dir()

  pattern, offset = _subproblem_to_pattern(cells, blocked, bbox)
  if not pattern:
    return None

  pattern_hash = _pattern_to_hash(pattern)
  cache_path = _get_cache_path(pattern_hash)
  lock_path = _get_lock_path(pattern_hash)

  if not os.path.exists(cache_path):
    return None

  try:
    with FileLock(lock_path, timeout=5):
      with open(cache_path, 'r') as f:
        data = json.load(f)

    # Denormalize solution coordinates
    min_x, min_y = offset
    solution = [(x + min_x, y + min_y) for x, y in data["solution"]]
    return solution
  except Exception:
    return None


def find_cached_subproblems_in_puzzle(all_cells: set, blocked: set, grid_size: int) -> list:
  """
  Search for any cached subproblems that exist within this puzzle.
  Returns list of (cells, blocked_subset, solution) tuples that match.
  Checks largest patterns first and avoids overlapping matches.
  """
  _ensure_cache_dir()

  matches = []
  claimed_cells = set()  # Track cells already matched to avoid overlaps

  if not os.path.exists(CACHE_DIR):
    return matches

  # Load all cached patterns
  cached_patterns = []
  for filename in os.listdir(CACHE_DIR):
    if not filename.endswith('.json'):
      continue
    cache_path = os.path.join(CACHE_DIR, filename)
    lock_path = cache_path.replace('.json', '.lock')
    try:
      with FileLock(lock_path, timeout=1):
        with open(cache_path, 'r') as f:
          data = json.load(f)
      # Calculate pattern properties
      pattern = data["pattern"]
      pattern_cells = pattern.count('.')
      obstacle_count = pattern.count('X')
      has_obstacles = obstacle_count > 0
      cached_patterns.append((has_obstacles, obstacle_count, pattern_cells, data))
    except Exception:
      continue

  # Sort: obstacle-containing patterns first, then by OBSTACLE COUNT descending, then by size descending
  # Patterns that cover more obstacles should match before ones covering fewer
  # (True sorts after False, so negate has_obstacles to get obstacles first)
  cached_patterns.sort(key=lambda x: (-x[0], -x[1], -x[2]))

  # For each cached pattern, try to find all non-overlapping matches
  # Only match obstacle-containing patterns - open space is handled by normal algorithm
  for has_obstacles, obstacle_count, pattern_size, data in cached_patterns:
    if not has_obstacles:
      continue  # Skip open-space patterns

    pattern = data["pattern"]
    solution = data["solution"]

    rows = pattern.split("\n")
    height = len(rows)
    width = len(rows[0]) if rows else 0

    # Try each possible offset
    for ox in range(1, grid_size - width + 2):
      for oy in range(1, grid_size - height + 2):
        match = True
        matched_cells = set()
        matched_blocked = set()

        for row_idx, row in enumerate(rows):
          y = oy + (height - 1 - row_idx)  # Pattern is top-to-bottom
          for col_idx, ch in enumerate(row):
            x = ox + col_idx
            pos = (x, y)

            if ch == '.':
              if pos not in all_cells or pos in claimed_cells:
                match = False
                break
              matched_cells.add(pos)
            elif ch == 'X':
              if pos not in blocked:
                match = False
                break
              matched_blocked.add(pos)
            # '?' means don't care
          if not match:
            break

        if match and matched_cells:
          # Denormalize solution
          denorm_solution = [(x + ox, y + oy) for x, y in solution]
          # Verify solution cells match
          if set(denorm_solution) == matched_cells:
            matches.append((matched_cells, matched_blocked, denorm_solution))
            # Claim these cells so they can't be used by other matches
            claimed_cells.update(matched_cells)

  return matches


def add_primer_subproblem(pattern: str):
  """
  Add a new primer subproblem to the cache by solving it.
  pattern: string with '.' for traversable, 'X' for obstacle, '?' for irrelevant
  Returns True if solved and cached, False if unsolvable or already cached.
  """
  _ensure_cache_dir()

  pattern_hash = _pattern_to_hash(pattern)
  cache_path = _get_cache_path(pattern_hash)
  lock_path = _get_lock_path(pattern_hash)

  # Early exit if already cached
  if os.path.exists(cache_path):
    return True

  # Parse pattern into cells and blocked sets
  rows = pattern.split("\n")
  cells = set()
  blocked = set()
  height = len(rows)

  for row_idx, row in enumerate(rows):
    y = height - 1 - row_idx  # Pattern is top-to-bottom, coords are bottom-to-top
    for x, ch in enumerate(row):
      if ch == '.':
        cells.add((x, y))
      elif ch == 'X':
        blocked.add((x, y))
      # '?' is ignored (not relevant)

  if len(cells) < 4:
    assert False, "Not enough cells in pattern: " + pattern
    return False  # Can't form a loop

  # Solve using the existing solver
  result = solve_hamilton_with_tracking(cells, max_iterations=500000)
  if not result[0]:
    assert False, "Unsolvable pattern: \n" + pattern
    return False  # Unsolvable

  solution = result[0]

  # Verify it forms a valid loop
  first, last = solution[0], solution[-1]
  if abs(first[0] - last[0]) + abs(first[1] - last[1]) != 1:
    return False  # Not a loop

  data = {
    "pattern": pattern,
    "solution": solution,
  }

  with FileLock(lock_path):
    with open(cache_path, 'w') as f:
      json.dump(data, f)

  return True


# prime_cache() is called later after solve_hamilton_with_tracking is defined


class Chunk:
  """Represents an arbitrary-shaped region of cells."""

  def __init__(self, chunk_id: int, cells: set):
    self.id = chunk_id
    self.cells = set(cells)  # Set of (x, y) coordinates
    self.solution = None  # Hamilton loop through this chunk's cells
    self.has_obstacles = False  # True if this chunk was created due to obstacles
    self.longest_failed_path = []  # Track longest path from failed solve attempts
    self.locked = False  # True if pre-solved from cache (shouldn't be merged)

  def is_solvable_trivially(self) -> bool:
    """Check if this is a simple 2x2 chunk with all cells present."""
    if len(self.cells) != 4:
      return False
    xs = {c[0] for c in self.cells}
    ys = {c[1] for c in self.cells}
    return len(xs) == 2 and len(ys) == 2

  def get_boundary_cells(self) -> set:
    """Get cells that are on the boundary (have neighbors outside chunk)."""
    boundary = set()
    for cell in self.cells:
      x, y = cell
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        neighbor = (x + dx, y + dy)
        if neighbor not in self.cells:
          boundary.add(cell)
          break
    return boundary

  def get_neighbor_cells(self, all_cells: set) -> set:
    """Get cells adjacent to this chunk but not in it."""
    neighbors = set()
    for cell in self.cells:
      x, y = cell
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        neighbor = (x + dx, y + dy)
        if neighbor in all_cells and neighbor not in self.cells:
          neighbors.add(neighbor)
    return neighbors

  def solve(self, max_iterations: int = 500000, blocked: set = None) -> bool:
    """Attempt to solve Hamilton loop for this chunk. Uses cache if available."""
    if len(self.cells) == 0:
      self.solution = []
      return True

    if len(self.cells) < 4:
      return False  # Can't form a loop with < 4 cells

    # Try cache lookup first
    blocked_in_bbox = set()
    if blocked:
      xs = [c[0] for c in self.cells]
      ys = [c[1] for c in self.cells]
      min_x, max_x = min(xs), max(xs)
      min_y, max_y = min(ys), max(ys)
      blocked_in_bbox = {b for b in blocked if min_x <= b[0] <= max_x and min_y <= b[1] <= max_y}

    cached = lookup_subproblem_solution(self.cells, blocked_in_bbox)
    if cached:
      self.solution = cached
      return True

    result = solve_hamilton_with_tracking(self.cells, max_iterations)
    if result[0]:
      self.solution = result[0]
      # Cache the solution
      cache_subproblem_solution(self.cells, blocked_in_bbox, self.solution)
      return True
    else:
      self.longest_failed_path = result[1]
      return False

  def get_unreachable_priority_neighbors(self, all_cells: set) -> list:
    """
    Get neighbor cells prioritized by proximity to cells that couldn't be reached
    in the longest failed path.
    """
    if not self.longest_failed_path:
      return list(self.get_neighbor_cells(all_cells))

    visited_in_path = set(self.longest_failed_path)
    unreached = self.cells - visited_in_path

    neighbors = self.get_neighbor_cells(all_cells)
    if not unreached:
      return list(neighbors)

    # Score neighbors by minimum distance to unreached cells
    def min_dist_to_unreached(cell):
      return min(abs(cell[0] - u[0]) + abs(cell[1] - u[1]) for u in unreached)

    return sorted(neighbors, key=min_dist_to_unreached)


def check_hamilton_feasibility(cells: set, all_cells: set = None) -> tuple:
  """
  Fast feasibility checks for Hamilton loop solvability.
  Returns (is_feasible, reason) where reason explains failure.
  all_cells: set of all traversable cells (to distinguish blocked cells from fillable holes)
  """
  if not cells or len(cells) < 4:
    return (False, "too_few_cells")

  cells = set(cells)

  # Check 1: Checkerboard parity - loop must have equal white/black cells
  white = sum(1 for x, y in cells if (x + y) % 2 == 0)
  black = len(cells) - white
  if white != black:
    return (False, f"parity_mismatch: {white} white vs {black} black")

  # Build adjacency for further checks
  def get_neighbors(pos):
    x, y = pos
    return [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if (x + dx, y + dy) in cells]

  # Check 2: Dead ends - cells with degree 1 can't be in a loop
  for cell in cells:
    if len(get_neighbors(cell)) < 2:
      return (False, f"dead_end at {cell}")

  # Check 3: Connectivity - must be single connected component
  visited = set()
  stack = [next(iter(cells))]
  while stack:
    node = stack.pop()
    if node in visited:
      continue
    visited.add(node)
    stack.extend(n for n in get_neighbors(node) if n not in visited)
  if len(visited) != len(cells):
    return (False, f"disconnected: {len(visited)}/{len(cells)} reachable")

  # Check 4: Articulation points - cells whose removal disconnects the graph
  # Check ALL cells, not just degree-2 (a higher-degree cell can still be a bottleneck)
  for cell in cells:
    degree = len(get_neighbors(cell))
    if degree >= 2:  # Only cells with 2+ neighbors can be articulation points
      # Check if removing this cell disconnects the remaining
      remaining = cells - {cell}
      if len(remaining) < 2:
        continue
      v_start = next(iter(remaining))
      v_visited = set()
      v_stack = [v_start]
      while v_stack:
        node = v_stack.pop()
        if node in v_visited:
          continue
        v_visited.add(node)
        x, y = node
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          n = (x + dx, y + dy)
          if n in remaining and n not in v_visited:
            v_stack.append(n)
      if len(v_visited) != len(remaining):
        return (False, f"articulation_point at {cell}")

  # Check 5: Interior holes - cells surrounded by chunk cells but not in chunk
  # A Hamilton loop cannot exist if there are interior holes
  # Only run this check if we know about all_cells (to distinguish blocked cells)
  if all_cells is not None:
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)

    for x in range(min_x + 1, max_x):
      for y in range(min_y + 1, max_y):
        if (x, y) not in cells:
          # Skip blocked cells - they're expected holes (obstacles)
          if (x, y) not in all_cells:
            continue
          # Check if this empty cell is surrounded by chunk cells (interior hole)
          neighbors_in_chunk = sum(1 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                                   if (x + dx, y + dy) in cells)
          if neighbors_in_chunk >= 3:
            # This is likely an interior hole - check if it's truly interior
            # by seeing if we can reach the boundary without crossing chunk cells
            can_escape = False
            frontier = [(x, y)]
            escaped_visited = {(x, y)}
            while frontier and not can_escape:
              cx, cy = frontier.pop()
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in escaped_visited:
                  continue
                if (nx, ny) in cells:
                  continue  # blocked by chunk
                if nx < min_x or nx > max_x or ny < min_y or ny > max_y:
                  can_escape = True
                  break
                escaped_visited.add((nx, ny))
                frontier.append((nx, ny))
            if not can_escape:
              return (False, f"interior_hole at ({x}, {y})")

  # Check 6: Degree-2 chain analysis - long chains of degree-2 cells are problematic
  degree_2_cells = [c for c in cells if len(get_neighbors(c)) == 2]
  if len(degree_2_cells) > len(cells) * 0.7:
    # Many degree-2 cells often indicates a "snake" shape that can't loop
    # Check if it forms a problematic chain
    chain_count = 0
    checked = set()
    for start_cell in degree_2_cells:
      if start_cell in checked:
        continue
      chain = [start_cell]
      checked.add(start_cell)
      # Follow the chain
      for neighbor in get_neighbors(start_cell):
        if neighbor in degree_2_cells and neighbor not in checked:
          curr = neighbor
          while curr and curr not in checked:
            checked.add(curr)
            chain.append(curr)
            nexts = [n for n in get_neighbors(curr) if n in degree_2_cells and n not in checked]
            curr = nexts[0] if nexts else None
      if len(chain) > 4:
        chain_count += 1
    # Multiple long chains often unsolvable
    if chain_count > 2:
      return (False, f"too_many_degree2_chains: {chain_count}")

  return (True, "feasible")


def solve_hamilton_with_tracking(cells: set, max_iterations: int = 50000) -> tuple:
  """
  Solve Hamilton loop, returning (solution, longest_path_on_failure).
  """
  if not cells or len(cells) < 4:
    return (None, [])

  # Run feasibility checks first
  feasible, reason = check_hamilton_feasibility(cells)
  if not feasible:
    return (None, [])

  cells = set(cells)
  start = min(cells)
  n_cells = len(cells)

  def get_neighbors(pos):
    x, y = pos
    return [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if (x + dx, y + dy) in cells]

  def is_adjacent(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

  def would_create_dead_end(candidate, visited):
    isolated_count = 0
    for neighbor in get_neighbors(candidate):
      if neighbor in visited:
        continue
      count = sum(1 for nn in get_neighbors(neighbor) if nn not in visited and nn != candidate)
      if count == 0 and neighbor != start:
        isolated_count += 1
        if isolated_count > 1:
          return True
    return False

  path = [start]
  visited = {start}
  iterations = [0]
  longest_path = [[]]

  def dfs():
    iterations[0] += 1
    if iterations[0] > max_iterations:
      return False

    if len(path) > len(longest_path[0]):
      longest_path[0] = list(path)

    if len(path) == n_cells:
      return is_adjacent(path[-1], start)

    current = path[-1]
    neighbors = []
    for n in get_neighbors(current):
      if n not in visited:
        degree = sum(1 for nn in get_neighbors(n) if nn not in visited)
        neighbors.append((n, degree))

    neighbors.sort(key=lambda x: x[1])

    for neighbor, degree in neighbors:
      if would_create_dead_end(neighbor, visited):
        continue
      path.append(neighbor)
      visited.add(neighbor)
      if dfs():
        return True
      path.pop()
      visited.remove(neighbor)

    return False

  if dfs():
    return (path, [])
  return (None, longest_path[0])


def format_cells_ascii_art(cells: set, blocked: set = None, grid_size: int = None) -> str:
  if blocked is None:
    blocked = set()
  if grid_size is None:
    max_x = 0
    max_y = 0
    if cells:
      max_x = max(max_x, max(x for x, _ in cells))
      max_y = max(max_y, max(y for _, y in cells))
    if blocked:
      max_x = max(max_x, max(x for x, _ in blocked))
      max_y = max(max_y, max(y for _, y in blocked))
    grid_size = max(max_x, max_y)

  lines = []
  for y in range(grid_size, 0, -1):
    row = []
    for x in range(1, grid_size + 1):
      pos = (x, y)
      if pos in blocked:
        row.append('X')
      elif pos in cells:
        row.append('.')
      else:
        row.append(' ')
    lines.append(''.join(row))
  return '\n'.join(lines)


def dump_unsolved_chunks(chunks: dict,
                         blocked: set = None,
                         all_cells: set = None,
                         grid_size: int = None,
                         header: str = None) -> None:
  if blocked is None:
    blocked = set()
  if grid_size is None:
    max_x = 0
    max_y = 0
    if all_cells:
      max_x = max(max_x, max(x for x, _ in all_cells))
      max_y = max(max_y, max(y for _, y in all_cells))
    if blocked:
      max_x = max(max_x, max(x for x, _ in blocked))
      max_y = max(max_y, max(y for _, y in blocked))
    if max_x and max_y:
      grid_size = max(max_x, max_y)

  unsolved = [c for c in chunks.values() if c.solution is None]
  if not unsolved:
    return

  if header:
    print(header)
  print(f"Unsolved chunks ({len(unsolved)}):")
  unsolved.sort(key=lambda c: (-len(c.cells), c.id))

  for c in unsolved:
    n = len(c.cells)
    feasible, reason = check_hamilton_feasibility(c.cells, all_cells)
    print(
      f"\nChunk {c.id}: {n} cells, has_obstacles={bool(c.has_obstacles)}, locked={bool(getattr(c, 'locked', False))}, feasible={feasible}, reason={reason}"
    )
    if grid_size is not None:
      print(format_cells_ascii_art(c.cells, blocked=blocked, grid_size=grid_size))
    else:
      print(format_cells_ascii_art(c.cells, blocked=blocked))


def create_initial_chunks(grid_size: int, blocked: set) -> tuple:
  """
  Create initial chunks at cell-level granularity.
  1. First, find cached subproblem matches and create pre-solved chunks
  2. Then, cells adjacent to remaining obstacles start as obstacle chunks (need solving)
  3. Other cells stay unassigned and get partitioned later
  """
  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked
  chunks = {}
  chunk_id = 0
  cell_to_chunk = {}

  # Step 1: Find cached subproblem matches BEFORE chunking
  cache_matches = find_cached_subproblems_in_puzzle(all_cells, blocked, grid_size)
  matched_cells = set()
  matched_blocked = set()

  for cells, blocked_subset, solution in cache_matches:
    # Create a pre-solved chunk from this cache match
    chunk = Chunk(chunk_id, cells)
    chunk.has_obstacles = bool(blocked_subset)
    chunk.solution = solution
    # Only lock obstacle-containing chunks - open space can be re-merged if needed
    chunk.locked = bool(blocked_subset)
    chunks[chunk_id] = chunk
    for cell in cells:
      cell_to_chunk[cell] = chunk_id
    matched_cells.update(cells)
    matched_blocked.update(blocked_subset)
    print(f"  Pre-solved chunk {chunk_id} from cache: {len(cells)} cells" +
          (" (locked)" if chunk.locked else ""))
    ascii_art = format_cells_ascii_art(cells, blocked=blocked_subset, grid_size=grid_size)
    print(ascii_art)
    chunk_id += 1

  # Step 2: Find cells adjacent to REMAINING obstacles (not covered by cache matches)
  remaining_blocked = blocked - matched_blocked
  obstacle_adjacent = set()
  for bx, by in remaining_blocked:
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      cell = (bx + dx, by + dy)
      if cell in all_cells and cell not in matched_cells:
        obstacle_adjacent.add(cell)

  # Create one chunk per connected group of obstacle-adjacent cells
  remaining_obstacle_adj = set(obstacle_adjacent)
  while remaining_obstacle_adj:
    start = min(remaining_obstacle_adj)
    # BFS to find connected component
    component = {start}
    queue = [start]
    while queue:
      cell = queue.pop(0)
      x, y = cell
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        neighbor = (x + dx, y + dy)
        if neighbor in remaining_obstacle_adj and neighbor not in component:
          component.add(neighbor)
          queue.append(neighbor)

    remaining_obstacle_adj -= component

    # Create chunk from this component
    chunk = Chunk(chunk_id, component)
    chunk.has_obstacles = True
    chunks[chunk_id] = chunk
    for cell in component:
      cell_to_chunk[cell] = chunk_id
    chunk_id += 1

  # Remaining cells (not adjacent to obstacles) stay unassigned for now
  # They'll be partitioned later in partition_open_space

  return chunks, all_cells, cell_to_chunk


def merge_chunks(chunks: dict, chunk1_id: int, chunk2_id: int, cell_to_chunk: dict) -> int:
  """Merge two chunks, returning the ID of the merged chunk."""
  if chunk1_id == chunk2_id:
    return chunk1_id

  # Handle stale chunk IDs (chunks that were already merged)
  if chunk1_id not in chunks:
    return chunk2_id if chunk2_id in chunks else -1
  if chunk2_id not in chunks:
    return chunk1_id

  c1 = chunks[chunk1_id]
  c2 = chunks[chunk2_id]

  # Don't merge locked chunks (pre-solved from cache)
  if c1.locked and c2.locked:
    return chunk1_id  # Both locked, can't merge
  if c1.locked:
    return chunk1_id  # c1 is locked, don't merge into it
  if c2.locked:
    return chunk2_id  # c2 is locked, don't merge into it

  # Merge into the one with obstacles, or the larger one
  if c2.has_obstacles and not c1.has_obstacles:
    keep, remove = chunk2_id, chunk1_id
  elif c1.has_obstacles and not c2.has_obstacles:
    keep, remove = chunk1_id, chunk2_id
  elif len(c1.cells) >= len(c2.cells):
    keep, remove = chunk1_id, chunk2_id
  else:
    keep, remove = chunk2_id, chunk1_id

  kept = chunks[keep]
  removed = chunks[remove]

  # Transfer cells
  for cell in removed.cells:
    kept.cells.add(cell)
    cell_to_chunk[cell] = keep

  kept.has_obstacles = kept.has_obstacles or removed.has_obstacles
  if not kept.locked:
    kept.solution = None  # Need to re-solve
  kept.longest_failed_path = []

  del chunks[remove]
  return keep


def expand_chunk(chunk: Chunk,
                 neighbor_cell: tuple,
                 cell_to_chunk: dict,
                 chunks: dict,
                 allow_merge_solved: bool = True) -> int:
  """
  Add a neighbor cell to this chunk. If cell belongs to another chunk, merge them.
  Returns the ID of the resulting chunk.
  If allow_merge_solved is False, won't merge with chunks that have solutions.
  """
  # Check if chunk still exists (might have been merged)
  if chunk.id not in chunks:
    return -1

  if neighbor_cell in chunk.cells:
    return chunk.id

  if neighbor_cell in cell_to_chunk:
    other_id = cell_to_chunk[neighbor_cell]
    if other_id != chunk.id:
      other_chunk = chunks.get(other_id)
      if other_chunk:
        # Never merge with locked chunks
        if other_chunk.locked:
          return chunk.id  # Skip this cell - can't merge with locked
        if other_chunk.solution is not None:
          # Don't merge with solved chunks unless:
          # 1. allow_merge_solved is True, OR
          # 2. The other chunk is small (<=4 cells)
          if not allow_merge_solved:
            is_small = len(other_chunk.cells) <= 4
            if not is_small:
              return chunk.id  # Skip this cell
      return merge_chunks(chunks, chunk.id, other_id, cell_to_chunk)
    return chunk.id

  chunk.cells.add(neighbor_cell)
  cell_to_chunk[neighbor_cell] = chunk.id
  chunk.solution = None
  chunk.longest_failed_path = []
  return chunk.id


def pick_best_expansion_cell(candidates: set,
                             chunk_cells: set,
                             blocked: set,
                             need_parity: int = None) -> tuple:
  """
  Pick the best cell to expand into. Prioritizes:
  1. Parity balance (if need_parity specified: 0=white, 1=black)
  2. Cells that fill interior holes (inside current bbox)
  3. Cells adjacent to blocked cells (obstacles)
  4. Cells with more neighbors already in chunk (more connected)
  """
  if not candidates:
    return None

  xs = [c[0] for c in chunk_cells]
  ys = [c[1] for c in chunk_cells]
  min_x, max_x = min(xs), max(xs)
  min_y, max_y = min(ys), max(ys)

  def score(cell):
    x, y = cell
    s = 0

    # Highest priority: parity balance
    cell_parity = (x + y) % 2
    if need_parity is not None:
      if cell_parity == need_parity:
        s += 10000  # Strong preference for needed parity
      else:
        s -= 5000  # Discourage wrong parity

    # Strong bonus for being inside current bbox (fills holes)
    if min_x <= x <= max_x and min_y <= y <= max_y:
      s += 1000
    # Bonus for being adjacent to blocked cells
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      if (x + dx, y + dy) in blocked:
        s += 500
    # Bonus for having more neighbors in chunk (more connected)
    neighbors_in_chunk = sum(1 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                             if (x + dx, y + dy) in chunk_cells)
    s += neighbors_in_chunk * 100
    # Slight preference for cells closer to center of chunk
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    s -= abs(x - cx) + abs(y - cy)
    return s

  return max(candidates, key=score)


def pick_best_expansion_pair(candidates: set, chunk_cells: set, blocked: set) -> list:
  """
  Pick the best pair of adjacent cells to add together (maintains parity balance).
  Returns list of 1 or 2 cells to add.
  """
  if not candidates:
    return []

  # Current parity
  white = sum(1 for x, y in chunk_cells if (x + y) % 2 == 0)
  black = len(chunk_cells) - white

  if white == black:
    # Balanced - add a pair of adjacent cells (one white, one black)
    best_pair = None
    best_score = -float('inf')

    for c1 in candidates:
      x1, y1 = c1
      for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        c2 = (x1 + dx, y1 + dy)
        if c2 in candidates and c2 != c1:
          # c1 and c2 are adjacent candidates - check parity
          p1 = (x1 + y1) % 2
          p2 = (c2[0] + c2[1]) % 2
          if p1 != p2:  # One white, one black
            # Score this pair
            score = 0
            for c in [c1, c2]:
              x, y = c
              # Bonus for adjacency to chunk
              neighbors_in_chunk = sum(1 for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                                       if (x + ddx, y + ddy) in chunk_cells)
              score += neighbors_in_chunk * 100
              # Bonus for being near obstacles
              for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if (x + ddx, y + ddy) in blocked:
                  score += 50
            if score > best_score:
              best_score = score
              best_pair = [c1, c2]

    if best_pair:
      return best_pair
    # Fall back to single cell if no pair found
    return [pick_best_expansion_cell(candidates, chunk_cells, blocked)]
  else:
    # Imbalanced - add single cell of needed parity
    need_white = black > white
    need_parity = 0 if need_white else 1
    return [pick_best_expansion_cell(candidates, chunk_cells, blocked, need_parity)]


def solve_obstacle_chunks(chunks: dict,
                          all_cells: set,
                          cell_to_chunk: dict,
                          blocked: set = None,
                          max_growth_iterations: int = 500,
                          max_chunk_size: int = 36) -> bool:
  """
  Grow and solve all obstacle-containing chunks until they're all solved.
  Strategy: grow chunks to rectangular shapes, limit size to stay solvable.
  """
  obstacle_chunks = [c for c in chunks.values() if c.has_obstacles]
  print(f"Initial obstacle chunks: {len(obstacle_chunks)}, max size: {max_chunk_size}")

  for iteration in range(max_growth_iterations):
    unsolved_ids = [c.id for c in chunks.values() if c.has_obstacles and c.solution is None]
    if not unsolved_ids:
      return True

    if iteration < 10 or iteration % 20 == 0:
      sizes = [len(chunks[uid].cells) for uid in unsolved_ids if uid in chunks]
      print(f"Iter {iteration}: {len(unsolved_ids)} unsolved, sizes: {sizes[:5]}")

    made_progress = False

    # Sort by size - try to solve smallest first
    unsolved_ids.sort(key=lambda uid: len(chunks[uid].cells) if uid in chunks else 999)

    for chunk_id in unsolved_ids:
      if chunk_id not in chunks:
        made_progress = True
        continue

      chunk = chunks[chunk_id]
      if chunk.solution is not None:
        continue

      # Expand small chunks first - use parity-aware expansion
      while len(chunk.cells) < 4:
        adj = set()
        for cell in chunk.cells:
          x, y = cell
          for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            n = (x + dx, y + dy)
            if n in all_cells and n not in chunk.cells:
              adj.add(n)
        if not adj:
          break
        # Use parity-aware expansion
        cells_to_add = pick_best_expansion_pair(adj, chunk.cells, blocked or set())
        for cell_to_add in cells_to_add:
          if cell_to_add and cell_to_add in all_cells and len(chunk.cells) < 4:
            new_id = expand_chunk(chunk, cell_to_add, cell_to_chunk, chunks)
            made_progress = True
            if new_id != chunk_id:
              chunk = chunks[new_id]
              chunk_id = new_id

      # Check feasibility before attempting expensive DFS
      n = len(chunk.cells)
      feasible, reason = check_hamilton_feasibility(chunk.cells, all_cells)

      # Debug: minimal output
      if iteration < 3 or iteration % 20 == 0:
        print(f"  Chunk {chunk_id}: {n} cells, feasible={feasible}")

      if not feasible:
        # Use reason to guide smart expansion
        adj = chunk.get_neighbor_cells(all_cells)
        if adj:
          if "parity_mismatch" in reason:
            # Need to add cell of opposite color to balance
            white = sum(1 for x, y in chunk.cells if (x + y) % 2 == 0)
            black = n - white
            need_white = black > white

            # First: check if merging with adjacent chunk would help balance parity
            # Find adjacent chunks with complementary parity
            adjacent_chunk_ids = set()
            for cell in chunk.cells:
              x, y = cell
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc = (x + dx, y + dy)
                if nc in cell_to_chunk and cell_to_chunk[nc] != chunk_id:
                  adjacent_chunk_ids.add(cell_to_chunk[nc])

            for other_id in adjacent_chunk_ids:
              if other_id not in chunks:
                continue
              other = chunks[other_id]
              if other.solution is not None:
                continue  # Don't merge with solved chunks
              other_white = sum(1 for x, y in other.cells if (x + y) % 2 == 0)
              other_black = len(other.cells) - other_white
              # Check if merging would balance parity
              combined_white = white + other_white
              combined_black = black + other_black
              if combined_white == combined_black:
                # Merge would balance parity!
                new_id = merge_chunks(chunks, chunk_id, other_id, cell_to_chunk)
                chunks[new_id].solution = None
                made_progress = True
                break
            if made_progress:
              continue

            # Otherwise try to add cell of needed color
            parity_adj = [c for c in adj if ((c[0] + c[1]) % 2 == 0) == need_white]
            if parity_adj:
              best = pick_best_expansion_cell(set(parity_adj), chunk.cells, blocked or set())
              new_id = expand_chunk(chunk, best, cell_to_chunk, chunks)
              made_progress = True
              if new_id != chunk_id:
                chunks[new_id].solution = None
              continue
          elif "dead_end" in reason:
            # Find the dead end and expand near it
            for cell in chunk.cells:
              x, y = cell
              neighbors_in_chunk = sum(1 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                                       if (x + dx, y + dy) in chunk.cells)
              if neighbors_in_chunk < 2:
                # Expand adjacent to this dead end
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                  nc = (x + dx, y + dy)
                  if nc in adj:
                    new_id = expand_chunk(chunk, nc, cell_to_chunk, chunks)
                    made_progress = True
                    if new_id != chunk_id:
                      chunks[new_id].solution = None
                    break
                if made_progress:
                  break
            if made_progress:
              continue
          elif "articulation_point" in reason:
            # Need to add alternative paths around bottleneck
            # Extract the articulation point from reason and expand near it
            match = re.search(r'at \((\d+), (\d+)\)', reason)
            if match:
              art_x, art_y = int(match.group(1)), int(match.group(2))
              # Add cells adjacent to the articulation point
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc = (art_x + dx, art_y + dy)
                if nc in adj:
                  new_id = expand_chunk(chunk, nc, cell_to_chunk, chunks)
                  made_progress = True
                  if new_id != chunk_id:
                    chunks[new_id].solution = None
                  break
              if made_progress:
                continue
          elif "interior_hole" in reason:
            # Fill the hole by adding the hole cell to the chunk
            match = re.search(r'at \((\d+), (\d+)\)', reason)
            if match:
              hole_x, hole_y = int(match.group(1)), int(match.group(2))
              hole_cell = (hole_x, hole_y)
              if hole_cell in all_cells:
                new_id = expand_chunk(chunk, hole_cell, cell_to_chunk, chunks)
                made_progress = True
                if new_id != chunk_id:
                  chunks[new_id].solution = None
                continue
          # Default: just expand with smart cell selection
          best = pick_best_expansion_cell(adj, chunk.cells, blocked or set())
          new_id = expand_chunk(chunk, best, cell_to_chunk, chunks)
          made_progress = True
          if new_id != chunk_id:
            chunks[new_id].solution = None
          continue

      # Try to solve - scale iterations with chunk size
      result = solve_hamilton_with_tracking(chunk.cells, 5000 * n + 50000)

      if result[0]:
        chunk.solution = result[0]
        made_progress = True
        print(f"Solved chunk {chunk_id}: {n} cells")
        continue

      chunk.longest_failed_path = result[1]

      # If chunk is getting too big, try a different expansion strategy
      if n > 40:
        # Try expanding toward the "dead ends" in the longest path
        if chunk.longest_failed_path:
          path_set = set(chunk.longest_failed_path)
          unreached = chunk.cells - path_set
          if unreached:
            # Find cells adjacent to unreached areas
            for cell in unreached:
              x, y = cell
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                n_cell = (x + dx, y + dy)
                if n_cell in all_cells and n_cell not in chunk.cells:
                  new_id = expand_chunk(chunk, n_cell, cell_to_chunk, chunks)
                  made_progress = True
                  if new_id != chunk_id:
                    chunks[new_id].solution = None
                  break
              if made_progress:
                break
          if made_progress:
            continue

      # Normal expansion - add cells in parity-balanced pairs
      adj = chunk.get_neighbor_cells(all_cells)
      adj = {
        c
        for c in adj if c not in cell_to_chunk or cell_to_chunk[c] not in chunks
        or not chunks[cell_to_chunk[c]].locked
      }
      if adj:
        # Use parity-aware expansion to maintain solvability
        cells_to_add = pick_best_expansion_pair(adj, chunk.cells, blocked or set())
        old_size = len(chunk.cells)
        for cell_to_add in cells_to_add:
          if cell_to_add and cell_to_add in all_cells:
            new_id = expand_chunk(chunk, cell_to_add, cell_to_chunk, chunks)
            if new_id != chunk_id:
              chunk = chunks[new_id]
              chunk_id = new_id
        # Only count as progress if chunk actually grew
        if len(chunk.cells) > old_size:
          made_progress = True
          if not chunks[chunk_id].locked:
            chunks[chunk_id].solution = None
      if not adj and not made_progress:
        # No neighbors in all_cells, must merge with adjacent chunk
        for cell in chunk.cells:
          x, y = cell
          for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            n = (x + dx, y + dy)
            if n in cell_to_chunk and cell_to_chunk[n] != chunk_id:
              other_id = cell_to_chunk[n]
              if other_id in chunks and not chunks[other_id].locked:
                new_id = merge_chunks(chunks, chunk_id, other_id, cell_to_chunk)
                if not chunks[new_id].locked:
                  chunks[new_id].solution = None
                made_progress = True
                break
          if made_progress:
            break

    if not made_progress:
      # Last resort - force merge
      unsolved = [c for c in chunks.values() if c.has_obstacles and c.solution is None]
      if not unsolved:
        return True
      smallest = min(unsolved, key=lambda c: len(c.cells))
      for cell in smallest.cells:
        x, y = cell
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          n = (x + dx, y + dy)
          if n in cell_to_chunk and cell_to_chunk[n] != smallest.id:
            other_id = cell_to_chunk[n]
            if other_id in chunks and not chunks[other_id].locked:
              new_id = merge_chunks(chunks, smallest.id, other_id, cell_to_chunk)
              if not chunks[new_id].locked:
                chunks[new_id].solution = None
              made_progress = True
              break
        if made_progress:
          break
      if not made_progress:
        # Check if unsolved chunks are surrounded only by locked chunks
        # If so, unlock the smallest adjacent locked chunk
        unsolved = [c for c in chunks.values() if c.has_obstacles and c.solution is None]
        for uc in unsolved:
          locked_neighbors = set()
          for cell in uc.cells:
            x, y = cell
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
              n = (x + dx, y + dy)
              if n in cell_to_chunk:
                other_id = cell_to_chunk[n]
                if other_id in chunks and chunks[other_id].locked:
                  locked_neighbors.add(other_id)
          if locked_neighbors:
            # Unlock the smallest locked neighbor
            smallest_locked_id = min(locked_neighbors, key=lambda lid: len(chunks[lid].cells))
            print(
              f"  Unlocking chunk {smallest_locked_id} ({len(chunks[smallest_locked_id].cells)} cells) to allow progress"
            )
            chunks[smallest_locked_id].locked = False
            chunks[smallest_locked_id].solution = None
            made_progress = True
            break
        if not made_progress:
          print(f"Stuck at iteration {iteration}")
          return False

  return False


def partition_open_space(chunks: dict, all_cells: set, cell_to_chunk: dict,
                         target_size: int) -> None:
  """
  Partition remaining open space into 2x2 chunks where possible.
  Leftover cells get their own singleton chunks (to be merged during solve).
  Never touches solved chunks.
  """
  # Find cells not yet in any chunk
  unassigned = all_cells - set(cell_to_chunk.keys())
  if not unassigned:
    return

  chunk_id = max(chunks.keys()) + 1 if chunks else 0

  # Greedily create 2x2 chunks from unassigned cells
  # Process in grid order for consistent results
  processed = set()
  for cell in sorted(unassigned):
    if cell in processed:
      continue
    x, y = cell
    # Try to form a 2x2 starting at this cell
    cells_2x2 = set()
    for dx in range(2):
      for dy in range(2):
        c = (x + dx, y + dy)
        if c in unassigned and c not in processed:
          cells_2x2.add(c)

    if len(cells_2x2) == 4:
      # Got a full 2x2 - don't pre-solve, leave for merging flexibility
      chunk = Chunk(chunk_id, cells_2x2)
      chunk.has_obstacles = False
      chunk.solution = None  # Will be solved after merging
      chunks[chunk_id] = chunk
      for c in cells_2x2:
        cell_to_chunk[c] = chunk_id
        processed.add(c)
      chunk_id += 1

  # Remaining cells become singleton chunks
  for cell in unassigned:
    if cell not in processed:
      chunk = Chunk(chunk_id, {cell})
      chunk.has_obstacles = False
      chunks[chunk_id] = chunk
      cell_to_chunk[cell] = chunk_id
      chunk_id += 1


def solve_open_chunks(chunks: dict,
                      cell_to_chunk: dict = None,
                      all_cells: set = None,
                      blocked: set = None,
                      max_attempts: int = 200) -> bool:
  """
  Solve all open space chunks. Grow and merge if needed.
  """
  MAX_OPEN_CHUNK_SIZE = 56  # soft cap for normal growth
  HARD_CHUNK_CAP = 64  # absolute cap to avoid runaway growth

  def neighbors4(cell):
    x, y = cell
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

  for attempt in range(max_attempts):
    # Get fresh list of unsolved chunk IDs each iteration
    unsolved_ids = [c.id for c in chunks.values() if not c.has_obstacles and c.solution is None]
    if not unsolved_ids:
      return True

    if attempt == 0 or (attempt < 10 and attempt % 5 == 0) or attempt % 50 == 0:
      print(f"  solve_open_chunks iter {attempt}: {len(unsolved_ids)} unsolved")

    made_progress = False

    for chunk_id in unsolved_ids:
      # Chunk may have been merged away
      if chunk_id not in chunks:
        made_progress = True
        continue

      chunk = chunks[chunk_id]
      if chunk.solution is not None:
        continue

      n = len(chunk.cells)

      # Check feasibility first
      feasible, reason = check_hamilton_feasibility(chunk.cells)

      # For articulation_point, try solving anyway - the check can be conservative
      if not feasible and "articulation_point" in str(reason) and n >= 20:
        print(f"  Chunk {chunk_id}: articulation_point detected, trying solve anyway...")
        if chunk.solve(max_iterations=10000 * n, blocked=blocked):
          made_progress = True
          continue

      if not feasible:
        # Don't abort on hard cap - try to fix structural issues first
        if n > HARD_CHUNK_CAP and n > 150:
          print(f"Chunk {chunk_id} exceeds hard cap ({n} cells), aborting open-chunk solve")
          print(
            f"  Cell y-range: {min(c[1] for c in chunk.cells)}-{max(c[1] for c in chunk.cells)}")
          print(
            f"  Cell x-range: {min(c[0] for c in chunk.cells)}-{max(c[0] for c in chunk.cells)}")
          print("  (X = obstacle for context, . = cells in this chunk, space = other)")
          print(format_cells_ascii_art(chunk.cells, blocked=blocked))
          return False

        # Need to grow or merge this chunk
        if cell_to_chunk is not None and all_cells is not None:
          # For oversized chunks (from parity merge), use higher cap to allow fixing structural issues
          effective_cap = max(MAX_OPEN_CHUNK_SIZE, n +
                              10) if n > MAX_OPEN_CHUNK_SIZE else MAX_OPEN_CHUNK_SIZE
          # Filter adjacent cells to exclude those in solved chunks (but allow merging with locked for dead_end fix)
          all_adj = chunk.get_neighbor_cells(all_cells)
          # If feasibility cites a specific choke point, bias growth to that area
          target = None
          m = re.search(r'at \((\d+), (\d+)\)', str(reason))
          if m:
            target = (int(m.group(1)), int(m.group(2)))

          # For articulation_point issues, find and widen the one-way street
          if "articulation_point" in str(reason) and target:
            tx, ty = target
            # Find the one-way street: cells near the articulation point that form a narrow corridor
            # (cells with exactly 2 neighbors in chunk, forming a line)
            one_way_cells = []
            for cell in chunk.cells:
              cx, cy = cell
              if abs(cx - tx) + abs(cy - ty) <= 5:  # Near the articulation point (wider search)
                neighbors_in_chunk = [n for n in neighbors4(cell) if n in chunk.cells]
                if len(neighbors_in_chunk) == 2:
                  # Check if neighbors are collinear (forming a corridor)
                  n1, n2 = neighbors_in_chunk
                  if n1[0] == n2[0] or n1[1] == n2[1]:  # Same row or column
                    one_way_cells.append(cell)

            print(
              f"    One-way street near {target}: {len(one_way_cells)} cells: {one_way_cells[:5]}")

            # Find cells adjacent to the one-way street that would widen it
            widening_candidates = set()
            all_adjacent_to_oneway = set()
            for cell in one_way_cells:
              for n in neighbors4(cell):
                if n not in chunk.cells:
                  all_adjacent_to_oneway.add(n)
                  if n in all_cells:
                    # Check this cell isn't in a locked chunk
                    owner = cell_to_chunk.get(n)
                    if owner is None or owner not in chunks or not chunks[owner].locked:
                      widening_candidates.add(n)

            print(
              f"    Adjacent to one-way: {len(all_adjacent_to_oneway)}, unlocked candidates: {len(widening_candidates)}"
            )

            # LAST RESORT: If no unlocked candidates, try unlocking a small locked chunk to widen
            if all_adjacent_to_oneway and not widening_candidates:
              # Find locked chunks adjacent to one-way street
              locked_neighbors = set()
              in_grid_count = 0
              in_chunk_count = 0
              for adj in all_adjacent_to_oneway:
                if adj in all_cells:
                  in_grid_count += 1
                  owner = cell_to_chunk.get(adj)
                  if owner is not None and owner in chunks:  # Fix: owner can be 0
                    if chunks[owner].locked:
                      locked_neighbors.add(owner)
                    elif owner == chunk_id:
                      in_chunk_count += 1

              print(
                f"      In grid: {in_grid_count}, in this chunk: {in_chunk_count}, locked neighbors: {locked_neighbors}"
              )
              # Debug: show what chunks own the adjacent cells
              for adj in list(all_adjacent_to_oneway)[:5]:
                if adj in all_cells:
                  owner = cell_to_chunk.get(adj)
                  if owner is not None and owner in chunks:  # Fix: owner can be 0
                    c = chunks[owner]
                    print(
                      f"        {adj} -> chunk {owner}: locked={c.locked}, has_obs={c.has_obstacles}, solved={c.solution is not None}"
                    )
                  else:
                    print(
                      f"        {adj} -> owner={owner}, in chunks={owner in chunks if owner is not None else 'N/A'}"
                    )

              if locked_neighbors:
                # Instead of unlocking entire chunk, steal just the cells adjacent to one-way street
                smallest_locked = min(locked_neighbors, key=lambda cid: len(chunks[cid].cells))
                locked_chunk = chunks[smallest_locked]

                # Find cells from locked chunk that are adjacent to one-way street
                cells_to_steal = set()
                for adj in all_adjacent_to_oneway:
                  if adj in all_cells and cell_to_chunk.get(adj) == smallest_locked:
                    cells_to_steal.add(adj)

                if cells_to_steal:
                  # Find a complete row/column to steal to avoid breaking locked chunk connectivity
                  # Group cells by y-coordinate (same row)
                  rows = {}
                  for c in cells_to_steal:
                    if c[1] not in rows:
                      rows[c[1]] = []
                    rows[c[1]].append(c)

                  # Find a row where we can steal ALL cells in that row from the locked chunk
                  # to maintain connectivity
                  best_row = None
                  best_row_cells = None
                  for y, row_cells in rows.items():
                    # Get ALL cells in this row from the locked chunk
                    full_row = [c for c in locked_chunk.cells if c[1] == y]
                    # Check if stealing this row would leave the locked chunk connected
                    remaining = locked_chunk.cells - set(full_row)
                    if len(remaining) >= 4:  # Need enough cells left to solve
                      # Check parity of full row
                      white = sum(1 for c in full_row if (c[0] + c[1]) % 2 == 0)
                      black = len(full_row) - white
                      if white == black:  # Balanced parity
                        if best_row_cells is None or len(full_row) < len(best_row_cells):
                          best_row = y
                          best_row_cells = full_row

                  if best_row_cells and len(best_row_cells) <= 12:
                    # Check if stealing would break the locked chunk
                    remaining = locked_chunk.cells - set(best_row_cells)
                    remaining_feasible, _ = check_hamilton_feasibility(remaining)
                    if remaining_feasible:
                      print(
                        f"    LAST RESORT: stealing row y={best_row} ({len(best_row_cells)} cells) from chunk {smallest_locked}"
                      )
                      steal_set = set(best_row_cells)
                      locked_chunk.cells -= steal_set
                      locked_chunk.solution = None
                      chunk.cells |= steal_set
                      for c in steal_set:
                        cell_to_chunk[c] = chunk_id
                      made_progress = True
                      continue
                    # Stealing would break locked chunk - unlock entirely
                  # Fallback: unlock entire chunk
                  print(
                    f"    LAST RESORT: unlocking chunk {smallest_locked} ({len(locked_chunk.cells)} cells)"
                  )
                  locked_chunk.locked = False
                  locked_chunk.solution = None
                  made_progress = True
                  continue

            if widening_candidates:
              # Prefer cells that would add a parallel row (adjacent to multiple one-way cells)
              def widening_score(c):
                adjacent_to_oneway = sum(1 for ow in one_way_cells
                                         if abs(c[0] - ow[0]) + abs(c[1] - ow[1]) == 1)
                return (-adjacent_to_oneway, abs(c[0] - tx) + abs(c[1] - ty))

              best = min(widening_candidates, key=widening_score)
              best_owner = cell_to_chunk.get(best)
              if best_owner is not None and best_owner in chunks and not chunks[best_owner].locked:
                expand_chunk(chunk, best, cell_to_chunk, chunks, allow_merge_solved=True)
                made_progress = True
                continue
              elif best_owner is None:
                expand_chunk(chunk, best, cell_to_chunk, chunks, allow_merge_solved=True)
                made_progress = True
                continue

          # For dead_end issues, allow merging with any non-locked chunk
          if "dead_end" in str(reason) and n > MAX_OPEN_CHUNK_SIZE:
            if not target:
              continue
            adj = {
              c
              for c in all_adj if c not in cell_to_chunk or cell_to_chunk[c] not in chunks
              or not chunks[cell_to_chunk[c]].locked
            }
            if not adj:
              # Debug: see what's around the dead end
              tx, ty = target
              neighbors = [(tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)]
              print(f"Dead end at {target}, neighbors: {neighbors}")
              for nb in neighbors:
                if nb in all_cells:
                  owner = cell_to_chunk.get(nb)
                  if owner is not None and owner in chunks:
                    print(
                      f"  {nb} -> chunk {owner}, locked={chunks[owner].locked}, size={len(chunks[owner].cells)}"
                    )
                  else:
                    print(f"  {nb} -> unassigned or missing chunk")
                else:
                  print(f"  {nb} -> not in grid")
          else:
            adj = {
              c
              for c in all_adj if c not in cell_to_chunk or cell_to_chunk[c] not in chunks
              or chunks[cell_to_chunk[c]].solution is None or (
                len(chunks[cell_to_chunk[c]].cells) <= 4 and not chunks[cell_to_chunk[c]].locked
                and len(chunk.cells) + len(chunks[cell_to_chunk[c]].cells) <= effective_cap)
            }

          # Special handling for parity mismatch: add a cell of the needed parity near frontier/dead-ends
          if "parity_mismatch" in str(reason):
            match = re.search(r'parity_mismatch:\s+(\d+)\s+white\s+vs\s+(\d+)\s+black', str(reason))
            needed_parity = None
            if match:
              white_cnt, black_cnt = int(match.group(1)), int(match.group(2))
              if white_cnt != black_cnt:
                needed_parity = 0 if white_cnt < black_cnt else 1
                print(
                  f"  Chunk {chunk_id}: parity mismatch {white_cnt} white vs {black_cnt} black, need parity {needed_parity}"
                )
            if needed_parity is not None:
              frontier = {
                c
                for c in chunk.cells if any(n not in chunk.cells for n in neighbors4(c))
              }
              dead_ends = {
                c
                for c in frontier if sum(1 for n in neighbors4(c) if n in chunk.cells) == 1
              }

              def parity_score(c):
                neighbor_count = sum(1 for n in neighbors4(c) if n in chunk.cells)
                dist_dead = min(abs(c[0] - d[0]) + abs(c[1] - d[1])
                                for d in dead_ends) if dead_ends else 0
                return (dist_dead, -neighbor_count, c[0], c[1])

              # Look at ALL neighbors (not just unsolved) for parity fix
              # Allow growth beyond soft cap to fix parity - this is critical
              all_adj = chunk.get_neighbor_cells(all_cells)
              parity_adj = [c for c in all_adj if (c[0] + c[1]) % 2 == needed_parity]
              # Filter out locked chunks
              parity_adj = [
                c for c in parity_adj if c not in cell_to_chunk or cell_to_chunk[c] not in chunks
                or not chunks[cell_to_chunk[c]].locked
              ]
              print(f"    all_adj={len(all_adj)}, parity_adj={len(parity_adj)}")
              parity_fixed = False
              if parity_adj:
                # Use a much higher cap for parity fixing - crucial to fix parity before chunks get stuck
                parity_cap = max(100, n + 30)  # Allow growing to ~100+ cells to fix parity

                # Key insight: when merging with another chunk, we get ALL its cells
                # So check if merge would IMPROVE parity, not make it worse
                def would_improve_parity(candidate):
                  owner = cell_to_chunk.get(candidate) if cell_to_chunk else None
                  if owner is None or owner not in chunks or owner == chunk.id:
                    # Adding single cell - always improves if it's the right parity
                    return True
                  other = chunks[owner]
                  if other.locked:
                    return False
                  # Check parity of other chunk
                  other_white = sum(1 for c in other.cells if (c[0] + c[1]) % 2 == 0)
                  other_black = len(other.cells) - other_white
                  # Current imbalance: white_cnt - black_cnt (positive = need black)
                  current_imbalance = white_cnt - black_cnt
                  other_imbalance = other_white - other_black
                  # After merge: imbalances add
                  new_imbalance = current_imbalance + other_imbalance
                  # Good if new imbalance is closer to 0
                  return abs(new_imbalance) < abs(current_imbalance)

                # Prefer candidates that improve parity, then by parity_score
                improving = [c for c in parity_adj if would_improve_parity(c)]
                sorted_candidates = sorted(improving, key=parity_score) if improving else sorted(
                  parity_adj, key=parity_score)

                for best in sorted_candidates:
                  best_owner = cell_to_chunk.get(best) if cell_to_chunk else None
                  best_owner_size = len(
                    chunks[best_owner].cells) if best_owner and best_owner in chunks else 0
                  if len(chunk.cells) < parity_cap:
                    # Ensure merge won't exceed parity cap
                    if cell_to_chunk is not None and cell_to_chunk.get(best) not in (None,
                                                                                     chunk.id):
                      other_id = cell_to_chunk[best]
                      if other_id in chunks:
                        if chunks[other_id].locked:
                          continue  # Try next candidate
                        elif len(chunk.cells) + len(chunks[other_id].cells) > parity_cap:
                          continue  # Try next candidate
                        else:
                          # Allow merging with solved chunks for parity fix
                          expand_chunk(chunk, best, cell_to_chunk, chunks, allow_merge_solved=True)
                          made_progress = True
                          parity_fixed = True
                          break
                    else:
                      if len(chunk.cells) + 1 <= parity_cap:
                        expand_chunk(chunk, best, cell_to_chunk, chunks, allow_merge_solved=True)
                        made_progress = True
                        parity_fixed = True
                        break
              # For parity mismatch, ONLY do parity fix - skip other growth to avoid undoing the fix
              if parity_fixed:
                continue
              # If we couldn't fix parity, still skip other growth - wait for next iteration
              continue

          def score_candidate(c):
            x, y = c
            neighbors_in_chunk = sum(1 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                                     if (x + dx, y + dy) in chunk.cells)
            dist = abs(x - target[0]) + abs(y - target[1]) if target else 0
            return (dist, -neighbors_in_chunk, x, y)

          # Keep growth local: around choke point if known, otherwise around frontier band
          if target and adj:
            tx, ty = target
            # Only move closer (or equal) to the choke point to avoid wandering away
            curr_dist = min(abs(px - tx) + abs(py - ty) for px, py in chunk.cells)
            # Identify other frontier dead-ends to connect toward
            frontier = {c for c in chunk.cells if any(n not in chunk.cells for n in neighbors4(c))}
            dead_ends = {
              c
              for c in frontier
              if sum(1 for n in neighbors4(c) if n in chunk.cells) == 1 and c != target
            }
            second_target = None
            best_pair_dist = None
            if dead_ends:
              second_target = min(dead_ends, key=lambda c: abs(c[0] - tx) + abs(c[1] - ty))
              best_pair_dist = abs(second_target[0] - tx) + abs(second_target[1] - ty)

            focus = {(tx + dx, ty + dy)
                     for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)] if (tx + dx, ty + dy) in adj}
            # interior_hole at (x,y): allow filling it directly
            if "interior_hole" in str(reason) and target in all_cells and target not in chunk.cells:
              focus.add(target)
            toward = {c for c in adj if abs(c[0] - tx) + abs(c[1] - ty) < curr_dist}
            if second_target and best_pair_dist is not None:
              toward = {
                c
                for c in toward
                if (abs(c[0] - second_target[0]) + abs(c[1] - second_target[1])) <= best_pair_dist
              } or toward

            if focus:
              adj = focus
            elif toward:
              adj = toward
            else:
              LOCAL_RADIUS = 3
              local = {
                c
                for c in adj if abs(c[0] - target[0]) + abs(c[1] - target[1]) <= LOCAL_RADIUS
              }
              if not local:
                LOCAL_RADIUS = 4
                local = {
                  c
                  for c in adj if abs(c[0] - target[0]) + abs(c[1] - target[1]) <= LOCAL_RADIUS
                }
              if local:
                adj = local
              else:
                adj = set(sorted(adj, key=score_candidate)[:min(len(adj), 24)])
            if second_target:

              def pair_score(c):
                d1 = abs(c[0] - tx) + abs(c[1] - ty)
                d2 = abs(c[0] - second_target[0]) + abs(c[1] - second_target[1])
                return (d1 + d2, d1, d2, -sum(1 for n in neighbors4(c) if n in chunk.cells), c[0],
                        c[1])

              adj = set(sorted(adj, key=pair_score)[:min(len(adj), 16)])
          else:
            # Build a frontier band (cells adjacent to exterior) and stay near it
            frontier = {c for c in chunk.cells if any(n not in chunk.cells for n in neighbors4(c))}
            if frontier:
              fx = [p[0] for p in frontier]
              fy = [p[1] for p in frontier]
              min_x, max_x = min(fx), max(fx)
              min_y, max_y = min(fy), max(fy)
              band = {
                c
                for c in adj
                if (min_x - 2) <= c[0] <= (max_x + 2) and (min_y - 2) <= c[1] <= (max_y + 2)
              }
              if band:
                adj = band
            # Prefer thickening (more neighbors) over tendrils
            adj = set(sorted(adj, key=score_candidate)[:min(len(adj), 24)])
          if adj:
            # Add cells using parity-aware expansion (don't merge with solved)
            cells_to_add = pick_best_expansion_pair(adj, chunk.cells, blocked or set())
            growth_budget = 1  # tighten growth to avoid ballooning
            for cell_to_add in cells_to_add:
              if growth_budget <= 0:
                break
              if len(chunk.cells) >= MAX_OPEN_CHUNK_SIZE:
                break
              if cell_to_add and cell_to_add in all_cells:
                # If this cell belongs to another chunk, ensure merge won't exceed max
                if cell_to_chunk is not None and cell_to_chunk.get(cell_to_add) not in (None,
                                                                                        chunk.id):
                  other_id = cell_to_chunk[cell_to_add]
                  if other_id in chunks:
                    if len(chunk.cells) + len(chunks[other_id].cells) > MAX_OPEN_CHUNK_SIZE:
                      continue
                else:
                  if len(chunk.cells) + 1 > MAX_OPEN_CHUNK_SIZE:
                    continue
                new_id = expand_chunk(chunk,
                                      cell_to_add,
                                      cell_to_chunk,
                                      chunks,
                                      allow_merge_solved=False)
                made_progress = True
                growth_budget -= 1
                if new_id != chunk_id:
                  chunk = chunks.get(new_id)
                  chunk_id = new_id
                  if chunk is None:
                    break
            continue
          else:
            # Try merging with adjacent unsolved chunk only
            merged = False
            for cell in list(chunk.cells):
              x, y = cell
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nc = (x + dx, y + dy)
                if nc in cell_to_chunk and cell_to_chunk[nc] != chunk_id:
                  other_id = cell_to_chunk[nc]
                  if other_id in chunks and chunks[other_id].solution is None:
                    # Avoid creating oversized chunks
                    if len(chunk.cells) + len(chunks[other_id].cells) > MAX_OPEN_CHUNK_SIZE:
                      continue
                    merge_chunks(chunks, chunk_id, other_id, cell_to_chunk)
                    made_progress = True
                    merged = True
                    break
              if merged:
                break
            continue
        continue

      # Try to solve - scale iterations with size
      # Large feasible chunks need many more iterations due to complex shapes
      if n > 60:
        max_iters = 50000 * n  # ~3-6M for large chunks
        print(f"  Solving chunk {chunk_id} ({n} cells) with {max_iters} iterations...")
      else:
        max_iters = 5000 * n + 50000
      if chunk.solve(max_iterations=max_iters, blocked=blocked):
        made_progress = True
      elif cell_to_chunk is not None and all_cells is not None and n < MAX_OPEN_CHUNK_SIZE:
        # Failed to solve - try growing
        # Allow merging with small solved chunks (≤4 cells) since they're trivially re-solvable
        # But never merge with locked chunks
        adj = chunk.get_neighbor_cells(all_cells)

        def score_candidate(c):
          x, y = c
          neighbors_in_chunk = sum(1 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                                   if (x + dx, y + dy) in chunk.cells)
          return (-neighbors_in_chunk, x, y)

        adj = set(sorted(adj, key=score_candidate)[:min(len(adj), 48)])
        adj = {
          c
          for c in adj if c not in cell_to_chunk or cell_to_chunk[c] not in chunks
          or chunks[cell_to_chunk[c]].solution is None or (
            len(chunks[cell_to_chunk[c]].cells) <= 4 and not chunks[cell_to_chunk[c]].locked)
        }
        if adj:
          cells_to_add = pick_best_expansion_pair(adj, chunk.cells, blocked or set())
          for cell_to_add in cells_to_add:
            if len(chunk.cells) >= MAX_OPEN_CHUNK_SIZE:
              break
            if cell_to_add and cell_to_add in all_cells:
              # Prevent merging if it would exceed size cap
              if cell_to_chunk is not None and cell_to_chunk.get(cell_to_add) not in (None,
                                                                                      chunk.id):
                other_id = cell_to_chunk[cell_to_add]
                if other_id in chunks:
                  if len(chunk.cells) + len(chunks[other_id].cells) > MAX_OPEN_CHUNK_SIZE:
                    continue
              else:
                if len(chunk.cells) + 1 > MAX_OPEN_CHUNK_SIZE:
                  continue
              expand_chunk(chunk, cell_to_add, cell_to_chunk, chunks, allow_merge_solved=False)
              made_progress = True

    if not made_progress and unsolved_ids:
      # Force merge smallest unsolved with a neighbor (prefer unsolved, but allow solved)
      valid_unsolved = [chunks[uid] for uid in unsolved_ids if uid in chunks]
      if not valid_unsolved:
        continue
      smallest = min(valid_unsolved, key=lambda c: len(c.cells))
      if cell_to_chunk is not None:
        # First try unsolved neighbors
        for cell in list(smallest.cells):
          x, y = cell
          for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nc = (x + dx, y + dy)
            if nc in cell_to_chunk and cell_to_chunk[nc] != smallest.id:
              other_id = cell_to_chunk[nc]
              if other_id in chunks and chunks[other_id].solution is None:
                if len(smallest.cells) + len(chunks[other_id].cells) > MAX_OPEN_CHUNK_SIZE:
                  continue
                merge_chunks(chunks, smallest.id, other_id, cell_to_chunk)
                made_progress = True
                break
          if made_progress:
            break
        # If no unsolved neighbor, merge with smallest solved neighbor and re-solve
        if not made_progress:
          best_neighbor = None
          best_size = float('inf')
          for cell in list(smallest.cells):
            x, y = cell
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
              nc = (x + dx, y + dy)
              if nc in cell_to_chunk and cell_to_chunk[nc] != smallest.id:
                other_id = cell_to_chunk[nc]
                if other_id in chunks and len(chunks[other_id].cells) < best_size:
                  best_neighbor = other_id
                  best_size = len(chunks[other_id].cells)
          if best_neighbor is not None:
            if len(smallest.cells) + len(chunks[best_neighbor].cells) > MAX_OPEN_CHUNK_SIZE:
              best_neighbor = None
          if best_neighbor is not None:
            new_id = merge_chunks(chunks, smallest.id, best_neighbor, cell_to_chunk)
            # Try to re-solve the merged chunk immediately
            merged_chunk = chunks[new_id]
            n = len(merged_chunk.cells)
            if n > 100:
              max_iters = 50000 * n  # ~10M for 200 cells
            else:
              max_iters = 5000 * n + 50000
            merged_chunk.solve(max_iterations=max_iters, blocked=blocked)
            made_progress = True
      if not made_progress:
        # Last resort: find complementary parity-mismatched chunks and force merge them
        parity_chunks = []
        for uid in unsolved_ids:
          if uid not in chunks:
            continue
          c = chunks[uid]
          if c.solution is not None:
            continue
          feasible, reason = check_hamilton_feasibility(c.cells)
          if "parity_mismatch" in str(reason):
            match = re.search(r'parity_mismatch:\s+(\d+)\s+white\s+vs\s+(\d+)\s+black', str(reason))
            if match:
              white_cnt, black_cnt = int(match.group(1)), int(match.group(2))
              parity_chunks.append(
                (uid, white_cnt - black_cnt))  # positive = needs black, negative = needs white

        # Find two adjacent chunks with opposite parity needs
        for i, (id1, imbalance1) in enumerate(parity_chunks):
          for id2, imbalance2 in parity_chunks[i + 1:]:
            if imbalance1 * imbalance2 < 0:  # opposite signs = complementary
              # Check if adjacent
              c1, c2 = chunks[id1], chunks[id2]
              adjacent = False
              for cell in c1.cells:
                cx, cy = cell
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                  if (cx + dx, cy + dy) in c2.cells:
                    adjacent = True
                    break
                if adjacent:
                  break
              if adjacent:
                print(f"Force-merging complementary parity chunks {id1} and {id2}")
                new_id = merge_chunks(chunks, id1, id2, cell_to_chunk)
                merged = chunks[new_id]
                n = len(merged.cells)
                if n > 100:
                  max_iters = 50000 * n  # ~10M for 200 cells
                else:
                  max_iters = 5000 * n + 50000
                merged.solve(max_iterations=max_iters, blocked=blocked)
                made_progress = True
                break
          if made_progress:
            break

      if not made_progress:
        dump_unsolved_chunks(
          chunks,
          blocked=blocked,
          all_cells=all_cells,
          header="\nFailed to make progress in solve_open_chunks. Dumping unsolved chunks:")
        return False

  return False


def find_parallel_boundary_segments(loop: list, boundary_cells: set, is_horizontal: bool) -> list:
  """
  Find segments of the loop that run parallel to the boundary.
  is_horizontal: True if looking for horizontal segments (y constant),
                 False for vertical segments (x constant).
  """
  segments = []
  n = len(loop)
  for i in range(n):
    curr = loop[i]
    next_cell = loop[(i + 1) % n]

    if curr not in boundary_cells or next_cell not in boundary_cells:
      continue

    if is_horizontal:
      # Both cells same y, different x (horizontal edge)
      if curr[1] == next_cell[1] and abs(curr[0] - next_cell[0]) == 1:
        segments.append((i, (i + 1) % n, curr[1]))
    else:
      # Both cells same x, different y (vertical edge)
      if curr[0] == next_cell[0] and abs(curr[1] - next_cell[1]) == 1:
        segments.append((i, (i + 1) % n, curr[0]))

  return segments


def can_merge_chunks(chunk1: Chunk, chunk2: Chunk) -> list:
  """
  Find all possible merge points between two adjacent chunks.
  Returns list of (seg1, seg2, is_horizontal) tuples.
  """
  if not chunk1.solution or not chunk2.solution:
    return []

  # Find shared boundary
  boundary1 = set()
  boundary2 = set()

  for cell in chunk1.cells:
    x, y = cell
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      neighbor = (x + dx, y + dy)
      if neighbor in chunk2.cells:
        boundary1.add(cell)
        boundary2.add(neighbor)

  if not boundary1:
    return []

  # Determine if boundary is primarily horizontal or vertical
  b1_xs = {c[0] for c in boundary1}
  b1_ys = {c[1] for c in boundary1}

  merge_options = []

  # Try horizontal segments (boundary spans x, constant y)
  h_segs1 = find_parallel_boundary_segments(chunk1.solution, boundary1, True)
  h_segs2 = find_parallel_boundary_segments(chunk2.solution, boundary2, True)

  for s1 in h_segs1:
    for s2 in h_segs2:
      # Check if at adjacent y coordinates
      y1 = s1[2]
      y2 = s2[2]
      if abs(y1 - y2) == 1:
        # Check x overlap
        x1_a, x1_b = chunk1.solution[s1[0]][0], chunk1.solution[s1[1]][0]
        x2_a, x2_b = chunk2.solution[s2[0]][0], chunk2.solution[s2[1]][0]
        if {x1_a, x1_b} == {x2_a, x2_b}:
          merge_options.append(((s1[0], s1[1]), (s2[0], s2[1]), True))

  # Try vertical segments
  v_segs1 = find_parallel_boundary_segments(chunk1.solution, boundary1, False)
  v_segs2 = find_parallel_boundary_segments(chunk2.solution, boundary2, False)

  for s1 in v_segs1:
    for s2 in v_segs2:
      x1 = s1[2]
      x2 = s2[2]
      if abs(x1 - x2) == 1:
        y1_a, y1_b = chunk1.solution[s1[0]][1], chunk1.solution[s1[1]][1]
        y2_a, y2_b = chunk2.solution[s2[0]][1], chunk2.solution[s2[1]][1]
        if {y1_a, y1_b} == {y2_a, y2_b}:
          merge_options.append(((s1[0], s1[1]), (s2[0], s2[1]), False))

  return merge_options


def merge_loops(loop1: list, seg1: tuple, loop2: list, seg2: tuple) -> list:
  """Merge two loops by cutting at segments and cross-connecting.
  
  seg1 = (i, j) means loop1 has edge from loop1[i] to loop1[j]
  seg2 = (i, j) means loop2 has edge from loop2[i] to loop2[j]
  
  We cut both edges and cross-connect:
  - loop1[seg1[0]] connects to loop2[seg2[0]] (must be adjacent)
  - loop1[seg1[1]] connects to loop2[seg2[1]] (must be adjacent)
  
  Result: loop1[seg1[1]] ... loop1[seg1[0]] -> loop2[seg2[0]] ... loop2[seg2[1]] -> back to loop1[seg1[1]]
  """
  n1, n2 = len(loop1), len(loop2)

  # Verify cross-connections are adjacent
  def is_adjacent(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

  # We need: loop1[seg1[0]] adjacent to loop2[seg2[0]]
  #          loop1[seg1[1]] adjacent to loop2[seg2[1]]
  seg2_swapped = False
  if not (is_adjacent(loop1[seg1[0]], loop2[seg2[0]])
          and is_adjacent(loop1[seg1[1]], loop2[seg2[1]])):
    # Try swapping seg2 indices
    if is_adjacent(loop1[seg1[0]], loop2[seg2[1]]) and is_adjacent(loop1[seg1[1]], loop2[seg2[0]]):
      seg2 = (seg2[1], seg2[0])
      seg2_swapped = True
    else:
      print(f"WARNING: merge_loops cross-connections not adjacent!")
      print(f"  loop1[{seg1[0]}]={loop1[seg1[0]]} -> loop2[{seg2[0]}]={loop2[seg2[0]]}")
      print(f"  loop1[{seg1[1]}]={loop1[seg1[1]]} -> loop2[{seg2[1]}]={loop2[seg2[1]]}")

  result = []

  # Part 1: loop1 from seg1[1] to seg1[0] (going the long way around, skipping the cut edge)
  i = seg1[1]
  while True:
    result.append(loop1[i])
    if i == seg1[0]:
      break
    i = (i + 1) % n1

  # Part 2: loop2 traversal direction depends on whether seg2 was swapped
  # Original seg2 = (a, (a+1)%n) means edge a->(a+1)%n, traverse backward from a to (a+1)%n
  # Swapped seg2 = ((a+1)%n, a), traverse forward from (a+1)%n to a
  i = seg2[0]
  if seg2_swapped:
    # Go forward
    while True:
      result.append(loop2[i])
      if i == seg2[1]:
        break
      i = (i + 1) % n2
  else:
    # Go backward
    while True:
      result.append(loop2[i])
      if i == seg2[1]:
        break
      i = (i - 1) % n2

  # Validate merge result
  expected_len = n1 + n2
  if len(result) != expected_len:
    print(f"WARNING: merge_loops lost cells! {len(result)} vs expected {expected_len}")
    print(f"  seg1={seg1}, seg2={seg2}, n1={n1}, n2={n2}")

  return result


def build_chunk_graph(chunks: dict) -> dict:
  """Build adjacency graph between chunks."""
  graph = {cid: set() for cid in chunks}

  chunk_list = list(chunks.values())
  for i, c1 in enumerate(chunk_list):
    for c2 in chunk_list[i + 1:]:
      # Check if chunks are adjacent
      for cell in c1.cells:
        x, y = cell
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          if (x + dx, y + dy) in c2.cells:
            graph[c1.id].add(c2.id)
            graph[c2.id].add(c1.id)
            break
        else:
          continue
        break

  return graph


def find_chunk_hamilton_path(chunks: dict, graph: dict, max_iter: int = 100000) -> Optional[list]:
  """Find Hamilton path/loop through chunk graph."""
  if not chunks:
    return None

  chunk_ids = list(chunks.keys())
  if len(chunk_ids) == 1:
    return chunk_ids

  # Debug: check graph connectivity and structure
  print(f"Chunk graph: {len(chunk_ids)} chunks")
  isolated = [cid for cid in chunk_ids if len(graph.get(cid, set())) == 0]
  if isolated:
    print(f"  WARNING: {len(isolated)} isolated chunks: {isolated}")
  degree_1 = [cid for cid in chunk_ids if len(graph.get(cid, set())) == 1]
  if degree_1:
    print(f"  WARNING: {len(degree_1)} degree-1 chunks (dead ends): {degree_1}")

  # Check for articulation points in chunk graph and find components
  articulation_chunk = None
  components = []
  for cid in chunk_ids:
    neighbors = graph.get(cid, set())
    if len(neighbors) >= 2:
      # Check if removing this chunk would disconnect the graph
      remaining = set(chunk_ids) - {cid}
      if remaining:
        # Find connected components
        found_components = []
        unvisited = set(remaining)
        while unvisited:
          start_remaining = next(iter(unvisited))
          component = set()
          stack = [start_remaining]
          while stack:
            node = stack.pop()
            if node in component:
              continue
            component.add(node)
            unvisited.discard(node)
            for neighbor in graph.get(node, set()):
              if neighbor in remaining and neighbor not in component:
                stack.append(neighbor)
          found_components.append(component)

        if len(found_components) > 1:
          print(
            f"  ARTICULATION: Chunk {cid} ({len(chunks[cid].cells)} cells) is a bridge - splits into {len(found_components)} components"
          )
          articulation_chunk = cid
          components = found_components
          break  # Use first articulation found

  # Check if all chunks have solutions
  unsolved = [cid for cid in chunk_ids if chunks[cid].solution is None]
  if unsolved:
    print(f"  WARNING: {len(unsolved)} chunks without solutions: {unsolved}")

  # Handle articulation chunk specially - solve each component and stitch through bridge
  if articulation_chunk is not None and len(components) == 2:
    print(
      f"  Handling articulation chunk {articulation_chunk} with 2 components of sizes {[len(c) for c in components]}"
    )

    # Find which chunks in each component are adjacent to the articulation chunk
    art_neighbors = graph.get(articulation_chunk, set())

    # For each component, find a path through it that starts/ends at articulation-adjacent chunks
    component_paths = []
    for comp_idx, component in enumerate(components):
      comp_neighbors_to_art = [cid for cid in component if cid in art_neighbors]
      print(
        f"    Component {comp_idx}: {len(component)} chunks, {len(comp_neighbors_to_art)} adjacent to articulation"
      )

      if len(comp_neighbors_to_art) < 1:
        print(f"    ERROR: Component has no adjacency to articulation chunk")
        return None

      # Build subgraph for this component
      comp_list = list(component)

      # Try to find a path through component starting and ending at articulation-adjacent chunks
      best_path = None
      for start_chunk in comp_neighbors_to_art:
        for end_chunk in comp_neighbors_to_art:
          if start_chunk == end_chunk and len(component) > 1:
            continue  # Need different start/end for path (unless component is size 1)

          # DFS to find path from start to end visiting all chunks in component
          path = [start_chunk]
          visited = {start_chunk}

          def find_component_path():
            if len(path) == len(component):
              return path[-1] == end_chunk or len(component) == 1

            current = path[-1]
            neighbors = [
              n for n in graph.get(current, set()) if n in component and n not in visited
            ]
            neighbors.sort(key=lambda n: len(
              [nn for nn in graph.get(n, set()) if nn in component and nn not in visited]))

            for neighbor in neighbors:
              path.append(neighbor)
              visited.add(neighbor)
              if find_component_path():
                return True
              path.pop()
              visited.remove(neighbor)
            return False

          if find_component_path():
            best_path = list(path)
            break
        if best_path:
          break

      if not best_path:
        print(f"    Failed to find path through component {comp_idx}")
        return None

      component_paths.append(best_path)

    # Stitch: component0 path -> articulation -> component1 path (reversed to connect back)
    # The final path should form a loop: comp0[0] ... comp0[-1] -> art -> comp1[0] ... comp1[-1] -> back to comp0[0]
    full_path = component_paths[0] + [articulation_chunk] + component_paths[1]
    print(f"  Articulation path: {len(full_path)} chunks")
    return full_path

  start = chunk_ids[0]
  path = [start]
  visited = {start}
  iterations = [0]

  def dfs():
    iterations[0] += 1
    if iterations[0] > max_iter:
      return False

    if len(path) == len(chunk_ids):
      # Check if we can return to start
      return start in graph[path[-1]]

    current = path[-1]
    neighbors = [n for n in graph[current] if n not in visited]
    neighbors.sort(key=lambda n: len([nn for nn in graph[n] if nn not in visited]))

    for neighbor in neighbors:
      path.append(neighbor)
      visited.add(neighbor)
      if dfs():
        return True
      path.pop()
      visited.remove(neighbor)

    return False

  if dfs():
    return path

  # Try different starting points
  for start in chunk_ids[1:]:
    path = [start]
    visited = {start}
    iterations[0] = 0
    if dfs():
      return path

  return None


def stitch_chunk_solutions(chunk_path: list, chunks: dict) -> Optional[list]:
  """Stitch chunk solutions together using greedy order (not strict path order)."""
  if not chunk_path:
    return None

  if len(chunk_path) == 1:
    return chunks[chunk_path[0]].solution

  # Calculate expected total cells
  total_expected = sum(len(chunks[cid].cells) for cid in chunk_path)

  # Use greedy stitching - always pick next chunk that can be merged
  remaining = set(chunk_path[1:])
  current_cells = set(chunks[chunk_path[0]].cells)
  current_loop = list(chunks[chunk_path[0]].solution)
  skipped_chunks = []

  while remaining:
    # Find a chunk that can be stitched to current loop
    stitched = False
    for chunk_id in list(remaining):
      chunk = chunks[chunk_id]
      if not chunk.solution:
        print(f"Chunk {chunk_id} has no solution ({len(chunk.cells)} cells), skipping")
        skipped_chunks.append(chunk_id)
        remaining.remove(chunk_id)
        stitched = True
        break

      merge_options = can_merge_chunks_from_loop(current_loop, current_cells, chunk)
      if merge_options:
        seg1, seg2 = merge_options[0]
        current_loop = merge_loops(current_loop, seg1, chunk.solution, seg2)
        current_cells = current_cells | chunk.cells
        remaining.remove(chunk_id)
        stitched = True
        break

    if not stitched:
      # No chunk can be stitched - try to find ANY adjacent chunk
      print(f"Greedy stitch stuck with {len(remaining)} chunks remaining")
      # Find which chunks are adjacent to current_cells
      adjacent_chunks = []
      for chunk_id in remaining:
        chunk = chunks[chunk_id]
        for cell in chunk.cells:
          x, y = cell
          for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if (x + dx, y + dy) in current_cells:
              adjacent_chunks.append(chunk_id)
              break
          else:
            continue
          break
      print(f"  Adjacent but unmergeable: {adjacent_chunks[:5]}")
      return None

  # Validate result
  if skipped_chunks:
    skipped_cells = sum(len(chunks[cid].cells) for cid in skipped_chunks)
    print(f"WARNING: Skipped {len(skipped_chunks)} chunks with {skipped_cells} cells")

  if len(current_loop) != total_expected:
    print(f"WARNING: Loop has {len(current_loop)} cells but expected {total_expected}")

  # Verify loop closes (first and last are adjacent)
  if len(current_loop) >= 2:
    first, last = current_loop[0], current_loop[-1]
    dist = abs(first[0] - last[0]) + abs(first[1] - last[1])
    if dist != 1:
      print(f"ERROR: Loop doesn't close! Start {first} and end {last} distance={dist}")
      # Try to verify all edges are valid
      broken_edges = []
      for i in range(len(current_loop)):
        a = current_loop[i]
        b = current_loop[(i + 1) % len(current_loop)]
        d = abs(a[0] - b[0]) + abs(a[1] - b[1])
        if d != 1:
          broken_edges.append((i, a, b, d))
      if broken_edges:
        print(f"  Found {len(broken_edges)} broken edges")
        for i, a, b, d in broken_edges[:5]:
          print(f"    Edge {i}: {a} -> {b} distance={d}")

  return current_loop


def can_merge_chunks_from_loop(loop: list, loop_cells: set, chunk: Chunk) -> list:
  """Find merge points between an accumulated loop and a new chunk."""
  if not loop or not chunk.solution:
    return []

  # Find boundary between loop_cells and chunk.cells
  boundary_loop = set()
  boundary_chunk = set()

  for cell in loop_cells:
    x, y = cell
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      neighbor = (x + dx, y + dy)
      if neighbor in chunk.cells:
        boundary_loop.add(cell)
        boundary_chunk.add(neighbor)

  if not boundary_loop:
    return []

  merge_options = []

  # Find parallel segments in both loops
  h_segs_loop = find_parallel_boundary_segments(loop, boundary_loop, True)
  h_segs_chunk = find_parallel_boundary_segments(chunk.solution, boundary_chunk, True)

  for s1 in h_segs_loop:
    for s2 in h_segs_chunk:
      y1 = s1[2]
      y2 = s2[2]
      if abs(y1 - y2) == 1:
        x1_a, x1_b = loop[s1[0]][0], loop[s1[1]][0]
        x2_a, x2_b = chunk.solution[s2[0]][0], chunk.solution[s2[1]][0]
        if {x1_a, x1_b} == {x2_a, x2_b}:
          merge_options.append(((s1[0], s1[1]), (s2[0], s2[1])))

  v_segs_loop = find_parallel_boundary_segments(loop, boundary_loop, False)
  v_segs_chunk = find_parallel_boundary_segments(chunk.solution, boundary_chunk, False)

  for s1 in v_segs_loop:
    for s2 in v_segs_chunk:
      x1 = s1[2]
      x2 = s2[2]
      if abs(x1 - x2) == 1:
        y1_a, y1_b = loop[s1[0]][1], loop[s1[1]][1]
        y2_a, y2_b = chunk.solution[s2[0]][1], chunk.solution[s2[1]][1]
        if {y1_a, y1_b} == {y2_a, y2_b}:
          merge_options.append(((s1[0], s1[1]), (s2[0], s2[1])))

  return merge_options


def solve_genetic(grid_size: int,
                  blocked: set,
                  max_generations: int = 5000,
                  pop_size: int = 300) -> Optional[list]:
  """
  Genetic algorithm for Hamilton loop finding with adaptive strategies.
  """
  import random

  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked
  cells_list = list(all_cells)
  n = len(cells_list)

  if n < 4:
    return None

  # Build adjacency for fast lookup
  adj = {c: set() for c in cells_list}
  for c in cells_list:
    x, y = c
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      nb = (x + dx, y + dy)
      if nb in all_cells:
        adj[c].add(nb)

  def fitness(path):
    """Count valid edges. n = perfect loop."""
    valid = sum(1 for i in range(len(path) - 1) if path[i + 1] in adj[path[i]])
    if path[-1] in adj[path[0]]:
      valid += 1
    return valid

  def count_broken_edges(path):
    """Return list of indices where edge is broken."""
    broken = []
    for i in range(len(path)):
      next_i = (i + 1) % len(path)
      if path[next_i] not in adj[path[i]]:
        broken.append(i)
    return broken

  def create_greedy_individual():
    """Create individual using Warnsdorff with randomization."""
    start = random.choice(cells_list)
    path = [start]
    remaining = set(cells_list) - {start}

    while remaining:
      current = path[-1]
      neighbors = [c for c in adj[current] if c in remaining]
      if neighbors:
        # Warnsdorff with randomization
        neighbors.sort(key=lambda c: (len([x for x in adj[c] if x in remaining]), random.random()))
        next_cell = neighbors[0]
      else:
        # Jump to random remaining cell
        next_cell = random.choice(list(remaining))
      path.append(next_cell)
      remaining.remove(next_cell)
    return path

  def crossover_edge_recombination(p1, p2):
    """Edge recombination crossover - preserves edges from both parents."""
    # Build edge table
    edge_table = {c: set() for c in cells_list}
    for path in [p1, p2]:
      for i in range(len(path)):
        c = path[i]
        prev_c = path[i - 1]
        next_c = path[(i + 1) % len(path)]
        edge_table[c].add(prev_c)
        edge_table[c].add(next_c)

    # Build child
    child = []
    current = random.choice([p1[0], p2[0]])
    remaining = set(cells_list)

    while remaining:
      child.append(current)
      remaining.discard(current)

      if not remaining:
        break

      # Remove current from all edge lists
      for c in edge_table:
        edge_table[c].discard(current)

      # Choose next: prefer cells in edge table, then adjacent, then random
      candidates = [c for c in edge_table[current] if c in remaining]
      if candidates:
        # Prefer cells with fewest remaining edges (Warnsdorff-like)
        candidates.sort(key=lambda c: len(edge_table[c]))
        current = candidates[0]
      else:
        # Try adjacent cells
        adj_remaining = [c for c in adj[current] if c in remaining]
        if adj_remaining:
          current = random.choice(adj_remaining)
        else:
          current = random.choice(list(remaining))

    return child

  def mutate_targeted_2opt(path):
    """2-opt focused on broken edges."""
    broken = count_broken_edges(path)
    if not broken:
      return

    i = random.choice(broken)
    # Try different j values
    best_path = path[:]
    best_fit = fitness(path)

    for _ in range(20):
      j = random.randint(0, len(path) - 1)
      if abs(i - j) < 2:
        continue

      if i < j:
        new_path = path[:i + 1] + path[i + 1:j + 1][::-1] + path[j + 1:]
      else:
        new_path = path[:j + 1] + path[j + 1:i + 1][::-1] + path[i + 1:]

      f = fitness(new_path)
      if f > best_fit:
        best_path = new_path
        best_fit = f

    path[:] = best_path

  def mutate_3opt(path):
    """3-opt move for escaping local optima."""
    n_path = len(path)
    if n_path < 6:
      return

    # Pick 3 random cut points
    cuts = sorted(random.sample(range(n_path), 3))
    i, j, k = cuts

    # Try different reconnections
    segments = [path[:i + 1], path[i + 1:j + 1], path[j + 1:k + 1], path[k + 1:]]

    # Different 3-opt moves
    options = [
      segments[0] + segments[2][::-1] + segments[1][::-1] + segments[3],
      segments[0] + segments[2] + segments[1] + segments[3],
      segments[0] + segments[1][::-1] + segments[2] + segments[3],
    ]

    best = max(options, key=fitness)
    if fitness(best) >= fitness(path):
      path[:] = best

  def intensive_local_search(path, max_iters=500):
    """More aggressive local search."""
    best_fit = fitness(path)

    for _ in range(max_iters):
      broken = count_broken_edges(path)
      if not broken:
        return path  # Perfect!

      # Focus on first broken edge
      i = broken[0]
      improved = False

      # Try all possible 2-opt moves from this position
      for j in range(len(path)):
        if abs(i - j) < 2:
          continue

        if i < j:
          new_path = path[:i + 1] + path[i + 1:j + 1][::-1] + path[j + 1:]
        else:
          new_path = path[:j + 1] + path[j + 1:i + 1][::-1] + path[i + 1:]

        f = fitness(new_path)
        if f > best_fit:
          path[:] = new_path
          best_fit = f
          improved = True
          break

      if not improved:
        # Try 3-opt
        mutate_3opt(path)
        new_fit = fitness(path)
        if new_fit > best_fit:
          best_fit = new_fit
        elif new_fit < best_fit - 2:
          # Got worse, try random restart of segment
          mutate_targeted_2opt(path)

    return path

  # Initialize population
  print(f"GA: Initializing population of {pop_size}...")
  population = [create_greedy_individual() for _ in range(pop_size)]

  best_fitness = 0
  best_individual = None
  stagnant_gens = 0
  mutation_rate = 0.3

  for gen in range(max_generations):
    # Evaluate fitness
    scores = [(fitness(ind), ind) for ind in population]
    scores.sort(reverse=True, key=lambda x: x[0])

    current_best = scores[0][0]

    if current_best > best_fitness:
      best_fitness = current_best
      best_individual = scores[0][1][:]
      stagnant_gens = 0
      mutation_rate = 0.3  # Reset mutation rate

      if best_fitness == n:
        print(f"GA: Found solution at generation {gen}!")
        return best_individual
    else:
      stagnant_gens += 1
      # Increase mutation rate when stagnant
      mutation_rate = min(0.9, mutation_rate + 0.01)

    if gen % 100 == 0 or gen < 10:
      print(
        f"Gen {gen}: best={best_fitness}/{n}, stagnant={stagnant_gens}, mut={mutation_rate:.2f}")

    # Population restart when very stuck
    if stagnant_gens > 200:
      print(f"GA: Restarting {pop_size//2} individuals...")
      # Keep best quarter, regenerate rest
      keep = pop_size // 4
      population = [scores[i][1][:] for i in range(keep)]

      # Apply intensive local search to best
      intensive_local_search(population[0])
      if fitness(population[0]) == n:
        print("GA: Local search found solution!")
        return population[0]

      # Generate new individuals
      while len(population) < pop_size:
        population.append(create_greedy_individual())

      stagnant_gens = 0
      mutation_rate = 0.5
      continue

    # Selection and reproduction
    new_pop = []

    # Elitism
    elite_count = max(2, pop_size // 20)
    for i in range(elite_count):
      new_pop.append(scores[i][1][:])

    # Tournament selection and crossover
    while len(new_pop) < pop_size:
      t1 = max(random.sample(scores, 5), key=lambda x: x[0])[1]
      t2 = max(random.sample(scores, 5), key=lambda x: x[0])[1]

      if random.random() < 0.7:
        child = crossover_edge_recombination(t1, t2)
      else:
        child = t1[:]

      # Adaptive mutation
      if random.random() < mutation_rate:
        mutate_targeted_2opt(child)
      if random.random() < mutation_rate * 0.5:
        mutate_3opt(child)

      new_pop.append(child)

    population = new_pop

  print(f"GA: Max generations reached, best={best_fitness}/{n}")

  # Final intensive local search
  if best_individual:
    print("GA: Final intensive local search...")
    intensive_local_search(best_individual, max_iters=2000)
    if fitness(best_individual) == n:
      print("GA: Final local search found solution!")
      return best_individual

  return None


def solve_serpentine(grid_size: int, blocked: set) -> Optional[list]:
  """
  Try to build a Hamilton loop using Warnsdorff with backtracking.
  """
  import random

  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked

  if len(all_cells) < 4:
    return None

  def get_neighbors(pos):
    x, y = pos
    return [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if (x + dx, y + dy) in all_cells]

  def is_adjacent(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

  n_cells = len(all_cells)
  cells_list = list(all_cells)
  best_path = []

  print(f"Trying Warnsdorff with backtracking ({n_cells} cells)...")

  # Try each cell as starting point with backtracking
  for start_idx, start in enumerate(cells_list):
    if start_idx > 0 and start_idx % 50 == 0:
      print(f"Tried {start_idx} starting points, best: {len(best_path)}/{n_cells}")

    path = [start]
    visited = {start}

    # Initialize with neighbors of start
    initial_neighbors = [n for n in get_neighbors(start) if n not in visited]
    initial_neighbors.sort(
      key=lambda n: (len([nn for nn in get_neighbors(n) if nn not in visited]), random.random()))
    choices_stack = [initial_neighbors]

    max_backtracks = 5000
    backtracks = 0

    while choices_stack:
      if len(path) == n_cells:
        if is_adjacent(path[-1], start):
          print(f"Found loop starting from cell {start_idx}!")
          return path
        # Path complete but doesn't close - backtrack
        if backtracks >= max_backtracks:
          break
        backtracks += 1
        visited.remove(path.pop())
        choices_stack.pop()
        continue

      # Try next choice at current level
      while choices_stack and not choices_stack[-1]:
        choices_stack.pop()
        if path:
          visited.remove(path.pop())
          backtracks += 1

      if not choices_stack or backtracks >= max_backtracks:
        break

      next_cell = choices_stack[-1].pop(0)
      path.append(next_cell)
      visited.add(next_cell)

      if len(path) > len(best_path):
        best_path = list(path)

      # Add neighbors for next level
      neighbors = [n for n in get_neighbors(next_cell) if n not in visited]
      neighbors.sort(
        key=lambda n: (len([nn for nn in get_neighbors(n) if nn not in visited]), random.random()))
      choices_stack.append(neighbors)

  # If systematic search fails, try random restarts
  print(f"Systematic search done, best: {len(best_path)}/{n_cells}. Trying random...")

  for attempt in range(200):
    start = random.choice(cells_list)
    path = [start]
    visited = {start}

    while len(path) < n_cells:
      current = path[-1]
      neighbors = [n for n in get_neighbors(current) if n not in visited]
      if not neighbors:
        break
      neighbors.sort(
        key=lambda n: (len([nn for nn in get_neighbors(n) if nn not in visited]), random.random()))
      path.append(neighbors[0])
      visited.add(neighbors[0])

    if len(path) == n_cells and is_adjacent(path[-1], start):
      print(f"Found loop on random attempt {attempt+1}!")
      return path

    if len(path) > len(best_path):
      best_path = list(path)

  print(f"All attempts failed, best: {len(best_path)}/{n_cells}")
  return None


def solve_constructive_repair(grid_size: int, blocked: set) -> Optional[list]:
  """
  Constructive approach: build serpentine base, then locally repair around obstacles.
  """
  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked

  def is_adjacent(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

  # Build base serpentine loop (works for obstacle-free grid)
  # Pattern: snake through rows, return via column 1
  base_loop = []
  for y in range(1, grid_size + 1):
    if y % 2 == 1:
      for x in range(2, grid_size + 1):
        base_loop.append((x, y))
    else:
      for x in range(grid_size, 1, -1):
        base_loop.append((x, y))
  # Return path via column 1
  for y in range(grid_size, 0, -1):
    base_loop.append((1, y))

  # Now we need to handle obstacles by local repair
  # Strategy: for each obstacle, find its position in the loop and reroute

  if not blocked:
    return base_loop

  # Convert loop to use only valid cells, rerouting around obstacles
  # This is the tricky part - we need to find alternative paths

  # Build adjacency
  adj = {c: set() for c in all_cells}
  for c in all_cells:
    x, y = c
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      nb = (x + dx, y + dy)
      if nb in all_cells:
        adj[c].add(nb)

  # Filter base loop to only valid cells
  valid_base = [c for c in base_loop if c in all_cells]

  # Check which edges are broken
  def count_valid_edges(path):
    count = 0
    for i in range(len(path)):
      next_i = (i + 1) % len(path)
      if path[next_i] in adj.get(path[i], set()):
        count += 1
    return count

  # Try to repair broken edges by local search
  path = valid_base[:]

  # Iterative repair
  for iteration in range(1000):
    valid_edges = count_valid_edges(path)
    if valid_edges == len(path):
      print(f"Constructive repair succeeded after {iteration} iterations!")
      return path

    # Find broken edges
    broken = []
    for i in range(len(path)):
      next_i = (i + 1) % len(path)
      if path[next_i] not in adj.get(path[i], set()):
        broken.append(i)

    if not broken:
      return path

    # Try to fix first broken edge with 2-opt
    improved = False
    i = broken[0]

    for j in range(len(path)):
      if abs(i - j) < 2:
        continue

      if i < j:
        new_path = path[:i + 1] + path[i + 1:j + 1][::-1] + path[j + 1:]
      else:
        new_path = path[:j + 1] + path[j + 1:i + 1][::-1] + path[i + 1:]

      if count_valid_edges(new_path) > valid_edges:
        path = new_path
        improved = True
        break

    if not improved:
      # Try 3-opt
      if len(path) >= 6:
        import random
        for _ in range(50):
          cuts = sorted(random.sample(range(len(path)), 3))
          a, b, c = cuts
          segs = [path[:a + 1], path[a + 1:b + 1], path[b + 1:c + 1], path[c + 1:]]

          options = [
            segs[0] + segs[2][::-1] + segs[1][::-1] + segs[3],
            segs[0] + segs[2] + segs[1] + segs[3],
            segs[0] + segs[1][::-1] + segs[2] + segs[3],
          ]

          for opt in options:
            if count_valid_edges(opt) > valid_edges:
              path = opt
              improved = True
              break
          if improved:
            break

  print(f"Constructive repair: best={count_valid_edges(path)}/{len(path)}")
  return None


def solve_expanding_barrage(grid_size: int, blocked: set) -> Optional[list]:
  """
  Main entry point for expanding barrage algorithm.
  """
  print(f"Solving {grid_size}x{grid_size} grid with {len(blocked)} blocked cells")

  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked
  n_cells = len(all_cells)

  # For small puzzles (<=64 cells), solve directly without chunking machinery
  if n_cells <= 64:
    print(f"Small puzzle ({n_cells} cells), solving directly...")
    # Try direct solve with Warnsdorff backtracking
    solution = solve_serpentine(grid_size, blocked)
    if solution:
      print(f"Direct solve succeeded!")
      return solution
    # If that fails, try with more iterations using the chunk solver
    chunk = Chunk(0, all_cells)
    chunk.has_obstacles = len(blocked) > 0
    max_iters = 100000 * n_cells  # Generous iteration limit for small puzzles
    if chunk.solve(max_iterations=max_iters, blocked=blocked):
      print(f"Direct chunk solve succeeded!")
      return chunk.solution
    print(f"Direct solve failed, falling back to chunking approach")

  # Fall back to chunking approach
  # Step 1: Create initial 2x2 chunks
  chunks, all_cells, cell_to_chunk = create_initial_chunks(grid_size, blocked)
  print(f"Created {len(chunks)} initial chunks")

  # Step 2: Solve/grow obstacle chunks
  if not solve_obstacle_chunks(chunks, all_cells, cell_to_chunk, blocked):
    print("Failed to solve obstacle chunks")
    dump_unsolved_chunks(chunks,
                         blocked=blocked,
                         all_cells=all_cells,
                         grid_size=grid_size,
                         header="\nDumping unsolved chunks after obstacle-chunk failure:")
    return None

  solved_obstacle_chunks = [c for c in chunks.values() if c.has_obstacles and c.solution]
  print(f"Solved {len(solved_obstacle_chunks)} obstacle chunks")

  # Step 3: Partition open space
  avg_size = 16  # Default target
  if solved_obstacle_chunks:
    avg_size = max(4,
                   sum(len(c.cells) for c in solved_obstacle_chunks) // len(solved_obstacle_chunks))
  partition_open_space(chunks, all_cells, cell_to_chunk, avg_size)
  print(f"After partitioning: {len(chunks)} total chunks")

  # Step 4: Solve open chunks
  if not solve_open_chunks(chunks, cell_to_chunk, all_cells, blocked=blocked):
    print("Failed to solve open chunks")
    dump_unsolved_chunks(chunks,
                         blocked=blocked,
                         all_cells=all_cells,
                         grid_size=grid_size,
                         header="\nDumping unsolved chunks after open-chunk failure:")
    return None

  # Step 4.5: Verify all chunks have solutions, re-solve any that don't
  unsolved_chunks = [c for c in chunks.values() if c.solution is None]
  for chunk in unsolved_chunks:
    n = len(chunk.cells)
    # Check feasibility first
    feasible, reason = check_hamilton_feasibility(chunk.cells)
    if not feasible:
      print(f"  Chunk {chunk.id} ({n} cells) infeasible: {reason}")
      continue
    # Large chunks need many more iterations
    if n > 100:
      max_iters = 200000 * n  # ~20-30M for large chunks
    else:
      max_iters = 10000 * n + 100000
    print(f"  Re-solving chunk {chunk.id} with {n} cells, {max_iters} iters")
    if not chunk.solve(max_iterations=max_iters, blocked=blocked):
      print(f"  Failed to solve chunk {chunk.id}")

  # Final check
  still_unsolved = [c.id for c in chunks.values() if c.solution is None]
  if still_unsolved:
    print(f"WARNING: {len(still_unsolved)} chunks still unsolved: {still_unsolved}")

  # Step 5: Build chunk graph and find Hamilton path
  graph = build_chunk_graph(chunks)
  chunk_path = find_chunk_hamilton_path(chunks, graph)

  if not chunk_path:
    print("Failed to find Hamilton path through chunks")
    dump_unsolved_chunks(chunks,
                         blocked=blocked,
                         all_cells=all_cells,
                         grid_size=grid_size,
                         header="\nDumping unsolved chunks after chunk-path failure:")
    return None

  print(f"Found chunk path: {chunk_path}")

  # Step 6: Stitch solutions together
  solution = stitch_chunk_solutions(chunk_path, chunks)

  if solution:
    print(f"Found solution with {len(solution)} cells")

  return solution


def get_response(subPass: int):
  """Get the placebo response for this question."""
  gridSize = get_grid_size(subPass)
  blocked = get_blocked_cells(subPass)

  if not blocked:

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

  # Solve several of the most common subpatterns in advance, helping
  # to prime the cache. Turn this algorithm from hours to seconds.

  add_primer_subproblem("""
...
.X.
.X.
...
  """.strip())

  add_primer_subproblem("""
...
.X.
.X.
...
...
...
  """.strip())

  add_primer_subproblem("""
....
.X..
.X..
....
....
....
  """.strip())

  add_primer_subproblem("""
...
.X.
...
...
.X.
...
  """.strip())

  add_primer_subproblem("""
...
.X.
.X.
.X.
.X.
...
  """.strip())

  add_primer_subproblem("""
XX..
XX..
XX..
XX..
XX..
....
....
  """.strip())

  add_primer_subproblem("""
......
......
XXXX..
......
.XX...
.XX...
......
  """.strip())

  add_primer_subproblem("""
....
.XX.
....
  """.strip())

  add_primer_subproblem("""
....
.XX.
.XX.
....
  """.strip())

  add_primer_subproblem("""
......
.X..X.
......
  """.strip())

  add_primer_subproblem("""
..........
.X......X.
.X......X.
..........
""".strip())

  add_primer_subproblem("""
..X......X..
..X......X..
............
............
""".strip())

  add_primer_subproblem("""
..??
..??
..??
..??
..??
..??
....
.XX.
.XX.
....
..??
..??
..??
..??
..??
..??
""".strip())

  # 4x5 primers for narrow side strips (helps avoid funnel shapes in frame-like open space)
  add_primer_subproblem("""
....
....
....
....
....
""".strip())

  # For any hard subpasses, use the expanding barrage solver
  solution = solve_expanding_barrage(gridSize, blocked)

  if solution:
    # Include all cells in the loop (solution[0] is the starting position)
    steps = [{"xy": list(pos)} for pos in solution]
    return {"steps": steps}, "Solved with expanding barrage algorithm"

  return {"steps": [], "error": "No solution found"}, "Failed to solve"


def cache_solutions():
  for sp in [1, 4, 5, 6, 7, 8]:
    print(f"\n{'='*50}")
    print(f"Testing subPass {sp}")
    print(f"{'='*50}")
    result, msg = get_response(sp)
    if 'error' in result:
      print(f"FAILED: {result}")
    else:
      print(f"SUCCESS: {len(result['steps'])} steps")
    print(result)
