import math, numpy
import random
import tempfile
import os
import json
import hashlib
import pybullet as p
import pybullet_data

SIMULATION_CACHE_VERSION = 9

title = "Intuitive Physics - Stacked Block Stability"

prompt = """
You are analyzing the stability of stacked objects. Each object has a mass and occupies a 
rectangular region in 3D space.

OBJECTS_DESCRIPTION

The bottom object rests on a flat surface (the ground). Objects are stacked on top of each other.
Gravity pulls downward (-Z direction).

If the blocks are placed loosely, determine:
1. Can the stack be built bottom-to-top without any single block tipping over?
2. If not, which block tips first?

Then assume the blocks are glued together to create a single rigid object. Determine:
3. Whether the object is stable?
4. If it is not stable and tips, which block touches the ground first?
5. If it is not stable and tips, after it comes to a rest, which blocks are touching the ground?
6. If it is stable, how many degrees of rotation are required to tip it over?

"""

structure = {
  "type":
  "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "looseStackable": {
      "type": "boolean",
      "description": "1. Can the stack be built bottom-to-top without any block tipping?"
    },
    "looseTippingBlock": {
      "type": "integer",
      "description":
      "2. If loose stacking fails, which block (1-indexed) tips first? 0 if stackable."
    },
    "gluedStable": {
      "type": "boolean",
      "description": "3. When glued as rigid body, is it stable on ground?"
    },
    "gluedFirstContact": {
      "type":
      "integer",
      "description":
      "4. If glued object tips, which block (1-indexed) touches ground first? 0 if stable."
    },
    "gluedRestingBlocks": {
      "type":
      "array",
      "items": {
        "type": "integer"
      },
      "description":
      "5. After tipping to rest, which blocks (1-indexed) touch ground? Empty if stable."
    },
    "degreesToTip": {
      "type": "number",
      "description": "6. If stable, minimum rotation degrees to tip over. 0 if already unstable."
    }
  },
  "propertyOrdering": [
    "reasoning", "looseStackable", "looseTippingBlock", "gluedStable", "gluedFirstContact",
    "gluedRestingBlocks", "degreesToTip"
  ],
  "required": [
    "reasoning", "looseStackable", "looseTippingBlock", "gluedStable", "gluedFirstContact",
    "gluedRestingBlocks", "degreesToTip"
  ],
  "additionalProperties":
  False
}


def compute_com(objects):
  """Compute combined center of mass."""
  total_mass = 0
  weighted_pos = [0, 0, 0]

  for obj in objects:
    m = obj["mass"]
    cx = (obj["x_min"] + obj["x_max"]) / 2
    cy = (obj["y_min"] + obj["y_max"]) / 2
    cz = (obj["z_min"] + obj["z_max"]) / 2

    weighted_pos[0] += m * cx
    weighted_pos[1] += m * cy
    weighted_pos[2] += m * cz
    total_mass += m

  if total_mass == 0:
    return [0, 0, 0]

  return [weighted_pos[0] / total_mass, weighted_pos[1] / total_mass, weighted_pos[2] / total_mass]


def check_loose_stability(objects):
  """Check if stack can be built loose bottom-to-top. Returns (stackable, tipping_block)."""
  n = len(objects)
  if n == 0:
    return True, 0

  parents = [-1] * n
  contact_rects = [None] * n
  eps = 1e-4
  min_overlap_fraction = 0.22  # each dimension overlap must be >= this fraction of child size

  # Determine supporting parent for each block (except base)
  for i in range(1, n):
    child = objects[i]
    parent_idx = None
    child_width = max(eps, child["x_max"] - child["x_min"])
    child_depth = max(eps, child["y_max"] - child["y_min"])
    for j in range(i - 1, -1, -1):
      parent = objects[j]
      if abs(child["z_min"] - parent["z_max"]) > eps:
        continue
      overlap_x_min = max(parent["x_min"], child["x_min"])
      overlap_x_max = min(parent["x_max"], child["x_max"])
      overlap_y_min = max(parent["y_min"], child["y_min"])
      overlap_y_max = min(parent["y_max"], child["y_max"])
      if overlap_x_max - overlap_x_min > eps and overlap_y_max - overlap_y_min > eps:
        overlap_w = overlap_x_max - overlap_x_min
        overlap_d = overlap_y_max - overlap_y_min
        if (overlap_w < child_width * min_overlap_fraction
            or overlap_d < child_depth * min_overlap_fraction):
          continue
        parent_idx = j
        contact_rects[i] = (overlap_x_min, overlap_x_max, overlap_y_min, overlap_y_max)
        break
    if parent_idx is None:
      return False, i + 1
    parents[i] = parent_idx

  # Build children adjacency lists
  children = [[] for _ in range(n)]
  for i in range(1, n):
    children[parents[i]].append(i)

  centers = []
  for obj in objects:
    centers.append([
      (obj["x_min"] + obj["x_max"]) / 2,
      (obj["y_min"] + obj["y_max"]) / 2,
      (obj["z_min"] + obj["z_max"]) / 2,
    ])

  def recurse(node_idx):
    obj = objects[node_idx]
    mass = obj["mass"]
    weighted = [
      mass * centers[node_idx][0], mass * centers[node_idx][1], mass * centers[node_idx][2]
    ]

    for child_idx in children[node_idx]:
      child_mass, child_com, failure = recurse(child_idx)
      if failure is not None:
        return 0.0, [0.0, 0.0, 0.0], failure

      rect = contact_rects[child_idx]
      if rect is None:
        return 0.0, [0.0, 0.0, 0.0], child_idx + 1

      if not (rect[0] - eps <= child_com[0] <= rect[1] + eps
              and rect[2] - eps <= child_com[1] <= rect[3] + eps):
        return 0.0, [0.0, 0.0, 0.0], child_idx + 1

      mass += child_mass
      weighted[0] += child_mass * child_com[0]
      weighted[1] += child_mass * child_com[1]
      weighted[2] += child_mass * child_com[2]

    com = [weighted[0] / mass, weighted[1] / mass, weighted[2] / mass]
    return mass, com, None

  _, _, failure = recurse(0)
  if failure is not None:
    return False, failure
  return True, 0


def get_base_footprint(objects):
  """Get the support polygon of the base object (convex hull of bottom face corners)."""
  base = objects[0]
  return [(base["x_min"], base["y_min"]), (base["x_max"], base["y_min"]),
          (base["x_max"], base["y_max"]), (base["x_min"], base["y_max"])]


def point_in_rect(px, py, x_min, x_max, y_min, y_max):
  """Check if point is inside rectangle."""
  return x_min <= px <= x_max and y_min <= py <= y_max


