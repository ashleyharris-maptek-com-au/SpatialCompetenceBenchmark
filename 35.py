import math
import random
import os

title = "Gear Train Reasoning - predict rotation directions and speeds"

prompt = """
You are analyzing a gear train system with special mechanical components.

GEAR_SYSTEM

The input gear (gear 1) is rotating CLOCKWISE at INPUT_SPEED RPM.

RULES_SECTION

For each gear in the system, determine:
1. Its rotation direction (clockwise, counterclockwise, or stopped)
2. Its rotation speed in RPM (use 0 if stopped, use average RPM for variable-speed gears)
"""

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "gears": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "gearNumber": {
            "type": "integer"
          },
          "direction": {
            "type": "string",
            "enum": ["clockwise", "counterclockwise", "stopped"]
          },
          "rpm": {
            "type": "number"
          },
        },
        "propertyOrdering": ["gearNumber", "direction", "rpm"],
        "required": ["gearNumber", "direction", "rpm"],
        "additionalProperties": False
      }
    }
  },
  "propertyOrdering": ["reasoning", "gears"],
  "required": ["reasoning", "gears"],
  "additionalProperties": False
}

# =============================================================================
# SOLVER FOR COMPLEX GEAR TRAINS WITH SPECIAL COMPONENTS
# =============================================================================


def solve_gear_train(gears_def, input_speed, complications=None):
  """
    Solve a gear train with optional complications.
    
    gears_def: list of dicts with:
        - 'teeth': number of teeth
        - 'meshes_with': list of gear numbers this meshes with
        - 'same_shaft_as': gear number on same shaft (optional)
        - 'chain_to': gear number connected by chain (same direction, optional)
        
    complications: dict with special behaviors:
        - 'clutches': {gear_num: 'disengaged'} - gear is disconnected
        - 'ratchets': {gear_num: 'forward'|'reverse'} - only allows one direction
        - 'shatter_threshold': {gear_num: max_rpm} - gear shatters above threshold
        - 'ellipse_gears': {gear_num: (min_ratio, max_ratio)} - variable ratio
        - 'springs': {gear_num: 'wound'|'unwound'} - stores/releases energy
        
    Returns list of expected results.
    """
  complications = complications or {}
  n = len(gears_def)
  rpms = [None] * n
  directions = [None] * n
  stopped = [False] * n
  notes = [""] * n

  # Handle clutches - mark disconnected gears
  clutches = complications.get('clutches', {})
  for gear_num, state in clutches.items():
    if state == 'disengaged':
      idx = gear_num - 1
      stopped[idx] = True
      rpms[idx] = 0
      directions[idx] = "stopped"
      notes[idx] = "Clutch disengaged"

  # Gear 1 is always input (unless clutched)
  if not stopped[0]:
    rpms[0] = input_speed
    directions[0] = "clockwise"

  # Check if input gear shatters
  shatter = complications.get('shatter_threshold', {})
  if 1 in shatter and input_speed > shatter[1]:
    stopped[0] = True
    rpms[0] = 0
    directions[0] = "stopped"
    notes[0] = f"Shattered (exceeded {shatter[1]} RPM)"

  # Iteratively solve until all gears are determined
  changed = True
  iterations = 0
  while changed and iterations < 200:
    changed = False
    iterations += 1

    for i, gear in enumerate(gears_def):
      if stopped[i]:
        continue

      if rpms[i] is not None:
        # This gear is solved, propagate to connected gears

        # Same shaft gears
        if 'same_shaft_as' in gear:
          j = gear['same_shaft_as'] - 1
          if not stopped[j] and rpms[j] is None:
            rpms[j] = rpms[i]
            directions[j] = directions[i]
            changed = True

        # Chain connections (same direction, same speed if same teeth)
        if 'chain_to' in gear:
          j = gear['chain_to'] - 1
          if not stopped[j] and rpms[j] is None:
            # Chain preserves direction, ratio based on sprocket teeth
            ratio = gears_def[i]['teeth'] / gears_def[j]['teeth']
            rpms[j] = rpms[i] * ratio
            directions[j] = directions[i]  # Same direction!
            notes[j] = "Chain drive"
            changed = True

        # Meshing gears
        for j in gear.get('meshes_with', []):
          j_idx = j - 1
          if stopped[j_idx] or rpms[j_idx] is not None:
            continue

          # Speed ratio = teeth_i / teeth_j
          new_rpm = rpms[i] * gears_def[i]['teeth'] / gears_def[j_idx]['teeth']
          new_dir = "counterclockwise" if directions[i] == "clockwise" else "clockwise"

          # Check ellipse gear variation
          ellipse = complications.get('ellipse_gears', {})
          if j in ellipse:
            min_r, max_r = ellipse[j]
            # Report average RPM but note the variation
            avg_ratio = (min_r + max_r) / 2
            new_rpm = rpms[i] * gears_def[i]['teeth'] / gears_def[j_idx]['teeth'] * avg_ratio
            notes[j_idx] = f"Ellipse gear: RPM varies {min_r:.2f}x to {max_r:.2f}x"

          # Check ratchet
          ratchets = complications.get('ratchets', {})
          if j in ratchets:
            allowed = ratchets[j]
            if (allowed == 'forward' and new_dir == 'counterclockwise') or \
               (allowed == 'reverse' and new_dir == 'clockwise'):
              stopped[j_idx] = True
              rpms[j_idx] = 0
              directions[j_idx] = "stopped"
              notes[j_idx] = f"Ratchet blocks {new_dir} rotation"
              changed = True
              continue

          # Check shatter threshold
          if j in shatter and new_rpm > shatter[j]:
            stopped[j_idx] = True
            rpms[j_idx] = 0
            directions[j_idx] = "stopped"
            notes[j_idx] = f"Shattered (exceeded {shatter[j]} RPM)"
            changed = True
            continue

          rpms[j_idx] = new_rpm
          directions[j_idx] = new_dir
          changed = True

      # Check if another gear drives this one
      if rpms[i] is None and not stopped[i]:
        for k, other in enumerate(gears_def):
          if stopped[k] or rpms[k] is None:
            continue

          if i + 1 in other.get('meshes_with', []):
            new_rpm = rpms[k] * other['teeth'] / gear['teeth']
            new_dir = "counterclockwise" if directions[k] == "clockwise" else "clockwise"

            # Check ratchet
            ratchets = complications.get('ratchets', {})
            if i + 1 in ratchets:
              allowed = ratchets[i + 1]
              if (allowed == 'forward' and new_dir == 'counterclockwise') or \
                 (allowed == 'reverse' and new_dir == 'clockwise'):
                stopped[i] = True
                rpms[i] = 0
                directions[i] = "stopped"
                notes[i] = f"Ratchet blocks {new_dir} rotation"
                changed = True
                continue

            # Check shatter
            if i + 1 in shatter and new_rpm > shatter[i + 1]:
              stopped[i] = True
              rpms[i] = 0
              directions[i] = "stopped"
              notes[i] = f"Shattered (exceeded {shatter[i + 1]} RPM)"
              changed = True
              continue

            rpms[i] = new_rpm
            directions[i] = new_dir
            changed = True
            break

          if 'same_shaft_as' in other and other['same_shaft_as'] == i + 1:
            rpms[i] = rpms[k]
            directions[i] = directions[k]
            changed = True
            break

          if 'chain_to' in other and other['chain_to'] == i + 1:
            ratio = other['teeth'] / gear['teeth']
            rpms[i] = rpms[k] * ratio
            directions[i] = directions[k]
            notes[i] = "Chain drive"
            changed = True
            break

  # Mark any unsolved gears as stopped (disconnected from drive)
  for i in range(n):
    if rpms[i] is None:
      rpms[i] = 0
      directions[i] = "stopped"
      notes[i] = notes[i] or "Disconnected from drive train"

  result = []
  for i in range(n):
    entry = {
      "gearNumber": i + 1,
      "direction": directions[i],
      "rpm": round(rpms[i], 6) if rpms[i] else 0
    }
    if notes[i]:
      entry["notes"] = notes[i]
    result.append(entry)

  return result


