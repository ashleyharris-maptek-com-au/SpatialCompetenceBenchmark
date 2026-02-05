import numpy as np
import math
import os

title = "Can you create build instructions for 3D structures?"
skip = True

# Connector definitions: which sockets each part type has
CONNECTOR_SOCKETS = {
  "P101": ["X+", "X-"],  # Inline extension
  "P102": ["X+", "Y+"],  # 90-degree elbow
  "P103": ["X+", "X-", "Y+"],  # T-junction
  "P104": ["X+", "Y+", "Z+"],  # 3-way corner
  "P105": ["X+", "X-", "Y+", "Y-"],  # Planar cross
  "P106": ["X+", "X-", "Y+", "Z+"],  # 3-way through corner
  "P107": ["X+", "X-", "Y+", "Y-", "Z+"],  # 5-way interior
  "P108": ["X+", "X-", "Y+", "Y-", "Z+", "Z-"],  # 6-way join
}

# Direction vectors for each socket label (in connector's local frame)
DIRECTION_VECTORS = {
  "X+": np.array([1, 0, 0]),
  "X-": np.array([-1, 0, 0]),
  "Y+": np.array([0, 1, 0]),
  "Y-": np.array([0, -1, 0]),
  "Z+": np.array([0, 0, 1]),
  "Z-": np.array([0, 0, -1]),
}

EXTRUSION_LENGTH = 1.0  # 1 meter


def rotation_matrix_from_vectors(from_vec, to_vec):
  """Create rotation matrix that rotates from_vec to to_vec."""
  from_vec = from_vec / np.linalg.norm(from_vec)
  to_vec = to_vec / np.linalg.norm(to_vec)

  if np.allclose(from_vec, to_vec):
    return np.eye(3)
  if np.allclose(from_vec, -to_vec):
    # 180 degree rotation - find perpendicular axis
    perp = np.array([1, 0, 0]) if abs(from_vec[0]) < 0.9 else np.array([0, 1, 0])
    axis = np.cross(from_vec, perp)
    axis = axis / np.linalg.norm(axis)
    # Rodrigues' rotation formula for 180 degrees
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + 2 * K @ K

  cross = np.cross(from_vec, to_vec)
  dot = np.dot(from_vec, to_vec)
  skew = np.array([[0, -cross[2], cross[1]], [cross[2], 0, -cross[0]], [-cross[1], cross[0], 0]])
  return np.eye(3) + skew + skew @ skew * (1 / (1 + dot))


def rotation_around_axis(axis, angle):
  """Create rotation matrix around given axis by angle (radians)."""
  axis = axis / np.linalg.norm(axis)
  K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
  return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K


def get_perpendicular_dirs(socket_label):
  """Get the valid perpendicular directions for white face given socket direction."""
  axis = socket_label[0]  # X, Y, or Z
  if axis == "X":
    return ["Y+", "Y-", "Z+", "Z-"]
  elif axis == "Y":
    return ["X+", "X-", "Z+", "Z-"]
  else:  # Z
    return ["X+", "X-", "Y+", "Y-"]


def opposite_socket(socket_label):
  """Get the opposite socket label (X+ -> X-, etc.)."""
  axis, sign = socket_label[0], socket_label[1]
  return axis + ("-" if sign == "+" else "+")


class AssemblyError(Exception):
  """Error during assembly validation."""
  pass


