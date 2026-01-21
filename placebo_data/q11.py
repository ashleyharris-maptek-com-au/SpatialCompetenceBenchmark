import random
import math, sys, os, hashlib, json, tempfile
from textwrap import dedent
from itertools import product
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

_q11_main = importlib.import_module("11")


def longest_nd_path(dim, size, start, walls, targets, depth_limit=50):
  """
  Find a long non-intersecting path in an N-dimensional grid.
  
  Args:
    dim: Number of dimensions
    size: List of grid sizes for each dimension
    start: Starting position (list/tuple)
    walls: List of wall positions to avoid
    targets: List of target positions that must be visited
  
  Returns:
    List of positions (tuples) forming the path
  """
  # Normalize inputs
  size = list(size)
  start = tuple(start)
  walls_set = set(tuple(w) for w in walls)
  targets_set = set(tuple(t) for t in targets)

  def is_valid(pos):
    """Check if position is within bounds and not a wall."""
    for i in range(dim):
      if pos[i] < 0 or pos[i] >= size[i]:
        return False
    return pos not in walls_set

  def get_neighbors(pos):
    """Get all valid adjacent positions (±1 in exactly one dimension)."""
    neighbors = []
    for d in range(dim):
      for delta in [-1, 1]:
        new_pos = list(pos)
        new_pos[d] += delta
        new_pos = tuple(new_pos)
        if is_valid(new_pos):
          neighbors.append(new_pos)
    return neighbors

  def count_reachable(pos, visited):
    """Count cells reachable from pos (BFS, limited for performance)."""
    if pos in visited:
      return 0
    seen = {pos}
    queue = deque([pos])
    count = 0
    max_count = 500  # Limit for performance in high dimensions
    while queue and count < max_count:
      curr = queue.popleft()
      count += 1
      for n in get_neighbors(curr):
        if n not in visited and n not in seen:
          seen.add(n)
          queue.append(n)
    return count

  def manhattan_distance(p1, p2):
    """Manhattan distance in N dimensions."""
    return sum(abs(a - b) for a, b in zip(p1, p2))

  def min_target_distance(pos, remaining_targets):
    """Minimum distance to any remaining target."""
    if not remaining_targets:
      return 0
    return min(manhattan_distance(pos, t) for t in remaining_targets)

  def is_dead_end_target(pos, visited):
    """Check if visiting pos would trap us (only 1 exit or less after visiting)."""
    future_neighbors = [n for n in get_neighbors(pos) if n not in visited and n != pos]
    return len(future_neighbors) <= 1

  def is_target_dead_end(target, visited):
    """Check if a target is a dead-end (0 or 1 exits after visiting)."""
    exits = [n for n in get_neighbors(target) if n not in visited]
    return len(exits) <= 1

  def greedy_search(start_pos, max_iterations=100000, visited_init=None):
    """
    Greedy search using Warnsdorff-like heuristic.
    Prefers moves that:
    1. Visit unvisited targets (but delay dead-end targets)
    2. Keep more future options open
    3. Move toward remaining targets
    """
    path = [start_pos]
    visited = visited_init.copy() if visited_init else {start_pos}
    visited.add(start_pos)
    remaining_targets = targets_set - visited
    iterations = 0

    while iterations < max_iterations:
      iterations += 1
      current = path[-1]
      neighbors = [n for n in get_neighbors(current) if n not in visited]

      if not neighbors:
        break

      # Check if all remaining targets are dead-ends
      safe_targets = {t for t in remaining_targets if not is_target_dead_end(t, visited)}
      only_dead_end_targets = remaining_targets and not safe_targets

      # Score each neighbor
      scored = []
      for n in neighbors:
        # Priority 1: Is it a target?
        is_target = n in remaining_targets

        # Priority 2: Warnsdorff heuristic - count available moves from n
        future_moves = len([m for m in get_neighbors(n) if m not in visited and m != n])

        # Priority 3: Distance to nearest remaining target (only safe ones if dead-ends exist)
        effective_targets = safe_targets if safe_targets else remaining_targets
        target_dist = min_target_distance(n, effective_targets) if effective_targets else 0

        # Priority 4: For space-filling, prefer moves that keep options open
        if dim <= 4:
          reachable = count_reachable(n, visited | {n})
        else:
          reachable = future_moves * 10  # Approximate for higher dims

        # Check if this is a dead-end target
        is_dead_end = is_target and future_moves == 0

        # Scoring: Lower score = better
        if is_target:
          if is_dead_end and reachable > 5:
            # Dead-end target but space remains - delay visiting it
            # Use same scoring as space-filling
            if future_moves == 0:
              score = (1000, -reachable)
            else:
              score = (future_moves, -reachable)
          else:
            # Safe target or space is mostly filled - visit it
            score = (-1000000, -reachable, target_dist, -future_moves)
        elif only_dead_end_targets:
          # Only dead-end targets remain - do pure space filling
          if future_moves == 0:
            score = (1000, -reachable)
          else:
            score = (future_moves, -reachable)
        elif remaining_targets:
          # Safe targets exist - balance between space-filling and target-seeking
          score = (target_dist, -reachable, -future_moves)
        else:
          # All targets visited - pure space filling
          if future_moves == 0:
            score = (1000, -reachable)
          else:
            score = (future_moves, -reachable)

        scored.append((score, n))

      # Sort by score and pick best
      scored.sort(key=lambda x: x[0])
      best = scored[0][1]

      path.append(best)
      visited.add(best)
      remaining_targets.discard(best)

    return path, remaining_targets

  def recursive_fill(start_pos, visited_init, remaining_targets_init, depth_limit=50):
    """
    Try multiple branches to find longer paths when stuck.
    Uses limited backtracking.
    """
    best_path = []
    best_remaining = remaining_targets_init.copy()

    def dfs(current, visited, remaining_targets, path, depth):
      nonlocal best_path, best_remaining

      if depth > depth_limit:
        return

      # Update best if this path is better (fewer remaining targets, or longer path)
      if (len(remaining_targets) < len(best_remaining)
          or (len(remaining_targets) == len(best_remaining) and len(path) > len(best_path))):
        best_path = path.copy()
        best_remaining = remaining_targets.copy()
        #print(f"Found path of length {len(best_path)} at depth {depth}")

      neighbors = [n for n in get_neighbors(current) if n not in visited]
      if not neighbors:
        return

      # Score neighbors similar to greedy
      scored = []
      for n in neighbors:
        is_target = n in remaining_targets
        future_moves = len([m for m in get_neighbors(n) if m not in visited and m != n])
        target_dist = min_target_distance(n, remaining_targets) if remaining_targets else 0

        if is_target:
          score = (-1000, target_dist, -future_moves)
        else:
          score = (0, target_dist, -future_moves)
        scored.append((score, n))

      scored.sort(key=lambda x: x[0])

      # Try top candidates
      for score, n in scored[:3]:  # Branch factor of 3
        new_visited = visited | {n}
        new_remaining = remaining_targets - {n}
        path.append(n)
        dfs(n, new_visited, new_remaining, path, depth + 1)
        path.pop()

    dfs(start_pos, visited_init, remaining_targets_init, [start_pos], 0)
    return best_path, best_remaining

  # Main algorithm: greedy search with optional refinement
  path, remaining = greedy_search(start)

  # If targets remain, try harder with backtracking
  if remaining and len(path) < 100:
    #print("Trying harder...")
    alt_path, alt_remaining = recursive_fill(start, {start}, targets_set - {start}, depth_limit)
    if len(alt_remaining) < len(remaining) or (len(alt_remaining) == len(remaining)
                                               and len(alt_path) > len(path)):
      path = alt_path
      remaining = alt_remaining

  # If still have remaining targets, try to extend path toward them
  if remaining:
    #print("Greedy continuation running...")
    # Continue greedy from current end
    visited_so_far = set(path)
    continuation, _ = greedy_search(path[-1], max_iterations=10000, visited_init=visited_so_far)
    if len(continuation) > 1:
      # continuation[0] is same as path[-1], so skip it
      path.extend(continuation[1:])

  # Verify our path to make sure we're only stepping 1 dimension at a time:
  curPos = path[0]
  for p in path[1:]:
    changedD = None
    for d in range(dim):
      if p[d] != curPos[d]:
        if changedD:
          assert False, f"Move changed more than one dimension. {curPos} -> {p  }"
        changedD = d
    curPos = p

  assert len(path) == len(set(path)), "Path contains duplicates"

  return path


