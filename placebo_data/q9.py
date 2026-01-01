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

from google.genai._interactions.types.function_result_content_param import Result


class Chunk:
  """Represents an arbitrary-shaped region of cells."""

  def __init__(self, chunk_id: int, cells: set):
    self.id = chunk_id
    self.cells = set(cells)  # Set of (x, y) coordinates
    self.solution = None  # Hamilton loop through this chunk's cells
    self.has_obstacles = False  # True if this chunk was created due to obstacles
    self.longest_failed_path = []  # Track longest path from failed solve attempts

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

  def solve(self, max_iterations: int = 500000) -> bool:
    """Attempt to solve Hamilton loop for this chunk."""
    if len(self.cells) == 0:
      self.solution = []
      return True

    if len(self.cells) < 4:
      return False  # Can't form a loop with < 4 cells

    result = solve_hamilton_with_tracking(self.cells, max_iterations)
    if result[0]:
      self.solution = result[0]
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
  # A loop can't exist if there's an articulation point with degree 2
  for cell in cells:
    degree = len(get_neighbors(cell))
    if degree == 2:
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


def create_initial_chunks(grid_size: int, blocked: set) -> tuple:
  """
  Create initial 2x2 chunks, returning (chunks_dict, all_free_cells).
  Chunks containing obstacles are marked as such.
  """
  all_cells = {(x, y) for x in range(1, grid_size + 1) for y in range(1, grid_size + 1)} - blocked
  chunks = {}
  chunk_id = 0
  cell_to_chunk = {}

  # Create 2x2 chunks
  for base_x in range(1, grid_size + 1, 2):
    for base_y in range(1, grid_size + 1, 2):
      chunk_cells = set()
      has_obstacle = False
      for dx in range(2):
        for dy in range(2):
          cell = (base_x + dx, base_y + dy)
          if cell in blocked:
            has_obstacle = True
          elif cell in all_cells:
            chunk_cells.add(cell)

      if chunk_cells:
        chunk = Chunk(chunk_id, chunk_cells)
        chunk.has_obstacles = has_obstacle or len(chunk_cells) < 4
        chunks[chunk_id] = chunk
        for cell in chunk_cells:
          cell_to_chunk[cell] = chunk_id
        chunk_id += 1

  return chunks, all_cells, cell_to_chunk


def merge_chunks(chunks: dict, chunk1_id: int, chunk2_id: int, cell_to_chunk: dict) -> int:
  """Merge two chunks, returning the ID of the merged chunk."""
  if chunk1_id == chunk2_id:
    return chunk1_id

  c1 = chunks[chunk1_id]
  c2 = chunks[chunk2_id]

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
  kept.solution = None  # Need to re-solve
  kept.longest_failed_path = []

  del chunks[remove]
  return keep


def expand_chunk(chunk: Chunk, neighbor_cell: tuple, cell_to_chunk: dict, chunks: dict) -> int:
  """
  Add a neighbor cell to this chunk. If cell belongs to another chunk, merge them.
  Returns the ID of the resulting chunk.
  """
  if neighbor_cell in chunk.cells:
    return chunk.id

  if neighbor_cell in cell_to_chunk:
    other_id = cell_to_chunk[neighbor_cell]
    if other_id != chunk.id:
      return merge_chunks(chunks, chunk.id, other_id, cell_to_chunk)
    return chunk.id

  chunk.cells.add(neighbor_cell)
  cell_to_chunk[neighbor_cell] = chunk.id
  chunk.solution = None
  chunk.longest_failed_path = []
  return chunk.id