class ExtrusionAssembly:
  """
  Walks the connector graph and builds 3D geometry.
  """

  def __init__(self, connectors_data):
    self.connectors_data = connectors_data
    self.extrusion_endpoints = {}  # extrusion_id -> [(connector_idx, socket, white_dir), ...]
    self.connector_positions = {}  # connector_idx -> (position, rotation_matrix)
    self.extrusion_geometry = {}  # extrusion_id -> (start_pos, end_pos, white_dir_world)
    self.errors = []

  def build_extrusion_map(self):
    """Build map of which connectors attach to each extrusion."""
    for conn_idx, connector in enumerate(self.connectors_data):
      part_num = connector.get("partNumber", "")
      connections = connector.get("connections", [])

      # Validate part number
      if part_num not in CONNECTOR_SOCKETS:
        self.errors.append(f"Connector {conn_idx}: Unknown part number '{part_num}'")
        continue

      valid_sockets = CONNECTOR_SOCKETS[part_num]

      for conn in connections:
        socket = conn.get("label", "")
        ext_id = conn.get("extrusionNumber", -1)
        white_dir = conn.get("orientationOfWhiteSide", "")

        # Validate socket
        if socket not in valid_sockets:
          self.errors.append(
            f"Connector {conn_idx} ({part_num}): Invalid socket '{socket}', valid: {valid_sockets}")
          continue

        # Validate white direction is perpendicular to socket
        valid_white = get_perpendicular_dirs(socket)
        if white_dir not in valid_white:
          self.errors.append(
            f"Connector {conn_idx}, socket {socket}: White direction '{white_dir}' not perpendicular, valid: {valid_white}"
          )
          continue

        if ext_id not in self.extrusion_endpoints:
          self.extrusion_endpoints[ext_id] = []

        self.extrusion_endpoints[ext_id].append((conn_idx, socket, white_dir))

    # Validate each extrusion has exactly 2 endpoints
    for ext_id, endpoints in self.extrusion_endpoints.items():
      if len(endpoints) < 2:
        self.errors.append(f"Extrusion {ext_id}: Only has {len(endpoints)} endpoint(s), needs 2")
      elif len(endpoints) > 2:
        self.errors.append(f"Extrusion {ext_id}: Has {len(endpoints)} endpoints, max is 2")

    return len(self.errors) == 0

  def walk_graph(self):
    """Walk the connector graph, placing each connector in world coordinates."""
    if not self.connectors_data:
      self.errors.append("No connectors provided")
      return False

    # Start with first connector at origin, identity rotation
    self.connector_positions[0] = (np.array([0.0, 0.0, 0.0]), np.eye(3))

    visited_connectors = {0}
    queue = [0]
    placed_extrusions = set()
    occupied_cells = {}  # grid position -> extrusion_id (for intersection detection)

    while queue:
      conn_idx = queue.pop(0)
      conn_pos, conn_rot = self.connector_positions[conn_idx]
      connector = self.connectors_data[conn_idx]

      for conn in connector.get("connections", []):
        socket = conn.get("label", "")
        ext_id = conn.get("extrusionNumber", -1)
        white_dir = conn.get("orientationOfWhiteSide", "")

        if ext_id in placed_extrusions:
          continue

        if ext_id not in self.extrusion_endpoints:
          continue

        endpoints = self.extrusion_endpoints[ext_id]
        if len(endpoints) != 2:
          continue

        # Find the other endpoint of this extrusion
        other_endpoint = None
        for ep in endpoints:
          if ep[0] != conn_idx or ep[1] != socket:
            other_endpoint = ep
            break

        if other_endpoint is None:
          # Same connector, different socket (loop back)
          for ep in endpoints:
            if ep[1] != socket:
              other_endpoint = ep
              break

        if other_endpoint is None:
          self.errors.append(f"Extrusion {ext_id}: Cannot find other endpoint")
          continue

        other_conn_idx, other_socket, other_white_dir = other_endpoint

        # Calculate extrusion geometry
        # Socket direction in world coordinates
        local_socket_dir = DIRECTION_VECTORS[socket]
        world_socket_dir = conn_rot @ local_socket_dir

        # Extrusion starts at connector and goes in socket direction
        start_pos = conn_pos
        end_pos = conn_pos + world_socket_dir * EXTRUSION_LENGTH

        # White direction in world
        local_white_dir = DIRECTION_VECTORS[white_dir]
        world_white_dir = conn_rot @ local_white_dir

        self.extrusion_geometry[ext_id] = (start_pos.copy(), end_pos.copy(), world_white_dir.copy())
        placed_extrusions.add(ext_id)

        # Check for self-intersection (check midpoints only, not endpoints since those meet at connectors)
        # Sample points along the extrusion (excluding very near endpoints)
        for t in [0.25, 0.5, 0.75]:
          sample_pos = start_pos + (end_pos - start_pos) * t
          grid_pos = tuple(np.round(sample_pos * 4).astype(int))  # Finer grid

          if grid_pos in occupied_cells and occupied_cells[grid_pos] != ext_id:
            self.errors.append(
              f"Extrusion {ext_id} intersects with extrusion {occupied_cells[grid_pos]}")
          occupied_cells[grid_pos] = ext_id

        # Validate or place the other connector
        if other_conn_idx in visited_connectors:
          # Other connector already placed - verify the extrusion actually reaches it
          other_pos, other_rot = self.connector_positions[other_conn_idx]

          # Check that extrusion end matches the other connector's position
          if not np.allclose(end_pos, other_pos, atol=0.01):
            self.errors.append(
              f"Extrusion {ext_id} endpoint mismatch: connector {other_conn_idx} at "
              f"({other_pos[0]:.2f}, {other_pos[1]:.2f}, {other_pos[2]:.2f}) but extrusion ends at "
              f"({end_pos[0]:.2f}, {end_pos[1]:.2f}, {end_pos[2]:.2f})")

          # Also verify the other connector's socket points back along the extrusion
          other_local_socket_dir = DIRECTION_VECTORS[other_socket]
          other_world_socket_dir = other_rot @ other_local_socket_dir
          expected_dir = -world_socket_dir  # Should point back towards this connector

          if not np.allclose(other_world_socket_dir, expected_dir, atol=0.01):
            self.errors.append(
              f"Extrusion {ext_id}: connector {other_conn_idx}'s socket {other_socket} points wrong direction"
            )

        elif other_conn_idx not in visited_connectors:
          # The other connector's socket points back along the extrusion
          # So its socket direction should be opposite to world_socket_dir
          other_local_socket_dir = DIRECTION_VECTORS[other_socket]

          # Build rotation for other connector:
          # 1. Its socket should point opposite to world_socket_dir
          # 2. Its white direction should match the extrusion's white direction

          # First, rotate so other socket points correctly
          target_socket_dir = -world_socket_dir
          rot1 = rotation_matrix_from_vectors(other_local_socket_dir, target_socket_dir)

          # Now align the white direction
          other_local_white = DIRECTION_VECTORS[other_white_dir]
          current_white = rot1 @ other_local_white

          # We need to rotate around the socket axis to align white
          # Both world_white_dir and current_white should be perpendicular to target_socket_dir
          if not np.allclose(current_white, world_white_dir):
            # Compute angle between current_white and world_white_dir in the plane perpendicular to socket
            dot = np.clip(np.dot(current_white, world_white_dir), -1, 1)
            cross = np.cross(current_white, world_white_dir)
            angle = np.arccos(dot)
            if np.dot(cross, target_socket_dir) < 0:
              angle = -angle
            rot2 = rotation_around_axis(target_socket_dir, angle)
            final_rot = rot2 @ rot1
          else:
            final_rot = rot1

          self.connector_positions[other_conn_idx] = (end_pos.copy(), final_rot)
          visited_connectors.add(other_conn_idx)
          queue.append(other_conn_idx)

    # Check if all connectors were placed
    for i in range(len(self.connectors_data)):
      if i not in visited_connectors:
        self.errors.append(f"Connector {i} is not connected to the main structure")

    return len(self.errors) == 0

  def find_stable_orientation(self):
    """
    Find the most stable orientation:
    - Lowest center of mass
    - Widest ground contact (convex hull area of points touching ground)
    Returns rotation matrix to apply.
    """
    if not self.extrusion_geometry:
      return np.eye(3), 0

    # Collect all endpoints
    all_points = []
    for ext_id, (start, end, _) in self.extrusion_geometry.items():
      all_points.append(start)
      all_points.append(end)

    all_points = np.array(all_points)

    # Try 6 principal orientations (each face down)
    best_score = float('-inf')
    best_rotation = np.eye(3)

    orientations = [
      np.eye(3),  # Z down (as-is)
      rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array([0, 0, -1])),  # Z up
      rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array([1, 0, 0])),  # X down
      rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array([-1, 0, 0])),  # -X down
      rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array([0, 1, 0])),  # Y down
      rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array([0, -1, 0])),  # -Y down
    ]

    for rot in orientations:
      rotated = (rot @ all_points.T).T

      # Find ground level (minimum z)
      min_z = rotated[:, 2].min()

      # Find points on ground (within tolerance)
      ground_points = rotated[rotated[:, 2] < min_z + 0.01]

      if len(ground_points) < 2:
        continue

      # Calculate convex hull area of ground contact
      if len(ground_points) >= 3:
        from scipy.spatial import ConvexHull
        try:
          hull = ConvexHull(ground_points[:, :2])
          contact_area = hull.volume  # In 2D, volume is area
        except:
          contact_area = 0
      else:
        # Line contact
        contact_area = np.linalg.norm(ground_points[0, :2] - ground_points[1, :2]) * 0.001

      # Center of mass height
      com_z = rotated[:, 2].mean()
      height_range = rotated[:, 2].max() - min_z

      # Score: maximize contact area, minimize COM height
      # Normalize COM by height range
      normalized_com = (com_z - min_z) / (height_range + 0.001)
      score = contact_area * 10 - normalized_com

      if score > best_score:
        best_score = score
        best_rotation = rot

    return best_rotation, best_score

  def to_scad(self, rotation=None):
    """Generate OpenSCAD code for the assembly."""
    if rotation is None:
      rotation = np.eye(3)

    scad = "// Auto-generated extrusion assembly\n"
    scad += "$fn = 20;\n\n"

    # Extrusion module
    scad += """
module extrusion_2020(length) {
  // 20mm x 20mm extrusion, colored faces
  translate([0, 0, length/2])
  difference() {
    cube([0.02, 0.02, length], center=true);
    // Hollow out slightly for visual effect
    cube([0.016, 0.016, length+0.001], center=true);
  }
}

module colored_extrusion(start, end, white_dir) {
  // Calculate direction and length
  dir = end - start;
  len = norm(dir);
  
  // Calculate rotation to align Z with direction
  if (len > 0.001) {
    translate(start)
    multmatrix(m=look_at(dir, white_dir))
    extrusion_2020(len);
  }
}

// Look-at matrix helper
function look_at(dir, up) = 
  let(
    z = dir / norm(dir),
    x = cross(up, z) / norm(cross(up, z)),
    y = cross(z, x)
  )
  [[x[0], y[0], z[0], 0],
   [x[1], y[1], z[1], 0],
   [x[2], y[2], z[2], 0],
   [0, 0, 0, 1]];

"""

    # Add connector module
    scad += """
module connector(pos) {
  translate(pos)
  color([0.3, 0.3, 0.3])
  sphere(r=0.015);
}

"""

    # Generate extrusions with rotation applied
    for ext_id, (start, end, white_dir) in self.extrusion_geometry.items():
      r_start = rotation @ start
      r_end = rotation @ end
      r_white = rotation @ white_dir

      # Simple colored cube for each extrusion
      direction = r_end - r_start
      length = np.linalg.norm(direction)
      midpoint = (r_start + r_end) / 2

      if length > 0.001:
        direction_norm = direction / length

        # Calculate rotation angles
        # Align Z axis with direction
        scad += f"// Extrusion {ext_id}\n"
        scad += f"translate([{midpoint[0]:.6f}, {midpoint[1]:.6f}, {midpoint[2]:.6f}])\n"

        # Calculate rotation to align with direction
        # Use atan2 for proper angles
        xy_len = math.sqrt(direction_norm[0]**2 + direction_norm[1]**2)
        rot_x = math.degrees(math.atan2(direction_norm[1],
                                        direction_norm[2])) if xy_len < 0.99 else 0
        rot_y = math.degrees(math.atan2(direction_norm[0], direction_norm[2]))
        rot_z = math.degrees(math.atan2(direction_norm[1],
                                        direction_norm[0])) if xy_len > 0.01 else 0

        # Simpler approach: use rotation from z-axis
        if abs(direction_norm[2]) > 0.999:
          # Nearly vertical
          if direction_norm[2] > 0:
            scad += f"color([0.7, 0.7, 0.8]) cube([0.02, 0.02, {length:.6f}], center=true);\n\n"
          else:
            scad += f"rotate([180, 0, 0]) color([0.7, 0.7, 0.8]) cube([0.02, 0.02, {length:.6f}], center=true);\n\n"
        else:
          # Calculate rotation
          angle_y = math.degrees(math.acos(np.clip(direction_norm[2], -1, 1)))
          angle_z = math.degrees(math.atan2(direction_norm[1], direction_norm[0]))
          scad += f"rotate([0, {angle_y:.2f}, {angle_z:.2f}]) color([0.7, 0.7, 0.8]) cube([0.02, 0.02, {length:.6f}], center=true);\n\n"

    # Add connectors
    for conn_idx, (pos, _) in self.connector_positions.items():
      r_pos = rotation @ pos
      scad += f"connector([{r_pos[0]:.6f}, {r_pos[1]:.6f}, {r_pos[2]:.6f}]);\n"

    return scad


