"""
Test 47: Crime Scene Physics Analysis

Can an AI analyze a "crime scene" (ragdoll final position on stairs) and determine
what type of fall/incident caused it?

Uses PyBullet physics simulation to generate realistic fall scenarios, then renders
the final state for the AI to analyze.
"""

import os
import math
import random
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional

import pybullet as p
import pybullet_data
import numpy as np
from LLMBenchCore.ResultPaths import report_relpath

tags = ["3D", "Physics Engine", "Simulation", "Image Input"]

title = "Can an AI determine how someone fell from the crime scene?"
skip = True

Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]

# Stair parameters (consistent across all scenarios)
STAIR_COUNT = 10
STAIR_RUN = 0.30  # metres (depth of each step)
STAIR_RISE = 0.20  # metres (height of each step)
STAIR_WIDTH = 2.0  # metres
TOP_HEIGHT = STAIR_COUNT * STAIR_RISE  # 2.0m total height


@dataclass
class Scenario:
  """Defines a fall scenario for simulation."""
  name: str  # Internal name
  description: str  # Human-readable description for the answer
  start_position: Vec3  # Where the ragdoll starts
  start_orientation: Tuple[float, float, float]  # Euler angles (roll, pitch, yaw)
  initial_velocity: Vec3  # Linear velocity
  initial_angular_velocity: Vec3  # Angular velocity
  sim_time: float  # How long to simulate


# Define the scenarios
SCENARIOS = [
  Scenario(
    name="fell_forward_top",
    description="Tripped and fell forward while descending from the top of the stairs",
    start_position=(0.3, 0.0, TOP_HEIGHT + 0.9),
    start_orientation=(0.0, 0.3, 0.0),  # Slight forward lean
    initial_velocity=(1.5, 0.0, 0.0),  # Moving forward/down
    initial_angular_velocity=(0.0, 2.0, 0.0),  # Tumbling forward
    sim_time=4.0,
  ),
  Scenario(
    name="fell_backward_top",
    description="Lost balance and fell backward from the top of the stairs",
    start_position=(0.3, 0.0, TOP_HEIGHT + 0.9),
    start_orientation=(0.0, -0.2, math.pi),  # Facing up stairs, leaning back
    initial_velocity=(1.0, 0.0, 0.0),  # Falling backward = positive x (down stairs)
    initial_angular_velocity=(0.0, -2.0, 0.0),  # Tumbling backward
    sim_time=4.0,
  ),
  Scenario(
    name="pushed_from_top",
    description="Was pushed/shoved from behind at the top of the stairs",
    start_position=(0.2, 0.0, TOP_HEIGHT + 0.9),
    start_orientation=(0.0, 0.0, 0.0),  # Upright, facing down
    initial_velocity=(4.0, 0.0, 1.0),  # Strong forward push with slight upward
    initial_angular_velocity=(0.0, 0.5, 0.0),
    sim_time=4.0,
  ),
  Scenario(
    name="jumped_from_top",
    description="Jumped or dove from the top of the stairs (intentional)",
    start_position=(0.1, 0.0, TOP_HEIGHT + 0.9),
    start_orientation=(0.0, 0.5, 0.0),  # Diving forward
    initial_velocity=(3.0, 0.0, 2.0),  # Strong forward + upward (jump arc)
    initial_angular_velocity=(0.0, 1.0, 0.0),
    sim_time=4.0,
  ),
  Scenario(
    name="fell_climbing_middle",
    description="Fell while climbing up, from the middle of the stairs",
    start_position=(1.5, 0.0, TOP_HEIGHT * 0.5 + 0.9),
    start_orientation=(0.0, -0.3, math.pi),  # Facing up stairs, leaning back
    initial_velocity=(1.5, 0.0, 0.0),  # Falls backward down the stairs
    initial_angular_velocity=(0.0, -2.5, 0.0),  # Tumbling backward
    sim_time=3.5,
  ),
  Scenario(
    name="fell_descending_middle",
    description="Slipped while descending, from the middle of the stairs",
    start_position=(1.2, 0.0, TOP_HEIGHT * 0.5 + 0.9),
    start_orientation=(0.0, 0.2, 0.0),
    initial_velocity=(2.0, 0.0, -0.5),  # Feet slipped out
    initial_angular_velocity=(0.0, 3.0, 0.0),  # Fast tumble
    sim_time=3.0,
  ),
  Scenario(
    name="collapsed_at_base",
    description="Collapsed or fainted at the base of the stairs (medical event)",
    start_position=(STAIR_COUNT * STAIR_RUN + 0.3, 0.0, 0.9),
    start_orientation=(0.0, 0.0, 0.0),
    initial_velocity=(0.0, 0.0, 0.0),  # No momentum - just dropped
    initial_angular_velocity=(0.0, 0.0, 0.0),
    sim_time=2.0,
  ),
  Scenario(
    name="slipped_on_ice",
    description="Slipped on ice/wet surface near the top and slid down",
    start_position=(0.6, 0.0, TOP_HEIGHT * 0.8 + 0.5),
    start_orientation=(0.0, 0.1, 0.0),
    initial_velocity=(0.5, 0.3, -0.5),  # Sliding motion
    initial_angular_velocity=(1.0, 0.5, 0.5),  # Chaotic spin
    sim_time=4.0,
  ),
]