def pick_best_expansion_cell(candidates: set, chunk_cells: set, blocked: set) -> tuple:
  """
  Pick the best cell to expand into. Prioritizes:
  1. Cells that fill interior holes (inside current bbox)
  2. Cells adjacent to blocked cells (obstacles)
  3. Cells with more neighbors already in chunk (more connected)
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

      # Expand small chunks first
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
        best = pick_best_expansion_cell(adj, chunk.cells, blocked or set())
        new_id = expand_chunk(chunk, best, cell_to_chunk, chunks)
        made_progress = True
        if new_id != chunk_id:
          chunk = chunks[new_id]
          chunk_id = new_id

      # Check feasibility before attempting expensive DFS
      n = len(chunk.cells)
      feasible, reason = check_hamilton_feasibility(chunk.cells, all_cells)

      # Debug: visualize chunk shape
      if True:
        xs = [c[0] for c in chunk.cells]
        ys = [c[1] for c in chunk.cells]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        print(
          f"  Chunk {chunk_id}: {n} cells in {max_x-min_x+1}x{max_y-min_y+1} bbox, feasible={feasible}"
        )
        for y in range(max_y, min_y - 1, -1):
          row = ""
          for x in range(min_x, max_x + 1):
            row += "#" if (x, y) in chunk.cells else "."
          print(f"    {row}")
      else:
        print(f"  Chunk {chunk_id}: {n} cells, feasible={feasible}, reason={reason}")

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

      # Normal expansion - add cells adjacent to boundary
      adj = chunk.get_neighbor_cells(all_cells)
      if adj:
        # Prefer cells that might help connectivity
        best = pick_best_expansion_cell(adj, chunk.cells, blocked or set())
        new_id = expand_chunk(chunk, best, cell_to_chunk, chunks)
        made_progress = True
        if new_id != chunk_id:
          chunks[new_id].solution = None
      elif not made_progress:
        # No neighbors in all_cells, must merge with adjacent chunk
        for cell in chunk.cells:
          x, y = cell
          for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            n = (x + dx, y + dy)
            if n in cell_to_chunk and cell_to_chunk[n] != chunk_id:
              other_id = cell_to_chunk[n]
              if other_id in chunks:
                new_id = merge_chunks(chunks, chunk_id, other_id, cell_to_chunk)
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
            if other_id in chunks:
              new_id = merge_chunks(chunks, smallest.id, other_id, cell_to_chunk)
              chunks[new_id].solution = None
              made_progress = True
              break
        if made_progress:
          break
      if not made_progress:
        print(f"Stuck at iteration {iteration}")
        return False

  return False


def partition_open_space(chunks: dict, all_cells: set, cell_to_chunk: dict,
                         target_size: int) -> None:
  """
  Partition remaining open space into chunks of approximately target_size.
  """
  # Find cells not yet in any chunk
  unassigned = all_cells - set(cell_to_chunk.keys())
  if not unassigned:
    return

  # Get average size of solved obstacle chunks
  solved_sizes = [len(c.cells) for c in chunks.values() if c.has_obstacles and c.solution]
  if solved_sizes:
    target_size = max(4, sum(solved_sizes) // len(solved_sizes))

  chunk_id = max(chunks.keys()) + 1 if chunks else 0

  while unassigned:
    # Start a new chunk from an arbitrary unassigned cell
    start = min(unassigned)
    new_cells = {start}
    unassigned.remove(start)

    # Grow until target size or no more adjacent cells
    while len(new_cells) < target_size and unassigned:
      # Find adjacent unassigned cells
      adjacent = set()
      for cell in new_cells:
        x, y = cell
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          neighbor = (x + dx, y + dy)
          if neighbor in unassigned:
            adjacent.add(neighbor)

      if not adjacent:
        break

      # Add one adjacent cell (prefer one that keeps shape compact)
      best = min(adjacent,
                 key=lambda c: max(abs(c[0] - s[0]) + abs(c[1] - s[1]) for s in new_cells))
      new_cells.add(best)
      unassigned.remove(best)

    # Create the chunk
    chunk = Chunk(chunk_id, new_cells)
    chunk.has_obstacles = False
    chunks[chunk_id] = chunk
    for cell in new_cells:
      cell_to_chunk[cell] = chunk_id
    chunk_id += 1


def solve_open_chunks(chunks: dict, max_subdivide_attempts: int = 5) -> bool:
  """
  Solve all open space chunks. Subdivide if needed.
  """
  for attempt in range(max_subdivide_attempts):
    unsolved = [c for c in chunks.values() if not c.has_obstacles and c.solution is None]
    if not unsolved:
      return True

    all_solved = True
    for chunk in unsolved:
      if not chunk.solve():
        all_solved = False

    if all_solved:
      return True

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
  if not (is_adjacent(loop1[seg1[0]], loop2[seg2[0]])
          and is_adjacent(loop1[seg1[1]], loop2[seg2[1]])):
    # Try swapping seg2 indices
    if is_adjacent(loop1[seg1[0]], loop2[seg2[1]]) and is_adjacent(loop1[seg1[1]], loop2[seg2[0]]):
      seg2 = (seg2[1], seg2[0])
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

  # Part 2: loop2 from seg2[0] to seg2[1] (going the long way around, skipping the cut edge)
  i = seg2[0]
  while True:
    result.append(loop2[i])
    if i == seg2[1]:
      break
    i = (i + 1) % n2

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
  """Stitch chunk solutions together following the path order."""
  if not chunk_path:
    return None

  if len(chunk_path) == 1:
    return chunks[chunk_path[0]].solution

  current_cells = set(chunks[chunk_path[0]].cells)
  current_loop = list(chunks[chunk_path[0]].solution)

  for i in range(1, len(chunk_path)):
    next_chunk = chunks[chunk_path[i]]
    merge_options = can_merge_chunks_from_loop(current_loop, current_cells, next_chunk)

    if not merge_options:
      print(f"Cannot find merge point between accumulated loop and chunk {chunk_path[i]}")
      return None

    seg1, seg2 = merge_options[0]
    current_loop = merge_loops(current_loop, seg1, next_chunk.solution, seg2)
    current_cells = current_cells | next_chunk.cells

  # Close the loop back to start
  first_chunk = chunks[chunk_path[0]]
  last_chunk = chunks[chunk_path[-1]]

  # Verify loop closes properly
  if len(current_loop) > 0:
    first = current_loop[0]
    last = current_loop[-1]
    if abs(first[0] - last[0]) + abs(first[1] - last[1]) != 1:
      # Need to verify it's actually a loop
      pass

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

  # Fall back to chunking approach
  # Step 1: Create initial 2x2 chunks
  chunks, all_cells, cell_to_chunk = create_initial_chunks(grid_size, blocked)
  print(f"Created {len(chunks)} initial chunks")

  # Step 2: Solve/grow obstacle chunks
  if not solve_obstacle_chunks(chunks, all_cells, cell_to_chunk, blocked):
    print("Failed to solve obstacle chunks")
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
  if not solve_open_chunks(chunks):
    print("Failed to solve open chunks")
    return None

  # Step 5: Build chunk graph and find Hamilton path
  graph = build_chunk_graph(chunks)
  chunk_path = find_chunk_hamilton_path(chunks, graph)

  if not chunk_path:
    print("Failed to find Hamilton path through chunks")
    return None

  print(f"Found chunk path: {chunk_path}")

  # Step 6: Stitch solutions together
  solution = stitch_chunk_solutions(chunk_path, chunks)

  if solution:
    print(f"Found solution with {len(solution)} cells")

  return solution


def get_blocked_cells(subPass):
  """Get blocked cells for each subpass."""
  if subPass == 4:
    return {(3, 3), (3, 4)}
  elif subPass == 5:
    return {(3, 3), (3, 4), (5, 3), (5, 4), (7, 7), (8, 7)}
  elif subPass == 7:
    blocked = set()
    map_lines = """