def solve_assembly(answer):
  """
  Main solver: validate and build the assembly from connector data.
  Returns (success, assembly, scad_code).
  Always returns assembly object and SCAD (if possible) for visualization even on failure.
  """
  if not isinstance(answer, dict):
    return False, "Invalid answer format: expected dict", ""

  connectors = answer.get("connectors", [])
  if not connectors:
    return False, "No connectors provided", ""

  assembly = ExtrusionAssembly(connectors)

  # Build extrusion map and validate (continue even if errors)
  assembly.build_extrusion_map()

  # Walk the graph (continue even if errors)
  assembly.walk_graph()

  # Find stable orientation
  rotation, score = assembly.find_stable_orientation()

  # Generate SCAD (even if there are errors, for visualization)
  scad = assembly.to_scad(rotation)

  success = len(assembly.errors) == 0
  return success, assembly, scad


prompt = """
You are given an effectively-infinite supply  of 2020 aluminium extrusions, 20mm x 20mm 
square extrusion, 1m long.

The long sides are coloured - Red, Green, Blue, White.

You are given an infinite pile of matching connectors:

P101 - Joins two 2020 extrusions (labelled X+, X- end to end. (an extension peice)
P102 - Joins two 2020 extrusions (labelled X+, Y+) at a 90 degree angle.
P103 - Joins 3 2020 extrusions (labelled X+, X-, and Y+) at a T junction
P104 - Joins 3 2020 extrusions (labelled X+, Y+, and Z+) at a 3-way corner 
P105 - Joins 4 2020 extrusions (labelled X+, X-, Y+, Y-) in an planar cross
P106 - Joins 4 2020 extrusions (labelled X+, X-, Y+, Z+) in 3-way through corner.
P107 - Joins 5 2020 extrusions (labelled X+, X-, Y+, Y-, and Z+) in 5-way interior corner
P108 - Joins 6 2020 extrusions in 6-way join.

You can build any shape you want out of these. For example:
- 4 x 1m extrusions and 4 x P102s could make a unit square.
- 8 x P104 and 12 x 1m extrusions could make a unit cube.
- 4 * P106, 8 P104, and 16 1m extrusions, could make a 2x1x1 prism.

You can create assembly instructions for any shape you wish to build,
taking note of the colours. So decide on how many extrusions you need, label them
1-N, and then, for each join:

- describe which part number it is.
- describe which extrusion is attached to which connector.
- describe the orientation of the WHITE face of the extrusion, so for example,
  plugging an extrusion into a X+ socket, the white face could +Y, -Y, +Z, or -Z.


For example, this is a unit square with the white facing outwards:

   P102                                  P102
  +===+                                 +====+
  |   ._______________________________X+.    |
  |   .Y+              1                .    |
  +...+                                 +....+
    |X+                                   |Y+
    |                                     |
    |                                     |
    |                                     |
    |2                                    |4
    |                                     |
    |                                     |
    |                                     |
    |X+                                   |X+
  +...+Y+              3             Y+ +....+
  |   ._________________________________.    |
  |   .                                 .    |
  +___+                                 +____+


So the parts are obviously:
- P102. (Top left)
        Y+ is connected to 1. White facing X- orientation.
        X+ is connected to 2. White facing Y- orientaiton.

- P102. (Top right)
        X+ is connected to 1. White is facing Y-
        Y+ is connected to 4. White is X-

- P102. (bottom left)
        X+ is connected to 2. White is Y-
        Y+ is connected to 3. White is X-

- P102. (bottom right)
        X+ is connected to 4. White is Y-
        Y+ is connected to 3. White is X-

Someone assembling this shape from instructions can start with any connector,
rotated in any orientation, and then follow the instructions to build the shape, 
and should get the exact same shape every time, with the white faces facing outwards,
regardless of which part they started with or which orientation they started in.

Generate the build instructions for a
"""