def _make_static_box(half_extents: Vec3, position: Vec3, orientation: Quat = (0, 0, 0, 1)) -> int:
  collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
  body_id = p.createMultiBody(
    baseMass=0.0,
    baseCollisionShapeIndex=collision,
    baseVisualShapeIndex=-1,
    basePosition=position,
    baseOrientation=orientation,
  )
  return body_id


def build_stairs_only():
  """Build just the staircase environment (no ragdoll yet)."""
  p.setAdditionalSearchPath(pybullet_data.getDataPath())
  p.setGravity(0.0, 0.0, -9.81)
  p.setTimeStep(1.0 / 240.0)
  p.setPhysicsEngineParameter(numSolverIterations=100, useSplitImpulse=1)

  plane_id = p.loadURDF("plane.urdf")
  p.changeDynamics(plane_id, -1, lateralFriction=0.8, restitution=0.0)

  stair_ids = []
  for i in range(STAIR_COUNT):
    half_extents = (STAIR_RUN / 2.0, STAIR_WIDTH / 2.0, STAIR_RISE / 2.0)
    x = (i * STAIR_RUN) + (STAIR_RUN / 2.0)
    top_z = TOP_HEIGHT - (i * STAIR_RISE)
    z = top_z - (STAIR_RISE / 2.0)
    stair_id = _make_static_box(half_extents=half_extents, position=(x, 0.0, z))
    p.changeDynamics(stair_id, -1, lateralFriction=0.6, restitution=0.0)
    stair_ids.append(stair_id)

  # Add landing at bottom
  landing_half = (0.5, STAIR_WIDTH / 2.0, 0.01)
  landing_x = STAIR_COUNT * STAIR_RUN + 0.5
  _make_static_box(landing_half, (landing_x, 0.0, 0.01))

  # Add platform at top
  platform_half = (0.3, STAIR_WIDTH / 2.0, 0.01)
  _make_static_box(platform_half, (-0.15, 0.0, TOP_HEIGHT + 0.01))

  return plane_id, stair_ids


# Scale factor to make the ~6m humanoid into a ~1.7m human
HUMANOID_SCALE = 0.28


def spawn_ragdoll(scenario: Scenario) -> int:
  """Spawn a ragdoll with the scenario's initial conditions."""
  humanoid_path = os.path.join("humanoid", "humanoid.urdf")

  orientation_quat = p.getQuaternionFromEuler(scenario.start_orientation)

  # Suppress C++ URDF warnings by redirecting both stdout and stderr
  import os as _os
  devnull_fd = _os.open(_os.devnull, _os.O_WRONLY)
  old_stdout_fd = _os.dup(1)
  old_stderr_fd = _os.dup(2)
  _os.dup2(devnull_fd, 1)
  _os.dup2(devnull_fd, 2)
  try:
    ragdoll_id = p.loadURDF(
      humanoid_path,
      scenario.start_position,
      orientation_quat,
      flags=p.URDF_USE_SELF_COLLISION,
      globalScaling=HUMANOID_SCALE,
    )
  finally:
    _os.dup2(old_stdout_fd, 1)
    _os.dup2(old_stderr_fd, 2)
    _os.close(devnull_fd)
    _os.close(old_stdout_fd)
    _os.close(old_stderr_fd)

  # Make it limp
  for joint_index in range(p.getNumJoints(ragdoll_id)):
    p.setJointMotorControl2(ragdoll_id,
                            joint_index,
                            p.VELOCITY_CONTROL,
                            targetVelocity=0.0,
                            force=0.0)

  # Apply initial velocity
  p.resetBaseVelocity(ragdoll_id,
                      linearVelocity=scenario.initial_velocity,
                      angularVelocity=scenario.initial_angular_velocity)

  # Add some damping
  p.changeDynamics(ragdoll_id, -1, linearDamping=0.05, angularDamping=0.05)

  return ragdoll_id