def get_response_impl(subPass: int):
  problem = _q11_main.problems[subPass]

  import time
  start_time = time.time()

  optimumPathLength = 1
  for s in problem['size']:
    optimumPathLength *= s

  optimumPathLength -= len(problem['walls'])

  if problem['walls']:
    # Allow for a few unsolvable cells due to walls making a true hamilton path
    # impossible.
    optimumPathLength -= 3

  #print(
  #  f"Starting to solve snake in {problem['dim']}D with size {problem['size']}. Target path size >= {optimumPathLength}"
  #)

  bestPath = None
  bestPathLen = 0

  food = set(tuple(f) for f in problem['food'])
  walls = set(tuple(w) for w in problem['walls'])

  originalFood = food.copy()

  while True:
    foodAsList = list(food)
    random.shuffle(foodAsList)
    path = longest_nd_path(problem['dim'], problem['size'], problem['start'], list(walls),
                           foodAsList, 10 if bestPath else 15)

    if len(path) > bestPathLen:
      bestPath = path
      #if bestPathLen:
      #  print(f"Improved path from {bestPathLen} to {len(path)}")
      bestPathLen = len(path)

    if bestPathLen >= optimumPathLength: break

    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time > 10: break

    if random.choice([True, False]):
      newFood = []
      for d in list(problem['size']):
        newFood.append(random.randint(0, d - 1))
      if tuple(newFood) in walls: continue

      food.add(tuple(newFood))
    else:
      food -= originalFood
      if food: food.remove(random.choice(list(food)))
      food |= originalFood

  #print(f"Found {problem['dim']}D path of length {bestPathLen}")

  return {"path": [{"pos": p} for p in bestPath]}


