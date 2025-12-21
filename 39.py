import math
import random

title = "Collision Prediction - Will moving objects collide?"

prompt = """
Multiple objects are moving through 3D space. Each object is a sphere with a given radius,
starting position, and constant velocity.

OBJECTS_DESCRIPTION

Assuming all objects continue moving in straight lines at constant speed:

1. Will any pair of objects collide? (Collision = their surfaces touch or overlap)
2. If yes, which pair collides first?
3. At what time does the first collision occur?
4. Where (XYZ coordinates) does the first collision happen?

Time starts at t=0. Positions are in meters, velocities in meters/second.
"""

structure = {
  "type": "object", "properties": {
    "reasoning": {"type": "string"}, "willCollide": {"type": "boolean"}, "collidingPair": {
      "type": "array", "items": {"type": "integer"}, "description":
      "The two object numbers that collide first (1-indexed), or empty if no collision"
    }, "collisionTime": {
      "type": "number", "description": "Time of first collision in seconds, or null if no collision"
    }, "collisionPoint": {
      "type": "array", "items": {"type": "number"}, "description":
      "[x, y, z] coordinates of collision point"
    }
  }, "propertyOrdering":
  ["reasoning", "willCollide", "collidingPair", "collisionTime", "collisionPoint"], "required":
  ["reasoning", "willCollide", "collidingPair", "collisionTime",
   "collisionPoint"], "additionalProperties": False
}


def find_collision_time(obj1, obj2):
  """
    Find collision time between two moving spheres.
    Returns (collision_time, collision_point) or (None, None) if no collision.
    """
  # Position: p1 + v1*t, p2 + v2*t
  # Distance squared: |p1 + v1*t - p2 - v2*t|^2
  # = |dp + dv*t|^2 where dp = p1-p2, dv = v1-v2
  # = |dp|^2 + 2*dp·dv*t + |dv|^2*t^2
  # Collision when distance = r1 + r2

  p1, v1, r1 = obj1["pos"], obj1["vel"], obj1["radius"]
  p2, v2, r2 = obj2["pos"], obj2["vel"], obj2["radius"]

  dp = [p1[i] - p2[i] for i in range(3)]
  dv = [v1[i] - v2[i] for i in range(3)]

  # Quadratic: a*t^2 + b*t + c = 0 where we want |dp + dv*t|^2 = (r1+r2)^2
  a = sum(dv[i]**2 for i in range(3))
  b = 2 * sum(dp[i] * dv[i] for i in range(3))
  c = sum(dp[i]**2 for i in range(3)) - (r1 + r2)**2

  if a < 1e-12:  # Objects moving parallel or both stationary
    if c <= 0:  # Already colliding at t=0
      return 0, [(p1[i] + p2[i]) / 2 for i in range(3)]
    return None, None

  discriminant = b**2 - 4 * a * c

  if discriminant < 0:
    return None, None  # No collision

  sqrt_disc = math.sqrt(discriminant)
  t1 = (-b - sqrt_disc) / (2 * a)
  t2 = (-b + sqrt_disc) / (2 * a)

  # Take earliest positive time
  if t1 >= 0:
    t = t1
  elif t2 >= 0:
    t = t2
  else:
    return None, None  # Collision was in the past

  # Calculate collision point (midpoint between sphere centers at collision time)
  pos1_at_t = [p1[i] + v1[i] * t for i in range(3)]
  pos2_at_t = [p2[i] + v2[i] * t for i in range(3)]
  collision_point = [(pos1_at_t[i] + pos2_at_t[i]) / 2 for i in range(3)]

  return t, collision_point


def analyze_problem(objects):
  """Find the first collision among all object pairs."""
  first_collision_time = float('inf')
  first_pair = None
  first_point = None

  for i in range(len(objects)):
    for j in range(i + 1, len(objects)):
      t, point = find_collision_time(objects[i], objects[j])
      if t is not None and t < first_collision_time:
        first_collision_time = t
        first_pair = [i + 1, j + 1]  # 1-indexed
        first_point = point

  if first_pair is None:
    return False, None, None, None

  return True, first_pair, first_collision_time, first_point


