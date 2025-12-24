"""
Test 48: Angry Birds Physics Challenge

Can an AI analyze a structure of blocks and targets, then determine optimal
catapult shots (bearing, elevation, speed) to maximize destruction?

Uses PyBullet physics simulation to:
1. Build stable structures from rectangular prisms (boxes, posts, beams)
2. Place targets that must be crushed or dislodged
3. Simulate projectile launches from a catapult
4. Score based on target destruction

Renders with OpenSCAD for visualization.
"""

import os
import math
import random
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional

import pybullet as p
import pybullet_data
import numpy as np

title = "Can an AI aim a catapult to destroy a structure?"

Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]

# World parameters
GROUND_SIZE = 20.0  # metres
CATAPULT_POSITION = (-8.0, 0.0, 0.0)  # Launch point
STRUCTURE_CENTER = (3.0, 0.0, 0.0)  # Where structures are built

# Physics constants
GRAVITY = -9.81
PROJECTILE_RADIUS = 0.3
PROJECTILE_MASS = 5.0

# Scoring
TARGET_DISLODGE_THRESHOLD = 0.5  # metres movement to count as dislodged
TARGET_CRUSH_BONUS = 0.5  # Extra points if target is under debris

singleThreaded = True


@dataclass
class Block:
  """A rectangular prism in the structure."""
  half_extents: Vec3  # Half-dimensions (x, y, z)
  position: Vec3  # Center position
  mass: float = 1.0  # 0 = static
  color: Tuple[float, float, float] = (0.6, 0.4, 0.2)  # Wood brown
  name: str = "block"


@dataclass
class Target:
  """A target to destroy (small sphere or box)."""
  position: Vec3
  radius: float = 0.2
  color: Tuple[float, float, float] = (0.0, 0.8, 0.0)  # Green
  name: str = "target"


@dataclass
class Structure:
  """A complete structure with blocks and targets."""
  name: str
  description: str
  blocks: List[Block] = field(default_factory=list)
  targets: List[Target] = field(default_factory=list)


def create_tower_structure() -> Structure:
  """Simple tower with targets on top."""
  blocks = []
  targets = []

  # Ground beams
  blocks.append(
    Block(half_extents=(0.5, 0.15, 0.15), position=(3.0, -0.4, 0.15), mass=2.0, name="base_beam_1"))
  blocks.append(
    Block(half_extents=(0.5, 0.15, 0.15), position=(3.0, 0.4, 0.15), mass=2.0, name="base_beam_2"))

  # Vertical posts
  for y_offset in [-0.4, 0.4]:
    for x_offset in [-0.35, 0.35]:
      blocks.append(
        Block(half_extents=(0.1, 0.1, 0.5),
              position=(3.0 + x_offset, y_offset, 0.8),
              mass=1.0,
              name=f"post_{x_offset}_{y_offset}"))

  # Cross beams
  blocks.append(
    Block(half_extents=(0.5, 0.15, 0.1), position=(3.0, -0.4, 1.4), mass=1.0, name="cross_1"))
  blocks.append(
    Block(half_extents=(0.5, 0.15, 0.1), position=(3.0, 0.4, 1.4), mass=1.0, name="cross_2"))

  # Top platform
  blocks.append(
    Block(half_extents=(0.6, 0.5, 0.08), position=(3.0, 0.0, 1.58), mass=1.5, name="platform"))

  # Second level posts
  blocks.append(
    Block(half_extents=(0.08, 0.08, 0.4),
          position=(3.0, -0.25, 2.06),
          mass=0.8,
          name="upper_post_1"))
  blocks.append(
    Block(half_extents=(0.08, 0.08, 0.4), position=(3.0, 0.25, 2.06), mass=0.8,
          name="upper_post_2"))

  # Roof
  blocks.append(
    Block(half_extents=(0.3, 0.4, 0.06), position=(3.0, 0.0, 2.52), mass=0.5, name="roof"))

  # Block the through shot.
  blocks.append(
    Block(half_extents=(0.1, 0.6, 1), position=(0, 0.0, 1.6), mass=10, name="annoying block"))
  blocks.append(
    Block(half_extents=(0.3, 0.3, 0.3), position=(2, 0.0, 0.4), mass=10, name="annoying block2"))

  # Targets inside the structure
  targets.append(Target(position=(3.0, 0.0, 0.5), name="target_ground"))
  targets.append(Target(position=(3.0, 0.0, 1.8), name="target_platform"))
  targets.append(Target(position=(3.0, 0.0, 2.7), name="target_roof"))

  return Structure(
    name="tower",
    description="A two-story tower with targets at ground, platform, and roof levels",
    blocks=blocks,
    targets=targets)


def create_wall_structure() -> Structure:
  """A defensive wall with targets behind it."""
  blocks = []
  targets = []

  # Wall segments (stacked bricks)
  for row in range(4):
    offset = 0.25 if row % 2 == 1 else 0.0
    for col in range(5):
      y_pos = -1.0 + col * 0.5 + offset
      if abs(y_pos) <= 1.2:
        blocks.append(
          Block(half_extents=(0.2, 0.22, 0.15),
                position=(2.5, y_pos, 0.15 + row * 0.3),
                mass=1.5,
                color=(0.7, 0.3, 0.2),
                name=f"brick_{row}_{col}"))

  # Targets behind the wall
  targets.append(Target(position=(3.5, -0.5, 0.3), name="target_back_left"))
  targets.append(Target(position=(3.5, 0.5, 0.3), name="target_back_right"))
  targets.append(Target(position=(3.5, 0.0, 0.3), name="target_back_center"))

  return Structure(name="wall",
                   description="A brick wall protecting three targets behind it",
                   blocks=blocks,
                   targets=targets)