import subprocess, json, time, sys

CACHE_DIR = os.path.join(tempfile.gettempdir(), "hyper_snake_subproblem_cache")

CACHE_VERSION = 1


def _problem_cache_key(subPass: int) -> str:
  problem = _q11_main.problems[subPass]
  key_obj = {
    "v": CACHE_VERSION,
    "dim": int(problem["dim"]),
    "size": list(problem["size"]),
    "start": list(problem["start"]),
    "walls": sorted([list(w) for w in problem["walls"]]),
    "food": sorted([list(f) for f in problem["food"]]),
  }
  raw = json.dumps(key_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
  return hashlib.sha256(raw).hexdigest()


def _cache_file_path(subPass: int) -> str:
  key = _problem_cache_key(subPass)
  return os.path.join(CACHE_DIR, f"{subPass}_{key[:32]}.json")


def _load_cached_path(subPass: int):
  cache_file = _cache_file_path(subPass)
  try:
    with open(cache_file, "r", encoding="utf-8") as f:
      data = json.load(f)
    path = data.get("path")
    if not isinstance(path, list):
      return None
    return path
  except FileNotFoundError:
    return None
  except Exception:
    return None


def _save_cached_path(subPass: int, bestPath):
  if not bestPath:
    return
  os.makedirs(CACHE_DIR, exist_ok=True)
  cache_file = _cache_file_path(subPass)
  tmp_file = cache_file + ".tmp"
  data = {"path": bestPath, "length": len(bestPath), "v": CACHE_VERSION}
  with open(tmp_file, "w", encoding="utf-8") as f:
    json.dump(data, f, separators=(",", ":"))
  os.replace(tmp_file, cache_file)


def get_response(subPass: int):
  problem = _q11_main.problems[subPass]

  max_cells = 1
  for s in problem["size"]:
    max_cells *= s
  max_cells -= len(problem["walls"])
  if problem["walls"]: max_cells -= 3  # for unsolvable paths

  bestPath = _load_cached_path(subPass)
  bestPathLen = len(bestPath) if bestPath else 0
  if bestPathLen >= max_cells and bestPath:
    print(f"Cache hit - path of length {bestPathLen} for subpass {subPass}")
    return {"path": bestPath}, "Naïve BFS algorithm with some tweaks."

  print(f"Solving subpass {subPass}, estimated solution >= {max_cells}")

  processes = []
  for i in range(16):
    processes.append(
      subprocess.Popen(
        [sys.executable, __file__, str(subPass)],
        stdout=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
      ))

  while processes:
    time.sleep(1)
    for t in processes:
      try:
        p, _ = t.communicate(timeout=5)
      except subprocess.TimeoutExpired:
        print("tick... (Solver is still running!)")
        continue
      data = json.loads(p)
      if data['path']:
        if not bestPath or len(data['path']) > bestPathLen:
          bestPath = data['path']
          if bestPathLen:
            print(f"Improved path from {bestPathLen} to {len(data['path'])}")
          else:
            print(
              f"Found path length of {len(data['path'])}, still looking in case there's better...")
          bestPathLen = len(data['path'])
          _save_cached_path(subPass, bestPath)

          if bestPathLen >= max_cells:
            for proc in processes:
              if proc.poll() is None:
                proc.terminate()
            processes.clear()
            break

      processes.remove(t)
      break

  print(f"Found path of length {bestPathLen} for subpass {subPass}")
  _save_cached_path(subPass, bestPath)

  return {"path": bestPath}, "Naïve BFS algorithm with some tweaks."


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print(get_response(6))
    sys.exit(0)

  subpass = sys.argv[1]
  print(json.dumps(get_response_impl(int(subpass))))