# Define problems
problems = [
  {
    "name":
    "Head-on collision", "objects": [
      {"pos": [0, 0, 0], "vel": [10, 0, 0], "radius": 1},
      {"pos": [100, 0, 0], "vel": [-10, 0, 0], "radius": 1},
    ], "description":
    """
Object 1: Sphere with radius 1m at (0, 0, 0), moving with velocity (10, 0, 0) m/s
Object 2: Sphere with radius 1m at (100, 0, 0), moving with velocity (-10, 0, 0) m/s
"""
  },
  {
    "name":
    "Near miss", "objects": [
      {"pos": [0, 0, 0], "vel": [10, 0, 0], "radius": 1},
      {"pos": [50, 3, 0], "vel": [-10, 0, 0], "radius": 1},
    ], "description":
    """
Object 1: Sphere with radius 1m at (0, 0, 0), moving with velocity (10, 0, 0) m/s
Object 2: Sphere with radius 1m at (50, 3, 0), moving with velocity (-10, 0, 0) m/s
"""
  },
  {
    "name":
    "Three objects - one collision", "objects": [
      {"pos": [0, 0, 0], "vel": [5, 5, 0], "radius": 2},
      {"pos": [100, 0, 0], "vel": [-5, 5, 0], "radius": 2},
      {"pos": [50, 200, 0], "vel": [0, -10, 0], "radius": 2},
    ], "description":
    """
Object 1: Sphere with radius 2m at (0, 0, 0), moving with velocity (5, 5, 0) m/s
Object 2: Sphere with radius 2m at (100, 0, 0), moving with velocity (-5, 5, 0) m/s
Object 3: Sphere with radius 2m at (50, 200, 0), moving with velocity (0, -10, 0) m/s
"""
  },
  {
    "name":
    "Pursuit collision", "objects": [
      {"pos": [0, 0, 0], "vel": [20, 0, 0], "radius": 1.5},
      {"pos": [50, 0, 0], "vel": [10, 0, 0], "radius": 1.5},
    ], "description":
    """
Object 1: Sphere with radius 1.5m at (0, 0, 0), moving with velocity (20, 0, 0) m/s
Object 2: Sphere with radius 1.5m at (50, 0, 0), moving with velocity (10, 0, 0) m/s

(Object 1 is chasing Object 2 from behind)
"""
  },
  {
    "name":
    "Complex 3D trajectories", "objects": [
      {"pos": [0, 0, 0], "vel": [10, 5, 3], "radius": 2},
      {"pos": [50, 25, 15], "vel": [-5, -2.5, -1.5], "radius": 2},
      {"pos": [100, 0, 50], "vel": [-10, 5, -5], "radius": 3},
      {"pos": [-50, 50, 0], "vel": [15, -5, 5], "radius": 1},
    ], "description":
    """
Object 1: Sphere with radius 2m at (0, 0, 0), moving with velocity (10, 5, 3) m/s
Object 2: Sphere with radius 2m at (50, 25, 15), moving with velocity (-5, -2.5, -1.5) m/s
Object 3: Sphere with radius 3m at (100, 0, 50), moving with velocity (-10, 5, -5) m/s
Object 4: Sphere with radius 1m at (-50, 50, 0), moving with velocity (15, -5, 5) m/s
"""
  },
]

# === SUPER-HARD CHALLENGES ===
# Many objects with complex trajectories


def generate_collision_problem(num_objects, seed, space_size=200):
  """Generate a random collision problem with many objects."""
  random.seed(seed)

  objects = []
  for i in range(num_objects):
    # Random position in space
    pos = [
      random.uniform(-space_size, space_size),
      random.uniform(-space_size, space_size),
      random.uniform(-space_size, space_size)
    ]

    # Random velocity (some objects faster than others)
    speed = random.uniform(5, 30)
    direction = [random.uniform(-1, 1) for _ in range(3)]
    mag = math.sqrt(sum(d**2 for d in direction))
    vel = [d / mag * speed for d in direction] if mag > 0.01 else [speed, 0, 0]

    # Random radius
    radius = random.uniform(1, 5)

    objects.append({"pos": pos, "vel": vel, "radius": radius})

  return objects