def generate_description(gears_def, input_speed, complications=None):
  """Generate human-readable description of a gear system."""
  complications = complications or {}
  lines = []

  for i, gear in enumerate(gears_def):
    gear_num = i + 1
    teeth = gear['teeth']

    parts = [f"Gear {gear_num}: {teeth} teeth"]

    if gear_num == 1:
      parts.append("(input gear)")

    if gear.get('meshes_with'):
      mesh_list = gear['meshes_with']
      if len(mesh_list) == 1:
        parts.append(f"meshes with Gear {mesh_list[0]}")
      else:
        parts.append(f"meshes with Gears {', '.join(map(str, mesh_list))}")

    if 'same_shaft_as' in gear:
      parts.append(f"SAME SHAFT as Gear {gear['same_shaft_as']}")

    if 'chain_to' in gear:
      parts.append(f"CHAIN DRIVE to Gear {gear['chain_to']}")

    # Add complication notes
    if gear_num in complications.get('clutches', {}):
      state = complications['clutches'][gear_num]
      parts.append(f"[CLUTCH: {state}]")

    if gear_num in complications.get('ratchets', {}):
      direction = complications['ratchets'][gear_num]
      parts.append(f"[RATCHET: only allows {direction} rotation]")

    if gear_num in complications.get('shatter_threshold', {}):
      threshold = complications['shatter_threshold'][gear_num]
      parts.append(f"[FRAGILE: shatters above {threshold} RPM]")

    if gear_num in complications.get('ellipse_gears', {}):
      min_r, max_r = complications['ellipse_gears'][gear_num]
      parts.append(f"[ELLIPSE: ratio varies {min_r:.2f}x to {max_r:.2f}x per revolution]")

    lines.append(", ".join(parts))

  return "\n".join(lines)


def generate_rules_section(complications):
  """Generate rules explanation for complications."""
  if not complications:
    return """
Standard gear rules apply:
- Meshing gears rotate in opposite directions
- Speed ratio = driving gear teeth / driven gear teeth
- Gears on the same shaft rotate together (same speed and direction)
"""

  rules = ["Special component rules for this system:"]

  if 'clutches' in complications:
    rules.append(
      "- CLUTCH: When disengaged, the gear and everything downstream is disconnected (0 RPM)")

  if 'ratchets' in complications:
    rules.append(
      "- RATCHET: Only allows rotation in one direction; blocks opposite direction (gear stops)")

  if 'shatter_threshold' in complications:
    rules.append("- FRAGILE GEAR: Shatters if RPM exceeds threshold; gear and downstream stop")

  if 'ellipse_gears' in complications:
    rules.append("- ELLIPSE GEAR: Non-circular gear with variable ratio; report average RPM")

  if 'chain_to' in str(complications) or any('chain_to' in g
                                             for g in complications.get('gears_def', [])):
    rules.append(
      "- CHAIN DRIVE: Unlike meshing gears, chain-connected gears rotate in the SAME direction")

  rules.append("")
  rules.append("Standard rules still apply:")
  rules.append("- Meshing gears rotate in opposite directions")
  rules.append("- Speed ratio = driving gear teeth / driven gear teeth")
  rules.append("- Gears on the same shaft rotate together")

  return "\n".join(rules)


# =============================================================================
# ALGORITHMIC GEAR SYSTEM GENERATORS
# =============================================================================


def generate_massive_linear_chain(num_gears, seed=42):
  """Generate a long linear chain of gears with varying teeth."""
  rng = random.Random(seed)
  primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

  gears = []
  for i in range(num_gears):
    teeth = rng.choice(primes)
    gear = {"teeth": teeth, "meshes_with": []}
    if i > 0:
      gear["meshes_with"].append(i)  # Mesh with previous gear
    if i < num_gears - 1:
      gear["meshes_with"].append(i + 2)  # Mesh with next gear
    gears.append(gear)

  return gears


def generate_compound_reduction(num_stages, seed=42):
  """Generate a compound gear train with multiple reduction stages."""
  rng = random.Random(seed)
  small_teeth = [11, 13, 15, 17, 19, 21, 23]
  large_teeth = [41, 43, 47, 51, 53, 57, 59, 61, 67, 71]

  gears = []
  gear_num = 1

  for stage in range(num_stages):
    # Small driving gear
    small = rng.choice(small_teeth)
    large = rng.choice(large_teeth)

    if stage == 0:
      # First gear is input
      gears.append({"teeth": small, "meshes_with": [2]})
    else:
      # Small gear on same shaft as previous large gear
      gears.append({"teeth": small, "meshes_with": [gear_num + 1], "same_shaft_as": gear_num - 1})

    gear_num += 1

    # Large driven gear
    if stage < num_stages - 1:
      gears.append({"teeth": large, "meshes_with": [gear_num - 1], "same_shaft_as": gear_num + 1})
    else:
      gears.append({"teeth": large, "meshes_with": [gear_num - 1]})

    gear_num += 1

  return gears