def simulate_scenario(scenario_index: int) -> Dict[str, Any]:
  """
  Run a full simulation for a scenario and return the final state.
  """
  scenario = SCENARIOS[scenario_index]

  # Connect to PyBullet
  if p.isConnected():
    p.disconnect()
  p.connect(p.DIRECT)
  p.setPhysicsEngineParameter(enableConeFriction=1)
  p.resetSimulation()

  # Build environment
  plane_id, stair_ids = build_stairs_only()

  # Spawn ragdoll
  ragdoll_id = spawn_ragdoll(scenario)

  # Simulate
  time_step = 1.0 / 240.0
  steps = int(scenario.sim_time / time_step)

  for _ in range(steps):
    p.stepSimulation()

  # Capture final state
  final_state = capture_ragdoll_state(ragdoll_id)
  final_state["scenario_index"] = scenario_index
  final_state["scenario_name"] = scenario.name

  p.disconnect()

  return final_state


def capture_ragdoll_state(ragdoll_id: int) -> Dict[str, Any]:
  """Capture the full state of the ragdoll for rendering."""
  base_pos, base_orn = p.getBasePositionAndOrientation(ragdoll_id)

  links = []
  for i in range(p.getNumJoints(ragdoll_id)):
    link_state = p.getLinkState(ragdoll_id, i, computeForwardKinematics=True)
    link_info = p.getJointInfo(ragdoll_id, i)
    links.append({
      "name": link_info[1].decode('utf-8'),
      "position": tuple(link_state[0]),
      "orientation": tuple(link_state[1]),
    })

  return {
    "base_position": tuple(base_pos),
    "base_orientation": tuple(base_orn),
    "links": links,
  }