def create_bridge_structure() -> Structure:
  """A bridge structure with targets underneath."""
  blocks = []
  targets = []

  # Support pillars
  for y in [-0.8, 0.8]:
    blocks.append(
      Block(half_extents=(0.15, 0.15, 0.6),
            position=(2.0, y, 0.6),
            mass=3.0,
            name=f"pillar_front_{y}"))
    blocks.append(
      Block(half_extents=(0.15, 0.15, 0.6),
            position=(4.0, y, 0.6),
            mass=3.0,
            name=f"pillar_back_{y}"))

  # Bridge decks
  blocks.append(
    Block(half_extents=(1.2, 1.0, 0.1),
          position=(3.0, 0.0, 1.3),
          mass=4.0,
          color=(0.5, 0.5, 0.5),
          name="deck"))

  blocks.append(
    Block(half_extents=(1.2, 1.0, 0.1),
          position=(0.0, 0.0, 1.3),
          mass=4.0,
          color=(0.5, 0.5, 0.5),
          name="deck"))

  # Railings
  blocks.append(
    Block(half_extents=(1.0, 0.05, 0.2), position=(3.0, -0.9, 1.6), mass=0.5, name="rail_left"))
  blocks.append(
    Block(half_extents=(1.0, 0.05, 0.2), position=(3.0, 0.9, 1.6), mass=0.5, name="rail_right"))

  # Block the under bridge trick shot.
  blocks.append(
    Block(half_extents=(0.5, 0.5, 0.5), position=(0.8, 0.0, 0.6), mass=10, name="annoying block"))

  # Targets under the bridge
  targets.append(Target(position=(3.0, 0.0, 0.3), name="target_under_center"))
  targets.append(Target(position=(2.5, 0.0, 0.3), name="target_under_front"))
  targets.append(Target(position=(3.5, 0.0, 0.3), name="target_under_back"))

  return Structure(name="bridge",
                   description="A bridge with targets hiding underneath - requires indirect hits",
                   blocks=blocks,
                   targets=targets)


def create_pyramid_structure() -> Structure:
  """A large pyramid of stacked bricks with targets on top."""
  blocks = []
  targets = []

  # Brick dimensions - wide and flat for stability
  brick_hx = 0.2  # half-depth in X
  brick_hy = 0.25  # half-width in Y
  brick_hz = 0.15  # half-height in Z
  brick_height = brick_hz * 2  # full height per layer

  # Build a 5-4-3-2-1 pyramid (5 rows, 15 bricks total)
  rows = [5, 4, 3, 2, 1]

  for row_idx, num_bricks in enumerate(rows):
    z = brick_hz + row_idx * brick_height  # stack directly on top
    # Center the row
    y_start = -(num_bricks - 1) * brick_hy
    for i in range(num_bricks):
      y = y_start + i * brick_hy * 2
      blocks.append(
        Block(
          half_extents=(brick_hx, brick_hy, brick_hz),
          position=(3.0, y, z),
          mass=2.0 - row_idx * 0.2,  # lighter toward top
          name=f"brick_{row_idx}_{i}"))

      blocks.append(
        Block(
          half_extents=(brick_hx, brick_hy, brick_hz),
          position=(1.0, y, z),
          mass=2.0 - row_idx * 0.2,  # lighter toward top
          name=f"brick_{row_idx}_{i}_2"))

  # Top of pyramid is at z = brick_hz + 4 * brick_height + brick_hz = 5 * 0.3 = 1.5
  top_z = brick_hz + len(rows) * brick_height

  # Two targets sitting ON TOP of the apex brick (not inside)
  targets.append(Target(position=(3.0, -0.15, top_z + 0.2), radius=0.15, name="target_crown_1"))
  targets.append(Target(position=(3.0, 0.15, top_z + 0.2), radius=0.15, name="target_crown_2"))

  return Structure(name="pyramid",
                   description="A tall pyramid of bricks with two targets balanced on the apex",
                   blocks=blocks,
                   targets=targets)


def create_fortress_structure() -> Structure:
  """A fortress with two towers connected by a wall, targets inside."""
  blocks = []
  targets = []

  # Left tower base
  for y in [-1.8, -1.4]:
    for x in [2.6, 3.0]:
      blocks.append(
        Block(half_extents=(0.15, 0.15, 0.6),
              position=(x, y, 0.6),
              mass=2.0,
              name=f"left_tower_post_{x}_{y}"))
  # Left tower platform
  blocks.append(
    Block(half_extents=(0.35, 0.35, 0.08),
          position=(2.8, -1.6, 1.28),
          mass=1.5,
          name="left_platform"))

  # Right tower base
  for y in [1.4, 1.8]:
    for x in [2.6, 3.0]:
      blocks.append(
        Block(half_extents=(0.15, 0.15, 0.6),
              position=(x, y, 0.6),
              mass=2.0,
              name=f"right_tower_post_{x}_{y}"))
  # Right tower platform
  blocks.append(
    Block(half_extents=(0.35, 0.35, 0.08),
          position=(2.8, 1.6, 1.28),
          mass=1.5,
          name="right_platform"))

  # Connecting wall between towers
  for row in range(3):
    for col in range(4):
      y = -0.75 + col * 0.5
      z = 0.2 + row * 0.4
      blocks.append(
        Block(half_extents=(0.15, 0.22, 0.18),
              position=(2.8, y, z),
              mass=1.0,
              color=(0.6, 0.35, 0.2),
              name=f"wall_{row}_{col}"))

  # Tower roofs (can be knocked off)
  blocks.append(
    Block(half_extents=(0.4, 0.4, 0.1), position=(2.8, -1.6, 1.46), mass=0.8, name="left_roof"))
  blocks.append(
    Block(half_extents=(0.4, 0.4, 0.1), position=(2.8, 1.6, 1.46), mass=0.8, name="right_roof"))

  # Targets on tower roofs and behind wall
  targets.append(Target(position=(2.8, -1.6, 1.7), name="target_left_tower"))
  targets.append(Target(position=(2.8, 1.6, 1.7), name="target_right_tower"))
  targets.append(Target(position=(3.5, 0.0, 0.3), name="target_behind_wall"))

  return Structure(name="fortress",
                   description="Twin towers connected by a wall - destroy the rooftop targets",
                   blocks=blocks,
                   targets=targets)