def generate_branching_system(num_branches, depth, seed=42):
  """Generate a system where power splits into multiple branches."""
  rng = random.Random(seed)
  teeth_options = [20, 25, 30, 35, 40, 45, 50, 60, 70, 80]

  gears = []
  gear_num = 1

  # Input gear meshes with all first-level branches
  branch_starts = list(range(2, 2 + num_branches))
  gears.append({"teeth": rng.choice(teeth_options), "meshes_with": branch_starts})
  gear_num += 1

  # Create each branch
  for branch in range(num_branches):
    branch_gears = []
    for d in range(depth):
      teeth = rng.choice(teeth_options)
      gear = {"teeth": teeth, "meshes_with": []}

      if d == 0:
        gear["meshes_with"].append(1)  # Connect to input
      else:
        gear["meshes_with"].append(gear_num - 1)  # Connect to previous in branch

      if d < depth - 1:
        gear["meshes_with"].append(gear_num + 1)  # Connect to next in branch

      gears.append(gear)
      gear_num += 1

  return gears


def generate_multi_shaft_cluster(num_shafts, gears_per_shaft, seed=42):
  """Generate a system with multiple gears on each shaft."""
  rng = random.Random(seed)
  teeth_options = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

  gears = []
  gear_num = 1
  shaft_starts = []

  for shaft in range(num_shafts):
    shaft_start = gear_num
    shaft_starts.append(shaft_start)

    for g in range(gears_per_shaft):
      teeth = rng.choice(teeth_options)
      gear = {"teeth": teeth, "meshes_with": []}

      # Same shaft connection
      if g > 0:
        gear["same_shaft_as"] = shaft_start

      gears.append(gear)
      gear_num += 1

  # Now connect shafts via meshing
  for shaft in range(num_shafts - 1):
    # Connect one gear from this shaft to one gear on next shaft
    from_gear = shaft_starts[shaft] + rng.randint(0, gears_per_shaft - 1)
    to_gear = shaft_starts[shaft + 1] + rng.randint(0, gears_per_shaft - 1)

    gears[from_gear - 1]["meshes_with"].append(to_gear)
    gears[to_gear - 1]["meshes_with"].append(from_gear)

  return gears


def generate_with_chains(num_gears, num_chains, seed=42):
  """Generate a gear system that includes chain drives."""
  rng = random.Random(seed)
  teeth_options = [15, 18, 20, 22, 24, 27, 30, 33, 36, 40]

  gears = []

  # Create base linear chain
  for i in range(num_gears):
    teeth = rng.choice(teeth_options)
    gear = {"teeth": teeth, "meshes_with": []}

    if i > 0 and i not in [c[1] - 1 for c in []]:  # Will be filled
      gear["meshes_with"].append(i)
    if i < num_gears - 1:
      gear["meshes_with"].append(i + 2)

    gears.append(gear)

  # Add chain connections (replacing some mesh connections)
  chain_positions = rng.sample(range(1, num_gears - 1), min(num_chains, num_gears - 2))
  for pos in chain_positions:
    # Remove mesh connection, add chain
    if pos + 1 in gears[pos - 1].get("meshes_with", []):
      gears[pos - 1]["meshes_with"].remove(pos + 1)
    gears[pos - 1]["chain_to"] = pos + 1

    # Remove reverse mesh
    if pos in gears[pos].get("meshes_with", []):
      gears[pos]["meshes_with"].remove(pos)

  return gears


# =============================================================================
# GEAR SYSTEM DEFINITIONS
# =============================================================================

gear_systems = []

# Test 0: 50-gear linear chain
_seed = 1001
_gears_50 = generate_massive_linear_chain(50, seed=_seed)
gear_systems.append({
  "name": "50-gear linear chain",
  "description": generate_description(_gears_50, 1000),
  "input_speed": 1000,
  "gears_def": _gears_50,
  "expected": solve_gear_train(_gears_50, 1000)
})

# Test 1: 10-stage compound reduction (20 gears)
_seed = 1002
_gears_compound = generate_compound_reduction(10, seed=_seed)
gear_systems.append({
  "name": "10-stage compound reduction",
  "description": generate_description(_gears_compound, 100000),
  "input_speed": 100000,
  "gears_def": _gears_compound,
  "expected": solve_gear_train(_gears_compound, 100000)
})

# Test 2: 5-branch system, depth 4 (21 gears)
_seed = 1003
_gears_branch = generate_branching_system(5, 4, seed=_seed)
gear_systems.append({
  "name": "5-way branching system",
  "description": generate_description(_gears_branch, 3000),
  "input_speed": 3000,
  "gears_def": _gears_branch,
  "expected": solve_gear_train(_gears_branch, 3000)
})

# Test 3: 8 shafts with 5 gears each (40 gears)
_seed = 1004
_gears_cluster = generate_multi_shaft_cluster(8, 5, seed=_seed)
gear_systems.append({
  "name": "8-shaft cluster (40 gears)",
  "description": generate_description(_gears_cluster, 2400),
  "input_speed": 2400,
  "gears_def": _gears_cluster,
  "expected": solve_gear_train(_gears_cluster, 2400)
})

# Test 4: Chain drive system (30 gears with 5 chains)
_seed = 1005
_gears_chain = generate_with_chains(30, 5, seed=_seed)
_complications_chain = {}  # Chains are in the gear def
gear_systems.append({
  "name": "30-gear chain drive system",
  "description": generate_description(_gears_chain, 1500) +
  "\n\nNote: Chain drives preserve rotation direction (unlike meshing gears).",
  "input_speed": 1500,
  "gears_def": _gears_chain,
  "complications": _complications_chain,
  "expected": solve_gear_train(_gears_chain, 1500, _complications_chain)
})

# Test 5: System with disengaged clutch
_seed = 1006
_gears_clutch = generate_massive_linear_chain(25, seed=_seed)
_complications_clutch = {"clutches": {10: "disengaged"}}
gear_systems.append({
  "name": "25-gear system with clutch",
  "description": generate_description(_gears_clutch, 500, _complications_clutch),
  "input_speed": 500,
  "gears_def": _gears_clutch,
  "complications": _complications_clutch,
  "expected": solve_gear_train(_gears_clutch, 500, _complications_clutch)
})

# Test 6: System with ratchets
_seed = 1007
_gears_ratchet = generate_massive_linear_chain(20, seed=_seed)
_complications_ratchet = {"ratchets": {8: "forward", 15: "reverse"}}
gear_systems.append({
  "name": "20-gear system with ratchets",
  "description": generate_description(_gears_ratchet, 800, _complications_ratchet),
  "input_speed": 800,
  "gears_def": _gears_ratchet,
  "complications": _complications_ratchet,
  "expected": solve_gear_train(_gears_ratchet, 800, _complications_ratchet)
})