def generate_scad_for_state(state: Dict[str, Any], scenario_index: int) -> str:
  """Generate OpenSCAD code to render the crime scene with capsule-based ragdoll."""
  scad = """// Crime Scene Render - Test 47
$fn = 20;

// Colors
stair_color = [0.6, 0.5, 0.4];
body_color = [0.85, 0.65, 0.55];
head_color = [0.9, 0.75, 0.65];
floor_color = [0.35, 0.35, 0.38];

// Capsule module - hull of two spheres
module capsule(p1, p2, r) {
  hull() {
    translate(p1) sphere(r=r);
    translate(p2) sphere(r=r);
  }
}

"""

  # Add stairs
  scad += "// Stairs\n"
  scad += f"color(stair_color) {{\n"
  for i in range(STAIR_COUNT):
    x = (i * STAIR_RUN) + (STAIR_RUN / 2.0)
    top_z = TOP_HEIGHT - (i * STAIR_RISE)
    z = top_z - (STAIR_RISE / 2.0)
    scad += f"  translate([{x}, 0, {z}]) cube([{STAIR_RUN}, {STAIR_WIDTH}, {STAIR_RISE}], center=true);\n"
  scad += "}\n\n"

  # Add floor
  scad += "// Floor\n"
  scad += f"color(floor_color) translate([2.5, 0, -0.025]) cube([5, 3, 0.05], center=true);\n\n"

  # Build a lookup of link positions by name
  base_pos = state["base_position"]
  link_positions = {"base": base_pos}
  for link in state.get("links", []):
    link_positions[link["name"]] = link["position"]

  # Define body segment connections: (from_link, to_link, radius)
  # Radii scaled to match HUMANOID_SCALE=0.28 applied to the ~6m URDF
  # Original URDF radii: torso ~0.36, thigh 0.22, shin 0.20, arm 0.18, forearm 0.16
  # Scaled: torso ~0.10, thigh 0.062, shin 0.056, arm 0.05, forearm 0.045
  body_segments = [
    # Torso - from pelvis up to shoulder level (skip the unrealistic neck joint)
    ("base", "chest", 0.10),  # Lower torso (abdomen)
    # Note: Don't draw chest-to-neck - it creates an unrealistic giraffe neck
    # The head will be placed between the shoulders instead

    # Right arm
    ("right_shoulder", "right_elbow", 0.05),  # Upper arm
    ("right_elbow", "right_wrist", 0.045),  # Forearm

    # Left arm
    ("left_shoulder", "left_elbow", 0.05),
    ("left_elbow", "left_wrist", 0.045),

    # Right leg
    ("base", "right_hip", 0.065),  # Hip/pelvis
    ("right_hip", "right_knee", 0.062),  # Thigh
    ("right_knee", "right_ankle", 0.056),  # Shin

    # Left leg
    ("base", "left_hip", 0.065),
    ("left_hip", "left_knee", 0.062),
    ("left_knee", "left_ankle", 0.056),
  ]

  scad += "// Ragdoll body (capsule-based)\n"
  scad += f"color(body_color) {{\n"

  for from_link, to_link, radius in body_segments:
    if from_link in link_positions and to_link in link_positions:
      p1 = link_positions[from_link]
      p2 = link_positions[to_link]

      # Skip if same point (for head sphere)
      if from_link == to_link:
        continue

      scad += f"  capsule([{p1[0]:.4f}, {p1[1]:.4f}, {p1[2]:.4f}], "
      scad += f"[{p2[0]:.4f}, {p2[1]:.4f}, {p2[2]:.4f}], {radius}); // {from_link} to {to_link}\n"

  # Add shoulder bar connecting the two shoulders through chest
  if "right_shoulder" in link_positions and "left_shoulder" in link_positions and "chest" in link_positions:
    rs = link_positions["right_shoulder"]
    ls = link_positions["left_shoulder"]
    chest = link_positions["chest"]
    # Draw shoulder bar
    scad += f"  capsule([{rs[0]:.4f}, {rs[1]:.4f}, {rs[2]:.4f}], [{ls[0]:.4f}, {ls[1]:.4f}, {ls[2]:.4f}], 0.07); // shoulders\n"
    # Draw connections from chest to shoulders
    scad += f"  capsule([{chest[0]:.4f}, {chest[1]:.4f}, {chest[2]:.4f}], [{rs[0]:.4f}, {rs[1]:.4f}, {rs[2]:.4f}], 0.065); // chest to right shoulder\n"
    scad += f"  capsule([{chest[0]:.4f}, {chest[1]:.4f}, {chest[2]:.4f}], [{ls[0]:.4f}, {ls[1]:.4f}, {ls[2]:.4f}], 0.065); // chest to left shoulder\n"

  scad += "}\n\n"

  # Draw head and neck using the actual neck joint from simulation
  # The neck joint tracks correctly during physics - just don't draw the long capsule TO it
  if "neck" in link_positions and "chest" in link_positions:
    neck = link_positions["neck"]
    chest = link_positions["chest"]
    # Short neck from chest toward neck joint direction, then head at neck
    scad += f"// Head and neck\n"

    headPos = ((neck[0] * 5 + chest[0]) / 6, (neck[1] * 5 + chest[1]) / 6,
               (neck[2] * 5 + chest[2]) / 6)

    scad += f"color(body_color) capsule([{chest[0]:.4f}, {chest[1]:.4f}, {chest[2]:.4f}], [{neck[0]:.4f}, {neck[1]:.4f}, {neck[2]:.4f}], 0.055); // neck\n"
    scad += f"color(head_color) translate([{headPos[0]:.4f}, {headPos[1]:.4f}, {headPos[2]:.4f}]) sphere(r=0.15); // head\n\n"

  # Draw hands and feet as small spheres
  scad += "// Hands and feet\n"
  scad += f"color(body_color) {{\n"

  extremities = [
    ("right_wrist", 0.04),  # Right hand
    ("left_wrist", 0.04),  # Left hand
    ("right_ankle", 0.055),  # Right foot (box in URDF, approximate as sphere)
    ("left_ankle", 0.055),  # Left foot
  ]

  for link_name, radius in extremities:
    if link_name in link_positions:
      pos = link_positions[link_name]
      # Offset slightly from joint
      scad += f"  translate([{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]) sphere(r={radius});\n"

  scad += "}\n"

  return scad