def create_domino_chain_structure() -> Structure:
  """A chain of dominoes that can cascade when hit."""
  blocks = []
  targets = []

  # Domino dimensions - tall and thin
  domino_hx = 0.08
  domino_hy = 0.25
  domino_hz = 0.4

  # Create a curved chain of dominoes
  num_dominoes = 12
  for i in range(num_dominoes):
    # Curve from catapult side toward back
    t = i / (num_dominoes - 1)
    y = -1.5 + t * 3.0  # sweep from -1.5 to 1.5
    x = 2.0 + t * 2.0  # move from 2.0 to 4.0

    # Angle each domino to face the next
    angle = math.atan2(3.0, 2.0)  # direction of chain

    blocks.append(
      Block(half_extents=(domino_hx, domino_hy, domino_hz),
            position=(x, y, domino_hz),
            mass=0.5,
            color=(0.5, 0.3, 0.1),
            name=f"domino_{i}"))

  # Target at the end of the chain
  targets.append(Target(position=(4.2, 1.7, 0.3), name="target_chain_end"))
  # Target that requires knocking over middle dominoes
  targets.append(Target(position=(3.0, 0.0, 0.3), name="target_chain_middle"))

  # Block the direct shot.
  blocks.append(
    Block(half_extents=(0.5, 0.5, 0.5), position=(0.8, 0.0, 0.6), mass=100, name="annoying block"))

  return Structure(name="domino_chain",
                   description="A chain of dominoes - hit the first to trigger a cascade",
                   blocks=blocks,
                   targets=targets)


def create_castle_structure() -> Structure:
  """A complex castle with multiple levels and battlements."""
  blocks = []
  targets = []

  # Castle base - thick walls
  base_positions = [
    (2.2, -1.0),
    (2.2, 0.0),
    (2.2, 1.0),  # front wall
    (3.8, -1.0),
    (3.8, 0.0),
    (3.8, 1.0),  # back wall
    (3.0, -1.2),
    (3.0, 1.2),  # side walls
  ]
  for x, y in base_positions:
    blocks.append(
      Block(half_extents=(0.2, 0.3, 0.4),
            position=(x, y, 0.4),
            mass=3.0,
            color=(0.5, 0.5, 0.55),
            name=f"base_{x}_{y}"))

  # Second level floor
  blocks.append(
    Block(half_extents=(0.9, 1.3, 0.1),
          position=(3.0, 0.0, 0.9),
          mass=4.0,
          color=(0.45, 0.45, 0.5),
          name="floor_2"))

  # Second level walls (thinner)
  for x in [2.3, 3.7]:
    for y in [-0.8, 0.0, 0.8]:
      blocks.append(
        Block(half_extents=(0.12, 0.25, 0.35),
              position=(x, y, 1.35),
              mass=1.5,
              color=(0.5, 0.5, 0.55),
              name=f"wall2_{x}_{y}"))

  # Battlements on top
  for y in [-0.9, -0.3, 0.3, 0.9]:
    blocks.append(
      Block(half_extents=(0.1, 0.15, 0.15),
            position=(2.3, y, 1.85),
            mass=0.5,
            color=(0.5, 0.5, 0.55),
            name=f"battlement_front_{y}"))
    blocks.append(
      Block(half_extents=(0.1, 0.15, 0.15),
            position=(3.7, y, 1.85),
            mass=0.5,
            color=(0.5, 0.5, 0.55),
            name=f"battlement_back_{y}"))

  # Central keep (tower in middle)
  blocks.append(
    Block(half_extents=(0.25, 0.25, 0.5),
          position=(3.0, 0.0, 1.5),
          mass=2.0,
          color=(0.55, 0.55, 0.6),
          name="keep"))
  blocks.append(
    Block(half_extents=(0.3, 0.3, 0.08), position=(3.0, 0.0, 2.08), mass=1.0, name="keep_roof"))

  # Targets
  targets.append(Target(position=(3.0, 0.0, 2.3), name="target_keep_top"))
  targets.append(Target(position=(3.0, 0.0, 0.5), name="target_courtyard"))
  targets.append(Target(position=(2.3, 0.0, 1.5), name="target_front_wall"))

  return Structure(name="castle",
                   description="A fortified castle with keep - destroy the king's tower",
                   blocks=blocks,
                   targets=targets)