# Test 7: System with fragile gears that shatter
_seed = 1008
_gears_shatter = generate_compound_reduction(8, seed=_seed)
_complications_shatter = {"shatter_threshold": {6: 5000, 12: 2000}}
gear_systems.append({
  "name":
  "16-gear system with fragile components",
  "description":
  generate_description(_gears_shatter, 50000, _complications_shatter),
  "input_speed":
  50000,
  "gears_def":
  _gears_shatter,
  "complications":
  _complications_shatter,
  "expected":
  solve_gear_train(_gears_shatter, 50000, _complications_shatter)
})

# Test 8: 100-gear monster chain
_seed = 1009
_gears_100 = generate_massive_linear_chain(100, seed=_seed)
gear_systems.append({
  "name": "100-gear linear chain",
  "description": generate_description(_gears_100, 10000),
  "input_speed": 10000,
  "gears_def": _gears_100,
  "expected": solve_gear_train(_gears_100, 10000)
})

# Test 9: 12 shafts with 8 gears each (96 gears)
_seed = 1010
_gears_mega_cluster = generate_multi_shaft_cluster(12, 8, seed=_seed)
gear_systems.append({
  "name": "12-shaft mega cluster (96 gears)",
  "description": generate_description(_gears_mega_cluster, 7200),
  "input_speed": 7200,
  "gears_def": _gears_mega_cluster,
  "expected": solve_gear_train(_gears_mega_cluster, 7200)
})

# Test 10: Complex system with multiple complications
_seed = 1011
_gears_complex = generate_branching_system(4, 6, seed=_seed)
_complications_complex = {
  "clutches": {
    8: "disengaged"
  },
  "ratchets": {
    12: "forward"
  },
  "shatter_threshold": {
    20: 1000
  }
}
gear_systems.append({
  "name":
  "Complex system with multiple complications",
  "description":
  generate_description(_gears_complex, 5000, _complications_complex),
  "input_speed":
  5000,
  "gears_def":
  _gears_complex,
  "complications":
  _complications_complex,
  "expected":
  solve_gear_train(_gears_complex, 5000, _complications_complex)
})

# Test 11: 200-gear extreme chain
_seed = 1012
_gears_200 = generate_massive_linear_chain(200, seed=_seed)
gear_systems.append({
  "name": "200-gear extreme chain",
  "description": generate_description(_gears_200, 50000),
  "input_speed": 50000,
  "gears_def": _gears_200,
  "expected": solve_gear_train(_gears_200, 50000)
})

# Test 12: Picture of 4 gears:
_gears_4 = generate_massive_linear_chain(4)
gear_systems.append({
  "name": "4-gear system, but you gotta count the teeth in the images.",
  "description": generate_description(_gears_4, 1000),
  "input_speed": 1000,
  "gears_def": _gears_4,
  "expected": solve_gear_train(_gears_4, 1000)
})

subpassParamSummary = [s["name"] for s in gear_systems]
promptChangeSummary = "Progressively more complex gear trains with special components"

subpassParamSummary[12] += """<br>
      <img src="35_input_12_front.png" style="min-width:200px"><br>
      <img src="35_input_12_topFar.png" style="min-width:200px"><br>
      <img src="35_input_12_topClose.png" style="min-width:200px"><br>
      <img src="35_input_12_side.png" style="min-width:200px"><br>
"""


