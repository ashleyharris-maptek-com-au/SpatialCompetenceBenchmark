import numpy as np
import OpenScad as vc
import random
import os
import tempfile
import json
import hashlib
import time
from LLMBenchCore.ResultPaths import result_path, report_relpath

# Cache for grading and visualization results
_cache_dir = os.path.join(tempfile.gettempdir(), "23_fluid_cache")
os.makedirs(_cache_dir, exist_ok=True)


def _get_cache_key(answer: dict, subPass: int, aiEngineName: str) -> str:
  """Generate a cache key from the answer, subPass, and engine name."""
  data = json.dumps(answer, sort_keys=True) + str(subPass) + aiEngineName + "v8"
  return hashlib.sha256(data.encode()).hexdigest()


def _load_from_cache(cache_key: str, cache_type: str):
  """Load result from cache if available."""
  cache_file = os.path.join(_cache_dir, f"{cache_type}_{cache_key}.json")
  if os.path.exists(cache_file):
    try:
      with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    except (json.JSONDecodeError, IOError):
      pass
  return None


def _save_to_cache(cache_key: str, cache_type: str, result):
  """Save result to cache."""
  cache_file = os.path.join(_cache_dir, f"{cache_type}_{cache_key}.json")
  try:
    with open(cache_file, 'w', encoding='utf-8') as f:
      json.dump(result, f)
  except IOError:
    pass


title = "Fluid simulation"
prompt = """
You are given a 3D voxel world, of dimensions PARAM_A * PARAM_A * 8 voxels,
currently filled with rock uniformly flat and solid at the layers z = [0,1,2]

Rainfall occurs at the top centre of the world, and follows the following rules:
- If air is below water, the water falls (z = z - 1)
- If water has ground or water below it, it "flood fills" out looking for any air voxels 
  at the z level below it, and moves to the nearest one.
- If water touches the sides or bottom of the world, it falls off and is lost forever.
- If water can't find a reachable air voxel to move to, it remains there as a pool of water.

Since the world is currently flat, rainfall currently all runs off the edge of the map,
meaning earthworks are required to achieve your goals. After your earthworks complete, 
there will be 1000s of voxels worth of rainfall (mostly centred at the centre of the world)
before your world is graded.

You can specify earthworks using a simple json format:
{
  "earthworks" : [
    {
      "xyzMin": [2, 2, 3],
      "xyzMax": [6, 6, 3],
      "material": "Rock"
    },
    {
      "xyzMin": [3, 3, 3],
      "xyzMax": [5, 5, 3],
      "material": "Air"
    }
  ]
}
This would add a 5x5 slab of rock at z = 3, and remove a 3x3 hole from it, leaving a
ring of rock at z = 3. This would capture 9 voxels of water. 

Rock connected (orthogonally) to other rock is rigid and supports itself, allowing caves, tunnels,
bridges, overhangs, and promontories. Floating rock without any support structure will 
obviously fall to the ground.

Now you understand the format - here is the task I need help with:

Add rock or air voxels to the world in order to ensure that after the rains end,
"""

subpassParamSummary = [
  "there is a lake of at least 36 voxels in surface area.",
  "there are 3 unconnected bodies of water each at least 2x2",
  "there is a lake of at least 2 voxels at z > 5",
  "there is an underground lake of at least 10 voxels in volume, "
  "but no water voxels are visible from above.",  #
  "there are 3 lakes on 3 different z levels",
  "there is a lake at least 6 voxels deep",
  "there are 2 lakes, each over 200 voxels in volume",
  "there is a ring-shaped lake (water surrounds a dry center of at least 3x3)",
  "there is water at z=3 AND z=6, but NO water at z=4 or z=5",
  "there is EXACTLY 100 voxels of water total (not more, not less)",
  "there are 4 separate underground lakes, each at least 5 voxels, none visible from above"
]