def create_scaffold_structure() -> Structure:
  """A scaffold with targets on narrow pedestals at varying heights."""
  blocks = []
  targets = []

  # Main frame - four corner posts
  for x in [2.2, 3.8]:
    for y in [-1.0, 1.0]:
      blocks.append(
        Block(half_extents=(0.12, 0.12, 1.2), position=(x, y, 1.2), mass=3.0, name=f"post_{x}_{y}"))

  # Cross beams connecting posts
  blocks.append(
    Block(half_extents=(0.1, 1.1, 0.1), position=(2.2, 0.0, 2.3), mass=1.5, name="beam_front"))
  blocks.append(
    Block(half_extents=(0.1, 1.1, 0.1), position=(3.8, 0.0, 2.3), mass=1.5, name="beam_back"))
  blocks.append(
    Block(half_extents=(0.9, 0.1, 0.1), position=(3.0, -1.0, 2.3), mass=1.5, name="beam_left"))
  blocks.append(
    Block(half_extents=(0.9, 0.1, 0.1), position=(3.0, 1.0, 2.3), mass=1.5, name="beam_right"))

  # Narrow pedestals at different heights inside the frame
  pedestal_configs = [
    (3.0, -0.5, 0.4, 0.4),  # (x, y, height, pedestal_half_h)
    (3.0, 0.5, 0.7, 0.7),
    (2.6, 0.0, 1.0, 1.0),
    (3.4, 0.0, 0.55, 0.55),
  ]
  for i, (x, y, h, ph) in enumerate(pedestal_configs):
    # Thin pedestal
    blocks.append(
      Block(half_extents=(0.06, 0.06, ph), position=(x, y, ph), mass=0.8, name=f"pedestal_{i}"))
    # Small platform on top
    blocks.append(
      Block(half_extents=(0.12, 0.12, 0.03),
            position=(x, y, ph * 2 + 0.03),
            mass=0.3,
            name=f"platform_{i}"))
    # Target on platform
    targets.append(Target(position=(x, y, ph * 2 + 0.25), radius=0.15, name=f"target_pedestal_{i}"))

  return Structure(
    name="scaffold",
    description="Targets on narrow pedestals at varying heights - precision required",
    blocks=blocks,
    targets=targets)


# All available structures
STRUCTURES = [
  create_tower_structure(),
  create_wall_structure(),
  create_bridge_structure(),
  create_pyramid_structure(),
  create_fortress_structure(),
  create_domino_chain_structure(),
  create_castle_structure(),
  create_scaffold_structure(),
]


def _make_box(half_extents: Vec3, position: Vec3, mass: float = 0.0) -> int:
  """Create a box body in PyBullet."""
  collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
  body_id = p.createMultiBody(
    baseMass=mass,
    baseCollisionShapeIndex=collision,
    basePosition=position,
  )
  return body_id


def _make_sphere(radius: float, position: Vec3, mass: float = 0.0) -> int:
  """Create a sphere body in PyBullet."""
  collision = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
  body_id = p.createMultiBody(
    baseMass=mass,
    baseCollisionShapeIndex=collision,
    basePosition=position,
  )
  return body_id


def build_scene(structure: Structure) -> Tuple[List[int], List[int], int]:
  """
    Build the physics scene with structure and ground.
    Returns (block_ids, target_ids, ground_id).
    """
  p.setAdditionalSearchPath(pybullet_data.getDataPath())
  p.setGravity(0.0, 0.0, GRAVITY)
  p.setTimeStep(1.0 / 240.0)
  p.setPhysicsEngineParameter(numSolverIterations=50)

  # Ground plane
  ground_id = p.loadURDF("plane.urdf")
  p.changeDynamics(ground_id, -1, lateralFriction=0.8, restitution=0.1)

  # Build blocks
  block_ids = []
  for block in structure.blocks:
    body_id = _make_box(block.half_extents, block.position, block.mass)
    p.changeDynamics(body_id, -1, lateralFriction=0.6, restitution=0.05)
    block_ids.append(body_id)

  # Build targets
  target_ids = []
  for target in structure.targets:
    body_id = _make_sphere(target.radius, target.position, mass=0.5)
    p.changeDynamics(body_id, -1, lateralFriction=0.5, restitution=0.2)
    target_ids.append(body_id)

  return block_ids, target_ids, ground_id


def wait_for_stability(max_steps: int = 2000, velocity_threshold: float = 0.01) -> bool:
  """
    Step simulation until all objects are stable.
    Returns True if stable, False if timed out.
    """
  for step in range(max_steps):
    p.stepSimulation()

    # Check every 100 steps
    if step % 100 == 99:
      max_velocity = 0.0
      for body_id in range(p.getNumBodies()):
        vel, ang_vel = p.getBaseVelocity(body_id)
        speed = math.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)
        max_velocity = max(max_velocity, speed)

      if max_velocity < velocity_threshold:
        return True

  return False


def capture_positions(block_ids: List[int], target_ids: List[int]) -> Dict[str, List[Vec3]]:
  """Capture current positions of all objects."""
  block_positions = []
  block_orientations = []
  for bid in block_ids:
    pos, orn = p.getBasePositionAndOrientation(bid)
    block_positions.append(tuple(pos))
    block_orientations.append(tuple(orn))

  target_positions = []
  for tid in target_ids:
    pos, _ = p.getBasePositionAndOrientation(tid)
    target_positions.append(tuple(pos))

  return {
    "block_positions": block_positions,
    "block_orientations": block_orientations,
    "target_positions": target_positions,
  }


def launch_projectile(bearing_deg: float, elevation_deg: float, speed: float) -> int:
  """
    Launch a projectile from the catapult position.
    
    bearing_deg: Horizontal angle in degrees (0 = straight ahead toward +X, positive = left/+Y)
    elevation_deg: Vertical angle in degrees (0 = horizontal, positive = up)
    speed: Initial speed in m/s
    
    Returns the projectile body ID.
    """
  # Convert angles to radians
  bearing_rad = math.radians(bearing_deg)
  elevation_rad = math.radians(elevation_deg)

  # Calculate velocity components
  # Bearing 0 = +X direction, positive bearing rotates toward +Y
  horizontal_speed = speed * math.cos(elevation_rad)
  vx = horizontal_speed * math.cos(bearing_rad)
  vy = horizontal_speed * math.sin(bearing_rad)
  vz = speed * math.sin(elevation_rad)

  # Create projectile at catapult position (slightly elevated)
  start_pos = (CATAPULT_POSITION[0], CATAPULT_POSITION[1], CATAPULT_POSITION[2] + 1.0)
  projectile_id = _make_sphere(PROJECTILE_RADIUS, start_pos, PROJECTILE_MASS)
  p.changeDynamics(projectile_id, -1, lateralFriction=0.5, restitution=0.3)

  # Apply initial velocity
  p.resetBaseVelocity(projectile_id, linearVelocity=(vx, vy, vz))

  return projectile_id