def prepareSubpassPrompt(index: int) -> str:
  if index >= len(gear_systems):
    raise StopIteration

  system = gear_systems[index]
  complications = system.get("complications", {})

  if index == 12:
    images = ensure_gear_images_exist(12)

    images = ["[[image:{path}]]".format(path=path) for path in images]

    p = prompt.replace("GEAR_SYSTEM", "(See attached images)" + "\n\n" + "\n".join(images))
    p = p.replace("INPUT_SPEED", "1000")
    p = p.replace("RULES_SECTION", "")
    return p

  p = prompt.replace("GEAR_SYSTEM", system["description"])
  p = p.replace("INPUT_SPEED", str(system["input_speed"]))
  p = p.replace("RULES_SECTION", generate_rules_section(complications))

  return p


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  system = gear_systems[subPass]
  expected = system["expected"]

  if not isinstance(answer, dict):
    return 0, "Answer must be a dictionary"

  gears = answer.get("gears", [])
  if not gears:
    return 0, "No gears provided"

  gear_dict = {}
  for g in gears:
    num = g.get("gearNumber", 0)
    gear_dict[num] = g

  total_score = 0
  max_score = len(expected) * 2  # 1 for direction, 1 for rpm
  errors = []
  correct_count = 0

  for exp in expected:
    num = exp["gearNumber"]
    if num not in gear_dict:
      errors.append(f"Missing gear {num}")
      continue

    g = gear_dict[num]
    gear_correct = True

    # Check direction
    actual_dir = g.get("direction", "").lower()
    expected_dir = exp["direction"]
    if actual_dir == expected_dir:
      total_score += 1
    else:
      gear_correct = False
      errors.append(f"G{num} dir: got {actual_dir}, expected {expected_dir}")

    # Check RPM (within 1% tolerance or 0.1 absolute for small values)
    expected_rpm = exp["rpm"]
    actual_rpm = g.get("rpm", 0)

    if expected_rpm == 0:
      # For stopped gears, actual must also be 0 (or very close)
      if abs(actual_rpm) <= 0.1:
        total_score += 1
      else:
        gear_correct = False
        errors.append(f"G{num} RPM: got {actual_rpm:.2f}, expected 0")
    elif abs(actual_rpm - expected_rpm) <= max(0.01 * abs(expected_rpm), 0.1):
      total_score += 1
    else:
      gear_correct = False
      errors.append(f"G{num} RPM: got {actual_rpm:.2f}, expected {expected_rpm:.2f}")

    if gear_correct:
      correct_count += 1

  # don't reward getting G1 right, it was litterally in the prompt.
  max_score -= 2
  total_score -= 2

  score = total_score / max_score if max_score > 0 else 0

  # Summary
  summary = f"{correct_count}/{len(expected)} gears correct"
  if errors:
    # Only show first 10 errors to avoid huge output
    if len(errors) > 10:
      summary += f"<br>First 10 errors: " + "<br> ".join(
        errors[:10]) + f"... and {len(errors)-10} more"
    else:
      summary += "<br>" + "<br> ".join(errors)

  score = score**2

  return score, summary


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
  gears = answer.get("gears", [])
  system = gear_systems[subPass]
  expected = system["expected"]
  gears_def = system["gears_def"]
  complications = system.get("complications", {})

  # Build comparison table - only show mismatches for large systems
  expected_dict = {e["gearNumber"]: e for e in expected}

  content = f"<b>{system['name']}</b> - {len(expected)} gears<br>"

  # Generate visualization for small/medium systems (<=30 gears)
  vis_html = ""
  if len(gears_def) <= 30:
    try:
      output_path = f"results/35_{subPass}_{aiEngineName}_gears.png"
      img_path, _ = render_gear_train_image(gears_def, complications, expected, output_path,
                                            subPass)
      if img_path:
        vis_html = f'<img src="{os.path.basename(img_path)}" style="max-width:max(400px,100%)" />'
    except Exception as e:
      vis_html = f"<i>Visualization error: {e}</i>"

  # Count correct/incorrect
  correct = 0
  wrong = []
  for exp in expected:
    num = exp["gearNumber"]
    if num in {g.get("gearNumber"): g for g in gears}:
      g = next(x for x in gears if x.get("gearNumber") == num)
      dir_ok = g.get("direction", "").lower() == exp["direction"]
      exp_rpm = exp["rpm"]
      act_rpm = g.get("rpm", 0)
      if exp_rpm == 0:
        rpm_ok = abs(act_rpm) <= 0.1
      else:
        rpm_ok = abs(act_rpm - exp_rpm) <= max(0.01 * abs(exp_rpm), 0.1)

      if dir_ok and rpm_ok:
        correct += 1
      else:
        wrong.append((num, g, exp))
    else:
      wrong.append((num, None, exp))

  content += f"<b>Score: {correct}/{len(expected)} correct</b><br>"

  has_table = False

  # For large systems with no errors, just show success message
  if len(expected) > 30 and len(wrong) == 0:
    content += "<i>All gears correct!</i>"
  elif len(expected) <= 30 or len(wrong) > 0:
    has_table = True
    # Show full table for small systems, or error table for large systems with errors
    if len(expected) <= 30:
      # Show full table for small/medium systems
      content += "<table border='1' style='font-size:10px'><tr><th>Gear</th><th>Got Dir</th><th>Exp Dir</th><th>Got RPM</th><th>Exp RPM</th></tr>"
      for exp in expected:
        num = exp["gearNumber"]
        g = next((x for x in gears if x.get("gearNumber") == num), {})
        act_dir = g.get("direction", "?")
        act_rpm = g.get("rpm", "?")
        exp_dir = exp["direction"]
        exp_rpm = exp["rpm"]

        dir_match = act_dir.lower() == exp_dir if isinstance(act_dir, str) else False
        if exp_rpm == 0:
          rpm_match = abs(act_rpm) <= 0.1 if isinstance(act_rpm, (int, float)) else False
        else:
          rpm_match = abs(act_rpm -
                          exp_rpm) <= max(0.01 *
                                          abs(exp_rpm), 0.1) if isinstance(act_rpm,
                                                                           (int, float)) else False

        dir_style = "" if dir_match else "background:#f00"
        rpm_style = "" if rpm_match else "background:#f00"

        content += f"<tr><td>{num}</td>"
        content += f"<td style='{dir_style}'>{act_dir}</td><td>{exp_dir}</td>"
        if isinstance(act_rpm, (int, float)):
          content += f"<td style='{rpm_style}'>{act_rpm:.2f}</td><td>{exp_rpm:.2f}</td></tr>"
        else:
          content += f"<td style='{rpm_style}'>{act_rpm}</td><td>{exp_rpm:.2f}</td></tr>"
      content += "</table>"
    else:
      # For large systems with errors, only show error table
      content += f"<b>Errors ({len(wrong)}):</b><br>"
      content += "<table border='1' style='font-size:10px'><tr><th>Gear</th><th>Got</th><th>Expected</th></tr>"
      for num, g, exp in wrong[:20]:  # Limit to 20 errors shown
        if g:
          content += f"<tr><td>{num}</td><td>{g.get('direction','?')} @ {g.get('rpm',0):.2f}</td><td>{exp['direction']} @ {exp['rpm']:.2f}</td></tr>"
        else:
          content += f"<tr><td>{num}</td><td>MISSING</td><td>{exp['direction']} @ {exp['rpm']:.2f}</td></tr>"
      if len(wrong) > 20:
        content += f"<tr><td colspan='3'>... and {len(wrong)-20} more errors</td></tr>"
      content += "</table>"

  content = content.replace("counterclockwise", "CCW")
  content = content.replace("clockwise", "CW")

  # TestRunner checks for "</td><td>" - if found, writes directly; if not, wraps in <td colspan='2'>
  # Include visualization if available
  if vis_html:
    return f"<td>{content}</td><td>{vis_html}</td>"
  elif has_table:
    return f"<td colspan='2'>{content}</td>"
  else:
    return content


# =============================================================================
# GEAR TRAIN VISUALIZATION
# =============================================================================

# Module (pitch) for gear sizing - radius = teeth * MODULE / 2
GEAR_MODULE = 0.1  # Adjust for visual sizing
GEAR_THICKNESS = 0.3