def format_collision_description(objects):
  """Format objects for the prompt."""
  desc = ""
  for i, obj in enumerate(objects):
    desc += f"\nObject {i+1}: Sphere with radius {obj['radius']:.1f}m "
    desc += f"at ({obj['pos'][0]:.1f}, {obj['pos'][1]:.1f}, {obj['pos'][2]:.1f}), "
    desc += f"moving with velocity ({obj['vel'][0]:.2f}, {obj['vel'][1]:.2f}, {obj['vel'][2]:.2f}) m/s"
  return desc


# Generate hard problems
hard_collision_data = [
  (8, 88801),
  (12, 88802),
  (15, 88803),
]

for num_obj, seed in hard_collision_data:
  objs = generate_collision_problem(num_obj, seed)
  problems.append({
    "name": f"{num_obj} objects chaotic motion - HARD", "objects": objs, "description":
    format_collision_description(objs)
  })

# Add a specific complex scenario with near-simultaneous collisions
problems.append({
  "name":
  "Near-simultaneous collisions - HARD", "objects": [
    {"pos": [0, 0, 0], "vel": [10, 0, 0], "radius": 2},
    {"pos": [100, 0, 0], "vel": [-10, 0, 0], "radius": 2},
    {"pos": [0, 100, 0], "vel": [0, -10, 0], "radius": 2},
    {"pos": [0, -100, 0], "vel": [0, 10, 0], "radius": 2},
    {"pos": [50, 50, 0], "vel": [-5, -5, 0], "radius": 3},
    {"pos": [-50, 50, 50], "vel": [5, -5, -5], "radius": 2.5},
    {"pos": [50, -50, 50], "vel": [-5, 5, -5], "radius": 2.5},
    {"pos": [-50, -50, -50], "vel": [5, 5, 5], "radius": 2},
  ], "description":
  """
Object 1: Sphere r=2m at (0, 0, 0), velocity (10, 0, 0) m/s
Object 2: Sphere r=2m at (100, 0, 0), velocity (-10, 0, 0) m/s
Object 3: Sphere r=2m at (0, 100, 0), velocity (0, -10, 0) m/s
Object 4: Sphere r=2m at (0, -100, 0), velocity (0, 10, 0) m/s
Object 5: Sphere r=3m at (50, 50, 0), velocity (-5, -5, 0) m/s
Object 6: Sphere r=2.5m at (-50, 50, 50), velocity (5, -5, -5) m/s
Object 7: Sphere r=2.5m at (50, -50, 50), velocity (-5, 5, -5) m/s
Object 8: Sphere r=2.5m at (-50, -50, -50), velocity (5, 5, 5) m/s

Multiple pairs are on collision courses. Which pair collides FIRST?
"""
})