structure = {
  "type": "object",
  "additionalProperties": False,
  "required": ["connectors"],
  "propertyOrdering": ["connectors"],
  "properties": {
    "connectors": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["partNumber", "connections"],
        "propertyOrdering": ["partNumber", "connections"],
        "properties": {
          "partNumber": {
            "type": "string"
          },
          "connections": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "label": {
                  "type": "string",
                  "enum": ["X+", "X-", "Y+", "Y-", "Z+", "Z-"]
                },
                "extrusionNumber": {
                  "type": "integer"
                },
                "orientationOfWhiteSide": {
                  "type": "string",
                  "enum": ["X+", "X-", "Y+", "Y-", "Z+", "Z-"]
                }
              },
              "additionalProperties": False,
              "required": ["extrusionNumber", "orientationOfWhiteSide", "label"],
              "propertyOrdering": ["extrusionNumber", "orientationOfWhiteSide", "label"]
            }
          }
        }
      }
    }
  }
}

# Test shapes to build (prompt suffix, expected properties)
test_shapes = [
  ("unit cube (1m x 1m x 1m)", {
    "connectors":
    8,
    "extrusions":
    12,
    "referenceScad":
    """
translate([0,0,0.5]) 
difference() 
{
  cube([1,1,1], center=true);
  cube([0.96,0.96,0.96], center=true);
}"""
  }),
  ("2x1x1 rectangular prism", {
    "connectors": 8,
    "extrusions": 12,
    "referenceScad":
    "translate([0,0,0.5]) difference() {cube([2,1,1], center=true);cube([1.92,0.96,0.96], center=true);}",
    "dims": (2, 1, 1)
  }),
  ("a simple chair frame (seat at 1m height, backrest to 2m, legs connected into a square, no unconnected extrusions)",
   {
     "connectors": 10,
     "extrusions": 15,
     "referenceScad":
     "translate([0,0,0.5]) difference() {cube([2,1,1], center=true);cube([1.92,0.96,0.96], center=true);}",
     "dims": (2, 1, 1)
   }),
  ("The 't' shape tetris peice. 3 adjacent cubes in a line, with a cube off to the side", {
    "connectors": 20,
    "extrusions": 0
  }),
  ("A livestock pen sized ~4x4m, encircled with a 1m high fence frame framing, with top and bottom runners and support posts every 1m.",
   {
     "connectors": 36,
     "extrusions": 56
   }),
  ("Scafolding. 1m wide. 2m high stories. Around a 10m * 10m skyscraper, reaching 4m on 3 sides and 8m on the 4th. Include safety railing 1m-high above all walkways. You do not need to include ladders or planks in your design.",
   {})
]