def calculate_gear_positions(gears_def, complications=None):
  """
  Calculate X, Y, Z positions for all gears so they mesh correctly.
  
  Returns list of dicts with 'x', 'y', 'z', 'radius' for each gear.
  """
  complications = complications or {}
  n = len(gears_def)

  positions = [None] * n
  z_levels = [0] * n  # Track Z level for each gear

  # Calculate radius for each gear based on teeth
  radii = [g['teeth'] * GEAR_MODULE / 2 for g in gears_def]

  # Build adjacency info for positioning
  # Group gears by shaft (same_shaft_as connections)
  shaft_groups = {}  # shaft_id -> list of gear indices
  gear_to_shaft = {}  # gear_index -> shaft_id

  next_shaft_id = 0
  for i, gear in enumerate(gears_def):
    if i not in gear_to_shaft:
      # Start a new shaft
      shaft_id = next_shaft_id
      next_shaft_id += 1
      shaft_groups[shaft_id] = [i]
      gear_to_shaft[i] = shaft_id

    # If this gear shares shaft with another, merge them
    if 'same_shaft_as' in gear:
      other_idx = gear['same_shaft_as'] - 1
      if other_idx in gear_to_shaft:
        # Merge into existing shaft
        shaft_id = gear_to_shaft[other_idx]
        if i not in shaft_groups[shaft_id]:
          shaft_groups[shaft_id].append(i)
        gear_to_shaft[i] = shaft_id
      else:
        # Add other to our shaft
        shaft_id = gear_to_shaft[i]
        shaft_groups[shaft_id].append(other_idx)
        gear_to_shaft[other_idx] = shaft_id

  # Place gear 1 at origin with rotation 0
  positions[0] = {'x': 0, 'y': 0, 'z': 0, 'radius': radii[0], 'rotation': 0}

  # Assign Z levels within each shaft group
  for shaft_id, gear_indices in shaft_groups.items():
    for z_offset, gear_idx in enumerate(sorted(gear_indices)):
      z_levels[gear_idx] = z_offset * GEAR_THICKNESS * 1.5

  # BFS to position all gears
  from collections import deque
  queue = deque([0])
  visited = {0}

  max_iterations = n * 10
  iteration = 0

  while queue and iteration < max_iterations:
    iteration += 1
    current = queue.popleft()
    current_pos = positions[current]
    current_gear = gears_def[current]

    # Process all connections from current gear
    connections = []

    # Meshing gears
    for mesh_target in current_gear.get('meshes_with', []):
      target_idx = mesh_target - 1
      if target_idx not in visited and 0 <= target_idx < n:
        connections.append(('mesh', target_idx))

    # Chain connections
    if 'chain_to' in current_gear:
      target_idx = current_gear['chain_to'] - 1
      if target_idx not in visited and 0 <= target_idx < n:
        connections.append(('chain', target_idx))

    # Same shaft connections
    if 'same_shaft_as' in current_gear:
      target_idx = current_gear['same_shaft_as'] - 1
      if target_idx not in visited and 0 <= target_idx < n:
        connections.append(('shaft', target_idx))

    # Also check reverse connections (other gears pointing to this one)
    for other_idx, other_gear in enumerate(gears_def):
      if other_idx in visited:
        continue
      if current + 1 in other_gear.get('meshes_with', []):
        connections.append(('mesh', other_idx))
      if other_gear.get('chain_to') == current + 1:
        connections.append(('chain', other_idx))
      if other_gear.get('same_shaft_as') == current + 1:
        connections.append(('shaft', other_idx))

    for conn_type, target_idx in connections:
      if target_idx in visited:
        continue

      if conn_type == 'shaft':
        # Same position, different Z, same rotation
        positions[target_idx] = {
          'x': current_pos['x'],
          'y': current_pos['y'],
          'z': z_levels[target_idx],
          'radius': radii[target_idx],
          'rotation': current_pos.get('rotation', 0)
        }
      elif conn_type == 'mesh':
        # Position so gears mesh (centers are r1 + r2 apart)
        distance = radii[current] + radii[target_idx]
        # Find an angle that doesn't collide with existing gears
        angle = find_free_angle(positions, current_pos, distance, radii[target_idx])
        new_x = current_pos['x'] + distance * math.cos(angle)
        new_y = current_pos['y'] + distance * math.sin(angle)
        # Find a Z level that doesn't overlap with existing gears at this XY
        new_z = find_free_z_level(positions, new_x, new_y, radii[target_idx], z_levels[target_idx])
        # Calculate rotation offset for proper tooth meshing
        current_teeth = gears_def[current]['teeth']
        target_teeth = gears_def[target_idx]['teeth']
        current_rot = current_pos.get('rotation', 0)
        # Half tooth pitch offset so teeth interleave at mesh point
        target_rot = angle + math.pi + math.pi / target_teeth
        positions[target_idx] = {
          'x': new_x,
          'y': new_y,
          'z': new_z,
          'radius': radii[target_idx],
          'rotation': target_rot
        }
      elif conn_type == 'chain':
        # Chain - place at a distance (chain length), same Z plane
        distance = radii[current] + radii[target_idx] + 1.0  # Extra space for chain
        angle = find_free_angle(positions, current_pos, distance, radii[target_idx])
        new_x = current_pos['x'] + distance * math.cos(angle)
        new_y = current_pos['y'] + distance * math.sin(angle)
        # Find a Z level that doesn't overlap with existing gears at this XY
        new_z = find_free_z_level(positions, new_x, new_y, radii[target_idx], z_levels[target_idx])
        positions[target_idx] = {
          'x': new_x,
          'y': new_y,
          'z': new_z,
          'radius': radii[target_idx],
          'rotation': 0
        }

      visited.add(target_idx)
      queue.append(target_idx)

  # Place any unvisited gears (disconnected) in a grid
  grid_x, grid_y = 20, 0
  for i in range(n):
    if positions[i] is None:
      positions[i] = {'x': grid_x, 'y': grid_y, 'z': z_levels[i], 'radius': radii[i], 'rotation': 0}
      grid_x += radii[i] * 2 + 1
      if grid_x > 50:
        grid_x = 20
        grid_y += 5

  return positions


def find_free_z_level(positions, x, y, radius, base_z=0):
  """Find a Z level at (x,y) that doesn't overlap with existing gears."""
  if not positions:
    return base_z

  # Find all gears that overlap in XY with this position
  overlapping_z_levels = []
  for pos in positions:
    if pos is None:
      continue
    dx = x - pos['x']
    dy = y - pos['y']
    dist_xy = math.sqrt(dx * dx + dy * dy)
    # If gears overlap in XY (centers closer than sum of radii)
    if dist_xy < radius + pos['radius'] - 0.01:
      overlapping_z_levels.append(pos['z'])

  if not overlapping_z_levels:
    return base_z

  # Find a Z level that doesn't conflict
  z = base_z
  while True:
    conflict = False
    for oz in overlapping_z_levels:
      if abs(z - oz) < GEAR_THICKNESS * 1.2:  # Need separation
        conflict = True
        break
    if not conflict:
      return z
    z += GEAR_THICKNESS * 1.5
    if z > 20:  # Safety limit
      break
  return z


def find_free_angle(positions, center_pos, distance, new_radius):
  """Find an angle from center_pos where a gear of new_radius won't collide."""
  # Try angles in increments, preferring rightward/downward placement
  for base_angle in [
      0, -math.pi / 2, math.pi / 2, math.pi, -math.pi / 4, math.pi / 4, -3 * math.pi / 4,
      3 * math.pi / 4
  ]:
    for offset in [0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.5, -0.5]:
      angle = base_angle + offset
      test_x = center_pos['x'] + distance * math.cos(angle)
      test_y = center_pos['y'] + distance * math.sin(angle)

      # Check collision with existing gears
      collision = False
      for pos in positions:
        if pos is None:
          continue
        dx = test_x - pos['x']
        dy = test_y - pos['y']
        dist = math.sqrt(dx * dx + dy * dy)
        min_dist = new_radius + pos['radius'] - 0.01  # Small tolerance
        if dist < min_dist:
          collision = True
          break

      if not collision:
        return angle

  # Fallback: just use 0
  return 0