def check_glued_stability(objects):
  """Check if glued rigid body is stable. Returns (stable, tip_direction)."""
  com = compute_com(objects)
  base = objects[0]

  stable = point_in_rect(com[0], com[1], base["x_min"], base["x_max"], base["y_min"], base["y_max"])

  if stable:
    return True, None

  cx_base = (base["x_min"] + base["x_max"]) / 2
  cy_base = (base["y_min"] + base["y_max"]) / 2
  dx = com[0] - cx_base
  dy = com[1] - cy_base

  if abs(dx) > abs(dy):
    tip_dir = "+x" if dx > 0 else "-x"
  else:
    tip_dir = "+y" if dy > 0 else "-y"

  return False, tip_dir


def find_first_contact_block(objects, tip_direction):
  """Find which block touches ground first when tipping in given direction."""
  base = objects[0]
  base_z_min = base["z_min"]

  if tip_direction == "+x":
    pivot_x = base["x_max"]
    extremes = [(i, obj["x_max"], obj["z_max"]) for i, obj in enumerate(objects)]
    best_idx = max(
      range(len(objects)),
      key=lambda i: math.atan2(objects[i]["z_max"] - base_z_min, objects[i]["x_max"] - pivot_x)
      if objects[i]["x_max"] > pivot_x else -999)
  elif tip_direction == "-x":
    pivot_x = base["x_min"]
    best_idx = max(
      range(len(objects)),
      key=lambda i: math.atan2(objects[i]["z_max"] - base_z_min, pivot_x - objects[i]["x_min"])
      if objects[i]["x_min"] < pivot_x else -999)
  elif tip_direction == "+y":
    pivot_y = base["y_max"]
    best_idx = max(
      range(len(objects)),
      key=lambda i: math.atan2(objects[i]["z_max"] - base_z_min, objects[i]["y_max"] - pivot_y)
      if objects[i]["y_max"] > pivot_y else -999)
  else:  # -y
    pivot_y = base["y_min"]
    best_idx = max(
      range(len(objects)),
      key=lambda i: math.atan2(objects[i]["z_max"] - base_z_min, pivot_y - objects[i]["y_min"])
      if objects[i]["y_min"] < pivot_y else -999)

  return best_idx + 1


def find_resting_blocks(objects, tip_direction):
  """Find which blocks touch ground after tipping to rest."""
  if tip_direction in ("+x", "-x"):
    if tip_direction == "+x":
      ground_level = max(obj["x_max"] for obj in objects)
      touching = [i + 1 for i, obj in enumerate(objects) if abs(obj["x_max"] - ground_level) < 0.01]
    else:
      ground_level = min(obj["x_min"] for obj in objects)
      touching = [i + 1 for i, obj in enumerate(objects) if abs(obj["x_min"] - ground_level) < 0.01]
  else:
    if tip_direction == "+y":
      ground_level = max(obj["y_max"] for obj in objects)
      touching = [i + 1 for i, obj in enumerate(objects) if abs(obj["y_max"] - ground_level) < 0.01]
    else:
      ground_level = min(obj["y_min"] for obj in objects)
      touching = [i + 1 for i, obj in enumerate(objects) if abs(obj["y_min"] - ground_level) < 0.01]

  return touching if touching else [1]


def compute_degrees_to_tip(objects):
  """Compute minimum rotation angle (degrees) to tip a stable glued object."""
  com = compute_com(objects)
  base = objects[0]

  com_x, com_y, com_z = com
  base_z = base["z_min"]
  h = com_z - base_z

  if h <= 0:
    return 90.0

  distances = [
    com_x - base["x_min"], base["x_max"] - com_x, com_y - base["y_min"], base["y_max"] - com_y
  ]

  min_dist = min(distances)
  if min_dist <= 0:
    return 0.0

  angle_rad = math.atan2(min_dist, h)
  return math.degrees(angle_rad)


# ============================================================================
# PyBullet Physics Simulation for Tipping
# ============================================================================


def _get_simulation_cache_dir():
  """Get cache directory for physics simulations."""
  cache_dir = os.path.join(tempfile.gettempdir(), "mesh_benchmark_cache", "physics_sim")
  os.makedirs(cache_dir, exist_ok=True)
  return cache_dir


def _compute_objects_hash(objects, tip_direction):
  """Compute hash key for caching simulation results."""
  payload = {"objects": objects, "tip_dir": tip_direction, "ver": SIMULATION_CACHE_VERSION}
  data = json.dumps(payload, sort_keys=True)
  return hashlib.sha256(data.encode()).hexdigest()[:16]


def _load_sim_cache(cache_key):
  """Load cached simulation results."""
  cache_path = os.path.join(_get_simulation_cache_dir(), f"{cache_key}.json")
  if os.path.exists(cache_path):
    try:
      with open(cache_path, 'r') as f:
        return json.load(f)
    except:
      pass
  return None


def _save_sim_cache(cache_key, results):
  """Save simulation results to cache."""
  cache_path = os.path.join(_get_simulation_cache_dir(), f"{cache_key}.json")
  try:
    with open(cache_path, 'w') as f:
      json.dump(results, f)
  except Exception as e:
    print(f"Warning: Failed to save simulation cache: {e}")


def _box_vertices(obj):
  """Get 8 corner vertices of a box object."""
  x0, x1 = obj["x_min"], obj["x_max"]
  y0, y1 = obj["y_min"], obj["y_max"]
  z0, z1 = obj["z_min"], obj["z_max"]
  return [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1],
          [x1, y1, z1], [x0, y1, z1]]