earlyFail = False

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "earthworks": {
      "type":
      "array",
      "items": {
        "type": "object",
        "properties": {
          "xyzMin": {
            "type": "array",
            "items": {
              "type": "number"
            },
          },
          "xyzMax": {
            "type": "array",
            "items": {
              "type": "number"
            },
          },
          "material": {
            "type": "string",
            "enum": ["Air", "Rock"]
          }
        },
        "propertyOrdering": ["xyzMin", "xyzMax", "material"],
        "additionalProperties": False,
        "required": ["xyzMin", "xyzMax", "material"]
      },
      "description":
      "List of voxel changes to make to the world. You can change multiple in one go by specifying a region in between xyzMin and xyzMax. A single voxel can be changed by setting xyzMin = xyzMax."
    }
  },
  "propertyOrdering": ["reasoning", "earthworks"],
  "additionalProperties": False,
  "required": ["reasoning", "earthworks"]
}


def getWorldSize(subPass):
  sizes = [16, 24, 32, 40, 48, 56, 64, 48, 56, 48, 64]
  return sizes[subPass] if subPass < len(sizes) else 56


def prepareSubpassPrompt(index):
  sizes = [16, 24, 32, 40, 48, 56, 64, 48, 56, 48, 64]
  if index < len(subpassParamSummary):
    return prompt.replace("PARAM_A", str(sizes[index])) + subpassParamSummary[index]
  raise StopIteration


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  # Check cache first
  cache_key = _get_cache_key(answer, subPass, aiEngineName)
  cached = _load_from_cache(cache_key, "grade")
  if cached is not None:
    print(f"Using cached grade result for {aiEngineName} subpass {subPass}. {_cache_dir}")
    return tuple(cached)

  result = _gradeAnswerImpl(answer, subPass, aiEngineName)
  _save_to_cache(cache_key, "grade", list(result))
  return result