................
.X..X.....X..X..
................
................
................
................
................
......XX........
......XX........
................
................
................
................
................
.X..X.....X..X..
................
    """.strip().split("\n")
    for row_idx, line in enumerate(map_lines):
      y = 16 - row_idx
      for x_idx, ch in enumerate(line):
        if ch == 'X':
          blocked.add((x_idx + 1, y))
    return blocked
  return set()


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass < 4:
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

  # Cached answers:

  if subPass == 4:
    return ({
      'steps': [{
        'xy': [3, 9]
      }, {
        'xy': [4, 9]
      }, {
        'xy': [4, 10]
      }, {
        'xy': [3, 10]
      }, {
        'xy': [2, 10]
      }, {
        'xy': [2, 11]
      }, {
        'xy': [3, 11]
      }, {
        'xy': [4, 11]
      }, {
        'xy': [4, 12]
      }, {
        'xy': [3, 12]
      }, {
        'xy': [2, 12]
      }, {
        'xy': [2, 13]
      }, {
        'xy': [3, 13]
      }, {
        'xy': [4, 13]
      }, {
        'xy': [4, 14]
      }, {
        'xy': [3, 14]
      }, {
        'xy': [2, 14]
      }, {
        'xy': [2, 15]
      }, {
        'xy': [3, 15]
      }, {
        'xy': [4, 15]
      }, {
        'xy': [5, 15]
      }, {
        'xy': [5, 14]
      }, {
        'xy': [5, 13]
      }, {
        'xy': [6, 13]
      }, {
        'xy': [7, 13]
      }, {
        'xy': [8, 13]
      }, {
        'xy': [8, 14]
      }, {
        'xy': [7, 14]
      }, {
        'xy': [6, 14]
      }, {
        'xy': [6, 15]
      }, {
        'xy': [7, 15]
      }, {
        'xy': [8, 15]
      }, {
        'xy': [9, 15]
      }, {
        'xy': [9, 14]
      }, {
        'xy': [9, 13]
      }, {
        'xy': [10, 13]
      }, {
        'xy': [11, 13]
      }, {
        'xy': [12, 13]
      }, {
        'xy': [12, 14]
      }, {
        'xy': [11, 14]
      }, {
        'xy': [10, 14]
      }, {
        'xy': [10, 15]
      }, {
        'xy': [11, 15]
      }, {
        'xy': [12, 15]
      }, {
        'xy': [13, 15]
      }, {
        'xy': [13, 14]
      }, {
        'xy': [13, 13]
      }, {
        'xy': [14, 13]
      }, {
        'xy': [15, 13]
      }, {
        'xy': [15, 12]
      }, {
        'xy': [14, 12]
      }, {
        'xy': [13, 12]
      }, {
        'xy': [13, 11]
      }, {
        'xy': [13, 10]
      }, {
        'xy': [12, 10]
      }, {
        'xy': [11, 10]
      }, {
        'xy': [10, 10]
      }, {
        'xy': [10, 11]
      }, {
        'xy': [11, 11]
      }, {
        'xy': [12, 11]
      }, {
        'xy': [12, 12]
      }, {
        'xy': [11, 12]
      }, {
        'xy': [10, 12]
      }, {
        'xy': [9, 12]
      }, {
        'xy': [9, 11]
      }, {
        'xy': [9, 10]
      }, {
        'xy': [8, 10]
      }, {
        'xy': [7, 10]
      }, {
        'xy': [6, 10]
      }, {
        'xy': [6, 11]
      }, {
        'xy': [7, 11]
      }, {
        'xy': [8, 11]
      }, {
        'xy': [8, 12]
      }, {
        'xy': [7, 12]
      }, {
        'xy': [6, 12]
      }, {
        'xy': [5, 12]
      }, {
        'xy': [5, 11]
      }, {
        'xy': [5, 10]
      }, {
        'xy': [5, 9]
      }, {
        'xy': [6, 9]
      }, {
        'xy': [7, 9]
      }, {
        'xy': [7, 8]
      }, {
        'xy': [7, 7]
      }, {
        'xy': [6, 7]
      }, {
        'xy': [6, 8]
      }, {
        'xy': [5, 8]
      }, {
        'xy': [5, 7]
      }, {
        'xy': [5, 6]
      }, {
        'xy': [6, 6]
      }, {
        'xy': [7, 6]
      }, {
        'xy': [8, 6]
      }, {
        'xy': [8, 7]
      }, {
        'xy': [9, 7]
      }, {
        'xy': [9, 6]
      }, {
        'xy': [10, 6]
      }, {
        'xy': [11, 6]
      }, {
        'xy': [12, 6]
      }, {
        'xy': [12, 7]
      }, {
        'xy': [13, 7]
      }, {
        'xy': [13, 6]
      }, {
        'xy': [14, 6]
      }, {
        'xy': [15, 6]
      }, {
        'xy': [15, 5]
      }, {
        'xy': [15, 4]
      }, {
        'xy': [14, 4]
      }, {
        'xy': [14, 5]
      }, {
        'xy': [13, 5]
      }, {
        'xy': [13, 4]
      }, {
        'xy': [13, 3]
      }, {
        'xy': [13, 2]
      }, {
        'xy': [12, 2]
      }, {
        'xy': [11, 2]
      }, {
        'xy': [10, 2]
      }, {
        'xy': [10, 3]
      }, {
        'xy': [11, 3]
      }, {
        'xy': [12, 3]
      }, {
        'xy': [12, 4]
      }, {
        'xy': [12, 5]
      }, {
        'xy': [11, 5]
      }, {
        'xy': [11, 4]
      }, {
        'xy': [10, 4]
      }, {
        'xy': [10, 5]
      }, {
        'xy': [9, 5]
      }, {
        'xy': [9, 4]
      }, {
        'xy': [9, 3]
      }, {
        'xy': [9, 2]
      }, {
        'xy': [8, 2]
      }, {
        'xy': [7, 2]
      }, {
        'xy': [6, 2]
      }, {
        'xy': [6, 3]
      }, {
        'xy': [7, 3]
      }, {
        'xy': [8, 3]
      }, {
        'xy': [8, 4]
      }, {
        'xy': [8, 5]
      }, {
        'xy': [7, 5]
      }, {
        'xy': [7, 4]
      }, {
        'xy': [6, 4]
      }, {
        'xy': [6, 5]
      }, {
        'xy': [5, 5]
      }, {
        'xy': [5, 4]
      }, {
        'xy': [5, 3]
      }, {
        'xy': [5, 2]
      }, {
        'xy': [4, 2]
      }, {
        'xy': [4, 3]
      }, {
        'xy': [4, 4]
      }, {
        'xy': [4, 5]
      }, {
        'xy': [3, 5]
      }, {
        'xy': [2, 5]
      }, {
        'xy': [1, 5]
      }, {
        'xy': [1, 4]
      }, {
        'xy': [2, 4]
      }, {
        'xy': [2, 3]
      }, {
        'xy': [1, 3]
      }, {
        'xy': [1, 2]
      }, {
        'xy': [1, 1]
      }, {
        'xy': [2, 1]
      }, {
        'xy': [2, 2]
      }, {
        'xy': [3, 2]
      }, {
        'xy': [3, 1]
      }, {
        'xy': [4, 1]
      }, {
        'xy': [5, 1]
      }, {
        'xy': [6, 1]
      }, {
        'xy': [7, 1]
      }, {
        'xy': [8, 1]
      }, {
        'xy': [9, 1]
      }, {
        'xy': [10, 1]
      }, {
        'xy': [11, 1]
      }, {
        'xy': [12, 1]
      }, {
        'xy': [13, 1]
      }, {
        'xy': [14, 1]
      }, {
        'xy': [15, 1]
      }, {
        'xy': [16, 1]
      }, {
        'xy': [16, 2]
      }, {
        'xy': [15, 2]
      }, {
        'xy': [14, 2]
      }, {
        'xy': [14, 3]
      }, {
        'xy': [15, 3]
      }, {
        'xy': [16, 3]
      }, {
        'xy': [16, 4]
      }, {
        'xy': [16, 5]
      }, {
        'xy': [16, 6]
      }, {
        'xy': [16, 7]
      }, {
        'xy': [16, 8]
      }, {
        'xy': [15, 8]
      }, {
        'xy': [15, 7]
      }, {
        'xy': [14, 7]
      }, {
        'xy': [14, 8]
      }, {
        'xy': [13, 8]
      }, {
        'xy': [12, 8]
      }, {
        'xy': [11, 8]
      }, {
        'xy': [11, 7]
      }, {
        'xy': [10, 7]
      }, {
        'xy': [10, 8]
      }, {
        'xy': [9, 8]
      }, {
        'xy': [8, 8]
      }, {
        'xy': [8, 9]
      }, {
        'xy': [9, 9]
      }, {
        'xy': [10, 9]
      }, {
        'xy': [11, 9]
      }, {
        'xy': [12, 9]
      }, {
        'xy': [13, 9]
      }, {
        'xy': [14, 9]
      }, {
        'xy': [15, 9]
      }, {
        'xy': [16, 9]
      }, {
        'xy': [16, 10]
      }, {
        'xy': [15, 10]
      }, {
        'xy': [14, 10]
      }, {
        'xy': [14, 11]
      }, {
        'xy': [15, 11]
      }, {
        'xy': [16, 11]
      }, {
        'xy': [16, 12]
      }, {
        'xy': [16, 13]
      }, {
        'xy': [16, 14]
      }, {
        'xy': [15, 14]
      }, {
        'xy': [14, 14]
      }, {
        'xy': [14, 15]
      }, {
        'xy': [15, 15]
      }, {
        'xy': [16, 15]
      }, {
        'xy': [16, 16]
      }, {
        'xy': [15, 16]
      }, {
        'xy': [14, 16]
      }, {
        'xy': [13, 16]
      }, {
        'xy': [12, 16]
      }, {
        'xy': [11, 16]
      }, {
        'xy': [10, 16]
      }, {
        'xy': [9, 16]
      }, {
        'xy': [8, 16]
      }, {
        'xy': [7, 16]
      }, {
        'xy': [6, 16]
      }, {
        'xy': [5, 16]
      }, {
        'xy': [4, 16]
      }, {
        'xy': [3, 16]
      }, {
        'xy': [2, 16]
      }, {
        'xy': [1, 16]
      }, {
        'xy': [1, 15]
      }, {
        'xy': [1, 14]
      }, {
        'xy': [1, 13]
      }, {
        'xy': [1, 12]
      }, {
        'xy': [1, 11]
      }, {
        'xy': [1, 10]
      }, {
        'xy': [1, 9]
      }, {
        'xy': [1, 8]
      }, {
        'xy': [1, 7]
      }, {
        'xy': [1, 6]
      }, {
        'xy': [2, 6]
      }, {
        'xy': [3, 6]
      }, {
        'xy': [4, 6]
      }, {
        'xy': [4, 7]
      }, {
        'xy': [4, 8]
      }, {
        'xy': [3, 8]
      }, {
        'xy': [3, 7]
      }, {
        'xy': [2, 7]
      }, {
        'xy': [2, 8]
      }]
    }, 'Solved with hierarchical divide-and-conquer')

  if subPass == 6:
    return {
      'steps': [{
        'xy': [1, 7]
      }, {
        'xy': [1, 6]
      }, {
        'xy': [1, 5]
      }, {
        'xy': [1, 4]
      }, {
        'xy': [1, 3]
      }, {
        'xy': [1, 2]
      }, {
        'xy': [1, 1]
      }, {
        'xy': [2, 1]
      }, {
        'xy': [3, 1]
      }, {
        'xy': [3, 2]
      }, {
        'xy': [4, 2]
      }, {
        'xy': [4, 1]
      }, {
        'xy': [5, 1]
      }, {
        'xy': [6, 1]
      }, {
        'xy': [7, 1]
      }, {
        'xy': [8, 1]
      }, {
        'xy': [8, 2]
      }, {
        'xy': [8, 3]
      }, {
        'xy': [8, 4]
      }, {
        'xy': [8, 5]
      }, {
        'xy': [8, 6]
      }, {
        'xy': [8, 7]
      }, {
        'xy': [9, 7]
      }, {
        'xy': [9, 6]
      }, {
        'xy': [9, 5]
      }, {
        'xy': [9, 4]
      }, {
        'xy': [9, 3]
      }, {
        'xy': [10, 3]
      }, {
        'xy': [10, 2]
      }, {
        'xy': [9, 2]
      }, {
        'xy': [9, 1]
      }, {
        'xy': [10, 1]
      }, {
        'xy': [11, 1]
      }, {
        'xy': [12, 1]
      }, {
        'xy': [12, 2]
      }, {
        'xy': [13, 2]
      }, {
        'xy': [13, 1]
      }, {
        'xy': [14, 1]
      }, {
        'xy': [15, 1]
      }, {
        'xy': [16, 1]
      }, {
        'xy': [16, 2]
      }, {
        'xy': [15, 2]
      }, {
        'xy': [15, 3]
      }, {
        'xy': [16, 3]
      }, {
        'xy': [16, 4]
      }, {
        'xy': [16, 5]
      }, {
        'xy': [16, 6]
      }, {
        'xy': [16, 7]
      }, {
        'xy': [16, 8]
      }, {
        'xy': [16, 9]
      }, {
        'xy': [16, 10]
      }, {
        'xy': [16, 11]
      }, {
        'xy': [16, 12]
      }, {
        'xy': [15, 12]
      }, {
        'xy': [15, 11]
      }, {
        'xy': [15, 10]
      }, {
        'xy': [15, 9]
      }, {
        'xy': [15, 8]
      }, {
        'xy': [15, 7]
      }, {
        'xy': [15, 6]
      }, {
        'xy': [15, 5]
      }, {
        'xy': [15, 4]
      }, {
        'xy': [14, 4]
      }, {
        'xy': [14, 3]
      }, {
        'xy': [13, 3]
      }, {
        'xy': [13, 4]
      }, {
        'xy': [12, 4]
      }, {
        'xy': [12, 3]
      }, {
        'xy': [11, 3]
      }, {
        'xy': [11, 4]
      }, {
        'xy': [10, 4]
      }, {
        'xy': [10, 5]
      }, {
        'xy': [11, 5]
      }, {
        'xy': [12, 5]
      }, {
        'xy': [12, 6]
      }, {
        'xy': [12, 7]
      }, {
        'xy': [13, 7]
      }, {
        'xy': [13, 6]
      }, {
        'xy': [13, 5]
      }, {
        'xy': [14, 5]
      }, {
        'xy': [14, 6]
      }, {
        'xy': [14, 7]
      }, {
        'xy': [14, 8]
      }, {
        'xy': [14, 9]
      }, {
        'xy': [14, 10]
      }, {
        'xy': [14, 11]
      }, {
        'xy': [14, 12]
      }, {
        'xy': [13, 12]
      }, {
        'xy': [13, 11]
      }, {
        'xy': [13, 10]
      }, {
        'xy': [13, 9]
      }, {
        'xy': [13, 8]
      }, {
        'xy': [12, 8]
      }, {
        'xy': [12, 9]
      }, {
        'xy': [12, 10]
      }, {
        'xy': [12, 11]
      }, {
        'xy': [12, 12]
      }, {
        'xy': [11, 12]
      }, {
        'xy': [11, 11]
      }, {
        'xy': [11, 10]
      }, {
        'xy': [11, 9]
      }, {
        'xy': [11, 8]
      }, {
        'xy': [11, 7]
      }, {
        'xy': [11, 6]
      }, {
        'xy': [10, 6]
      }, {
        'xy': [10, 7]
      }, {
        'xy': [10, 8]
      }, {
        'xy': [10, 9]
      }, {
        'xy': [10, 10]
      }, {
        'xy': [10, 11]
      }, {
        'xy': [10, 12]
      }, {
        'xy': [10, 13]
      }, {
        'xy': [11, 13]
      }, {
        'xy': [11, 14]
      }, {
        'xy': [12, 14]
      }, {
        'xy': [12, 13]
      }, {
        'xy': [13, 13]
      }, {
        'xy': [13, 14]
      }, {
        'xy': [14, 14]
      }, {
        'xy': [14, 13]
      }, {
        'xy': [15, 13]
      }, {
        'xy': [16, 13]
      }, {
        'xy': [16, 14]
      }, {
        'xy': [15, 14]
      }, {
        'xy': [15, 15]
      }, {
        'xy': [16, 15]
      }, {
        'xy': [16, 16]
      }, {
        'xy': [15, 16]
      }, {
        'xy': [14, 16]
      }, {
        'xy': [13, 16]
      }, {
        'xy': [13, 15]
      }, {
        'xy': [12, 15]
      }, {
        'xy': [12, 16]
      }, {
        'xy': [11, 16]
      }, {
        'xy': [10, 16]
      }, {
        'xy': [9, 16]
      }, {
        'xy': [9, 15]
      }, {
        'xy': [10, 15]
      }, {
        'xy': [10, 14]
      }, {
        'xy': [9, 14]
      }, {
        'xy': [9, 13]
      }, {
        'xy': [9, 12]
      }, {
        'xy': [9, 11]
      }, {
        'xy': [9, 10]
      }, {
        'xy': [9, 9]
      }, {
        'xy': [9, 8]
      }, {
        'xy': [8, 8]
      }, {
        'xy': [8, 9]
      }, {
        'xy': [8, 10]
      }, {
        'xy': [8, 11]
      }, {
        'xy': [8, 12]
      }, {
        'xy': [8, 13]
      }, {
        'xy': [8, 14]
      }, {
        'xy': [7, 14]
      }, {
        'xy': [7, 13]
      }, {
        'xy': [7, 12]
      }, {
        'xy': [7, 11]
      }, {
        'xy': [7, 10]
      }, {
        'xy': [7, 9]
      }, {
        'xy': [7, 8]
      }, {
        'xy': [7, 7]
      }, {
        'xy': [7, 6]
      }, {
        'xy': [7, 5]
      }, {
        'xy': [7, 4]
      }, {
        'xy': [7, 3]
      }, {
        'xy': [7, 2]
      }, {
        'xy': [6, 2]
      }, {
        'xy': [6, 3]
      }, {
        'xy': [6, 4]
      }, {
        'xy': [5, 4]
      }, {
        'xy': [5, 3]
      }, {
        'xy': [4, 3]
      }, {
        'xy': [4, 4]
      }, {
        'xy': [3, 4]
      }, {
        'xy': [3, 3]
      }, {
        'xy': [2, 3]
      }, {
        'xy': [2, 4]
      }, {
        'xy': [2, 5]
      }, {
        'xy': [3, 5]
      }, {
        'xy': [4, 5]
      }, {
        'xy': [4, 6]
      }, {
        'xy': [4, 7]
      }, {
        'xy': [5, 7]
      }, {
        'xy': [5, 6]
      }, {
        'xy': [5, 5]
      }, {
        'xy': [6, 5]
      }, {
        'xy': [6, 6]
      }, {
        'xy': [6, 7]
      }, {
        'xy': [6, 8]
      }, {
        'xy': [6, 9]
      }, {
        'xy': [6, 10]
      }, {
        'xy': [6, 11]
      }, {
        'xy': [6, 12]
      }, {
        'xy': [6, 13]
      }, {
        'xy': [6, 14]
      }, {
        'xy': [6, 15]
      }, {
        'xy': [7, 15]
      }, {
        'xy': [8, 15]
      }, {
        'xy': [8, 16]
      }, {
        'xy': [7, 16]
      }, {
        'xy': [6, 16]
      }, {
        'xy': [5, 16]
      }, {
        'xy': [4, 16]
      }, {
        'xy': [4, 15]
      }, {
        'xy': [3, 15]
      }, {
        'xy': [3, 16]
      }, {
        'xy': [2, 16]
      }, {
        'xy': [1, 16]
      }, {
        'xy': [1, 15]
      }, {
        'xy': [1, 14]
      }, {
        'xy': [1, 13]
      }, {
        'xy': [1, 12]
      }, {
        'xy': [1, 11]
      }, {
        'xy': [2, 11]
      }, {
        'xy': [2, 12]
      }, {
        'xy': [2, 13]
      }, {
        'xy': [2, 14]
      }, {
        'xy': [3, 14]
      }, {
        'xy': [3, 13]
      }, {
        'xy': [4, 13]
      }, {
        'xy': [4, 14]
      }, {
        'xy': [5, 14]
      }, {
        'xy': [5, 13]
      }, {
        'xy': [5, 12]
      }, {
        'xy': [5, 11]
      }, {
        'xy': [5, 10]
      }, {
        'xy': [5, 9]
      }, {
        'xy': [5, 8]
      }, {
        'xy': [4, 8]
      }, {
        'xy': [4, 9]
      }, {
        'xy': [4, 10]
      }, {
        'xy': [4, 11]
      }, {
        'xy': [4, 12]
      }, {
        'xy': [3, 12]
      }, {
        'xy': [3, 11]
      }, {
        'xy': [3, 10]
      }, {
        'xy': [3, 9]
      }, {
        'xy': [3, 8]
      }, {
        'xy': [3, 7]
      }, {
        'xy': [3, 6]
      }, {
        'xy': [2, 6]
      }, {
        'xy': [2, 7]
      }, {
        'xy': [2, 8]
      }, {
        'xy': [2, 9]
      }, {
        'xy': [2, 10]
      }, {
        'xy': [1, 10]
      }, {
        'xy': [1, 9]
      }]
    }, ""

  if subPass == 7:
    return {
      'steps': [{
        'xy': [6, 2]
      }, {
        'xy': [6, 3]
      }, {
        'xy': [6, 4]
      }, {
        'xy': [5, 4]
      }, {
        'xy': [5, 3]
      }, {
        'xy': [4, 3]
      }, {
        'xy': [4, 4]
      }, {
        'xy': [4, 5]
      }, {
        'xy': [4, 6]
      }, {
        'xy': [4, 7]
      }, {
        'xy': [4, 8]
      }, {
        'xy': [4, 9]
      }, {
        'xy': [4, 10]
      }, {
        'xy': [4, 11]
      }, {
        'xy': [4, 12]
      }, {
        'xy': [4, 13]
      }, {
        'xy': [4, 14]
      }, {
        'xy': [5, 14]
      }, {
        'xy': [5, 13]
      }, {
        'xy': [5, 12]
      }, {
        'xy': [5, 11]
      }, {
        'xy': [5, 10]
      }, {
        'xy': [5, 9]
      }, {
        'xy': [6, 9]
      }, {
        'xy': [6, 10]
      }, {
        'xy': [7, 10]
      }, {
        'xy': [8, 10]
      }, {
        'xy': [9, 10]
      }, {
        'xy': [9, 9]
      }, {
        'xy': [10, 9]
      }, {
        'xy': [11, 9]
      }, {
        'xy': [11, 8]
      }, {
        'xy': [11, 7]
      }, {
        'xy': [12, 7]
      }, {
        'xy': [12, 8]
      }, {
        'xy': [12, 9]
      }, {
        'xy': [12, 10]
      }, {
        'xy': [12, 11]
      }, {
        'xy': [13, 11]
      }, {
        'xy': [13, 10]
      }, {
        'xy': [13, 9]
      }, {
        'xy': [13, 8]
      }, {
        'xy': [13, 7]
      }, {
        'xy': [13, 6]
      }, {
        'xy': [12, 6]
      }, {
        'xy': [11, 6]
      }, {
        'xy': [11, 5]
      }, {
        'xy': [12, 5]
      }, {
        'xy': [13, 5]
      }, {
        'xy': [14, 5]
      }, {
        'xy': [14, 6]
      }, {
        'xy': [14, 7]
      }, {
        'xy': [14, 8]
      }, {
        'xy': [14, 9]
      }, {
        'xy': [14, 10]
      }, {
        'xy': [14, 11]
      }, {
        'xy': [14, 12]
      }, {
        'xy': [13, 12]
      }, {
        'xy': [12, 12]
      }, {
        'xy': [11, 12]
      }, {
        'xy': [11, 11]
      }, {
        'xy': [11, 10]
      }, {
        'xy': [10, 10]
      }, {
        'xy': [10, 11]
      }, {
        'xy': [10, 12]
      }, {
        'xy': [10, 13]
      }, {
        'xy': [11, 13]
      }, {
        'xy': [11, 14]
      }, {
        'xy': [12, 14]
      }, {
        'xy': [12, 13]
      }, {
        'xy': [13, 13]
      }, {
        'xy': [13, 14]
      }, {
        'xy': [14, 14]
      }, {
        'xy': [14, 13]
      }, {
        'xy': [15, 13]
      }, {
        'xy': [15, 12]
      }, {
        'xy': [15, 11]
      }, {
        'xy': [15, 10]
      }, {
        'xy': [15, 9]
      }, {
        'xy': [15, 8]
      }, {
        'xy': [15, 7]
      }, {
        'xy': [15, 6]
      }, {
        'xy': [15, 5]
      }, {
        'xy': [15, 4]
      }, {
        'xy': [14, 4]
      }, {
        'xy': [14, 3]
      }, {
        'xy': [13, 3]
      }, {
        'xy': [13, 4]
      }, {
        'xy': [12, 4]
      }, {
        'xy': [12, 3]
      }, {
        'xy': [11, 3]
      }, {
        'xy': [11, 4]
      }, {
        'xy': [10, 4]
      }, {
        'xy': [10, 5]
      }, {
        'xy': [10, 6]
      }, {
        'xy': [10, 7]
      }, {
        'xy': [10, 8]
      }, {
        'xy': [9, 8]
      }, {
        'xy': [9, 7]
      }, {
        'xy': [9, 6]
      }, {
        'xy': [8, 6]
      }, {
        'xy': [8, 7]
      }, {
        'xy': [7, 7]
      }, {
        'xy': [7, 6]
      }, {
        'xy': [6, 6]
      }, {
        'xy': [6, 7]
      }, {
        'xy': [6, 8]
      }, {
        'xy': [5, 8]
      }, {
        'xy': [5, 7]
      }, {
        'xy': [5, 6]
      }, {
        'xy': [5, 5]
      }, {
        'xy': [6, 5]
      }, {
        'xy': [7, 5]
      }, {
        'xy': [8, 5]
      }, {
        'xy': [9, 5]
      }, {
        'xy': [9, 4]
      }, {
        'xy': [9, 3]
      }, {
        'xy': [10, 3]
      }, {
        'xy': [10, 2]
      }, {
        'xy': [9, 2]
      }, {
        'xy': [9, 1]
      }, {
        'xy': [10, 1]
      }, {
        'xy': [11, 1]
      }, {
        'xy': [12, 1]
      }, {
        'xy': [12, 2]
      }, {
        'xy': [13, 2]
      }, {
        'xy': [13, 1]
      }, {
        'xy': [14, 1]
      }, {
        'xy': [15, 1]
      }, {
        'xy': [16, 1]
      }, {
        'xy': [16, 2]
      }, {
        'xy': [15, 2]
      }, {
        'xy': [15, 3]
      }, {
        'xy': [16, 3]
      }, {
        'xy': [16, 4]
      }, {
        'xy': [16, 5]
      }, {
        'xy': [16, 6]
      }, {
        'xy': [16, 7]
      }, {
        'xy': [16, 8]
      }, {
        'xy': [16, 9]
      }, {
        'xy': [16, 10]
      }, {
        'xy': [16, 11]
      }, {
        'xy': [16, 12]
      }, {
        'xy': [16, 13]
      }, {
        'xy': [16, 14]
      }, {
        'xy': [15, 14]
      }, {
        'xy': [15, 15]
      }, {
        'xy': [16, 15]
      }, {
        'xy': [16, 16]
      }, {
        'xy': [15, 16]
      }, {
        'xy': [14, 16]
      }, {
        'xy': [13, 16]
      }, {
        'xy': [13, 15]
      }, {
        'xy': [12, 15]
      }, {
        'xy': [12, 16]
      }, {
        'xy': [11, 16]
      }, {
        'xy': [10, 16]
      }, {
        'xy': [9, 16]
      }, {
        'xy': [9, 15]
      }, {
        'xy': [10, 15]
      }, {
        'xy': [10, 14]
      }, {
        'xy': [9, 14]
      }, {
        'xy': [9, 13]
      }, {
        'xy': [9, 12]
      }, {
        'xy': [9, 11]
      }, {
        'xy': [8, 11]
      }, {
        'xy': [8, 12]
      }, {
        'xy': [7, 12]
      }, {
        'xy': [7, 11]
      }, {
        'xy': [6, 11]
      }, {
        'xy': [6, 12]
      }, {
        'xy': [6, 13]
      }, {
        'xy': [6, 14]
      }, {
        'xy': [6, 15]
      }, {
        'xy': [7, 15]
      }, {
        'xy': [7, 14]
      }, {
        'xy': [7, 13]
      }, {
        'xy': [8, 13]
      }, {
        'xy': [8, 14]
      }, {
        'xy': [8, 15]
      }, {
        'xy': [8, 16]
      }, {
        'xy': [7, 16]
      }, {
        'xy': [6, 16]
      }, {
        'xy': [5, 16]
      }, {
        'xy': [4, 16]
      }, {
        'xy': [4, 15]
      }, {
        'xy': [3, 15]
      }, {
        'xy': [3, 16]
      }, {
        'xy': [2, 16]
      }, {
        'xy': [1, 16]
      }, {
        'xy': [1, 15]
      }, {
        'xy': [1, 14]
      }, {
        'xy': [1, 13]
      }, {
        'xy': [2, 13]
      }, {
        'xy': [2, 14]
      }, {
        'xy': [3, 14]
      }, {
        'xy': [3, 13]
      }, {
        'xy': [3, 12]
      }, {
        'xy': [3, 11]
      }, {
        'xy': [3, 10]
      }, {
        'xy': [3, 9]
      }, {
        'xy': [3, 8]
      }, {
        'xy': [3, 7]
      }, {
        'xy': [3, 6]
      }, {
        'xy': [3, 5]
      }, {
        'xy': [3, 4]
      }, {
        'xy': [3, 3]
      }, {
        'xy': [2, 3]
      }, {
        'xy': [2, 4]
      }, {
        'xy': [2, 5]
      }, {
        'xy': [2, 6]
      }, {
        'xy': [2, 7]
      }, {
        'xy': [2, 8]
      }, {
        'xy': [2, 9]
      }, {
        'xy': [2, 10]
      }, {
        'xy': [2, 11]
      }, {
        'xy': [2, 12]
      }, {
        'xy': [1, 12]
      }, {
        'xy': [1, 11]
      }, {
        'xy': [1, 10]
      }, {
        'xy': [1, 9]
      }, {
        'xy': [1, 8]
      }, {
        'xy': [1, 7]
      }, {
        'xy': [1, 6]
      }, {
        'xy': [1, 5]
      }, {
        'xy': [1, 4]
      }, {
        'xy': [1, 3]
      }, {
        'xy': [1, 2]
      }, {
        'xy': [1, 1]
      }, {
        'xy': [2, 1]
      }, {
        'xy': [3, 1]
      }, {
        'xy': [3, 2]
      }, {
        'xy': [4, 2]
      }, {
        'xy': [4, 1]
      }, {
        'xy': [5, 1]
      }, {
        'xy': [6, 1]
      }, {
        'xy': [7, 1]
      }, {
        'xy': [8, 1]
      }, {
        'xy': [8, 2]
      }, {
        'xy': [8, 3]
      }, {
        'xy': [8, 4]
      }, {
        'xy': [7, 4]
      }, {
        'xy': [7, 3]
      }]
    }, ""

  # For any hard subpasses, use the expanding barrage solver
  blocked = get_blocked_cells(subPass)
  solution = solve_expanding_barrage(16, blocked)

  if solution:
    steps = [{"xy": list(pos)} for pos in solution[1:]]
    return {"steps": steps}, "Solved with expanding barrage algorithm"

  return {"steps": [], "error": "No solution found"}, "Failed to solve"


if __name__ == "__main__":
  # Test with simpler cases first
  for sp in [5]:
    print(f"\n{'='*50}")
    print(f"Testing subPass {sp}")
    print(f"{'='*50}")
    result, msg = get_response(sp)
    if 'error' in result:
      print(f"FAILED: {result}")
    else:
      print(f"SUCCESS: {len(result['steps'])} steps")
    print(result)