import OpenScad as vc

earlyFail = False


def prepareSubpassPrompt(index: int) -> str:
  if index >= 2:
    raise StopIteration

  shape_desc, _ = test_shapes[index]
  return prompt + shape_desc


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if not isinstance(answer, dict):
    return 0, "Invalid answer format"

  shape_desc, expected = test_shapes[subPass]

  # Try to solve the assembly
  success, result, scad = solve_assembly(answer)

  # Handle early failures (no assembly object)
  if isinstance(result, str):
    return 0, f"Assembly failed: {result}"

  assembly = result

  # Basic scoring
  score = 0
  feedback = []

  num_connectors = len(assembly.connectors_data)
  num_extrusions = len(assembly.extrusion_geometry)

  feedback.append(f"Connectors: {num_connectors}, Extrusions: {num_extrusions}")

  # Check if structure is valid (no errors)
  if not assembly.errors:
    score += 0.3
    feedback.append("Structure is valid")
  else:
    feedback.append(f"Errors: {', '.join(assembly.errors)}")

  # Check connector count matches expected (if specified)
  if "connectors" in expected:
    if num_connectors == expected["connectors"]:
      score += 0.2
      feedback.append(f"Correct connector count ({expected['connectors']})")
    else:
      feedback.append(f"Expected {expected['connectors']} connectors, got {num_connectors}")

  # Check extrusion count matches expected (if specified)
  if "extrusions" in expected:
    if num_extrusions == expected["extrusions"]:
      score += 0.2
      feedback.append(f"Correct extrusion count ({expected['extrusions']})")
    else:
      feedback.append(f"Expected {expected['extrusions']} extrusions, got {num_extrusions}")

  # Check geometry bounds
  if assembly.extrusion_geometry:
    all_points = []
    for ext_id, (start, end, _) in assembly.extrusion_geometry.items():
      all_points.append(start)
      all_points.append(end)
    all_points = np.array(all_points)

    dims = all_points.max(axis=0) - all_points.min(axis=0)
    dims_sorted = tuple(sorted(dims, reverse=True))
    feedback.append(
      f"Dimensions: {dims_sorted[0]:.2f} x {dims_sorted[1]:.2f} x {dims_sorted[2]:.2f}")

    # Check if it's a cube
    if expected.get("is_cube"):
      if np.allclose(dims_sorted, (1, 1, 1), atol=0.1):
        score += 0.3
        feedback.append("Correct cube dimensions")
      else:
        feedback.append("Not a unit cube")

    # Check expected dimensions
    if "dims" in expected:
      exp_dims = tuple(sorted(expected["dims"], reverse=True))
      if np.allclose(dims_sorted, exp_dims, atol=0.1):
        score += 0.3
        feedback.append("Correct dimensions")
      else:
        feedback.append(f"Expected dimensions {exp_dims}")

  import scad_format

  # Save SCAD file for visualization
  scad_path = f"results/46_shape_{aiEngineName}_{subPass}.scad"
  with open(scad_path, "w") as f:
    f.write(scad_format.format(scad, vc.formatConfig))

  # Render to PNG
  try:
    vc.render_scadText_to_png(scad, f"results/46_shape_{aiEngineName}_{subPass}.png")
  except Exception as e:
    feedback.append(f"Render failed: {e}")

  return min(score, 1.0), "<br>".join(feedback)