def generate_gear_scad(gears_def, positions, complications=None, expected=None):
  """Generate OpenSCAD code for gear train visualization."""
  complications = complications or {}

  scad = "// Gear Train Visualization\n"
  scad += "$fn = 32;\n\n"

  # Color palette for gears
  colors = [
    [0.7, 0.3, 0.3],  # red
    [0.3, 0.7, 0.3],  # green
    [0.3, 0.3, 0.7],  # blue
    [0.7, 0.7, 0.3],  # yellow
    [0.7, 0.3, 0.7],  # magenta
    [0.3, 0.7, 0.7],  # cyan
    [0.8, 0.5, 0.2],  # orange
    [0.5, 0.3, 0.7],  # purple
  ]

  # Special colors for complications
  clutch_color = [0.4, 0.4, 0.4]  # gray for disengaged
  ratchet_color = [0.9, 0.6, 0.1]  # orange-yellow
  fragile_color = [0.9, 0.9, 0.9]  # white/glass-like
  shattered_color = [0.3, 0.1, 0.1]  # dark red

  for i, (gear, pos) in enumerate(zip(gears_def, positions)):
    gear_num = i + 1
    teeth = gear['teeth']
    radius = pos['radius']
    x, y, z = pos['x'], pos['y'], pos['z']
    rotation = pos.get('rotation', 0)

    # Determine color based on complications
    color = colors[i % len(colors)]
    label_parts = [f"G{gear_num}"]

    # Check for complications
    is_shattered = False
    if expected:
      exp_gear = next((e for e in expected if e['gearNumber'] == gear_num), None)
      if exp_gear and 'notes' in exp_gear and 'Shattered' in exp_gear.get('notes', ''):
        is_shattered = True
        color = shattered_color
        label_parts.append("BROKEN")

    if gear_num in complications.get('clutches', {}):
      state = complications['clutches'][gear_num]
      if state == 'disengaged':
        color = clutch_color
        label_parts.append("CLUTCH")

    if gear_num in complications.get('ratchets', {}):
      color = ratchet_color
      label_parts.append("RATCHET")

    if gear_num in complications.get('shatter_threshold', {}) and not is_shattered:
      color = fragile_color
      threshold = complications['shatter_threshold'][gear_num]
      label_parts.append(f"FRAGILE<{threshold}")

    if gear_num in complications.get('ellipse_gears', {}):
      label_parts.append("ELLIPSE")

    # Check for chain drive
    if 'chain_to' in gear:
      label_parts.append(f"CHAIN->{gear['chain_to']}")

    # Check for same shaft
    if 'same_shaft_as' in gear:
      label_parts.append(f"SHAFT={gear['same_shaft_as']}")

    label = " ".join(label_parts)

    scad += f"// Gear {gear_num}: {teeth} teeth\n"
    scad += f"color([{color[0]},{color[1]},{color[2]}]) translate([{x:.3f},{y:.3f},{z:.3f}]) {{\n"

    if is_shattered:
      # Render as broken pieces
      scad += f"  // Shattered gear\n"
      for j in range(5):
        angle = j * 72 * math.pi / 180
        ox = radius * 0.3 * math.cos(angle)
        oy = radius * 0.3 * math.sin(angle)
        scad += f"  translate([{ox:.3f},{oy:.3f},0]) cylinder(r={radius*0.3:.3f}, h={GEAR_THICKNESS:.3f});\n"
    else:
      # Proper gear geometry:
      # - Pitch radius = where gears mesh (radius variable)
      # - Addendum = tooth height above pitch = module
      # - Dedendum = tooth depth below pitch = 1.25 * module
      addendum = GEAR_MODULE
      dedendum = GEAR_MODULE * 1.25
      dedendum_radius = radius - dedendum
      addendum_radius = radius + addendum

      # Main gear body at dedendum circle (smaller than pitch)
      scad += f"  difference(){{\n"
      scad += f"    cylinder(r={dedendum_radius:.3f}, h={GEAR_THICKNESS:.3f});\n"
      # Center hole
      scad += f"    translate([0,0,-0.01]) cylinder(r={radius*0.15:.3f}, h={GEAR_THICKNESS+0.02:.3f});\n"
      scad += f"  }}\n"

      # Add teeth as proper involute-ish shapes (trapezoids)
      # Tooth width at pitch circle ≈ π * module / 2
      tooth_width = math.pi * GEAR_MODULE / 2
      for t in range(teeth):
        angle = rotation + t * 2 * math.pi / teeth
        # Tooth as a rotated trapezoid shape using hull of two cylinders
        scad += f"  hull() {{\n"
        # Inner edge (at dedendum)
        inner_x = dedendum_radius * math.cos(angle)
        inner_y = dedendum_radius * math.sin(angle)
        scad += f"    translate([{inner_x:.3f},{inner_y:.3f},0]) cylinder(r={tooth_width*0.4:.3f}, h={GEAR_THICKNESS:.3f}, $fn=12);\n"
        # Outer edge (at addendum) - narrower
        outer_x = addendum_radius * math.cos(angle)
        outer_y = addendum_radius * math.sin(angle)
        scad += f"    translate([{outer_x:.3f},{outer_y:.3f},0]) cylinder(r={tooth_width*0.25:.3f}, h={GEAR_THICKNESS:.3f}, $fn=12);\n"
        scad += f"  }}\n"

    scad += "}\n"

    # Add label
    if len(label) < 5:
      label_size = max(0.3, radius * 0.3)
      scad += f"color([0,0,0]) translate([{x:.3f},{y:.3f},{z + GEAR_THICKNESS + 0.1:.3f}]) "
      scad += f"linear_extrude(0.01) text(\"{label}\", size={label_size:.2f}, halign=\"center\");\n"
      scad += "\n"
    else:
      label_size = max(0.2, radius * 0.2)
      scad += f"color([1,1,1]) translate([{x:.3f},{(y+radius * 1.5):.3f},{z + GEAR_THICKNESS + 0.1:.3f}]) "
      scad += f"linear_extrude(0.01) text(\"{label}\", size={label_size:.2f}, halign=\"center\");\n"
      scad += "\n"

  # Draw chain connections
  for i, gear in enumerate(gears_def):
    if 'chain_to' in gear:
      target_idx = gear['chain_to'] - 1
      if 0 <= target_idx < len(positions):
        p1 = positions[i]
        p2 = positions[target_idx]
        scad += f"// Chain from Gear {i+1} to Gear {gear['chain_to']}\n"
        scad += f"color([0.2,0.2,0.2]) hull() {{\n"
        scad += f"  translate([{p1['x']:.3f},{p1['y']:.3f},{p1['z'] + GEAR_THICKNESS/2:.3f}]) sphere(r=0.05);\n"
        scad += f"  translate([{p2['x']:.3f},{p2['y']:.3f},{p2['z'] + GEAR_THICKNESS/2:.3f}]) sphere(r=0.05);\n"
        scad += "}\n"

  # Draw shaft connections (vertical lines)
  shaft_groups = {}
  for i, gear in enumerate(gears_def):
    if 'same_shaft_as' in gear:
      other_idx = gear['same_shaft_as'] - 1
      key = min(i, other_idx)
      if key not in shaft_groups:
        shaft_groups[key] = set()
      shaft_groups[key].add(i)
      shaft_groups[key].add(other_idx)

  for group in shaft_groups.values():
    indices = list(group)
    if len(indices) >= 2:
      p = positions[indices[0]]
      min_z = min(positions[idx]['z'] for idx in indices)
      max_z = max(positions[idx]['z'] + GEAR_THICKNESS for idx in indices)
      scad += f"// Shaft\n"
      scad += f"color([0.3,0.3,0.3]) translate([{p['x']:.3f},{p['y']:.3f},{min_z:.3f}]) "
      scad += f"cylinder(r=0.08, h={max_z - min_z:.3f});\n"

  return scad


