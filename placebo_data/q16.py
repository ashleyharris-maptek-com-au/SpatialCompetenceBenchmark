import hashlib
import json
import math, sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Toggle to enable the perfect (exact) solver - slower but guaranteed optimal
USE_PERFECT_SOLVER = True

# Debug: disable symmetry breaking (slower but more thorough search)
DISABLE_SYMMETRY_BREAKING = False  # Re-enable for performance

# Cache directory for perfect solver results
CACHE_DIR = Path(tempfile.gettempdir()) / "q16_perfect_cache"

sys.path.append("..")
sys.path.append(".")

g = {}
exec(open("16.py").read(), g)

import threading

mutexLock = threading.Lock()


def get_response(subPass: int):
  """Get the placebo response for this question."""

  with mutexLock:
    print("Starting subpass", subPass)
    prismList = g["prismList"][0:subPass + 1]

    # Expand prismList into individual prisms with all rotation variants
    prisms = []
    for count, x, y, z in prismList:
      dims = sorted([x, y, z], reverse=True)
      for _ in range(count):
        prisms.append(tuple(dims))

    # Sort prisms by volume (largest first) for better packing
    prisms.sort(key=lambda p: p[0] * p[1] * p[2], reverse=True)

    print(f"Prisms count: {len(prisms)}, largest: {prisms[0]}, smallest: {prisms[-1]}")

    def get_rotations(dims):
      """Get all unique rotations of a prism."""
      x, y, z = dims
      rotations = set()
      for perm in [(x, y, z), (x, z, y), (y, x, z), (y, z, x), (z, x, y), (z, y, x)]:
        rotations.add(perm)
      return list(rotations)

    def boxes_overlap(b1, b2):
      """Check if two boxes overlap."""
      return (b1['XyzMin'][0] < b2['XyzMax'][0] and b1['XyzMax'][0] > b2['XyzMin'][0]
              and b1['XyzMin'][1] < b2['XyzMax'][1] and b1['XyzMax'][1] > b2['XyzMin'][1]
              and b1['XyzMin'][2] < b2['XyzMax'][2] and b1['XyzMax'][2] > b2['XyzMin'][2])

    def can_place(placed, new_box):
      """Check if new_box can be placed without overlap."""
      for box in placed:
        if boxes_overlap(box, new_box):
          return False
      return True

    def get_candidate_positions(placed, max_coord):
      """Get candidate positions (corners of existing boxes + origin)."""
      positions = [(0, 0, 0)]
      for box in placed:
        # Add corners of existing boxes as candidates
        for x in [box['XyzMin'][0], box['XyzMax'][0]]:
          for y in [box['XyzMin'][1], box['XyzMax'][1]]:
            for z in [box['XyzMin'][2], box['XyzMax'][2]]:
              if x <= max_coord and y <= max_coord and z <= max_coord:
                positions.append((x, y, z))
      return list(set(positions))

    def bounding_volume(placed):
      """Calculate bounding box volume of placed boxes."""
      if not placed:
        return 0
      max_x = max(b['XyzMax'][0] for b in placed)
      max_y = max(b['XyzMax'][1] for b in placed)
      max_z = max(b['XyzMax'][2] for b in placed)
      return max_x * max_y * max_z

    def pack_greedy(prisms_to_place):
      """Greedy bottom-left-back packing with rotation."""
      placed = []
      max_coord = sum(max(p) for p in prisms_to_place)  # Upper bound

      for dims in prisms_to_place:
        best_pos = None
        best_rot = None
        best_score = float('inf')

        candidates = get_candidate_positions(placed, max_coord)
        # Sort candidates by (z, y, x) for bottom-left-back preference
        candidates.sort(key=lambda p: (p[2], p[1], p[0]))

        for rot in get_rotations(dims):
          dx, dy, dz = rot
          for px, py, pz in candidates:
            new_box = {'XyzMin': [px, py, pz], 'XyzMax': [px + dx, py + dy, pz + dz]}
            if can_place(placed, new_box):
              # Score by resulting bounding volume
              test_placed = placed + [new_box]
              score = bounding_volume(test_placed)
              if score < best_score:
                best_score = score
                best_pos = (px, py, pz)
                best_rot = rot

        if best_pos is None:
          # Fallback: stack on top
          max_z = max((b['XyzMax'][2] for b in placed), default=0) if placed else 0
          best_pos = (0, 0, max_z)
          best_rot = dims

        px, py, pz = best_pos
        dx, dy, dz = best_rot
        placed.append({'XyzMin': [px, py, pz], 'XyzMax': [px + dx, py + dy, pz + dz]})

      return placed

    # =====================================================================
    # Perfect Solver: Branch and Bound with Extreme Points
    # =====================================================================

    def get_cache_key(prisms_list: List[Tuple[int, int, int]]) -> str:
      """Generate a unique cache key for a set of prisms."""
      sorted_prisms = sorted(prisms_list)
      key_str = str(sorted_prisms)
      return hashlib.md5(key_str.encode()).hexdigest()

    def load_cached_result(cache_key: str) -> Optional[Dict]:
      """Load cached result if available."""
      cache_path = CACHE_DIR / f"{cache_key}.json"
      if cache_path.exists():
        try:
          with open(cache_path, 'r') as f:
            return json.load(f)
        except (json.JSONDecodeError, IOError):
          pass
      return None

    def save_cached_result(cache_key: str, result: Dict) -> None:
      """Save result to cache."""
      try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = CACHE_DIR / f"{cache_key}.json"
        with open(cache_path, 'w') as f:
          json.dump(result, f)
      except IOError:
        pass

    def get_divisors(n: int) -> List[int]:
      """Get all divisors of n."""
      divs = []
      for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
          divs.append(i)
          if i != n // i:
            divs.append(n // i)
      return sorted(divs)

    def is_1d_feasible(prisms: List[Tuple[int, int, int]], target: int,
                       axis_dims_per_prism: List[set]) -> bool:
      """Check if prisms can stack along one axis to exactly fill target length.
    
    For each prism, axis_dims_per_prism contains the set of dimensions it can
    contribute along the stacking axis. We need to pick one dimension per prism
    such that they sum to exactly target.
    
    Uses dynamic programming: dp[i][s] = can we achieve sum s using first i prisms?
    """
      n = len(prisms)
      if n == 0:
        return target == 0

      # dp[s] = True if sum s is achievable
      dp = {0}

      for i, available_dims in enumerate(axis_dims_per_prism):
        new_dp = set()
        for s in dp:
          for d in available_dims:
            new_sum = s + d
            if new_sum <= target:
              new_dp.add(new_sum)
        dp = new_dp
        if not dp:
          return False

      return target in dp

    def check_1d_stacking_feasibility(prisms: List[Tuple[int, int, int]], container: Tuple[int, int,
                                                                                           int],
                                      valid_rotations_cache: Dict) -> Tuple[bool, str]:
      """Check if prisms can feasibly stack to fill container's Z dimension.
    
    Even for 3D arrangements, prisms must have Z dimensions that can sum to D.
    This is a necessary (not sufficient) condition for perfect packing.
    
    Returns (is_feasible, reason).
    """
      W, H, D = container

      # For each prism, collect ALL Z dimensions it can contribute from valid rotations
      z_dims_per_prism = []

      for dims in prisms:
        rotations = valid_rotations_cache.get(dims, [])
        if not rotations:
          return False, f"Prism {dims} has no valid rotations"
        # Collect all possible Z dimensions from all valid rotations
        z_dims = {r[2] for r in rotations}
        z_dims_per_prism.append(z_dims)

      # Check if ANY assignment of Z dimensions can sum to D
      if not is_1d_feasible(prisms, D, z_dims_per_prism):
        # Count available dimensions for error message
        dim_counts = {}
        for z_dims in z_dims_per_prism:
          for d in z_dims:
            dim_counts[d] = dim_counts.get(d, 0) + 1
        return False, f"1D infeasible: {len(prisms)} prisms must sum Z to {D}, available Z dims (max counts): {dim_counts}"

      return True, "1D check passed"

    def get_candidate_containers_from_factorization(
        tsp_result: Tuple[bool, str]) -> List[Tuple[int, int, int]]:
      """Extract candidate containers from isTheoreticallySolvablePerfectly result.
    
    Parses the plausible_decompositions from the result string.
    These are already filtered for geometric validity.
    """
      if not tsp_result[0]:
        return []

      reason = tsp_result[1]
      # Parse "Potentially solvable with bounding boxes: [(5, 7, 193), ...]"
      if "bounding boxes:" in reason:
        import ast
        try:
          boxes_str = reason.split("bounding boxes:")[1].strip()
          containers = ast.literal_eval(boxes_str)
          # Sort by surface area (smaller often easier to pack)
          containers.sort(key=lambda c: 2 * (c[0] * c[1] + c[1] * c[2] + c[0] * c[2]))
          return containers
        except (ValueError, SyntaxError):
          pass
      return []

    def get_valid_rotations(dims: Tuple[int, int, int],
                            container: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
      """Get rotations of a prism that actually fit within the container.
    
    This is a key optimization - if container is (5, 7, 193) and prism is (11, 7, 5),
    then only rotation (5, 7, 11) fits. This dramatically reduces the search space.
    
    Rotations are sorted to prefer those that fill more of the X,Y cross-section,
    which leads to simpler search spaces (layer-by-layer stacking).
    """
      W, H, D = container
      valid = []
      tried = set()

      for rot in get_rotations(dims):
        if rot in tried:
          continue
        tried.add(rot)
        dx, dy, dz = rot
        # Rotation fits if it can be placed at origin without exceeding container
        if dx <= W and dy <= H and dz <= D:
          valid.append(rot)

      # Sort rotations: prefer those that fill more of the XY cross-section
      # This encourages layer-by-layer packing which is easier to search
      def cross_section_score(rot):
        dx, dy, dz = rot
        # Higher score = fills more of cross-section = try first
        fill_ratio = (dx * dy) / (W * H)
        # Secondary: prefer smaller Z extent for tighter stacking
        return (-fill_ratio, dz)

      valid.sort(key=cross_section_score)
      return valid

    def get_extreme_points(placed: List[Dict],
                           container: Tuple[int, int, int],
                           all_box_dims: set = None) -> List[Tuple[int, int, int]]:
      """Get candidate positions where new boxes can be placed.
    
    Uses extreme points (corners of placed boxes) plus additional positions
    based on box dimensions to ensure all valid tilings can be found.
    """
      W, H, D = container
      if not placed:
        return [(0, 0, 0)]

      # Collect coordinates from box corners
      x_coords = {0}
      y_coords = {0}
      z_coords = {0}

      for box in placed:
        x_coords.add(box['XyzMax'][0])
        y_coords.add(box['XyzMax'][1])
        z_coords.add(box['XyzMax'][2])
        x_coords.add(box['XyzMin'][0])
        y_coords.add(box['XyzMin'][1])
        z_coords.add(box['XyzMin'][2])

      # Add intermediate X,Y positions based on box dimensions
      # This handles cases where cross-section-filling boxes leave structured space
      # Only add if we have few Y or X positions (indicating layered packing)
      if all_box_dims and (len(x_coords) <= 2 or len(y_coords) <= 2):
        for dim in all_box_dims:
          if dim > 0:
            # Add Y positions that allow tiling
            for y in range(0, H, dim):
              y_coords.add(y)
            # Add X positions that allow tiling
            for x in range(0, W, dim):
              x_coords.add(x)

      # Generate candidate points
      points = []
      for x in x_coords:
        for y in y_coords:
          for z in z_coords:
            if x < W and y < H and z < D:
              points.append((x, y, z))

      # Sort by (z, y, x) for bottom-left-back preference
      points.sort(key=lambda p: (p[2], p[1], p[0]))
      return points

    def fits_in_container(box: Dict, container: Tuple[int, int, int]) -> bool:
      """Check if box fits within container bounds."""
      W, H, D = container
      return (box['XyzMax'][0] <= W and box['XyzMax'][1] <= H and box['XyzMax'][2] <= D)

    def get_min_prism_dim(prisms_list: List[Tuple[int, int, int]]) -> int:
      """Get the smallest dimension across all prisms."""
      return min(min(p) for p in prisms_list) if prisms_list else 0

    def has_dead_space(placed: List[Dict], container: Tuple[int, int, int], min_dim: int,
                       all_box_dims: set) -> bool:
      """Check if there are gaps that cannot be filled by any available prism dimension.
    
    This is a conservative heuristic - we only check if grid cell dimensions
    are achievable by the available prism dimensions using the can_sum_to logic.
    """
      if not placed or min_dim <= 1:
        return False

      W, H, D = container

      # Collect grid boundaries from placed boxes
      x_coords = sorted({0} | {b['XyzMin'][0]
                               for b in placed} | {b['XyzMax'][0]
                                                   for b in placed} | {W})
      y_coords = sorted({0} | {b['XyzMin'][1]
                               for b in placed} | {b['XyzMax'][1]
                                                   for b in placed} | {H})
      z_coords = sorted({0} | {b['XyzMin'][2]
                               for b in placed} | {b['XyzMax'][2]
                                                   for b in placed} | {D})

      # Check if any grid cell dimension is impossible to tile
      for i in range(len(x_coords) - 1):
        gap = x_coords[i + 1] - x_coords[i]
        if gap > 0 and gap < min_dim and gap not in all_box_dims:
          return True
      for i in range(len(y_coords) - 1):
        gap = y_coords[i + 1] - y_coords[i]
        if gap > 0 and gap < min_dim and gap not in all_box_dims:
          return True
      for i in range(len(z_coords) - 1):
        gap = z_coords[i + 1] - z_coords[i]
        if gap > 0 and gap < min_dim and gap not in all_box_dims:
          return True

      return False

    def pack_perfect_recursive(remaining: List[Tuple[int, int, int]],
                               placed: List[Dict],
                               container: Tuple[int, int, int],
                               placed_volume: int,
                               valid_rotations_cache: Dict,
                               min_dim: int,
                               all_box_dims: set,
                               last_placement: Tuple = None) -> Optional[List[Dict]]:
      """Recursive backtracking solver with pruning."""
      if not remaining:
        return placed  # All prisms placed successfully

      # Pruning: check if remaining volume can fit
      remaining_volume = sum(p[0] * p[1] * p[2] for p in remaining)
      W, H, D = container
      container_volume = W * H * D
      if placed_volume + remaining_volume != container_volume:
        return None  # Volume mismatch - can't be perfect

      # Pruning: check for dead space (gaps too small for any prism)
      if has_dead_space(placed, container, min_dim, all_box_dims):
        return None

      # Get next prism to place (largest first for better pruning)
      dims = remaining[0]
      rest = remaining[1:]

      # Get candidate positions (pass all_box_dims for intermediate position generation)
      positions = get_extreme_points(placed, container, all_box_dims)

      # Use pre-computed valid rotations for this prism+container combo
      rotations = valid_rotations_cache.get(dims, get_valid_rotations(dims, container))

      # If no rotations fit at all, this branch is dead
      if not rotations:
        return None

      # Symmetry breaking: if this prism is identical to the previous one,
      # only try placements that come "after" the last placement to avoid duplicates
      # Disable for end-game (few prisms left) to allow complex 3D tilings
      use_symmetry_breaking = (not DISABLE_SYMMETRY_BREAKING and last_placement is not None
                               and len(placed) > 0 and dims == last_placement[0]
                               and len(remaining) > 8)

      for rot in rotations:
        dx, dy, dz = rot

        for px, py, pz in positions:
          # Quick bounds check before creating box dict
          if px + dx > W or py + dy > H or pz + dz > D:
            continue

          # Symmetry breaking: skip placements that would be explored in another branch
          if use_symmetry_breaking:
            last_rot, last_pos = last_placement[1], last_placement[2]
            # Only explore if (rot, pos) >= (last_rot, last_pos) lexicographically
            if (rot, (px, py, pz)) < (last_rot, last_pos):
              continue

          new_box = {'XyzMin': [px, py, pz], 'XyzMax': [px + dx, py + dy, pz + dz]}

          # Check overlap with existing boxes
          if not can_place(placed, new_box):
            continue

          # Recurse with symmetry info
          this_placement = (dims, rot, (px, py, pz))
          result = pack_perfect_recursive(rest, placed + [new_box], container,
                                          placed_volume + dx * dy * dz, valid_rotations_cache,
                                          min_dim, all_box_dims, this_placement)
          if result is not None:
            return result

      return None  # No valid placement found

    def pack_perfect(prisms_list: List[Tuple[int, int, int]],
                     hint_containers: List[Tuple[int, int, int]] = None) -> Optional[List[Dict]]:
      """Attempt to find a perfect packing using branch and bound.
    
    Args:
      prisms_list: List of prism dimensions to pack
      hint_containers: Pre-computed valid containers from factorization analysis.
                       If provided, only these containers are tried (major speedup).
    
    Returns the packing if found, or None if no perfect packing exists.
    Results are cached to avoid recomputation.
    """
      cache_key = get_cache_key(prisms_list)

      # Check cache first
      cached = load_cached_result(cache_key)
      if cached is not None:
        if cached.get('impossible'):
          print("Proven impossible in previous run.")
          return None
        print("Found cached result. " + str(CACHE_DIR))
        return cached.get('boxes')

      # Use hint containers if provided, otherwise we can't solve
      if not hint_containers:
        print("  No valid containers from factorization - cannot find perfect packing")
        save_cached_result(cache_key, {'impossible': True})
        return None

      candidates = hint_containers
      print(f"  Trying {len(candidates)} candidate container(s): {candidates}")

      # Sort prisms by volume (largest first) for better pruning
      sorted_prisms = sorted(prisms_list, key=lambda p: p[0] * p[1] * p[2], reverse=True)

      for container in candidates:
        W, H, D = container

        # Pre-compute valid rotations for each unique prism size
        unique_prisms = set(sorted_prisms)
        valid_rotations_cache = {}

        print(f"  Testing container {container}...")
        all_prisms_can_fit = True
        for dims in unique_prisms:
          valid_rots = get_valid_rotations(dims, container)
          if not valid_rots:
            print(f"    Prism {dims} cannot fit in container {container} in any orientation")
            all_prisms_can_fit = False
            break
          valid_rotations_cache[dims] = valid_rots
          if len(valid_rots) < 6:
            print(f"    Prism {dims} has only {len(valid_rots)} valid rotation(s): {valid_rots}")

        if not all_prisms_can_fit:
          continue

        # 1D FEASIBILITY CHECK: If all prisms must fill the cross-section,
        # verify that their Z dimensions can sum to exactly D
        feasible, reason = check_1d_stacking_feasibility(sorted_prisms, container,
                                                         valid_rotations_cache)
        if not feasible:
          print(f"    {reason}")
          continue

        # OPTIMIZATION: Pre-place prisms that fill the entire X,Y cross-section.
        # When a prism's only way to fit involves filling the full cross-section,
        # it MUST stack along Z. Also handle prisms where ALL valid rotations
        # fill the cross-section (they can be stacked in any of those rotations).
        pre_placed = []
        remaining_prisms = list(sorted_prisms)
        current_z = 0

        # Find prisms where ALL valid rotations fill the X,Y cross-section
        # OR there's only ONE valid rotation that fills it
        forced_prism_types = []
        for dims in unique_prisms:
          rots = valid_rotations_cache[dims]
          # Check if ANY rotation fills the cross-section
          cross_section_rots = [r for r in rots if r[0] == W and r[1] == H]
          if cross_section_rots:
            # If this is the ONLY valid rotation, or if ALL rotations fill cross-section
            if len(rots) == 1 or len(cross_section_rots) == len(rots):
              # Pick the rotation with smallest Z extent (stack more efficiently)
              best_rot = min(cross_section_rots, key=lambda r: r[2])
              forced_prism_types.append((dims, best_rot))

        # Sort forced prisms by Z extent (largest first) to fill efficiently
        forced_prism_types.sort(key=lambda x: x[1][2], reverse=True)

        if forced_prism_types:
          print(f"    Found forced prisms (must stack along Z): {forced_prism_types}")
          for dims, rot in forced_prism_types:
            count = remaining_prisms.count(dims)
            for _ in range(count):
              remaining_prisms.remove(dims)
              box = {'XyzMin': [0, 0, current_z], 'XyzMax': [rot[0], rot[1], current_z + rot[2]]}
              pre_placed.append(box)
              current_z += rot[2]
          print(f"    Pre-placed {len(pre_placed)} forced prisms, Z now at {current_z}")
          print(f"    Remaining prisms to search: {len(remaining_prisms)}")

          # Check 1D feasibility for remaining prisms in remaining Z space
          if remaining_prisms:
            remaining_z = D - current_z
            remaining_container = (W, H, remaining_z)
            # Recompute valid rotations for remaining container
            remaining_rot_cache = {}
            for dims in set(remaining_prisms):
              remaining_rot_cache[dims] = get_valid_rotations(dims, remaining_container)

            feasible, reason = check_1d_stacking_feasibility(remaining_prisms, remaining_container,
                                                             remaining_rot_cache)
            if not feasible:
              print(f"    {reason}")
              continue

        # Compute min dimension and all box dims for dead space pruning
        min_dim = get_min_prism_dim(sorted_prisms)
        all_box_dims = set()
        for p in sorted_prisms:
          all_box_dims.update(p)

        placed_volume = sum((b['XyzMax'][0] - b['XyzMin'][0]) * (b['XyzMax'][1] - b['XyzMin'][1]) *
                            (b['XyzMax'][2] - b['XyzMin'][2]) for b in pre_placed)

        result = pack_perfect_recursive(remaining_prisms, pre_placed, container, placed_volume,
                                        valid_rotations_cache, min_dim, all_box_dims)
        if result is not None:
          # Found a perfect packing!
          print(f"  Found perfect packing in container {container}!")
          save_cached_result(cache_key, {'boxes': result, 'container': container})

          return result
        else:
          print(f"    No valid packing found for container {container}")

      # No perfect packing exists
      save_cached_result(cache_key, {'impossible': True})
      return None

    # =====================================================================
    # Main packing logic
    # =====================================================================

    packings = None
    method = "greedy"

    tsp = list(g["isTheoreticallySolvablePerfectly"](subPass))

    if tsp[0]:
      print("Is theoretically solvable perfectly. " + tsp[1])
      if USE_PERFECT_SOLVER:
        # Extract pre-computed valid containers from factorization analysis
        hint_containers = get_candidate_containers_from_factorization(tsp)
        packings = pack_perfect(prisms, hint_containers)
        if packings is not None:
          method = "perfect (exact)"
    else:
      print("Not solvable perfectly, just using greedy packing. " + tsp[1])

    if packings is None:
      packings = pack_greedy(prisms)
      method = "greedy"
      tsp[1] = "Because " + tsp[1][0].lower() + tsp[1][1:]
      if tsp[0]:
        method = "greedy packing, and we showed that it's impossible to do perfect"
        tsp[1] = ""

    assert len(packings) == len(prisms)

    if subPass == 16:
      import random
      rng = random.Random(42)  # deterministic random number generator
      packings, method = get_guess(subPass, rng)

    return {"boxes": packings}, f"Calculated with {method} packing. " + tsp[1]


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  prismList = g["prismList"]
  boxes = []
  cursor = [0, 0, 0]
  for count, x, y, z in prismList[0:subPass + 1]:
    for _ in range(count):
      dx, dy, dz = rng.choice([(x, y, z), (x, z, y), (y, x, z), (y, z, x), (z, x, y), (z, y, x)])
      min_corner = [cursor[0], cursor[1], cursor[2]]
      max_corner = [cursor[0] + dx, cursor[1] + dy, cursor[2] + dz]
      boxes.append({"XyzMin": min_corner, "XyzMax": max_corner})
      cursor[0] += dx
  return boxes, "Random guess"


def cache_solutions():
  for sp in len(g["prismList"]):
    get_response(sp)