def _quat_to_matrix(quat):
  """Convert quaternion [x,y,z,w] to 3x3 rotation matrix."""
  x, y, z, w = quat
  xx, yy, zz = x * x, y * y, z * z
  xy, xz, yz = x * y, x * z, y * z
  wx, wy, wz = w * x, w * y, w * z

  return [[1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
          [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
          [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)]]


def _quat_to_axis_angle_deg(quat):
  """Convert quaternion to (angle in degrees, axis vector)."""
  x, y, z, w = quat
  w = max(-1.0, min(1.0, w))
  angle = 2 * math.acos(w)
  s = math.sqrt(max(1e-12, 1 - w * w))
  if s < 1e-6:
    axis = [1, 0, 0]
  else:
    axis = [x / s, y / s, z / s]
  return math.degrees(angle), axis


def _quat_angle_rad(quat):
  """Return rotation magnitude (radians) encoded by quaternion."""
  w = max(-1.0, min(1.0, quat[3]))
  return 2 * math.acos(w)


def _apply_transform(point, com_offset, rot_matrix, final_pos):
  """Apply rotation+translation used in simulation to a point."""
  # Move point relative to CoM
  rel = [point[i] - com_offset[i] for i in range(3)]
  # Rotate
  rotated = [
    rot_matrix[0][0] * rel[0] + rot_matrix[0][1] * rel[1] + rot_matrix[0][2] * rel[2],
    rot_matrix[1][0] * rel[0] + rot_matrix[1][1] * rel[1] + rot_matrix[1][2] * rel[2],
    rot_matrix[2][0] * rel[0] + rot_matrix[2][1] * rel[1] + rot_matrix[2][2] * rel[2]
  ]
  # Translate to final position
  return [rotated[i] + final_pos[i] for i in range(3)]


def simulate_tipping(objects, tip_direction):
  """
  Run PyBullet simulation to determine:
  - first_contact_block: which block (1-indexed) hits ground first
  - resting_blocks: which blocks (1-indexed) touch ground at rest
  - final_transforms: list of (position, orientation) for each block at rest
  """
  cache_key = _compute_objects_hash(objects, tip_direction)
  cached = _load_sim_cache(cache_key)
  if cached:
    print(f"Physics sim cache hit: {cache_key}")
    return cached

  print(f"Running PyBullet tipping simulation...")

  # Connect to PyBullet in DIRECT mode (no GUI)
  physics_client = p.connect(p.DIRECT)
  p.setAdditionalSearchPath(pybullet_data.getDataPath())
  p.setGravity(0, 0, -9.81)

  # Create ground plane
  ground_id = p.createCollisionShape(p.GEOM_PLANE)
  p.createMultiBody(0, ground_id)

  # Compute combined center of mass and total mass
  com = compute_com(objects)
  total_mass = sum(obj["mass"] for obj in objects)

  # Create collision shapes for each block as boxes
  collision_shapes = []
  shape_positions = []  # Position relative to CoM
  shape_orientations = []

  for obj in objects:
    half_x = (obj["x_max"] - obj["x_min"]) / 2
    half_y = (obj["y_max"] - obj["y_min"]) / 2
    half_z = (obj["z_max"] - obj["z_min"]) / 2

    col_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[half_x, half_y, half_z])
    collision_shapes.append(col_shape)

    # Position of box center relative to compound CoM
    cx = (obj["x_min"] + obj["x_max"]) / 2 - com[0]
    cy = (obj["y_min"] + obj["y_max"]) / 2 - com[1]
    cz = (obj["z_min"] + obj["z_max"]) / 2 - com[2]
    shape_positions.append([cx, cy, cz])
    shape_orientations.append([0, 0, 0, 1])

  # Create compound body using createMultiBody with collision shape arrays
  if len(objects) == 1:
    body_id = p.createMultiBody(baseMass=total_mass,
                                baseCollisionShapeIndex=collision_shapes[0],
                                basePosition=com,
                                baseOrientation=[0, 0, 0, 1])
  else:
    # Use first shape as base, rest as fixed links (mass=0 for links to make them fixed)
    base_shape = collision_shapes[0]
    link_shapes = collision_shapes[1:]
    link_masses = [0] * len(link_shapes)  # 0 mass = fixed to parent
    link_positions = shape_positions[1:]
    link_orientations = shape_orientations[1:]
    link_inertial_positions = [[0, 0, 0]] * len(link_shapes)
    link_inertial_orientations = [[0, 0, 0, 1]] * len(link_shapes)
    link_parent_indices = [0] * len(link_shapes)  # All attached to base
    link_joint_types = [p.JOINT_FIXED] * len(link_shapes)
    link_joint_axes = [[0, 0, 0]] * len(link_shapes)

    body_id = p.createMultiBody(
      baseMass=total_mass,
      baseCollisionShapeIndex=base_shape,
      basePosition=com,
      baseOrientation=[0, 0, 0, 1],
      baseInertialFramePosition=[0, 0, 0],  # CoM is at body origin
      baseInertialFrameOrientation=[0, 0, 0, 1],
      linkMasses=link_masses,
      linkCollisionShapeIndices=link_shapes,
      linkVisualShapeIndices=[-1] * len(link_shapes),
      linkPositions=link_positions,
      linkOrientations=link_orientations,
      linkInertialFramePositions=link_inertial_positions,
      linkInertialFrameOrientations=link_inertial_orientations,
      linkParentIndices=link_parent_indices,
      linkJointTypes=link_joint_types,
      linkJointAxis=link_joint_axes)

  # Set friction and reduce bounciness for realistic settling
  p.changeDynamics(body_id,
                   -1,
                   linearDamping=0.02,
                   angularDamping=0.02,
                   lateralFriction=0.5,
                   restitution=0.05)
  p.changeDynamics(ground_id, -1, lateralFriction=0.5, restitution=0.05)

  # Find the topmost point of the stack to apply force there
  top_z = max(obj["z_max"] for obj in objects)
  top_point = [com[0], com[1], top_z]  # Apply force at top

  # Calculate force direction and magnitude based on tip direction
  # Apply horizontal force at top to create tipping torque
  # Force needs to overcome the restoring torque from gravity
  base = objects[0]
  tower_height = top_z - base["z_min"]
  base_width_x = base["x_max"] - base["x_min"]
  base_width_y = base["y_max"] - base["y_min"]
  # Use max width to ensure enough force for any direction
  pivot_width = max(base_width_x, base_width_y)
  # Torque needed = mass * g * (pivot_width/2), applied at height = tower_height
  # Force = Torque / height, with large safety factor
  force_magnitude = total_mass * 9.81 * pivot_width / tower_height * 12.0
  if tip_direction == "+x":
    force_dir = [force_magnitude, 0, 0]
  elif tip_direction == "-x":
    force_dir = [-force_magnitude, 0, 0]
  elif tip_direction == "+y":
    force_dir = [0, force_magnitude, 0]
  else:  # -y
    force_dir = [0, -force_magnitude, 0]

  # Track first contact
  first_contact_block = 0
  first_contact_step = -1
  contact_detected = False

  # Run simulation
  max_steps = 5000  # allow plenty of time to settle
  settle_threshold = 0.005
  settle_count = 0
  settle_required = 100  # Need 100 consecutive low-velocity steps with ground contact
  min_tilt_for_rest = math.radians(8.0)  # must be tilted at least 8 deg to be considered "fallen"

  force_duration = 200  # Apply force for first 200 steps (~0.8 sec at 240Hz)

  for step in range(max_steps):
    # Apply tipping force at the top of the tower for initial steps
    if step < force_duration:
      # Convert top_point to position relative to body CoM
      pos, orn = p.getBasePositionAndOrientation(body_id)
      # Apply force in world frame at position relative to CoM
      # Apply force at top of tower in world frame
      p.applyExternalForce(body_id, -1, force_dir, top_point, p.WORLD_FRAME)

    p.stepSimulation()

    # Check for contacts with ground
    contacts = p.getContactPoints(body_id, ground_id)
    has_ground_contact = len(contacts) > 0

    if has_ground_contact:
      if not contact_detected:
        contact_detected = True

      if first_contact_block == 0:
        pos, orn = p.getBasePositionAndOrientation(body_id)
        inv_pos, inv_orn = p.invertTransform(pos, orn)

        assigned_block = 0
        for contact in contacts:
          contact_pos = contact[5]
          local_contact = p.multiplyTransforms(inv_pos, inv_orn, contact_pos, [0, 0, 0, 1])[0]
          orig_contact = [
            local_contact[0] + com[0], local_contact[1] + com[1], local_contact[2] + com[2]
          ]

          block_idx = 0
          for i, obj in enumerate(objects):
            margin = 0.1
            if (obj["x_min"] - margin <= orig_contact[0] <= obj["x_max"] + margin
                and obj["y_min"] - margin <= orig_contact[1] <= obj["y_max"] + margin
                and obj["z_min"] - margin <= orig_contact[2] <= obj["z_max"] + margin):
              block_idx = i + 1
              break

          if block_idx > 1:
            assigned_block = block_idx
            break

        if assigned_block > 0:
          first_contact_block = assigned_block
          first_contact_step = step

    # Check if simulation has settled: need ground contact + low velocity + significant tilt
    vel, ang_vel = p.getBaseVelocity(body_id)
    speed = math.sqrt(sum(v**2 for v in vel) + sum(v**2 for v in ang_vel))
    _, current_orn = p.getBasePositionAndOrientation(body_id)
    current_tilt = _quat_angle_rad(current_orn)

    if has_ground_contact and speed < settle_threshold and current_tilt >= min_tilt_for_rest:
      settle_count += 1
      if settle_count >= settle_required:
        break
    else:
      settle_count = 0

  # Get final transform
  final_pos, final_orn = p.getBasePositionAndOrientation(body_id)

  # Determine which blocks are touching the ground at rest
  resting_blocks = []
  contacts = p.getContactPoints(body_id, ground_id)

  if contacts:
    contact_positions = [c[5] for c in contacts]  # Positions on body

    # Transform each contact to original frame
    inv_pos, inv_orn = p.invertTransform(final_pos, final_orn)

    for contact_pos in contact_positions:
      local_contact = p.multiplyTransforms(inv_pos, inv_orn, contact_pos, [0, 0, 0, 1])[0]
      orig_contact = [
        local_contact[0] + com[0], local_contact[1] + com[1], local_contact[2] + com[2]
      ]

      for i, obj in enumerate(objects):
        margin = 0.15
        if (obj["x_min"] - margin <= orig_contact[0] <= obj["x_max"] + margin
            and obj["y_min"] - margin <= orig_contact[1] <= obj["y_max"] + margin
            and obj["z_min"] - margin <= orig_contact[2] <= obj["z_max"] + margin):
          if (i + 1) not in resting_blocks:
            resting_blocks.append(i + 1)
          break

  if not resting_blocks:
    resting_blocks = [1]  # Fallback

  # Convert quaternion to euler for easier use
  final_euler = p.getEulerFromQuaternion(final_orn)

  p.disconnect()

  results = {
    "first_contact_block": first_contact_block if first_contact_block > 0 else 1,
    "resting_blocks": sorted(resting_blocks),
    "final_position": list(final_pos),
    "final_orientation_quat": list(final_orn),
    "final_orientation_euler": list(final_euler),
    "com_offset": com,  # Original CoM used as body origin
    "simulation_steps": step + 1
  }

  _save_sim_cache(cache_key, results)
  print(
    f"Simulation complete: first_contact={results['first_contact_block']}, resting={results['resting_blocks']}"
  )

  return results