# Add orbital-like crossing paths
problems.append({
  "name":
  "Orbital crossing paths - HARD", "objects": [
    {"pos": [100, 0, 0], "vel": [0, 20, 5], "radius": 3},
    {"pos": [0, 100, 0], "vel": [20, 0, -5], "radius": 3},
    {"pos": [-100, 0, 0], "vel": [0, -20, 5], "radius": 3},
    {"pos": [0, -100, 0], "vel": [-20, 0, -5], "radius": 3},
    {"pos": [70, 70, 50], "vel": [-14, -14, -10], "radius": 4},
    {"pos": [-70, 70, -50], "vel": [14, -14, 10], "radius": 4},
    {"pos": [70, -70, -50], "vel": [-14, 14, 10], "radius": 4},
    {"pos": [-70, -70, 50], "vel": [14, 14, -10], "radius": 4},
    {"pos": [0, 0, 100], "vel": [0, 0, -25], "radius": 5},
    {"pos": [0, 0, -100], "vel": [0, 0, 25], "radius": 5},
  ], "description":
  """
Object 1: Sphere r=3m at (100, 0, 0), velocity (0, 20, 5) m/s
Object 2: Sphere r=3m at (0, 100, 0), velocity (20, 0, -5) m/s
Object 3: Sphere r=3m at (-100, 0, 0), velocity (0, -20, 5) m/s
Object 4: Sphere r=3m at (0, -100, 0), velocity (-20, 0, -5) m/s
Object 5: Sphere r=4m at (70, 70, 50), velocity (-14, -14, -10) m/s
Object 6: Sphere r=4m at (-70, 70, -50), velocity (14, -14, 10) m/s
Object 7: Sphere r=4m at (70, -70, -50), velocity (-14, 14, 10) m/s
Object 8: Sphere r=4m at (-70, -70, 50), velocity (14, 14, -10) m/s
Object 9: Sphere r=5m at (0, 0, 100), velocity (0, 0, -25) m/s
Object 10: Sphere r=5m at (0, 0, -100), velocity (0, 0, 25) m/s

Objects moving in complex crossing patterns. Find the first collision.
"""
})

# Pre-compute expected answers
for prob in problems:
  will_collide, pair, time, point = analyze_problem(prob["objects"])
  prob["will_collide"] = will_collide
  prob["pair"] = pair
  prob["time"] = time
  prob["point"] = point

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Various collision scenarios in 3D"


def prepareSubpassPrompt(index: int) -> str:

  if index >= len(problems):
    raise StopIteration
  return prompt.replace("OBJECTS_DESCRIPTION", problems[index]["description"])


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  prob = problems[subPass]

  score = 0
  details = []

  # Check collision prediction (worth 0.3)
  will_collide = answer.get("willCollide", None)
  if will_collide == prob["will_collide"]:
    score += 0.3
    details.append(f"Collision prediction correct: {will_collide}")
  else:
    details.append(
      f"Collision prediction wrong: got {will_collide}, expected {prob['will_collide']}")

  if not prob["will_collide"]:
    # No collision expected - other fields don't matter
    if not will_collide:
      score += 0.7  # Full credit for correctly saying no collision
    return score, "<br>".join(details)

  # Check colliding pair (worth 0.2)
  pair = answer.get("collidingPair", [])
  expected_pair = prob["pair"]
  if isinstance(pair, list) and sorted(pair) == sorted(expected_pair):
    score += 0.2
    details.append(f"Colliding pair correct: {pair}")
  else:
    details.append(f"Colliding pair wrong: got {pair}, expected {expected_pair}")

  # Check collision time (worth 0.25)
  time = answer.get("collisionTime", None)
  expected_time = prob["time"]
  if time is not None and expected_time is not None:
    time_error = abs(time - expected_time)
    tolerance = max(0.1, 0.05 * expected_time)  # 5% or 0.1s

    if time_error <= tolerance:
      score += 0.25
      details.append(f"Collision time correct: {time:.3f}s")
    else:
      # Partial credit
      partial = max(0, 0.25 * (1 - time_error / expected_time))
      score += partial
      details.append(f"Collision time off: got {time:.3f}s, expected {expected_time:.3f}s")
  else:
    details.append(f"Collision time: got {time}, expected {expected_time}")

  # Check collision point (worth 0.25)
  point = answer.get("collisionPoint", None)
  expected_point = prob["point"]
  if isinstance(point, list) and len(point) >= 3 and expected_point:
    dist = math.sqrt(sum((point[i] - expected_point[i])**2 for i in range(3)))
    tolerance = 2.0  # Allow 2m error

    if dist <= tolerance:
      score += 0.25
      details.append(f"Collision point correct: {point}")
    else:
      partial = max(0, 0.25 * (1 - dist / 20))
      score += partial
      details.append(f"Collision point off by {dist:.2f}m: got {point}, expected {expected_point}")
  else:
    details.append(f"Collision point: got {point}, expected {expected_point}")

  return score, "<br>".join(details)