def resultToNiceReport(answer, subPass, aiEngineName):
  if not isinstance(answer, dict):
    return "<p>Invalid answer</p>"

  shape_desc, _ = test_shapes[subPass]

  success, result, scad = solve_assembly(answer)

  html = f"<p><b>Shape requested:</b> {shape_desc}</p>"

  # Handle early failures (result is error string)
  if isinstance(result, str):
    html += f"<p style='color:red'><b>Error:</b> {result}</p>"
    return html

  assembly = result
  html += f"<p><b>Connectors:</b> {len(assembly.connectors_data)}, <b>Extrusions:</b> {len(assembly.extrusion_geometry)}</p>"

  # Show errors if any
  if assembly.errors:
    html += f"<p style='color:red'><b>Validation errors:</b><br>{'<br>'.join(assembly.errors)}</p>"

  # Show visualization (even if there are errors)
  if os.path.exists(f"results/46_shape_{aiEngineName}_{subPass}.png"):
    html += f"<img src='46_shape_{aiEngineName}_{subPass}.png' style='max-width:400px'><br>"

  # Show connector details
  html += "<details><summary>Connector details</summary><pre>"
  for i, conn in enumerate(assembly.connectors_data):
    html += f"Connector {i}: {conn.get('partNumber', '?')}\n"
    for c in conn.get('connections', []):
      html += f"  {c.get('label', '?')} -> Extrusion {c.get('extrusionNumber', '?')} (white: {c.get('orientationOfWhiteSide', '?')})\n"
  html += "</pre></details>"

  # Show SCAD code
  html += "<details><summary>OpenSCAD code</summary><pre>"
  html += scad[:2000] + ("..." if len(scad) > 2000 else "")
  html += "</pre></details>"

  return html


highLevelSummary = """
Can an AI generate valid build instructions for 3D structures?<br><br>

This test asks the AI to create assembly instructions for structures made from
20mm x 20mm aluminium extrusions (1m long) with color-coded faces and various
connector types.<br><br>

The solver validates:<ul>
<li>Connector part numbers are valid</li>
<li>Socket labels match the connector type</li>
<li>Each extrusion connects exactly 2 connectors</li>
<li>No self-intersections</li>
<li>All connectors are part of one connected structure</li>
</ul><br>

The assembly is rendered in OpenSCAD in the most stable orientation (lowest center
of mass with widest ground contact).
"""

subpassParamSummary = [
  "Build a unit cube (8 corners, 12 edges)",
  "Build a 2x1x1 rectangular prism",
  "Build a simple chair frame.",
  "Build a 'T' shaped tetris piece",
]
promptChangeSummary = "Different shapes of increasing complexity"