def simulate_salvo(structure_index: int, shots: List[Tuple[float, float, float]]) -> Dict[str, Any]:
  """
    Simulate a full salvo of shots against a structure.
    
    shots: List of (bearing_deg, elevation_deg, speed) tuples
    
    Returns simulation results including destruction scores.
    """
  if p.isConnected():
    p.disconnect()
  p.connect(p.DIRECT)
  p.resetSimulation()

  structure = STRUCTURES[structure_index]
  block_ids, target_ids, ground_id = build_scene(structure)

  # Wait for initial stability
  wait_for_stability()

  # Capture initial positions
  initial_state = capture_positions(block_ids, target_ids)
  initial_target_positions = initial_state["target_positions"]

  # Launch projectiles with delays between shots
  projectile_ids = []
  projectile_paths = []  # List of paths, one per projectile
  for i, (bearing, elevation, speed) in enumerate(shots):
    # Clamp values to reasonable ranges
    bearing = max(-45, min(45, bearing))
    elevation = max(5, min(75, elevation))
    speed = max(5, min(30, speed))

    proj_id = launch_projectile(bearing, elevation, speed)
    projectile_ids.append(proj_id)
    path = []  # Track this projectile's path

    # Simulate for a bit before next shot (give time to hit)
    for step in range(int(240 * 2.0)):  # 2 seconds per shot
      p.stepSimulation()
      # Sample position every 10 steps (~24 samples per second)
      if step % 10 == 0:
        pos, _ = p.getBasePositionAndOrientation(proj_id)
        path.append(tuple(pos))
    projectile_paths.append(path)

  # Continue simulation to let debris settle
  wait_for_stability(max_steps=3000)

  # Capture final state
  final_state = capture_positions(block_ids, target_ids)
  final_target_positions = final_state["target_positions"]

  # Score destruction
  target_scores = []
  for i, (init_pos, final_pos) in enumerate(zip(initial_target_positions, final_target_positions)):
    displacement = math.sqrt((final_pos[0] - init_pos[0])**2 + (final_pos[1] - init_pos[1])**2 +
                             (final_pos[2] - init_pos[2])**2)

    dislodged = displacement > TARGET_DISLODGE_THRESHOLD

    # Check if fallen (z significantly lower)
    fallen = final_pos[2] < init_pos[2] - 0.3

    score = 0.0
    if dislodged:
      score = 1.0
    if fallen:
      score += TARGET_CRUSH_BONUS

    target_scores.append({
      "name": structure.targets[i].name,
      "initial_position": init_pos,
      "final_position": final_pos,
      "displacement": displacement,
      "dislodged": dislodged,
      "fallen": fallen,
      "score": min(1.5, score),
    })

  # Calculate block movement for visual interest
  block_movements = []
  for i, (init_pos, final_pos) in enumerate(
      zip(initial_state["block_positions"], final_state["block_positions"])):
    displacement = math.sqrt((final_pos[0] - init_pos[0])**2 + (final_pos[1] - init_pos[1])**2 +
                             (final_pos[2] - init_pos[2])**2)
    block_movements.append(displacement)

  total_score = sum(t["score"] for t in target_scores)
  max_score = len(target_scores) * 1.5

  result = {
    "structure_index": structure_index,
    "structure_name": structure.name,
    "shots": shots,
    "target_scores": target_scores,
    "total_score": total_score,
    "max_score": max_score,
    "normalized_score": total_score / max_score if max_score > 0 else 0,
    "final_block_positions": final_state["block_positions"],
    "final_block_orientations": final_state["block_orientations"],
    "final_target_positions": final_state["target_positions"],
    "block_movements": block_movements,
    "projectile_paths": projectile_paths,
  }

  p.disconnect()
  return result