def render_gear_train_image(gears_def,
                            complications=None,
                            expected=None,
                            output_path=None,
                            subpass=None):
  """Render gear train to PNG image."""
  import VolumeComparison as vc

  positions = calculate_gear_positions(gears_def, complications)
  scad = generate_gear_scad(gears_def, positions, complications, expected)

  if output_path is None:
    output_path = f"results/35_gear_train_{subpass}.png"

  os.makedirs("results", exist_ok=True)

  # Calculate camera position based on gear positions
  if positions:
    all_x = [p['x'] for p in positions if p]
    all_y = [p['y'] for p in positions if p]
    all_z = [p['z'] for p in positions if p]

    center_x = (min(all_x) + max(all_x)) / 2
    center_y = (min(all_y) + max(all_y)) / 2
    center_z = (min(all_z) + max(all_z)) / 2

    extent = max(max(all_x) - min(all_x), max(all_y) - min(all_y), 5)
    cam_dist = extent * 1.5

    # Isometric-ish view
    camera_arg = f"--camera={center_x + cam_dist},{center_y - cam_dist},{center_z + cam_dist},{center_x},{center_y},{center_z}"
  else:
    camera_arg = "--camera=10,-10,10,0,0,0"

  try:
    vc.render_scadText_to_png(scad, output_path, cameraArg=camera_arg)
    return output_path, scad
  except Exception as e:
    print(f"Failed to render gear train: {e}")
    return None, scad


def render_gear_train_views(gears_def, complications=None, subpass=None):
  """Render multiple views of a gear train for AI input."""
  import VolumeComparison as vc

  positions = calculate_gear_positions(gears_def, complications)
  scad = generate_gear_scad(gears_def, positions, complications)

  os.makedirs("results", exist_ok=True)

  if not positions:
    return []

  all_x = [p['x'] for p in positions if p]
  all_y = [p['y'] for p in positions if p]
  all_z = [p['z'] for p in positions if p]

  center_x = (min(all_x) + max(all_x)) / 2
  center_y = (min(all_y) + max(all_y)) / 2
  center_z = (min(all_z) + max(all_z)) / 2

  extent = max(max(all_x) - min(all_x), max(all_y) - min(all_y), 5)
  cam_dist = extent * 1.5

  # Multiple camera angles for better coverage
  views = [
    ("front", center_x, center_y - cam_dist, center_z + cam_dist * 0.5),
    ("topFar", center_x, center_y, center_z + cam_dist * 2),
    ("topClose", center_x, center_y, center_z + cam_dist),
    ("side", center_x + cam_dist, center_y, center_z + cam_dist * 0.5),
  ]

  image_paths = []
  for view_name, cx, cy, cz in views:
    output_path = f"results/35_input_{subpass}_{view_name}.png"
    camera_arg = f"--camera={cx:.2f},{cy:.2f},{cz:.2f},{center_x:.2f},{center_y:.2f},{center_z:.2f}"
    try:
      vc.render_scadText_to_png(scad,
                                output_path,
                                cameraArg=camera_arg,
                                extraScadArgs=["--no-autocenter"])
      image_paths.append(output_path)
    except Exception as e:
      print(f"Failed to render {view_name} view: {e}")

  return image_paths


def ensure_gear_images_exist(subpass):
  """Ensure gear train images exist for a subpass, render if not."""
  system = gear_systems[subpass]
  gears_def = system["gears_def"]
  complications = system.get("complications", {})

  # Check if images already exist
  front_path = f"results/35_input_{subpass}_front.png"
  if os.path.exists(front_path):
    # Return existing paths
    return [
      f"results/35_input_{subpass}_front.png",
      f"results/35_input_{subpass}_topClose.png",
      f"results/35_input_{subpass}_topFar.png",
      f"results/35_input_{subpass}_side.png",
    ]

  # Render new images
  return render_gear_train_views(gears_def, complications, subpass)


# Subpasses that use image input instead of/in addition to text description
IMAGE_INPUT_SUBPASSES = set()  # Empty by default, can be configured to add image-based subpasses

highLevelSummary = """
Tests mechanical reasoning about complex gear trains with special components.
<br><br>
Key concepts:
<ul>
<li>Meshing gears rotate in opposite directions</li>
<li>Speed ratio = driving gear teeth / driven gear teeth</li>
<li>Gears on the same shaft rotate together</li>
<li>Chain drives preserve rotation direction (unlike meshing)</li>
<li>Clutches can disconnect parts of the drive train</li>
<li>Ratchets only allow rotation in one direction</li>
<li>Fragile gears shatter above certain RPM thresholds</li>
</ul>
This tests whether an LLM can trace cause-and-effect through massive mechanical systems
with up to 200 gears and special complications.
"""