def render_scenario_image(scenario_index: int, force_rebuild: bool = False) -> str:
  """Simulate scenario and render to PNG. Returns path to image."""
  import OpenScad as vc, scad_format

  os.makedirs("results", exist_ok=True)
  image_path = f"results/47_scene_{scenario_index}.png"
  scad_path = f"results/47_scene_{scenario_index}.scad"

  if os.path.exists(image_path) and not force_rebuild:
    return image_path

  print(f"Simulating scenario {scenario_index}: {SCENARIOS[scenario_index].name}...")

  # Run simulation
  state = simulate_scenario(scenario_index)

  # Generate SCAD
  scad = generate_scad_for_state(state, scenario_index)

  # Save SCAD
  with open(scad_path, "w") as f:
    f.write(scad_format.format(scad, vc.formatConfig))

  # Render to PNG
  # Camera format: --camera=x,y,z,rot_x,rot_y,rot_z,distance
  # Position camera to see full staircase with ragdoll
  camera_arg = "--camera=2,3,1.5,60,0,30,8"
  try:
    vc.render_scadText_to_png(scad, image_path, cameraArg=camera_arg)
  except Exception as e:
    print(f"Warning: OpenSCAD render failed: {e}")
    # Create a placeholder image
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (800, 600), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    draw.text((200, 280), f"Scene {scenario_index} (render failed)", fill=(255, 255, 255))
    img.save(image_path)

  return image_path


# Build all scenario images on module load (for --setup)
def setup():
  """Pre-render all scenario images."""
  for i in range(len(SCENARIOS)):
    render_scenario_image(i)


# Run setup if images don't exist
if not os.path.exists("results/47_scene_0.png"):
  try:
    setup()
  except Exception as e:
    print(f"Warning: Could not pre-render scenarios: {e}")

# ============== Test Interface ==============


# Each subpass shows a different scenario
def prepareSubpassPrompt(index: int) -> str:
  if index >= len(SCENARIOS):
    raise StopIteration

  scenario = SCENARIOS[index]
  image_path = render_scenario_image(index)

  # Build multiple choice options (correct answer + distractors)
  all_descriptions = [s.description for s in SCENARIOS]
  correct_answer = scenario.description

  # Select 3 random wrong answers
  wrong_answers = [d for d in all_descriptions if d != correct_answer]
  random.seed(index * 12345)  # Deterministic shuffle per subpass
  random.shuffle(wrong_answers)
  wrong_answers = wrong_answers[:3]

  # Combine and shuffle options
  options = [correct_answer] + wrong_answers
  random.shuffle(options)

  # Create lettered options
  option_letters = ['A', 'B', 'C', 'D']
  options_text = ""
  correct_letter = ""
  for i, opt in enumerate(options):
    options_text += f"  {option_letters[i]}. {opt}\n"
    if opt == correct_answer:
      correct_letter = option_letters[i]

  prompt = f"""You are a forensic analyst examining a crime scene photograph showing the final 
position of a person who fell on a staircase.

The image shows:
- A staircase with {STAIR_COUNT} steps
- The stairs descend from left to right (top of stairs is on the left)
- A person (shown as connected spheres representing body parts) in their final resting position
- The floor is at the bottom/right of the image

Based on the position and orientation of the body, determine the most likely cause of the fall.

The options are:
{options_text}
E. I don't know.

[[image:{image_path}]]
"""

  return prompt


structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Your analysis of the body position and what it indicates"
    },
    "answer": {
      "type": "string",
      "enum": ["A", "B", "C", "D", "E"],
      "description": "The letter of your chosen answer"
    }
  },
  "required": ["reasoning", "answer"],
  "additionalProperties": False,
  "propertyOrdering": ["reasoning", "answer"]
}


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str) -> Tuple[float, str]:
  if not isinstance(answer, dict):
    return 0, "Invalid answer format"

  if subPass >= len(SCENARIOS):
    return 0, "Invalid subpass"

  scenario = SCENARIOS[subPass]
  correct_answer = scenario.description

  # Rebuild the options to find correct letter
  all_descriptions = [s.description for s in SCENARIOS]
  wrong_answers = [d for d in all_descriptions if d != correct_answer]
  random.seed(subPass * 12345)
  random.shuffle(wrong_answers)
  wrong_answers = wrong_answers[:3]

  options = [correct_answer] + wrong_answers
  random.shuffle(options)

  option_letters = ['A', 'B', 'C', 'D']
  correct_letter = ""
  for i, opt in enumerate(options):
    if opt == correct_answer:
      correct_letter = option_letters[i]
      break

  given_answer = answer.get("answer", "").upper().strip()

  if given_answer == correct_letter:
    return 1.0, f"Correct! The answer was {correct_letter}: {correct_answer}"
  elif given_answer == "E":
    # Partial credit for reasonable reasoning
    reasoning = answer.get("reasoning", "").lower()
    partial = 0

    # Check if reasoning mentions relevant keywords
    scenario_keywords = {
      "fell_forward_top": ["forward", "tumbl", "trip", "descend", "top"],
      "fell_backward_top": ["backward", "back", "lost balance", "top"],
      "pushed_from_top": ["push", "shov", "force", "thrown", "top"],
      "jumped_from_top": ["jump", "dive", "leap", "intentional", "top"],
      "fell_climbing_middle": ["climb", "up", "middle", "ascending"],
      "fell_descending_middle": ["slip", "middle", "descend"],
      "collapsed_at_base": ["collaps", "faint", "medical", "bottom", "base"],
      "slipped_on_ice": ["slip", "ice", "wet", "slid"],
    }

    keywords = scenario_keywords.get(scenario.name, [])
    matches = sum(1 for kw in keywords if kw in reasoning)
    if matches >= 2:
      partial = 0.25

    return partial, f"You didn't know, which is wise. The correct was {correct_letter}: {correct_answer}"
  else:
    return -0.5, f"Incorrect. You answered {given_answer}, correct was {correct_letter}: {correct_answer}"


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str) -> str:
  if not isinstance(answer, dict):
    return "<p>Invalid answer</p>"

  scenario = SCENARIOS[subPass]

  html = f"<p><b>Scenario:</b> {scenario.name}</p>"
  html += f"<p><b>Correct Answer:</b> {scenario.description}</p>"

  if "reasoning" in answer:
    html += f"<p><b>AI Reasoning:</b> {answer.get('reasoning', 'None')[:500]}</p>"

  html += f"<p><b>AI Choice:</b> {answer.get('answer', '?')}</p>"

  image_path = render_scenario_image(subPass)
  if os.path.exists(image_path):
    html += f"<img src='{report_relpath(image_path, aiEngineName)}' style='max-width:400px'><br>"

  return html


highLevelSummary = """
<b>Crime Scene Physics Analysis</b><br><br>

This test simulates various fall scenarios on a staircase using PyBullet physics simulation:
<ul>
<li>Tripping and falling forward</li>
<li>Losing balance and falling backward</li>
<li>Being pushed from behind</li>
<li>Jumping or diving intentionally</li>
<li>Falling while climbing up</li>
<li>Slipping while descending</li>
<li>Collapsing at the base (medical event)</li>
<li>Slipping on ice/wet surface</li>
</ul>

The AI must analyze the final body position rendered in OpenSCAD and determine which 
type of fall caused the scene, choosing from 4 multiple-choice options.<br><br>

This tests spatial reasoning, physics intuition, and the ability to work backward
from effects to causes.
"""

subpassParamSummary = [s.description[:50] + "..." for s in SCENARIOS]
promptChangeSummary = "Each subpass shows a different fall scenario"

earlyFail = False

if __name__ == "__main__":
  # Test simulation
  print("Testing scenario simulation...")
  for i, scenario in enumerate(SCENARIOS):
    print(f"\n{i}: {scenario.name}")
    state = simulate_scenario(i)
    print(f"   Final position: {state['base_position']}")
    print(f"   Links captured: {len(state.get('links', []))}")