def generate_tower_problem(num_objects,
                           seed,
                           offset_range=1.5,
                           min_size_ratio=0.5,
                           base_size_x=None,
                           base_size_y=None,
                           base_height=None,
                           base_x_min=None,
                           base_y_min=None,
                           base_z_min=0.0,
                           branch_budget=2,
                           branch_chance=0.35,
                           branch_decay=0.75,
                           allow_long=True):
  """Generate a random tower with occasional long spans and branched subtowers."""
  rng = random.Random(seed)

  base_size_x = base_size_x if base_size_x is not None else rng.uniform(3.5, 7.5)
  base_size_y = base_size_y if base_size_y is not None else rng.uniform(3.5, 7.5)
  base_height = base_height if base_height is not None else rng.uniform(0.8, 1.8)
  base_x_min = base_x_min if base_x_min is not None else rng.uniform(-2.0, 2.0)
  base_y_min = base_y_min if base_y_min is not None else rng.uniform(-2.0, 2.0)

  objects = []
  objects.append({
    "mass": rng.uniform(20, 60),
    "x_min": base_x_min,
    "x_max": base_x_min + base_size_x,
    "y_min": base_y_min,
    "y_max": base_y_min + base_size_y,
    "z_min": base_z_min,
    "z_max": base_z_min + base_height
  })
  current_z = base_z_min + base_height

  branch_tasks = []

  for i in range(1, num_objects):
    prev = objects[i - 1]
    prev_width = max(0.5, prev["x_max"] - prev["x_min"])
    prev_depth = max(0.5, prev["y_max"] - prev["y_min"])
    prev_cx = (prev["x_min"] + prev["x_max"]) / 2
    prev_cy = (prev["y_min"] + prev["y_max"]) / 2

    # Sizes shrink with height but remain positive.
    min_width = max(0.5, prev_width * min_size_ratio)
    min_depth = max(0.5, prev_depth * min_size_ratio)
    size_x = rng.uniform(min_width, max(min_width + 0.1, prev_width * 1.2))
    size_y = rng.uniform(min_depth, max(min_depth + 0.1, prev_depth * 0.95))
    height = rng.uniform(0.6, 2.5)

    long_axis = None
    if allow_long and rng.random() < 0.2:  # occasionally create long beam segments
      long_axis = rng.choice(["x", "y"])
      stretch = rng.uniform(2.5, 5.5)
      if long_axis == "x":
        size_x = min(prev_width * 10, size_x * stretch)
      else:
        size_y = min(prev_depth * 3, size_y * stretch)
      height = rng.uniform(0.4, 1.8)

    # Guarantee contact by picking an overlap interval on the previous top surface.
    overlap_fraction_x = rng.uniform(max(0.2, 1 - 0.1 * offset_range), 0.9)
    contact_span_x = min(prev_width, size_x) * overlap_fraction_x
    contact_start_x = rng.uniform(prev["x_min"], prev["x_max"] - contact_span_x)
    leftover_x = max(0.0, size_x - contact_span_x)
    shift_extra_x = rng.uniform(0, leftover_x)
    x_min = contact_start_x - shift_extra_x
    x_max = x_min + size_x

    overlap_fraction_y = rng.uniform(max(0.2, 1 - 0.1 * offset_range), 0.9)
    contact_span_y = min(prev_depth, size_y) * overlap_fraction_y
    contact_start_y = rng.uniform(prev["y_min"], prev["y_max"] - contact_span_y)
    leftover_y = max(0.0, size_y - contact_span_y)
    shift_extra_y = rng.uniform(0, leftover_y)
    y_min = contact_start_y - shift_extra_y
    y_max = y_min + size_y

    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    offset_distance = math.hypot(cx - prev_cx, cy - prev_cy)

    mass = rng.uniform(5, 40) * (1 + 0.05 * i)
    if long_axis:
      mass *= 1.2

    objects.append({
      "mass": mass,
      "x_min": x_min,
      "x_max": x_max,
      "y_min": y_min,
      "y_max": y_max,
      "z_min": current_z,
      "z_max": current_z + height
    })

    current_z += height

    if branch_budget > 0 and size_x > 5 and rng.random() < branch_chance:

      for x in range(int(x_min) + 1, int(x_max) + 1, 2):
        branch_seed = rng.randrange(1_000_000_000)
        branch_width = 1
        branch_depth = max(0.8, size_y * rng.uniform(0.3, 0.6))
        branch_height = max(0.4, height * rng.uniform(0.5, 0.9))
        anchor_x_min = x
        anchor_y_min = rng.uniform(y_min, y_max - branch_depth)
        branch_objects = rng.randint(1, 2 + num_objects)
        branch_tasks.append({
          "num_objects": branch_objects,
          "seed": branch_seed,
          "offset_range": offset_range * rng.uniform(0.8, 1.1),
          "min_size_ratio": max(0.25, min_size_ratio * rng.uniform(0.85, 1.05)),
          "base_size_x": branch_width / 4,
          "base_size_y": branch_depth,
          "base_height": branch_height,
          "base_x_min": anchor_x_min,
          "base_y_min": anchor_y_min,
          "base_z_min": current_z,
          "branch_budget": branch_budget - 1,
          "branch_chance": branch_chance * branch_decay,
          "branch_decay": branch_decay,
          "allow_long": False
        })
      break

    subLong = rng.choice(branch_tasks + [None])
    if subLong:
      subLong["allow_long"] = True
      for s in branch_tasks:
        if s != subLong:
          s["branch_budget"] = 0
          s["num_objects"] = max(1, s["num_objects"] // 2)
          s["branch_chance"] = 0
        else:
          s["num_objects"] *= 2

  for task in branch_tasks:
    objects.extend(generate_tower_problem(**task))

  objects.sort(key=lambda obj: obj["z_min"])

  return objects


def format_objects_description(objects):
  """Format objects list as description string."""
  desc = ""
  for i, obj in enumerate(objects):
    desc += f"\nObject {i+1}: Mass {obj['mass']:.1f} kg, occupies region "
    desc += f"X:[{obj['x_min']:.2f},{obj['x_max']:.2f}], "
    desc += f"Y:[{obj['y_min']:.2f},{obj['y_max']:.2f}], "
    desc += f"Z:[{obj['z_min']:.2f},{obj['z_max']:.2f}]"
  return desc


def create_procedural_problem(index, total_subpasses):
  """Create a deterministic problem for a given subpass index."""
  difficulty = index + 1
  # Later subpasses have more objects and larger offsets.
  num_objects = 3 + difficulty
  offset_range = 0.6 + 0.2 * difficulty
  min_size_ratio = 0.75 - 0.03 * difficulty
  seed = 80000 + index
  objects = generate_tower_problem(num_objects,
                                   seed,
                                   offset_range=offset_range,
                                   min_size_ratio=min_size_ratio,
                                   branch_budget=difficulty // 2)

  name = f"Procedural tower {index + 1}/{total_subpasses}"
  return {"name": name, "objects": objects, "description": format_objects_description(objects)}


TOTAL_SUBPASSES = 30
problems = [create_procedural_problem(i, TOTAL_SUBPASSES) for i in range(TOTAL_SUBPASSES)]

# Pre-compute expected answers
for prob in problems:
  objects = prob["objects"]

  # Loose stacking analysis
  loose_ok, loose_tip = check_loose_stability(objects)
  prob["loose_stackable"] = loose_ok
  prob["loose_tipping_block"] = loose_tip

  # Glued rigid body analysis
  glued_ok, tip_dir = check_glued_stability(objects)
  prob["glued_stable"] = glued_ok
  prob["tip_direction"] = tip_dir

  if glued_ok:
    prob["glued_first_contact"] = 0
    prob["glued_resting_blocks"] = []
    prob["degrees_to_tip"] = round(compute_degrees_to_tip(objects), 1)
    prob["sim_results"] = None
  else:
    # Use PyBullet simulation for accurate tipping physics
    sim_results = simulate_tipping(objects, tip_dir)
    prob["glued_first_contact"] = sim_results["first_contact_block"]
    prob["glued_resting_blocks"] = sim_results["resting_blocks"]
    prob["degrees_to_tip"] = 0.0
    prob["sim_results"] = sim_results

  prob["com"] = compute_com(objects)

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Various stacking configurations testing stability"


def prepareSubpassPrompt(index: int) -> str:

  if index >= len(problems):
    raise StopIteration
  return prompt.replace("OBJECTS_DESCRIPTION", problems[index]["description"])


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  prob = problems[subPass]
  score = 0
  details = []

  # Q1: Loose stackable (0.15)
  loose_ans = answer.get("looseStackable", None)
  if loose_ans == prob["loose_stackable"]:
    score += 0.15
    details.append(f"Loose stackable correct: {loose_ans}")
  else:
    details.append(f"Loose stackable wrong: got {loose_ans}, expected {prob['loose_stackable']}")

  # Q2: Loose tipping block (0.1)
  loose_tip_ans = answer.get("looseTippingBlock", None)
  if loose_tip_ans == prob["loose_tipping_block"]:
    score += 0.1
    details.append(f"Loose tipping block correct: {loose_tip_ans}")
  else:
    details.append(
      f"Loose tipping block wrong: got {loose_tip_ans}, expected {prob['loose_tipping_block']}")

  # Q3: Glued stable (0.15)
  glued_ans = answer.get("gluedStable", None)
  if glued_ans == prob["glued_stable"]:
    score += 0.15
    details.append(f"Glued stable correct: {glued_ans}")
  else:
    details.append(f"Glued stable wrong: got {glued_ans}, expected {prob['glued_stable']}")

  # Q4: First contact block (0.15)
  first_contact_ans = answer.get("gluedFirstContact", None)
  if first_contact_ans == prob["glued_first_contact"]:
    score += 0.15
    details.append(f"First contact correct: {first_contact_ans}")
  else:
    details.append(
      f"First contact wrong: got {first_contact_ans}, expected {prob['glued_first_contact']}")

  # Q5: Resting blocks (0.2)
  resting_ans = answer.get("gluedRestingBlocks", [])
  expected_resting = prob["glued_resting_blocks"]
  if set(resting_ans) == set(expected_resting):
    score += 0.2
    details.append(f"Resting blocks correct: {resting_ans}")
  elif set(resting_ans) & set(expected_resting):
    partial = 0.2 * len(set(resting_ans) & set(expected_resting)) / max(len(expected_resting), 1)
    score += partial
    details.append(f"Resting blocks partial: got {resting_ans}, expected {expected_resting}")
  else:
    details.append(f"Resting blocks wrong: got {resting_ans}, expected {expected_resting}")

  # Q6: Degrees to tip (0.25)
  degrees_ans = answer.get("degreesToTip", 0)
  expected_degrees = prob["degrees_to_tip"]
  if isinstance(degrees_ans, (int, float)):
    error = abs(degrees_ans - expected_degrees)
    if error <= 2.0:
      score += 0.25
      details.append(f"Degrees to tip correct: {degrees_ans}")
    elif error <= 10.0:
      partial = 0.25 * (1 - error / 15)
      score += max(0, partial)
      details.append(f"Degrees to tip close: got {degrees_ans}, expected {expected_degrees}")
    else:
      details.append(f"Degrees to tip wrong: got {degrees_ans}, expected {expected_degrees}")
  else:
    details.append(f"Invalid degrees format: {degrees_ans}")

  score = numpy.clip(score, 0, 1)
  score = score**2

  return score, "<br>".join(details)


BLOCK_COLORS = [
  [0.8, 0.3, 0.3],  # red
  [0.3, 0.8, 0.3],  # green
  [0.3, 0.3, 0.8],  # blue
  [0.8, 0.8, 0.3],  # yellow
  [0.8, 0.3, 0.8],  # magenta
  [0.3, 0.8, 0.8],  # cyan
  [0.9, 0.6, 0.3],  # orange
  [0.6, 0.3, 0.9],  # purple
  [0.3, 0.9, 0.6],  # teal
  [0.9, 0.5, 0.5],  # pink
  [0.5, 0.7, 0.5],  # light green
  [0.5, 0.5, 0.7],  # light blue
]


def _scad_ground(objects, margin=2):
  """Generate ground plane SCAD."""
  all_x = [obj["x_min"] for obj in objects] + [obj["x_max"] for obj in objects]
  all_y = [obj["y_min"] for obj in objects] + [obj["y_max"] for obj in objects]
  gx0, gx1 = min(all_x) - margin, max(all_x) + margin
  gy0, gy1 = min(all_y) - margin, max(all_y) + margin
  return f"color([0.6, 0.6, 0.6]) translate([{gx0}, {gy0}, -0.1]) cube([{gx1 - gx0}, {gy1 - gy0}, 0.1]);\n"


def _scad_block(i, obj, alpha=0.8, ghost=False):
  """Generate SCAD for a single block."""
  color = BLOCK_COLORS[i % len(BLOCK_COLORS)]
  if ghost:
    color = [0.4, 0.4, 0.4]
    alpha = 0.3
  x_size = obj["x_max"] - obj["x_min"]
  y_size = obj["y_max"] - obj["y_min"]
  z_size = obj["z_max"] - obj["z_min"]
  cx = (obj["x_min"] + obj["x_max"]) / 2
  cy = (obj["y_min"] + obj["y_max"]) / 2
  cz = (obj["z_min"] + obj["z_max"]) / 2
  scad = f"color([{color[0]}, {color[1]}, {color[2]}, {alpha}]) "
  scad += f"translate([{obj['x_min']}, {obj['y_min']}, {obj['z_min']}]) "
  scad += f"cube([{x_size}, {y_size}, {z_size}]);\n"
  scad += f"color([1, 1, 1]) translate([{cx}, {cy}, {cz}]) "
  scad += f"linear_extrude(0.01) text(\"{i+1}\", size={min(x_size, y_size, z_size)*0.4}, halign=\"center\", valign=\"center\");\n"
  return scad


def _scad_com_marker(com):
  """Generate CoM marker SCAD."""
  scad = f"color([1, 0, 0]) translate([{com[0]}, {com[1]}, {com[2]}]) sphere(r=0.3);\n"
  scad += f"color([1, 0, 0, 0.5]) translate([{com[0]}, {com[1]}, 0]) cylinder(r=0.05, h={com[2]});\n"
  return scad


def generate_scad_full(prob):
  """Full stack as designed."""
  objects = prob["objects"]
  scad = "$fn = 32;\n" + _scad_ground(objects)
  for i, obj in enumerate(objects):
    scad += _scad_block(i, obj)
  return scad


def generate_scad_loose_stackable(prob):
  """Only blocks that can be loosely stacked (before tipping)."""
  objects = prob["objects"]
  tip_block = prob["loose_tipping_block"]
  scad = "$fn = 32;\n" + _scad_ground(objects)
  for i, obj in enumerate(objects):
    if tip_block > 0 and i + 1 >= tip_block:
      scad += _scad_block(i, obj, ghost=True)  # ghost the unstackable ones
    else:
      scad += _scad_block(i, obj)
  return scad


def generate_scad_com(prob):
  """Full stack with CoM annotated."""
  objects = prob["objects"]
  scad = "$fn = 32;\n" + _scad_ground(objects)
  for i, obj in enumerate(objects):
    scad += _scad_block(i, obj)
  scad += _scad_com_marker(prob["com"])
  return scad


def _compute_tipped_positions(objects, tip_dir, rotation_deg):
  """Compute object positions after rotating around tipping edge."""
  com = compute_com(objects)
  # Find pivot point (edge of base in tip direction)
  base = objects[0]
  if tip_dir == "+x":
    pivot_x, pivot_y = base["x_max"], (base["y_min"] + base["y_max"]) / 2
  elif tip_dir == "-x":
    pivot_x, pivot_y = base["x_min"], (base["y_min"] + base["y_max"]) / 2
  elif tip_dir == "+y":
    pivot_x, pivot_y = (base["x_min"] + base["x_max"]) / 2, base["y_max"]
  else:  # -y
    pivot_x, pivot_y = (base["x_min"] + base["x_max"]) / 2, base["y_min"]

  rad = math.radians(rotation_deg)
  cos_r, sin_r = math.cos(rad), math.sin(rad)

  tipped = []
  for obj in objects:
    cx = (obj["x_min"] + obj["x_max"]) / 2
    cy = (obj["y_min"] + obj["y_max"]) / 2
    cz = (obj["z_min"] + obj["z_max"]) / 2
    w = obj["x_max"] - obj["x_min"]
    d = obj["y_max"] - obj["y_min"]
    h = obj["z_max"] - obj["z_min"]

    # Rotate center around pivot
    if tip_dir in ["+x", "-x"]:
      dx = cx - pivot_x
      new_dx = dx * cos_r - cz * sin_r if tip_dir == "+x" else dx * cos_r + cz * sin_r
      new_cz = dx * sin_r + cz * cos_r if tip_dir == "+x" else -dx * sin_r + cz * cos_r
      new_cx = pivot_x + new_dx
      new_cy = cy
    else:
      dy = cy - pivot_y
      new_dy = dy * cos_r - cz * sin_r if tip_dir == "+y" else dy * cos_r + cz * sin_r
      new_cz = dy * sin_r + cz * cos_r if tip_dir == "+y" else -dy * sin_r + cz * cos_r
      new_cy = pivot_y + new_dy
      new_cx = cx

    tipped.append({
      "cx": new_cx,
      "cy": new_cy,
      "cz": max(0, new_cz),
      "w": w,
      "d": d,
      "h": h,
      "rot": rotation_deg,
      "tip_dir": tip_dir,
      "orig_idx": objects.index(obj)
    })
  return tipped, (pivot_x, pivot_y)


def generate_scad_tipped_first_contact(prob):
  """Show stack at moment of first contact (tipping) - all blocks as rigid body."""
  objects = prob["objects"]
  tip_dir = prob.get("tip_direction", "+x")
  if prob["glued_stable"]:
    rot = prob["degrees_to_tip"] * 0.95 if prob["degrees_to_tip"] > 0 else 15
  else:
    rot = 45

  base = objects[0]
  # Pivot is at edge of base in tip direction
  if tip_dir == "+x":
    px, py = base["x_max"], (base["y_min"] + base["y_max"]) / 2
    rot_vec = [0, rot, 0]
  elif tip_dir == "-x":
    px, py = base["x_min"], (base["y_min"] + base["y_max"]) / 2
    rot_vec = [0, -rot, 0]
  elif tip_dir == "+y":
    px, py = (base["x_min"] + base["x_max"]) / 2, base["y_max"]
    rot_vec = [-rot, 0, 0]
  else:
    px, py = (base["x_min"] + base["x_max"]) / 2, base["y_min"]
    rot_vec = [rot, 0, 0]

  scad = "$fn = 32;\n"
  scad += "// Ground plane\n"
  min_x = min(obj["x_min"] for obj in objects)
  max_x = max(obj["x_max"] for obj in objects)
  min_y = min(obj["y_min"] for obj in objects)
  max_y = max(obj["y_max"] for obj in objects)
  ground_margin = 1.5
  ground_x = min_x - ground_margin
  ground_y = min_y - ground_margin
  ground_w = (max_x - min_x) + 2 * ground_margin
  ground_d = (max_y - min_y) + 2 * ground_margin
  scad += (f"color([0.6, 0.6, 0.6]) translate([{ground_x}, {ground_y}, -0.1]) "
           f"cube([{ground_w}, {ground_d}, 0.1]);\n")

  # Rotate entire assembly as rigid body around pivot
  scad += f"translate([{px}, {py}, 0]) rotate([{rot_vec[0]}, {rot_vec[1]}, {rot_vec[2]}]) translate([{-px}, {-py}, 0]) {{\n"
  for i, obj in enumerate(objects):
    color = BLOCK_COLORS[i % len(BLOCK_COLORS)]
    highlight = (i + 1 == prob["glued_first_contact"])
    alpha = 1.0 if highlight else 0.6
    if highlight:
      color = [1.0, 0.2, 0.2]
    w = obj["x_max"] - obj["x_min"]
    d = obj["y_max"] - obj["y_min"]
    h = obj["z_max"] - obj["z_min"]
    scad += f"  color([{color[0]}, {color[1]}, {color[2]}, {alpha}]) "
    scad += f"translate([{obj['x_min']}, {obj['y_min']}, {obj['z_min']}]) cube([{w}, {d}, {h}]);\n"
  scad += "}\n"
  return scad


def generate_scad_tipped_resting(prob):
  """Show stack at rest using PyBullet simulation results."""
  objects = prob["objects"]
  if prob["glued_stable"]:
    return generate_scad_full(prob)

  resting = prob["glued_resting_blocks"]
  sim_results = prob.get("sim_results")

  if not sim_results:
    # Fallback if no simulation results
    return generate_scad_full(prob)

  # Get final transform from simulation
  final_pos = sim_results["final_position"]
  final_quat = sim_results["final_orientation_quat"]
  com_offset = sim_results["com_offset"]

  rot_matrix = _quat_to_matrix(final_quat)

  # Transform all vertices to determine bounds relative to ground plane
  transformed_vertices = []
  for obj in objects:
    for v in _box_vertices(obj):
      transformed_vertices.append(_apply_transform(v, com_offset, rot_matrix, final_pos))

  min_z = min(v[2] for v in transformed_vertices)
  z_shift = min_z  # amount to subtract to bring lowest point to z=0
  adjusted_vertices = [[vx, vy, vz - z_shift] for (vx, vy, vz) in transformed_vertices]

  min_x = min(v[0] for v in adjusted_vertices)
  max_x = max(v[0] for v in adjusted_vertices)
  min_y = min(v[1] for v in adjusted_vertices)
  max_y = max(v[1] for v in adjusted_vertices)

  final_pos = [final_pos[0], final_pos[1], final_pos[2] - z_shift]

  # Convert quaternion to axis-angle for OpenSCAD
  angle_deg, axis = _quat_to_axis_angle_deg(final_quat)

  # Ground plane following tipped resting position
  ground_margin = 2
  ground_x_min = min_x - ground_margin
  ground_x_max = max_x + ground_margin
  ground_y_min = min_y - ground_margin
  ground_y_max = max_y + ground_margin

  scad = "$fn = 32;\n"
  scad += "// Ground plane (simulated)\n"
  scad += (f"color([0.6, 0.6, 0.6]) translate([{ground_x_min}, {ground_y_min}, -0.1]) "
           f"cube([{ground_x_max - ground_x_min}, {ground_y_max - ground_y_min}, 0.1]);\n")

  # Apply the simulated transform:
  # 1. Translate to move CoM to origin
  # 2. Apply rotation
  # 3. Translate to final position
  scad += f"translate([{final_pos[0]}, {final_pos[1]}, {final_pos[2]}]) "
  scad += f"rotate(a={angle_deg}, v=[{axis[0]}, {axis[1]}, {axis[2]}]) "
  scad += f"translate([{-com_offset[0]}, {-com_offset[1]}, {-com_offset[2]}]) {{\n"

  for i, obj in enumerate(objects):
    color = BLOCK_COLORS[i % len(BLOCK_COLORS)]
    highlight = (i + 1) in resting
    alpha = 1.0
    if highlight:
      color = [0.2, 1.0, 0.2]
    w = obj["x_max"] - obj["x_min"]
    d = obj["y_max"] - obj["y_min"]
    h = obj["z_max"] - obj["z_min"]
    scad += f"  color([{color[0]}, {color[1]}, {color[2]}, {alpha}]) "
    scad += f"translate([{obj['x_min']}, {obj['y_min']}, {obj['z_min']}]) cube([{w}, {d}, {h}]);\n"

  scad += "}\n"
  return scad


def build_flickbook_html(image_paths, labels, viewer_id):
  """Build CSS flickbook HTML for multiple images."""
  import hashlib
  image_tags = []
  for idx, (path, label) in enumerate(zip(image_paths, labels)):
    import os
    image_tags.append(f'<img src="{os.path.basename(path)}" class="stack-view view-{idx}" '
                      f'title="{label}" style="max-width: 100%;">')

  radio_name = f"{viewer_id}-view"
  radio_ids = [f"{viewer_id}-view-{idx}" for idx in range(len(image_paths))]
  inputs = []
  for idx, radio_id in enumerate(radio_ids):
    checked = " checked" if idx == 0 else ""
    inputs.append(f'<input type="radio" name="{radio_name}" id="{radio_id}"{checked}>')

  nav_labels = []
  for idx in range(len(radio_ids)):
    prev_idx = (idx - 1) % len(radio_ids)
    next_idx = (idx + 1) % len(radio_ids)
    nav_labels.append(
      f'<label class="stack-prev prev-{idx}" for="{radio_ids[prev_idx]}">&#8592;</label>')
    nav_labels.append(
      f'<label class="stack-next next-{idx}" for="{radio_ids[next_idx]}">&#8594;</label>')

  # Label buttons for direct navigation
  label_btns = []
  for idx, label in enumerate(labels):
    label_btns.append(
      f'<label class="stack-label-btn label-{idx}" for="{radio_ids[idx]}">{label}</label>')

  style_lines = [
    f'#{viewer_id} {{ display:flex; flex-direction:column; align-items:center; gap:8px; }}',
    f'#{viewer_id} .nav-row {{ display:flex; align-items:center; gap:8px; }}',
    f'#{viewer_id} input[type="radio"] {{ display:none; }}',
    f'#{viewer_id} .stack-frame {{ flex:1; text-align:center; }}',
    f'#{viewer_id} .stack-prev, #{viewer_id} .stack-next {{ cursor:pointer; font-size:24px; display:none; padding:8px; }}',
    f'#{viewer_id} .stack-view {{ display:none; max-width:100%; }}',
    f'#{viewer_id} .label-row {{ display:flex; gap:4px; flex-wrap:wrap; justify-content:center; }}',
    f'#{viewer_id} .stack-label-btn {{ cursor:pointer; padding:4px 8px; background:#ddd; border-radius:4px; font-size:11px; }}',
  ]
  for idx, radio_id in enumerate(radio_ids):
    style_lines.append(
      f'#{radio_id}:checked ~ .nav-row .stack-frame .view-{idx} {{ display:block; }}')
    style_lines.append(f'#{radio_id}:checked ~ .nav-row .prev-{idx} {{ display:inline-flex; }}')
    style_lines.append(f'#{radio_id}:checked ~ .nav-row .next-{idx} {{ display:inline-flex; }}')
    style_lines.append(
      f'#{radio_id}:checked ~ .label-row .label-{idx} {{ background:#888; color:white; }}')

  html = (f'<div id="{viewer_id}" class="stack-viewer">'
          f'<style>{" ".join(style_lines)}</style>'
          f'{"".join(inputs)}'
          f'<div class="nav-row">'
          f'{"".join(nav_labels)}'
          f'<div class="stack-frame">'
          f'{"".join(image_tags)}'
          f'</div>'
          f'</div>'
          f'<div class="label-row">{"".join(label_btns)}</div>'
          f'</div>')
  return html


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
  import OpenScad as vc
  import os
  import hashlib

  prob = problems[subPass]
  objects = prob["objects"]

  # Calculate camera parameters
  all_x = [obj["x_min"] for obj in objects] + [obj["x_max"] for obj in objects]
  all_y = [obj["y_min"] for obj in objects] + [obj["y_max"] for obj in objects]
  all_z = [obj["z_min"] for obj in objects] + [obj["z_max"] for obj in objects]
  center_x = (min(all_x) + max(all_x)) / 2
  center_y = (min(all_y) + max(all_y)) / 2
  center_z = (min(all_z) + max(all_z)) / 2
  extent = max(max(all_x) - min(all_x), max(all_y) - min(all_y), max(all_z) - min(all_z))
  cam_dist = extent * 2.5

  camera_arg = f"--camera={center_x},{center_y - cam_dist},{center_z + cam_dist/3},{center_x},{center_y},{center_z}"

  # Generate multiple visualizations
  views = [
    ("full", "As Designed", generate_scad_full),
    ("loose", "Loose Stackable", generate_scad_loose_stackable),
    ("com", "Center of Mass", generate_scad_com),
    ("tip_contact", "First Contact", generate_scad_tipped_first_contact),
    ("tip_rest", "Resting State", generate_scad_tipped_resting),
  ]

  image_paths = []
  labels = []
  base_name = f"38_{subPass}_{aiEngineName}"

  try:
    for view_id, label, gen_func in views:
      scad = gen_func(prob)
      output_path = f"results/{base_name}_{view_id}.png"
      vc.render_scadText_to_png(scad, output_path, cameraArg=camera_arg)
      image_paths.append(output_path)
      labels.append(label)

    viewer_id = f"stack-viewer-{hashlib.md5(base_name.encode()).hexdigest()[:8]}"
    vis_html = build_flickbook_html(image_paths, labels, viewer_id)
  except Exception as e:
    vis_html = f"<i>Visualization error: {e}</i>"

  # Text content in left column
  html = "<td><b>Your answer:</b><br>"
  html += f"1. Loose Stackable: {answer.get('looseStackable', 'N/A')}<br>"
  html += f"2. Loose Tipping Block: {answer.get('looseTippingBlock', 'N/A')}<br>"
  html += f"3. Glued Stable: {answer.get('gluedStable', 'N/A')}<br>"
  html += f"4. First Contact: {answer.get('gluedFirstContact', 'N/A')}<br>"
  html += f"5. Resting Blocks: {answer.get('gluedRestingBlocks', 'N/A')}<br>"
  html += f"6. Degrees to Tip: {answer.get('degreesToTip', 'N/A')}<br>"

  html += "<br><b>Expected:</b><br>"
  html += f"1. Loose Stackable: {prob['loose_stackable']}<br>"
  html += f"2. Loose Tipping Block: {prob['loose_tipping_block']}<br>"
  html += f"3. Glued Stable: {prob['glued_stable']}<br>"
  html += f"4. First Contact: {prob['glued_first_contact']}<br>"
  html += f"5. Resting Blocks: {prob['glued_resting_blocks']}<br>"
  html += f"6. Degrees to Tip: {prob['degrees_to_tip']}<br>"

  html += f"</td><td>{vis_html}</td>"

  return html


highLevelSummary = """
Tests intuitive physics understanding of stacked block stability.
<br><br>
Key concepts tested:
<ul>
<li>Loose stacking: Can blocks be placed one-by-one without tipping?</li>
<li>Glued rigid body: Is the combined object stable on its base?</li>
<li>Tipping dynamics: Which block hits ground first when falling?</li>
<li>Final rest state: Which blocks end up touching the ground?</li>
<li>Stability margin: How much rotation before tipping occurs?</li>
</ul>
Crucial for robotics, construction planning, and physical reasoning.
"""
