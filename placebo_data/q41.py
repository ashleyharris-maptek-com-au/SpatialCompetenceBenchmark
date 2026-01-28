import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    # Pentagram with center spokes
    # 5 vertices on circle of radius 50 centered at (50,50)
    # Laser starts at center (50,50) going down (0,-1)

    center = [50.0, 50.0]
    radius = 50.0

    # Calculate 5 vertices (starting at bottom, going counterclockwise)
    vertices = []
    for i in range(5):
      angle = -math.pi / 2 + i * (2 * math.pi / 5)
      vertices.append([center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)])
    # V0 = (50, 0) bottom
    # V1 = (~97.5, ~34.5) lower right
    # V2 = (~79.4, ~90.5) upper right
    # V3 = (~20.6, ~90.5) upper left
    # V4 = (~2.4, ~34.5) lower left

    def normalize(v):
      length = math.sqrt(v[0]**2 + v[1]**2)
      return [v[0] / length, v[1] / length]

    # Angles from center to each vertex
    vertex_angles = []
    for v in vertices:
      vertex_angles.append(math.atan2(v[1] - center[1], v[0] - center[0]))

    # Incoming beam direction is (0, -1), angle = -90°
    incoming_angle = -math.pi / 2

    # Place beam splitters SPACED OUT along the downward path
    # This prevents reflected beams from hitting other splitters
    beam_splitters = []

    # Splitters close to center, but spaced enough to avoid cross-reflections
    # Upper beams first (go up, won't hit lower splitters)
    # Using 0.5 unit spacing for tighter clustering near center
    splitter_configs = [
      (2, 49.5),  # V2 (upper right) at y=49.5
      (3, 49.0),  # V3 (upper left) at y=49.0
      (1, 48.5),  # V1 (lower right) at y=48.5
      (4, 48.0),  # V4 (lower left) at y=48.0
    ]

    for vi, y_pos in splitter_configs:
      splitter_pos = [center[0], y_pos]
      target_vertex = vertices[vi]
      # Calculate angle from splitter position to target vertex
      dx = target_vertex[0] - splitter_pos[0]
      dy = target_vertex[1] - splitter_pos[1]
      target_angle = math.atan2(dy, dx)
      normal_angle = (incoming_angle + target_angle) / 2 + math.pi / 2
      beam_splitters.append({
        "position": splitter_pos,
        "normal": [math.cos(normal_angle), math.sin(normal_angle)]
      })

    # Mirrors at each vertex to reflect incoming beams toward next vertex
    # Each vertex receives a beam from a specific splitter position
    splitter_sources = {
      0: [50.0, 48.0],  # V0 receives from last splitter (beam continues down)
      1: [50.0, 48.5],  # V1 receives from splitter at y=48.5
      2: [50.0, 49.5],  # V2 receives from splitter at y=49.5
      3: [50.0, 49.0],  # V3 receives from splitter at y=49.0
      4: [50.0, 48.0],  # V4 receives from splitter at y=48.0
    }

    mirrors = []

    for i in range(5):
      v = vertices[i]
      next_v = vertices[(i + 1) % 5]
      source = splitter_sources[i]

      # Incoming direction: from splitter source to this vertex
      incoming_dir = normalize([v[0] - source[0], v[1] - source[1]])
      incoming_ang = math.atan2(incoming_dir[1], incoming_dir[0])

      # Outgoing direction: from this vertex to next vertex
      outgoing_dir = normalize([next_v[0] - v[0], next_v[1] - v[1]])
      outgoing_ang = math.atan2(outgoing_dir[1], outgoing_dir[0])

      # Mirror normal bisects incoming and outgoing, rotated 90°
      normal_angle = (incoming_ang + outgoing_ang) / 2 + math.pi / 2

      mirrors.append({"position": v, "normal": [math.cos(normal_angle), math.sin(normal_angle)]})

    return {"reasoning": "", "beamSplitters": beam_splitters, "mirrors": mirrors}, ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  beam_splitters = []
  mirrors = []
  for _ in range(4):
    beam_splitters.append({
      "position": [rng.uniform(0.0, 100.0), rng.uniform(0.0, 100.0)],
      "normal": [rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)],
    })
  for _ in range(6):
    mirrors.append({
      "position": [rng.uniform(0.0, 100.0), rng.uniform(0.0, 100.0)],
      "normal": [rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)],
    })
  return {
    "reasoning": "Random guess",
    "beamSplitters": beam_splitters,
    "mirrors": mirrors
  }, "Random guess"