def generate_scad_scene(structure: Structure,
                        block_positions: Optional[List[Vec3]] = None,
                        block_orientations: Optional[List[Quat]] = None,
                        target_positions: Optional[List[Vec3]] = None,
                        projectile_positions: Optional[List[Vec3]] = None,
                        projectile_paths: Optional[List[List[Vec3]]] = None,
                        show_catapult: bool = True,
                        show_grid: bool = True) -> str:
  """Generate OpenSCAD code for the scene."""
  scad = """// Angry Birds Scene - Test 48
$fn = 24;

// Colors
ground_color = [0.3, 0.5, 0.2];
wood_color = [0.6, 0.4, 0.2];
target_color = [0.1, 0.8, 0.1];
catapult_color = [0.4, 0.3, 0.25];
projectile_color = [0.8, 0.2, 0.2];
grid_color = [0.5, 0.5, 0.5, 0.3];
path_colors = [[1.0, 0.3, 0.3], [0.3, 0.3, 1.0], [1.0, 0.8, 0.2]];  // Red, Blue, Yellow for shots 1,2,3

"""

  # Ground
  scad += "// Ground\n"
  scad += f"color(ground_color) translate([0, 0, -0.05]) cube([{GROUND_SIZE}, {GROUND_SIZE}, 0.1], center=true);\n\n"

  # Grid marks
  if show_grid:
    scad += "// Grid marks\n"
    scad += "color(grid_color) {\n"
    for x in range(-8, 9, 2):
      scad += f"  translate([{x}, 0, 0.01]) cube([0.05, 16, 0.02], center=true);\n"
    for y in range(-8, 9, 2):
      scad += f"  translate([0, {y}, 0.01]) cube([16, 0.05, 0.02], center=true);\n"
    scad += "}\n\n"

  # Catapult
  if show_catapult:
    cx, cy, cz = CATAPULT_POSITION
    scad += "// Catapult\n"
    scad += "color(catapult_color) {\n"
    # Base
    scad += f"  translate([{cx}, {cy}, 0.15]) cube([0.8, 0.6, 0.3], center=true);\n"
    # Arm support posts
    scad += f"  translate([{cx-0.2}, {cy-0.2}, 0.5]) cube([0.1, 0.1, 0.7], center=true);\n"
    scad += f"  translate([{cx-0.2}, {cy+0.2}, 0.5]) cube([0.1, 0.1, 0.7], center=true);\n"
    # Cross bar
    scad += f"  translate([{cx-0.2}, {cy}, 0.85]) cube([0.1, 0.5, 0.1], center=true);\n"
    # Throwing arm (at rest position)
    scad += f"  translate([{cx+0.3}, {cy}, 0.75]) rotate([0, -30, 0]) cube([1.2, 0.08, 0.08], center=true);\n"
    # Cup
    scad += f"  translate([{cx+0.8}, {cy}, 1.0]) sphere(r=0.2);\n"
    scad += "}\n\n"

  # Blocks
  scad += "// Structure blocks\n"
  for i, block in enumerate(structure.blocks):
    if block_positions and i < len(block_positions):
      pos = block_positions[i]
    else:
      pos = block.position

    if block_orientations and i < len(block_orientations):
      orn = block_orientations[i]
      # Convert quaternion to euler angles for OpenSCAD
      # Using simplified conversion
      x, y, z, w = orn
      # Roll (x-axis rotation)
      sinr_cosp = 2 * (w * x + y * z)
      cosr_cosp = 1 - 2 * (x * x + y * y)
      roll = math.atan2(sinr_cosp, cosr_cosp)
      # Pitch (y-axis rotation)
      sinp = 2 * (w * y - z * x)
      if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
      else:
        pitch = math.asin(sinp)
      # Yaw (z-axis rotation)
      siny_cosp = 2 * (w * z + x * y)
      cosy_cosp = 1 - 2 * (y * y + z * z)
      yaw = math.atan2(siny_cosp, cosy_cosp)

      rot_str = f"rotate([{math.degrees(roll):.2f}, {math.degrees(pitch):.2f}, {math.degrees(yaw):.2f}])"
    else:
      rot_str = ""

    hx, hy, hz = block.half_extents
    r, g, b = block.color
    scad += f"color([{r}, {g}, {b}]) translate([{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]) "
    if rot_str:
      scad += rot_str + " "
    scad += f"cube([{hx*2:.3f}, {hy*2:.3f}, {hz*2:.3f}], center=true);\n"

  scad += "\n// Targets\n"
  for i, target in enumerate(structure.targets):
    if target_positions and i < len(target_positions):
      pos = target_positions[i]
    else:
      pos = target.position

    r, g, b = target.color
    scad += f"color([{r}, {g}, {b}]) translate([{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]) sphere(r={target.radius});\n"

  # Projectiles (if any)
  if projectile_positions:
    scad += "\n// Projectiles\n"
    for pos in projectile_positions:
      scad += f"color(projectile_color) translate([{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]) sphere(r={PROJECTILE_RADIUS});\n"

  # Projectile paths (trajectories)
  if projectile_paths:
    scad += "\n// Projectile trajectories\n"
    for shot_idx, path in enumerate(projectile_paths):
      if not path:
        continue
      color_idx = shot_idx % 3
      scad += f"// Shot {shot_idx + 1} trajectory\n"
      scad += f"color(path_colors[{color_idx}]) {{\n"
      for pos in path:
        # Small spheres along the path
        scad += f"  translate([{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]) sphere(r=0.08);\n"
      scad += "}\n"

  return scad


# Camera angle definitions for multiple views
# Format: (name, camera_arg, description)
# Using vector camera format: --camera=eyeX,eyeY,eyeZ,centerX,centerY,centerZ
# Key positions: Catapult at (-8,0,0), Structure at (3,0,~1.5)
CAMERA_ANGLES = [
  # Overview - elevated diagonal view showing full field (catapult left, structure right)
  ("overview", "--camera=-4,25,15,-2,0,1", "Overview from side"),
  # Catapult's aiming view - from behind catapult looking at structure
  ("catapult_view", "--camera=-9,1,2.5,3,0,1.5", "View from behind catapult toward target"),
  # Behind structure - looking back toward catapult (what's coming at you)
  ("behind_target", "--camera=7,1,3,-6,0,1", "View from behind structure toward catapult"),
  # Structure close-up front-left - see structure details and targets
  ("structure_front", "--camera=0,6,4,3,0,1.2", "Structure close-up from front-left"),
  # Structure close-up front-right - opposite angle
  ("structure_side", "--camera=0,-6,4,3,0,1.2", "Structure close-up from front-right"),
  # Top-down aerial view - see spatial layout
  ("top_down", "--camera=-2,0.1,25,-2,0,0", "Top-down view of the field"),
]