def generate_collision_scene_scad(prob):
  """Generate OpenSCAD code for collision visualization."""
  objects = prob["objects"]

  # Analyze all pairs to determine collision status
  collision_info = {}  # (i, j) -> time or None
  for i in range(len(objects)):
    for j in range(i + 1, len(objects)):
      t, point = find_collision_time(objects[i], objects[j])
      collision_info[(i, j)] = t

  # Find first collision
  first_pair = None
  first_time = float('inf')
  for pair, t in collision_info.items():
    if t is not None and t < first_time:
      first_time = t
      first_pair = pair

  # Determine color for each object based on collision status
  obj_colors = {}
  for i in range(len(objects)):
    obj_colors[i] = [0.2, 0.8, 0.2]  # Default green (safe)

    # Check if involved in any collision
    for (obj_i, obj_j), t in collision_info.items():
      if t is not None and (i == obj_i or i == obj_j):
        if (obj_i, obj_j) == first_pair:
          # First collision - red
          obj_colors[i] = [1.0, 0.2, 0.2]
          break
        else:
          # Will collide but not first - yellow
          obj_colors[i] = [1.0, 0.8, 0.2]

  scad = "// Collision scene visualization\n"
  scad += "$fn = 32;\n"

  # Draw each object
  for i, obj in enumerate(objects):
    pos = obj["pos"]
    radius = obj["radius"]
    vel = obj["vel"]
    color = obj_colors[i]

    # Draw sphere
    scad += f"// Object {i+1}\n"
    scad += f"color([{color[0]}, {color[1]}, {color[2]}, 0.7]) "
    scad += f"translate([{pos[0]}, {pos[1]}, {pos[2]}]) sphere(r={radius});\n"

    # Draw velocity vector as arrow
    vel_mag = math.sqrt(sum(v**2 for v in vel))
    if vel_mag > 0.1:
      # Arrow length proportional to velocity (scaled for visibility)
      arrow_len = min(vel_mag * 0.5, 30)  # Cap at 30 for visibility
      vel_norm = [v / vel_mag for v in vel]

      # Arrow endpoint
      arrow_end = [pos[i] + vel_norm[i] * arrow_len for i in range(3)]

      # Draw arrow shaft as thin cylinder
      # Calculate rotation to align with velocity vector
      theta = math.degrees(math.acos(vel_norm[2])) if abs(vel_norm[2]) <= 1 else 0
      phi = math.degrees(math.atan2(vel_norm[1], vel_norm[0]))

      scad += f"color([{color[0]}, {color[1]}, {color[2]}, 0.5]) "
      scad += f"translate([{pos[0]}, {pos[1]}, {pos[2]}]) "
      scad += f"rotate([0, {theta}, {phi}]) "
      scad += f"cylinder(r={radius*0.1}, h={arrow_len});\n"

      # Arrow head as cone
      scad += f"color([{color[0]}, {color[1]}, {color[2]}, 0.5]) "
      scad += f"translate([{arrow_end[0]}, {arrow_end[1]}, {arrow_end[2]}]) "
      scad += f"rotate([0, {theta}, {phi}]) "
      scad += f"cylinder(r1={radius*0.3}, r2=0, h={radius*0.6});\n"

    # Label
    scad += f"color([1, 1, 1]) translate([{pos[0]}, {pos[1]}, {pos[2] + radius + 2}]) "
    scad += f"linear_extrude(0.1) text(\"{i+1}\", size={radius*0.6}, halign=\"center\");\n"

  # If there's a collision, draw the collision point
  if first_pair and first_time < float('inf'):
    obj_i, obj_j = first_pair
    t, point = find_collision_time(objects[obj_i], objects[obj_j])
    if point:
      scad += f"// Collision point\n"
      scad += f"color([1, 0, 0, 0.8]) translate([{point[0]}, {point[1]}, {point[2]}]) "
      scad += f"sphere(r=2);\n"

  return scad


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
  import VolumeComparison as vc
  import os

  prob = problems[subPass]

  # Generate visualization
  vis_html = ""
  try:
    scad = generate_collision_scene_scad(prob)
    output_path = f"results/39_{subPass}_{aiEngineName}_scene.png"

    # Calculate camera position based on object positions
    all_pos = [obj["pos"] for obj in prob["objects"]]
    center_x = sum(p[0] for p in all_pos) / len(all_pos)
    center_y = sum(p[1] for p in all_pos) / len(all_pos)
    center_z = sum(p[2] for p in all_pos) / len(all_pos)

    # Find max extent for camera distance
    max_dist = max(
      math.sqrt(sum((p[i] - [center_x, center_y, center_z][i])**2 for i in range(3)))
      for p in all_pos)
    cam_dist = max(max_dist * 3, 100)

    camera_arg = f"--camera={center_x + cam_dist},{center_y - cam_dist},{center_z + cam_dist},{center_x},{center_y},{center_z}"
    vc.render_scadText_to_png(scad, output_path, cameraArg=camera_arg)
    vis_html = f'<img src="{os.path.basename(output_path)}" />'
  except Exception as e:
    vis_html = f"<i>Visualization error: {e}</i>"

  # Text content in left column
  html = "<td><b>Your answer:</b><br>"
  html += f"Will Collide: {answer.get('willCollide', 'not provided')}<br>"
  html += f"Colliding Pair: {answer.get('collidingPair', 'not provided')}<br>"
  html += f"Collision Time: {answer.get('collisionTime', 'not provided')}<br>"
  html += f"Collision Point: {answer.get('collisionPoint', 'not provided')}<br>"

  html += "<br><b>Expected:</b><br>"
  html += f"Will Collide: {prob['will_collide']}<br>"
  html += f"Colliding Pair: {prob['pair']}<br>"
  if prob['time']:
    html += f"Collision Time: {prob['time']:.3f}s<br>"
  if prob['point']:
    html += f"Collision Point: {[round(c, 2) for c in prob['point']]}<br>"

  html += "<br><b>Legend:</b><br>"
  html += "<span style='color:red'>●</span> Red = Colliding pair (first)<br>"
  html += "<span style='color:orange'>●</span> Yellow = Will collide (later)<br>"
  html += "<span style='color:green'>●</span> Green = Safe (no collision)<br>"

  html += f"</td><td>{vis_html}</td>"

  return html