def _gradeAnswerImpl(answer: dict, subPass: int, aiEngineName: str):
  import numpy as np
  from collections import deque

  earthworks = answer.get("earthworks", [])
  if not isinstance(earthworks, list):
    return 0, "earthworks must be a list"

  WORLD_SIZE = getWorldSize(subPass)
  WORLD_HEIGHT = 8

  # 0 = air, 1 = rock, 2 = water
  world = np.zeros((WORLD_SIZE, WORLD_SIZE, WORLD_HEIGHT), dtype=np.uint8)

  # Fill z=0,1,2 with rock initially
  world[:, :, 0] = 1
  world[:, :, 1] = 1
  world[:, :, 2] = 1

  # Apply AI's earthworks
  for v in earthworks:
    xyzMin = v.get("xyzMin", [0, 0, 0])
    xyzMax = v.get("xyzMax", [0, 0, 0])
    if len(xyzMin) < 3 or len(xyzMax) < 3:
      print(f"Invalid coordinates (length < 3): {xyzMin} {xyzMax}")
      continue
    xMin, yMin, zMin = int(xyzMin[0]), int(xyzMin[1]), int(xyzMin[2])
    xMax, yMax, zMax = int(xyzMax[0]), int(xyzMax[1]), int(xyzMax[2])
    if xMin < 0 or xMax >= WORLD_SIZE or yMin < 0 or yMax >= WORLD_SIZE or zMin < 0 or zMax >= WORLD_HEIGHT:
      print(f"Invalid coordinates (out of bounds): {xyzMin} {xyzMax}")
      continue  # Skip invalid coordinates
    if xMin > xMax or yMin > yMax or zMin > zMax:
      print(f"Invalid coordinates (min > max): {xyzMin} {xyzMax}")
      continue  # Skip invalid coordinates
    material = v.get("material", "Air")
    for x in range(xMin, xMax + 1):
      for y in range(yMin, yMax + 1):
        for z in range(zMin, zMax + 1):
          if material == "Rock":
            world[x, y, z] = 1
          elif material == "Air":
            world[x, y, z] = 0

  # Rock stability simulation - floating rock falls to the ground
  # Find all connected components of rock and check if grounded
  def find_rock_components():
    """Find all connected components of rock using 3D flood fill."""
    visited = np.zeros_like(world, dtype=bool)
    components = []

    for x in range(WORLD_SIZE):
      for y in range(WORLD_SIZE):
        for z in range(WORLD_HEIGHT):
          if world[x, y, z] == 1 and not visited[x, y, z]:
            # BFS to find connected rock component
            component = []
            queue = deque([(x, y, z)])
            visited[x, y, z] = True
            while queue:
              cx, cy, cz = queue.popleft()
              component.append((cx, cy, cz))
              # Check 6 orthogonal neighbors
              for dx, dy, dz in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1),
                                 (0, 0, -1)]:
                nx, ny, nz = cx + dx, cy + dy, cz + dz
                if 0 <= nx < WORLD_SIZE and 0 <= ny < WORLD_SIZE and 0 <= nz < WORLD_HEIGHT:
                  if world[nx, ny, nz] == 1 and not visited[nx, ny, nz]:
                    visited[nx, ny, nz] = True
                    queue.append((nx, ny, nz))
            components.append(component)
    return components

  def is_grounded(component):
    """Check if component has any voxel at z=0 (connected to ground)."""
    return any(z == 0 for x, y, z in component)

  def drop_component(component):
    """Drop a floating component until it hits ground or other rock."""
    if not component:
      return
    # Find minimum z in the component
    min_z = min(z for x, y, z in component)
    # Calculate how far we can drop
    drop_distance = 0
    for test_drop in range(1, min_z + 1):
      can_drop = True
      for x, y, z in component:
        new_z = z - test_drop
        if new_z < 0:
          can_drop = False
          break
        # Check if destination is occupied by rock NOT in this component
        if world[x, y, new_z] == 1 and (x, y, new_z) not in component_set:
          can_drop = False
          break
      if can_drop:
        drop_distance = test_drop
      else:
        break

    if drop_distance > 0:
      # Clear old positions
      for x, y, z in component:
        world[x, y, z] = 0
      # Set new positions
      for x, y, z in component:
        world[x, y, z - drop_distance] = 1

  # Keep simulating until no more drops occur
  changed = True
  RockFell = False
  while changed:
    changed = False
    components = find_rock_components()

    if len(components) != 1:
      print("Multiple rock components found! World is not stable.")
      RockFell = True

    for component in components:
      if not is_grounded(component):
        component_set = set(component)
        RockFell = [(x, y) for x, y, z in component_set]
        min_z = min(z for x, y, z in component)
        if min_z > 0:  # Can potentially drop
          print("Floating rock found! Dropping component at", min_z)
          drop_component(component)
          changed = True

  lastSettledDrop = 0

  def is_edge(x, y, z):
    """Check if position is at world edge (water escapes)"""
    return x == 0 or x == WORLD_SIZE - 1 or y == 0 or y == WORLD_SIZE - 1 or z == 0

  def simulate_water_drop(x, y, z):
    """Simulate a single water drop from the top"""
    while True:
      if z <= 0: return True
      # Check what's below
      below = world[x, y, z - 1]

      if below == 0:  # Air below - fall down
        z -= 1
        continue

      # Ground or water below - try to flood fill to find a drop point
      # BFS to find nearest air cell at z-1 that we can reach via walkable cells at current z
      visited = set()
      queue = deque([(x, y, 0)])  # (x, y, distance)
      visited.add((x, y))

      best_drop = None
      best_dist = float('inf')
      touches_edge = False

      while queue:
        cx, cy, dist = queue.popleft()

        # Check if this cell touches edge at current z level
        if cx == 0 or cx == WORLD_SIZE - 1 or cy == 0 or cy == WORLD_SIZE - 1:
          touches_edge = True
          continue

        # Check if we can drop down from here
        if world[cx, cy, z - 1] == 0:  # Air below
          if dist < best_dist:
            best_dist = dist
            best_drop = (cx, cy)

        # Expand to neighbors (can walk through air or water at same z level)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
          nx, ny = cx + dx, cy + dy
          if 0 <= nx < WORLD_SIZE and 0 <= ny < WORLD_SIZE:
            if (nx, ny) not in visited:
              # Can move through air or water at this z level
              if world[nx, ny, z] != 1:  # Not rock
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))

      if best_drop:
        # Move to the drop point and fall
        x, y = best_drop
        z -= 1
        continue

      # If we can't drop but can reach the edge, water escapes
      if touches_edge:
        return True  # Water lost

      # No escape, no drop point - water settles in basin
      # Find any unfilled air cell in the reachable region at this z level
      for (cx, cy) in visited:
        if world[cx, cy, z] == 0:  # Air cell we can fill
          world[cx, cy, z] = 2
          return False

      # All cells at this level are filled, try to rise
      # Check if there's air above any visited cell
      for (cx, cy) in visited:
        if z + 1 < WORLD_HEIGHT and world[cx, cy, z + 1] == 0:
          # Water can rise here
          world[cx, cy, z + 1] = 2
          return False

      # Basin completely full or blocked
      if touches_edge:
        return True  # Let it spill if the reachable region touches an edge
      return True  # No space to store water; count as escaped instead of disappearing
    return True

  # Run the rain simulation - three stages:
  # 1. 1 drop at every x,y position - ensure every tiny dip has some water in it,
  #    as will occurs in real life when rain falls on a rough surface. This also
  #    helps with the case when there's a flat plane with a small dip far off to
  #    one side, 500 DFS searches might not be enough to find it. We do this to
  #    solve this corner case by pre-finding every local minima and we help it accumulate.
  startTime = time.time()
  for x in range(WORLD_SIZE):
    for y in range(WORLD_SIZE):
      simulate_water_drop(x, y, WORLD_HEIGHT - 1)

  print("Rain simulation first sprinkle ({subpass}) took {time}".format(subpass=subPass,
                                                                        time=time.time() -
                                                                        startTime))

  # 2. Minimum 500 drops at the centre - This is what the AI is expecting.
  #    Since the world size is even and exact centre is not represetntable,
  #    we make the rain fall in a 2x2 square around the exact centre.
  for i in range(500):
    simulate_water_drop(WORLD_SIZE // 2, WORLD_SIZE // 2, WORLD_HEIGHT - 1)
    simulate_water_drop(WORLD_SIZE // 2 + 1, WORLD_SIZE // 2, WORLD_HEIGHT - 1)
    simulate_water_drop(WORLD_SIZE // 2, WORLD_SIZE // 2 + 1, WORLD_HEIGHT - 1)
    simulate_water_drop(WORLD_SIZE // 2 + 1, WORLD_SIZE // 2 + 1, WORLD_HEIGHT - 1)

  print("Rain simulation 500 voxel downpour ({subpass}) took {time}".format(subpass=subPass,
                                                                            time=time.time() -
                                                                            startTime))

  # 3. Keep filling until 500 drops in a row fall off the edge, indiciating all
  #    basins are filled.
  totalDropCount = 0
  while lastSettledDrop < 500:
    fellOff = True
    fellOff &= simulate_water_drop(WORLD_SIZE // 2, WORLD_SIZE // 2, WORLD_HEIGHT - 1)
    fellOff &= simulate_water_drop(WORLD_SIZE // 2 + 1, WORLD_SIZE // 2, WORLD_HEIGHT - 1)
    fellOff &= simulate_water_drop(WORLD_SIZE // 2, WORLD_SIZE // 2 + 1, WORLD_HEIGHT - 1)
    fellOff &= simulate_water_drop(WORLD_SIZE // 2 + 1, WORLD_SIZE // 2 + 1, WORLD_HEIGHT - 1)
    totalDropCount += 4

    if totalDropCount % 1000 == 0:
      print("Rain simulation final run-out ({subpass}) {totalDropCount} drops have fallen".format(
        subpass=subPass, totalDropCount=totalDropCount))
      assert totalDropCount < WORLD_SIZE * WORLD_SIZE * WORLD_HEIGHT + 500, \
      "If this triggers, there's a bug making water disappear without recording it as escaping."

    if lastSettledDrop and lastSettledDrop % 100 == 0:
      print("Rain simulation final run-out ({subpass}) {lastSettledDrop} drops have escaped".format(
        subpass=subPass, lastSettledDrop=lastSettledDrop))

    if fellOff:
      lastSettledDrop += 1
    else:
      lastSettledDrop = 0

  print("Rain simulation final run-out ({subpass}) took {time}".format(subpass=subPass,
                                                                       time=time.time() -
                                                                       startTime))

  # Helper: find connected components of water in 3D
  def find_water_bodies():
    visited = np.zeros_like(world, dtype=bool)
    bodies = []

    for x in range(WORLD_SIZE):
      for y in range(WORLD_SIZE):
        for z in range(WORLD_HEIGHT):
          if world[x, y, z] == 2 and not visited[x, y, z]:
            # BFS to find connected water body
            body = []
            queue = deque([(x, y, z)])
            visited[x, y, z] = True
            while queue:
              cx, cy, cz = queue.popleft()
              body.append((cx, cy, cz))
              for dx, dy, dz in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1),
                                 (0, 0, -1)]:
                nx, ny, nz = cx + dx, cy + dy, cz + dz
                if 0 <= nx < WORLD_SIZE and 0 <= ny < WORLD_SIZE and 0 <= nz < WORLD_HEIGHT:
                  if world[nx, ny, nz] == 2 and not visited[nx, ny, nz]:
                    visited[nx, ny, nz] = True
                    queue.append((nx, ny, nz))
            bodies.append(body)
    return bodies

  # Helper: get surface area (unique x,y positions) of a water body
  def surface_area(body):
    return len(set((x, y) for x, y, z in body))

  # Helper: check if body contains at least one 2x2 contiguous surface block
  def is_at_least_2x2(body):
    # Get all (x,y) positions in the body (surface projection)
    surface = set((x, y) for x, y, z in body)
    # Check if any 2x2 block exists
    for (x, y) in surface:
      if (x + 1, y) in surface and (x, y + 1) in surface and (x + 1, y + 1) in surface:
        return True
    return False

  # Helper: check if water voxel is underground (has rock above it at some level)
  def is_underground(x, y, z):
    for zz in range(z + 1, WORLD_HEIGHT):
      if world[x, y, zz] == 1:  # Rock above
        return True
    return False

  out = None

  if subPass == 0:
    # Search for a lake of at least 36 voxels in surface area
    bodies = find_water_bodies()
    max_surface = max((surface_area(b) for b in bodies), default=0)
    if max_surface >= 36:
      out = 1, f"Lake with surface area {max_surface} >= 36"
    else:
      out = min(1, max_surface / 36), f"Largest lake surface area: {max_surface}/36"

  elif subPass == 1:
    # Search for 3 unconnected bodies of water each at least 2x2
    bodies = find_water_bodies()
    qualifying = [b for b in bodies if is_at_least_2x2(b)]
    count = len(qualifying)
    if count >= 3:
      out = 1, f"Found {count} bodies of water each at least 2x2"
    else:
      out = min(1, count / 3), f"Found {count}/3 qualifying water bodies"

  elif subPass == 2:
    # Search for a lake of at least 2 voxels at z > 5
    high_water = np.sum((world[:, :, 6:] == 2))
    if high_water >= 2:
      out = 1, f"Found {high_water} water voxels at z > 5"
    else:
      out = min(1, high_water / 2), f"Found {high_water}/2 high water voxels"

  elif subPass == 3:
    # Search for underground lake of at least 10 voxels, NO water visible from above
    underground_count = 0
    visible_count = 0
    for x in range(WORLD_SIZE):
      for y in range(WORLD_SIZE):
        for z in range(WORLD_HEIGHT):
          if world[x, y, z] == 2:
            if is_underground(x, y, z):
              underground_count += 1
            else:
              visible_count += 1
    if visible_count > 0:
      # Penalty: visible water means failure
      out = 0, f"Found {visible_count} visible water voxels - must have NO visible water"
    elif underground_count >= 10:
      out = 1, f"Found {underground_count} underground water voxels, none visible"
    else:
      out = min(1, underground_count / 10), f"Found {underground_count}/10 underground water voxels"

  elif subPass == 4:
    # Search for 3 separate lakes (bodies) on 3 different z levels
    bodies = find_water_bodies()
    # For each body, find its primary z level (mode or lowest)
    body_z_levels = []
    for body in bodies:
      z_counts = {}
      for x, y, z in body:
        z_counts[z] = z_counts.get(z, 0) + 1
      # Primary z level is the one with most voxels
      primary_z = max(z_counts.keys(), key=lambda z: z_counts[z])
      body_z_levels.append(primary_z)
    # Count how many distinct z levels have at least one body
    unique_z_with_bodies = len(set(body_z_levels))
    # We need 3 separate bodies AND they must be on 3 different z levels
    if len(bodies) >= 3 and unique_z_with_bodies >= 3:
      out = 1, f"Found {len(bodies)} bodies on {unique_z_with_bodies} different z levels"
    elif len(bodies) < 3:
      out = len(bodies) / 3, f"Found {len(bodies)}/3 separate water bodies"
    else:
      out = min(1, unique_z_with_bodies /
                3), f"Found {len(bodies)} bodies but only on {unique_z_with_bodies}/3 z levels"

  elif subPass == 5:
    # Search for a lake at least 6 voxels deep
    max_depth = 0
    for x in range(WORLD_SIZE):
      for y in range(WORLD_SIZE):
        # Find continuous water column depth at this x,y
        depth = 0
        for z in range(WORLD_HEIGHT):
          if world[x, y, z] == 2:
            depth += 1
            max_depth = max(max_depth, depth)
          else:
            depth = 0
    if max_depth >= 6:
      out = 1, f"Found water column {max_depth} deep"
    else:
      out = min(1, max_depth / 6), f"Deepest water column: {max_depth}/6"

  elif subPass == 6:
    # Search for 2 lakes, each over 200 voxels in volume
    bodies = find_water_bodies()
    qualifying = [b for b in bodies if len(b) >= 200]
    count = len(qualifying)
    if count >= 2:
      out = 1, f"Found {count} bodies of water each >= 200 voxels"
    else:
      out = min(1, count / 2), f"Found {count}/2 qualifying water bodies"

  elif subPass == 7:
    # Ring-shaped lake: water must surround a dry center of at least 3x3
    bodies = find_water_bodies()
    for body in bodies:
      # Get the surface projection (x,y positions)
      surface = set((x, y) for x, y, z in body)
      if len(surface) < 12:  # Need at least 12 surface cells to surround 3x3
        continue
      # Find bounding box of the water surface
      xs = [x for x, y in surface]
      ys = [y for x, y in surface]
      min_x, max_x = min(xs), max(xs)
      min_y, max_y = min(ys), max(ys)
      # Check for a 3x3 dry center completely surrounded by this water body
      for cx in range(min_x + 1, max_x - 1):
        for cy in range(min_y + 1, max_y - 1):
          # Check if 3x3 block at (cx,cy) is dry
          dry_center = True
          for dx in range(3):
            for dy in range(3):
              if (cx + dx, cy + dy) in surface:
                dry_center = False
                break
            if not dry_center:
              break
          if not dry_center:
            continue
          # Check if water surrounds the 3x3 on all 4 sides
          surrounded = True
          # Check top edge (y = cy - 1)
          for dx in range(3):
            if (cx + dx, cy - 1) not in surface:
              surrounded = False
              break
          # Check bottom edge (y = cy + 3)
          if surrounded:
            for dx in range(3):
              if (cx + dx, cy + 3) not in surface:
                surrounded = False
                break
          # Check left edge (x = cx - 1)
          if surrounded:
            for dy in range(3):
              if (cx - 1, cy + dy) not in surface:
                surrounded = False
                break
          # Check right edge (x = cx + 3)
          if surrounded:
            for dy in range(3):
              if (cx + 3, cy + dy) not in surface:
                surrounded = False
                break
          if surrounded:
            out = 1, f"Found ring-shaped lake surrounding dry 3x3 at ({cx},{cy})"
    if not out: out = 0, "No ring-shaped lake found surrounding a dry 3x3 center"

  elif subPass == 8:
    # Water at z=3 AND z=6, but NO water at z=4 or z=5
    has_z3 = np.any(world[:, :, 3] == 2)
    has_z6 = np.any(world[:, :, 6] == 2)
    has_z4 = np.any(world[:, :, 4] == 2)
    has_z5 = np.any(world[:, :, 5] == 2)
    score = (1 if has_z3 else 0) + (1 if has_z6 else 0)
    if has_z4 or has_z5:
      out = 0, f"Water found at forbidden z levels (z=4: {has_z4}, z=5: {has_z5})"
    elif score == 2:
      out = 1, "Water at z=3 and z=6, none at z=4 or z=5"
    else:
      out = score / 2, f"Water at z=3: {has_z3}, z=6: {has_z6}"

  elif subPass == 9:
    # EXACTLY 100 voxels of water total
    total_water = np.sum(world == 2)
    if total_water == 100:
      out = 1, "Exactly 100 water voxels"
    # Partial credit based on how close
    error = abs(total_water - 100)
    score = max(0, 1 - error / 100)
    if score == 1:
      out = 1, f"Found {total_water} water voxels (need exactly 100)"
    else:
      out = score, f"Found {total_water} water voxels (need exactly 100)"

  elif subPass == 10:
    # 4 separate underground lakes, each at least 5 voxels, none visible from above
    bodies = find_water_bodies()
    underground_bodies = []
    visible_water = False
    for body in bodies:
      all_underground = True
      for x, y, z in body:
        if not is_underground(x, y, z):
          all_underground = False
          visible_water = True
          break
      if all_underground and len(body) >= 5:
        underground_bodies.append(body)
    count = len(underground_bodies)
    if visible_water:
      out = 0, "Some water is visible from above - all water must be underground"
    elif count >= 4:
      out = 1, f"Found {count} underground lakes each >= 5 voxels"
    elif count < 4:
      out = count / 4, f"Found {count}/4 qualifying underground lakes"
    else:
      out = min(1, count / 4), f"Found {count}/4 qualifying underground lakes"

  import numpy as np
  import hashlib

  WORLD_SIZE = getWorldSize(subPass)
  WORLD_HEIGHT = 8

  scad_content = "union() {\n"

  for x in range(WORLD_SIZE):
    for y in range(WORLD_SIZE):
      for z in range(WORLD_HEIGHT):
        if world[x, y, z] == 2:
          scad_content += f'    translate([{x}, {y}, {z}]) color("blue") cube([0.9, 0.9, 0.9],center=true);\n'
        elif world[x, y, z] == 1:
          if x == 0 and y == 0:
            scad_content += f'    translate([{x}, {y}, {z}]) color("white") cube([1, 1, 1],center=true);\n'
          elif RockFell and (x, y) in RockFell:
            scad_content += f'    translate([{x}, {y}, {z}]) color("red") cube([1, 1, 1],center=true);\n'
          else:
            scad_content += f'    translate([{x}, {y}, {z}]) color("brown") cube([1, 1, 1],center=true);\n'

  scad_content += "}\n"

  base_name = f"23_Visualization_{aiEngineName}_{subPass}"

  center_x = WORLD_SIZE / 2
  center_y = WORLD_SIZE / 2
  center_z = WORLD_HEIGHT / 2

  def build_camera_arg(eye_x, eye_y, eye_z, target_x=None, target_y=None, target_z=None):
    if target_x is None:
      target_x = center_x
    if target_y is None:
      target_y = center_y
    if target_z is None:
      target_z = center_z
    return (f"--camera={eye_x:.3f},{eye_y:.3f},{eye_z:.3f},"
            f"{target_x:.3f},{target_y:.3f},{target_z:.3f}")

  offset = WORLD_SIZE * 1.5
  offset_close = WORLD_SIZE * 0.9
  side_height = WORLD_SIZE * 1.8

  views = [
    ("northeast", build_camera_arg(center_x + offset * 0.7, center_y - offset * 0.7, side_height)),
    ("above", build_camera_arg(center_x, center_y, WORLD_SIZE * 4)),
    ("north", build_camera_arg(center_x, center_y - offset, side_height)),
    ("south", build_camera_arg(center_x, center_y + offset, side_height)),
    ("west", build_camera_arg(center_x - offset, center_y, side_height)),
    ("east", build_camera_arg(center_x + offset, center_y, side_height)),
    ("northwest", build_camera_arg(center_x - offset * 0.7, center_y - offset * 0.7, side_height)),
    ("southeast", build_camera_arg(center_x + offset * 0.7, center_y + offset * 0.7, side_height)),
    ("southwest", build_camera_arg(center_x - offset * 0.7, center_y + offset * 0.7, side_height)),
  ]

  image_paths = []
  for view_name, camera_arg in views:
    filename = f"{base_name}_{view_name}.png"
    output_path = result_path(filename, aiEngineName)
    vc.render_scadText_to_png(scad_content, output_path, camera_arg, ["--no-autocenter"])
    image_paths.append(output_path)

  print(f"Saved {len(image_paths)} visualization views for subpass {subPass}")

  viewer_id = f"voxel-viewer-{hashlib.md5(base_name.encode()).hexdigest()}"
  image_tags = []
  for idx, path in enumerate(image_paths):
    image_tags.append(f'<img src="{report_relpath(path, aiEngineName)}" class="voxel-view view-{idx}" '
                      f'style="max-width: 100%;">')

  radio_name = f"{viewer_id}-view"
  radio_ids = [f"{viewer_id}-view-{idx}" for idx in range(len(image_paths))]
  inputs = []
  for idx, radio_id in enumerate(radio_ids):
    checked = " checked" if idx == 0 else ""
    inputs.append(f'<input type="radio" name="{radio_name}" id="{radio_id}"{checked}>')

  labels = []
  for idx in range(len(radio_ids)):
    prev_idx = (idx - 1) % len(radio_ids)
    next_idx = (idx + 1) % len(radio_ids)
    labels.append(
      f'<label class="voxel-prev prev-{idx}" for="{radio_ids[prev_idx]}">&#8592;</label>')
    labels.append(
      f'<label class="voxel-next next-{idx}" for="{radio_ids[next_idx]}">&#8594;</label>')

  style_lines = [
    f'#{viewer_id} {{ display:flex; align-items:center; gap:8px; }}',
    f'#{viewer_id} input[type="radio"] {{ display:none; }}',
    f'#{viewer_id} .voxel-frame {{ flex:1; text-align:center; order:1; }}',
    f'#{viewer_id} .voxel-prev {{ order:0; cursor:pointer; font-size:18px; display:none; }}',
    f'#{viewer_id} .voxel-next {{ order:2; cursor:pointer; font-size:18px; display:none; }}',
    f'#{viewer_id} .voxel-view {{ display:none; max-width:100%; }}',
  ]
  for idx, radio_id in enumerate(radio_ids):
    style_lines.append(f'#{radio_id}:checked ~ .voxel-frame .view-{idx} {{ display:block; }}')
    style_lines.append(f'#{radio_id}:checked ~ .prev-{idx} {{ display:inline-flex; }}')
    style_lines.append(f'#{radio_id}:checked ~ .next-{idx} {{ display:inline-flex; }}')

  html = (f'White indicates 0,0.<br><div id="{viewer_id}" class="voxel-viewer">'
          f'<style>{" ".join(style_lines)}</style>'
          f'{"".join(inputs)}'
          f'{"".join(labels)}'
          f'<div class="voxel-frame">'
          f'{"".join(image_tags)}'
          f'</div>'
          f'</div>')

  if RockFell:
    html = "This world was unstable! Floating rocks fell to the ground! (marked in red)<br>" + html

  return out[0], out[1], html


if __name__ == "__main__":
  gradeAnswer({"voxels": [{"xyz": [4, 4, 2], "material": "Air"}]}, 6, "Test")

  resultToNiceReport("", 0, "Test")

highLevelSummary = """
Can the LLM build a voxel world which manages water in specific ways?
<br><br>
This requires either an intuition on how water flows, or the ability to
create fluid dynamic simulations.
<br><br>
LLMs seem to get the details right but forget the big picture.<br><br>
Its quite funny watching them carve elaborate funnels and then high walls around a 
lake system but leave one voxel open and it all flows out when it rains.
"""