def render_scene_image(structure_index: int,
                       suffix: str = "",
                       post_salvo_result: Optional[Dict] = None,
                       force_rebuild: bool = False,
                       camera_angle: str = "overview") -> str:
  """Render a scene to PNG from a specific camera angle. Returns path to image."""
  import VolumeComparison as vc

  os.makedirs("results", exist_ok=True)

  # Find camera settings
  camera_arg = "--camera=0,12,8,55,0,25,25"  # default
  for name, cam, desc in CAMERA_ANGLES:
    if name == camera_angle:
      camera_arg = cam
      break

  angle_suffix = f"_{camera_angle}" if camera_angle != "overview" else ""
  image_path = f"results/48_scene_{structure_index}{suffix}{angle_suffix}.png"
  scad_path = f"results/48_scene_{structure_index}{suffix}.scad"

  if os.path.exists(image_path) and not force_rebuild:
    return image_path

  structure = STRUCTURES[structure_index]

  if post_salvo_result:
    scad = generate_scad_scene(
      structure,
      block_positions=post_salvo_result.get("final_block_positions"),
      block_orientations=post_salvo_result.get("final_block_orientations"),
      target_positions=post_salvo_result.get("final_target_positions"),
      projectile_paths=post_salvo_result.get("projectile_paths"),
      show_catapult=True,
      show_grid=True,
    )
  else:
    # Initial scene - verify stability first
    if p.isConnected():
      p.disconnect()
    p.connect(p.DIRECT)
    p.resetSimulation()

    block_ids, target_ids, _ = build_scene(structure)
    wait_for_stability()
    state = capture_positions(block_ids, target_ids)
    p.disconnect()

    scad = generate_scad_scene(
      structure,
      block_positions=state["block_positions"],
      block_orientations=state["block_orientations"],
      target_positions=state["target_positions"],
      show_catapult=True,
      show_grid=True,
    )

  # Save SCAD (only once per structure, not per angle)
  if not os.path.exists(scad_path) or force_rebuild:
    with open(scad_path, "w") as f:
      f.write(scad)

  # Render to PNG
  try:
    vc.render_scadText_to_png(scad,
                              image_path,
                              cameraArg=camera_arg,
                              extraScadArgs=["--no-autocenter"])
  except Exception as e:
    print(f"Warning: OpenSCAD render failed: {e}")
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (800, 600), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    draw.text((200, 280),
              f"Scene {structure_index} {camera_angle} (render failed)",
              fill=(255, 255, 255))
    img.save(image_path)

  return image_path


def render_all_angles(structure_index: int,
                      suffix: str = "",
                      post_salvo_result: Optional[Dict] = None,
                      force_rebuild: bool = False) -> Dict[str, str]:
  """Render a scene from all camera angles. Returns dict of angle_name -> image_path."""
  images = {}
  for angle_name, _, _ in CAMERA_ANGLES:
    img_path = render_scene_image(structure_index,
                                  suffix=suffix,
                                  post_salvo_result=post_salvo_result,
                                  force_rebuild=force_rebuild,
                                  camera_angle=angle_name)
    images[angle_name] = img_path
  return images


# Pre-render initial scenes
def setup():
  """Pre-render all initial scene images from all angles."""
  for i in range(len(STRUCTURES)):
    print(f"Rendering structure {i}: {STRUCTURES[i].name}...")
    for angle_name, _, _ in CAMERA_ANGLES:
      print(f"  - {angle_name}...")
      render_scene_image(i, camera_angle=angle_name)


# ============== Test Interface ==============


def prepareSubpassPrompt(index: int) -> str:
  if index >= len(STRUCTURES):
    raise StopIteration

  structure = STRUCTURES[index]

  # Render all camera angles
  images = render_all_angles(index)

  # Build target list
  target_list = "\n".join([
    f"  - {t.name} at position ({t.position[0]:.1f}, {t.position[1]:.1f}, {t.position[2]:.1f})"
    for t in structure.targets
  ])

  prompt = f"""You are controlling a catapult to destroy a structure and its targets.

**Scene Description:**
{structure.description}

**Targets to destroy (green spheres):**
{target_list}

**Catapult Position:** ({CATAPULT_POSITION[0]}, {CATAPULT_POSITION[1]}, {CATAPULT_POSITION[2]})
The catapult is located to the LEFT of the structure (negative X). The structure is centered around X=3.

**Physics:**
- Projectiles are spheres with radius {PROJECTILE_RADIUS}m and mass {PROJECTILE_MASS}kg
- Gravity is {abs(GRAVITY)} m/s²
- Targets must be displaced by at least {TARGET_DISLODGE_THRESHOLD}m to count as destroyed

**Your Task:**
Provide exactly 3 shots. For each shot, specify:
1. **bearing** (degrees): Horizontal aim angle. 0° = straight toward +X (toward structure), positive = left (+Y direction)
2. **elevation** (degrees): Vertical angle above horizontal. Range: 5° to 75°
3. **speed** (m/s): Launch speed. Range: 5 to 30 m/s

**Tips:**
- The structure is about 11 meters away (catapult at x=-8, structure at x=3)
- A 45° elevation with ~15 m/s speed travels roughly 22 meters
- Lower elevations hit faster but may miss high targets
- Consider destroying supporting blocks to topple the structure

---

**SCENE IMAGES:**

**1. Overview (side view of entire field):**
[[image:{images['overview']}]]

**2. Catapult's View (looking from catapult toward structure):**
[[image:{images['catapult_view']}]]

**3. Behind Structure (looking back at catapult):**
[[image:{images['behind_target']}]]

**4. Structure Close-up (front-left angle):**
[[image:{images['structure_front']}]]

**5. Structure Close-up (front-right angle):**
[[image:{images['structure_side']}]]

**6. Top-Down View (aerial view of field):**
[[image:{images['top_down']}]]
"""

  return prompt


structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Your analysis of the structure and strategy for destruction"
    },
    "shots": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "bearing": {
            "type": "number",
            "description": "Horizontal angle in degrees (0 = straight ahead, positive = left)"
          },
          "elevation": {
            "type": "number",
            "description": "Vertical angle in degrees above horizontal (5-75)"
          },
          "speed": {
            "type": "number",
            "description": "Launch speed in m/s (5-30)"
          }
        },
        "required": ["bearing", "elevation", "speed"],
        "additionalProperties": False
      },
      "minItems": 3,
      "maxItems": 3
    }
  },
  "required": ["reasoning", "shots"],
  "additionalProperties": False,
  "propertyOrdering": ["reasoning", "shots"]
}

# Store results for reporting
_salvo_results = {}


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str) -> Tuple[float, str]:
  global _salvo_results

  if not isinstance(answer, dict):
    return 0, "Invalid answer format"

  if subPass >= len(STRUCTURES):
    return 0, "Invalid subpass"

  shots_data = answer.get("shots", [])
  if not isinstance(shots_data, list) or len(shots_data) != 3:
    return 0, "Must provide exactly 3 shots"

  # Parse shots
  shots = []
  for i, shot in enumerate(shots_data):
    if not isinstance(shot, dict):
      return 0, f"Shot {i+1} is not a valid object"

    try:
      bearing = float(shot.get("bearing", 0))
      elevation = float(shot.get("elevation", 45))
      speed = float(shot.get("speed", 15))
    except (TypeError, ValueError):
      return 0, f"Shot {i+1} has invalid numeric values"

    shots.append((bearing, elevation, speed))

  # Run simulation
  print(f"Simulating salvo for structure {subPass}: {STRUCTURES[subPass].name}...")
  result = simulate_salvo(subPass, shots)

  # Store for reporting
  _salvo_results[(subPass, aiEngineName)] = result

  # Render post-salvo scene
  render_scene_image(subPass,
                     suffix=f"_post_{aiEngineName[:10]}",
                     post_salvo_result=result,
                     force_rebuild=True)

  score = result["normalized_score"]

  targets_hit = sum(1 for t in result["target_scores"] if t["dislodged"])
  total_targets = len(result["target_scores"])

  explanation = f"Hit {targets_hit}/{total_targets} targets. "
  explanation += f"Score: {result['total_score']:.1f}/{result['max_score']:.1f}"

  return score, explanation


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str) -> str:
  result = _salvo_results.get((subPass, aiEngineName))

  if not result:
    return "<p>No simulation result available</p>"

  structure = STRUCTURES[subPass]

  html = f"<h3>Structure: {structure.name}</h3>"
  html += f"<p>{structure.description}</p>"

  # Show reasoning
  if "reasoning" in answer:
    html += f"<p><b>AI Strategy:</b> {answer.get('reasoning', 'None')[:500]}</p>"

  # Show shots
  html += "<h4>Shots Fired:</h4><ul>"
  for i, (b, e, s) in enumerate(result["shots"]):
    html += f"<li>Shot {i+1}: bearing={b:.1f}°, elevation={e:.1f}°, speed={s:.1f} m/s</li>"
  html += "</ul>"

  # Show target results
  html += "<h4>Target Results:</h4><ul>"
  for t in result["target_scores"]:
    status = "✓ DESTROYED" if t["dislodged"] else "✗ Missed"
    if t["fallen"]:
      status += " (fallen)"
    html += f"<li>{t['name']}: {status} (moved {t['displacement']:.2f}m)</li>"
  html += "</ul>"

  html += f"<p><b>Total Score:</b> {result['total_score']:.1f}/{result['max_score']:.1f} ({result['normalized_score']*100:.0f}%)</p>"

  # Images
  initial_img = f"48_scene_{subPass}.png"
  post_img = f"48_scene_{subPass}_post_{aiEngineName[:10]}.png"

  html += "<div style='display:flex; gap:20px;'>"
  if os.path.exists(f"results/{initial_img}"):
    html += f"<div><p>Before:</p><img src='{initial_img}' style='max-width:350px'></div>"
  if os.path.exists(f"results/{post_img}"):
    html += f"<div><p>After:</p><img src='{post_img}' style='max-width:350px'></div>"
  html += "</div>"

  return html


highLevelSummary = """
<b>Angry Birds Physics Challenge</b><br><br>

This test presents the AI with structures made of blocks (boxes, posts, beams) containing 
targets that must be destroyed using a catapult.<br><br>

The AI must analyze:
<ul>
<li>The structure's layout and weak points</li>
<li>Target positions within/behind the structure</li>
<li>Physics of projectile motion (bearing, elevation, speed)</li>
<li>How to maximize destruction with 3 shots</li>
</ul>

Structures include:
<ul>
<li><b>Tower:</b> Multi-story structure with targets at different heights</li>
<li><b>Wall:</b> Defensive barrier protecting targets behind it</li>
<li><b>Bridge:</b> Elevated structure with targets hiding underneath</li>
<li><b>Pyramid:</b> Stacked blocks with targets in gaps</li>
</ul>

Scoring is based on how many targets are dislodged or destroyed by the salvo.
"""

subpassParamSummary = [s.description[:60] + "..." for s in STRUCTURES]
promptChangeSummary = "Each subpass presents a different structure to destroy"

if __name__ == "__main__":
  for i in range(2):
    a = {
      'reasoning':
      'Three shots aimed at the left, center, and right behind the brick wall to disrupt the structure and displace the three green targets (displacement >= 0.5 m required). Each shot uses a small yaw offset from straight ahead to reach the three positions, with moderate elevation to clear the wall and ensure impact.',
      'shots': [{
        'bearing': -4,
        'elevation': 38,
        'speed': 14
      }, {
        'bearing': 0,
        'elevation': 42,
        'speed': 15
      }, {
        'bearing': 4,
        'elevation': 34,
        'speed': 14
      }]
    }

    print(gradeAnswer(a, i, ""))

    print(resultToNiceReport(a, i, ""))