highLevelSummary = """
Tests ability to predict collisions between moving objects in 3D space.
<br><br>
Key concepts:
<ul>
<li>Relative motion between objects</li>
<li>Solving quadratic equations for collision time</li>
<li>Understanding near misses vs actual collisions</li>
<li>Finding earliest collision among multiple pairs</li>
</ul>
This is fundamental for physics simulations, games, robotics, and autonomous navigation.
"""

if __name__ == "__main__":
  print(
    resultToNiceReport(
      {
        'reasoning':
        'To determine if two spheres collide, the distance between their centers must be less than or equal to the sum of their radii. Since both objects are spheres with a radius of 1m, the condition for collision is that the distance between their centers is at most 2m. Object 1 is moving in the positive x-direction at 10 m/s, while Object 2 is moving in the negative x-direction at 10 m/s. The relative velocity between them is 20 m/s (10 m/s + 10 m/s). The initial distance between their centers is 100 m. To calculate the time at which they collide, we solve for t in the equation: distance - (relative velocity * t) = 2m. Solving for t gives us t = (100 - 2) / 20 = 4.9 seconds. At this time, the position of the collision in the x-direction can be calculated for either object. For Object 1, x = 0 + 10 * 4.9 = 49 m. The y and z values remain 0 since both objects are only moving along the x-axis. Therefore, the collision occurs at (49, 0, 0)',
        'willCollide': True, 'collidingPair': [1, 2], 'collisionTime': 4.9, 'collisionPoint':
        [49, 0, 0]
      }, 0, "blah"))
