import math

import OpenScad

title = "CSG Union of Polyhedra"

# Base prompt template - DESCRIPTION is replaced per test case
promptTemplate = """
You can output polyhedrons in a json format. For example here is a simple cube, every face has 4 vertices, and there are 6 faces:

``` json
{
"polyhedron":
  {
    "vertex":[{"xyz":[-1.0,-1.0,-1.0]},{"xyz":[1.0,-1.0,-1.0]},{"xyz":[1.0,1.0,-1.0]},{"xyz":[-1.0,1.0,-1.0]},{"xyz":[-1.0,-1.0,1.0]},{"xyz":[1.0,-1.0,1.0]},{"xyz":[1.0,1.0,1.0]},{"xyz":[-1.0,1.0,1.0]}],
    "faces":[{"vertex":[3,2,1,0]},{"vertex":[4,5,6,7]},{"vertex":[0,1,5,4]},{"vertex":[7,6,2,3]},{"vertex":[3,0,4,7]},{"vertex":[1,2,6,5]}]
  }
}
```

Now you've learnt the format, use it to solve the following problem:

DESCRIPTION

Return a polyhedron that is the union of all the solid objects described above.
- Ensure faces have normals encoded in a consistent direction (outward-facing).
- Ensure no geometry occurs inside the polyhedron, and no faces cross through it.
- Note that some faces may have more than 4 vertices.
- Your output should have no degenerate faces or redundant vertices.
- The task is a failure if the output is not watertight.
"""

# Run the test 3 times (on simple cube pairings) if the average score is below 0.1 on those
# easy tests, consider all following tests a failure to save tokens.
earlyFail = True
earlyFailThreshold = 0.1
earlyFailSubpassSampleCount = 3

# Test cases: (description, scad_code, summary)
# For spheres/cylinders, we use $fn=24 for consistent polygonization
testParams = [
  # Basic cube combinations
  ("You are given two solid cubes, each with side length 10cm. "
   "The first cube is centered at the origin (0, 0, 0). "
   "The second cube is centered at (8, 0, 0)",
   "translate([0,0,0]) cube([10,10,10], center=true); translate([8,0,0]) cube([10,10,10], center=true);",
   "Two cubes overlapping 2cm in X"),
  ("You are given two solid cubes, each with side length 10cm. "
   "The first cube is centered at the origin (0, 0, 0). "
   "The second cube is centered at (5, 5, 0)",
   "translate([0,0,0]) cube([10,10,10], center=true); translate([5,5,0]) cube([10,10,10], center=true);",
   "Two cubes overlapping at corner"),
  ("You are given two solid cubes, each with side length 10cm. "
   "The first cube is centered at (0, 0, 0). "
   "The second cube is centered at (15, 0, 0)",
   "translate([0,0,0]) cube([10,10,10], center=true); translate([15,0,0]) cube([10,10,10], center=true);",
   "Two separate cubes (no intersection)"),
  ("You are given two solid cubes. "
   "The first cube has side length 20cm and is centered at the origin. "
   "The second cube has side length 10cm and is also centered at the origin.",
   "cube([20,20,20], center=true); cube([10,10,10], center=true);", "Small cube inside large cube"),

  # Rectangular prism combinations
  ("You are given a rectangular prism of size 10cm x 20cm x 30cm centered at (0, 0, 0). "
   "You are also given a cube with side length 15cm centered at (10, 0, 0).",
   "cube([10,20,30], center=true); translate([10,0,0]) cube([15,15,15], center=true);",
   "Rectangular prism and cube overlapping"),
  ("You are given two rectangular prisms. "
   "The first is 30cm x 10cm x 10cm centered at (0, 0, 0). "
   "The second is 10cm x 30cm x 10cm centered at (0, 0, 0).",
   "cube([30,10,10], center=true); cube([10,30,10], center=true);", "Two prisms forming a cross"),
  ("You are given three rectangular prisms, all centered at the origin. "
   "The first is 30cm x 10cm x 10cm. "
   "The second is 10cm x 30cm x 10cm. "
   "The third is 10cm x 10cm x 30cm.",
   "cube([30,10,10], center=true); cube([10,30,10], center=true); cube([10,10,30], center=true);",
   "Three prisms forming 3D jack"),

  # Wedge/ramp shapes (using polyhedron in scad)
  ("You are given a cube with side length 10cm centered at (0, 0, 0). "
   "You are also given a triangular prism (wedge) that is 10cm wide (Y), 10cm deep (X), and 10cm tall (Z), "
   "with the sloped face going from the top-front edge to the bottom-back edge. "
   "The wedge is positioned with its base centered at (10, 0, 0).",
   """cube([10,10,10], center=true);
translate([10,0,0]) polyhedron(
  points=[[-5,-5,0],[5,-5,0],[5,5,0],[-5,5,0],[-5,-5,10],[-5,5,10]],
  faces=[[0,1,2,3],[4,5,3,0],[1,0,4],[2,1,4,5],[3,5,4,0],[2,5,3]]
);""", "Cube and triangular wedge"),

  # Pyramid (tetrahedron)
  ("You are given a cube with side length 10cm centered at the origin. "
   "You are also given a regular tetrahedron with vertices at: "
   "(0, 0, 15), (8.16, 0, 5), (-4.08, 7.07, 5), (-4.08, -7.07, 5). ",
   """cube([10,10,10], center=true);
polyhedron(
  points=[[0,0,15],[8.16,0,5],[-4.08,7.07,5],[-4.08,-7.07,5]],
  faces=[[0,1,2],[0,2,3],[0,3,1],[1,3,2]]
);""", "Cube with tetrahedron on top"),

  # L-shaped combinations
  ("You are given two rectangular prisms. "
   "The first prism is 30cm x 10cm x 10cm centered at (0, 0, 0). "
   "The second prism is 10cm x 20cm x 10cm centered at (10, 5, 0). ",
   "cube([30,10,10], center=true); translate([10,5,0]) cube([10,20,10], center=true);",
   "L-shaped prisms"),

  # Staircase
  ("You are given three cubes. "
   "The first cube (10cm) is centered at (0, 0, 0). "
   "The second cube (10cm) is centered at (10, 0, 5). "
   "The third cube (10cm) is centered at (20, 0, 10).",
   "cube([10,10,10], center=true); translate([10,0,5]) cube([10,10,10], center=true); translate([20,0,10]) cube([10,10,10], center=true);",
   "Three cubes forming stairs"),

  # Cylinder tests (explicit $fn for reproducibility)
  ("You are given a cylinder with radius 5cm and height 20cm, centered at the origin with its axis along Z. "
   "The cylinder is approximated as a 24-sided prism. "
   "You are also given a cube with side length 8cm centered at (6, 0, 0).",
   "cylinder(r=5, h=20, center=true, $fn=24); translate([6,0,0]) cube([8,8,8], center=true);",
   "Cylinder (24-gon) and cube"),
  ("You are given two cylinders, each with radius 5cm and height 20cm, approximated as 24-sided prisms. "
   "The first cylinder has its axis along Z, centered at origin. "
   "The second cylinder has its axis along X, centered at origin. "
   "They intersect at the center.",
   "cylinder(r=5, h=20, center=true, $fn=24); rotate([0,90,0]) cylinder(r=5, h=20, center=true, $fn=24);",
   "Two perpendicular cylinders"),

  # Hexagonal prism
  ("You are given a regular hexagonal prism with circumradius 5cm and height 10cm, centered at origin with axis along Z. "
   "You are also given a cube with side length 6cm centered at (6, 0, 0).",
   "cylinder(r=5, h=10, center=true, $fn=6); translate([6,0,0]) cube([6,6,6], center=true);",
   "Hexagonal prism and cube"),

  # Octagonal prism
  ("You are given a regular octagonal prism with circumradius 5cm and height 10cm, centered at origin with axis along Z. "
   "You are also given a cube with side length 8cm also centered at origin.",
   "cylinder(r=5, h=10, center=true, $fn=8); cube([8,8,8], center=true);",
   "Octagonal prism inside cube"),

  # Multiple small cubes
  ("You are given four cubes, each with side length 5cm. "
   "They are centered at: (0, 0, 0), (4, 0, 0), (0, 4, 0), and (4, 4, 0). ",
   "cube([5,5,5], center=true); translate([4,0,0]) cube([5,5,5], center=true); translate([0,4,0]) cube([5,5,5], center=true); translate([4,4,0]) cube([5,5,5], center=true);",
   "2x2 grid of overlapping cubes"),

  # Sphere (24-segment approximation)
  ("You are given a sphere with radius 8cm centered at origin, approximated as a polyhedron with 24 longitude and 12 latitude segments. "
   "You are also given a cube with side length 10cm centered at (8, 0, 0).",
   "sphere(r=8, $fn=24); translate([8,0,0]) cube([10,10,10], center=true);",
   "Sphere (24-segment) and cube"),

  # Touching faces (edge case)
  ("You are given two cubes, each with side length 10cm. "
   "The first is centered at (0, 0, 0). "
   "The second is centered at (10, 0, 0).",
   "cube([10,10,10], center=true); translate([10,0,0]) cube([10,10,10], center=true);",
   "Two cubes sharing a face"),

  # Rotated cube
  ("You are given a cube with side length 10cm centered at origin. "
   "You are also given a cube with side length 10cm centered at origin but rotated 45 degrees around the Z axis.",
   "cube([10,10,10], center=true); rotate([0,0,45]) cube([10,10,10], center=true);",
   "Two cubes, one rotated 45°"),

  # T-junction
  ("You are given two rectangular prisms."
   "The first is 30cm x 10cm x 10cm centered at (0, 0, 5). "
   "The second is 10cm x 10cm x 20cm centered at (0, 0, -5).",
   "translate([0,0,5]) cube([30,10,10], center=true); translate([0,0,-5]) cube([10,10,20], center=true);",
   "T-shaped prisms"),

  # Cone approximation
  ("You are given a cone with base radius 8cm and height 15cm, centered with base at Z=0 and apex at Z=15. "
   "The cone is approximated as a 24-sided pyramid. "
   "You are also given a cube with side length 10cm centered at (0, 0, 5).",
   "cylinder(r1=8, r2=0, h=15, $fn=24); translate([0,0,5]) cube([10,10,10], center=true);",
   "Cone (24-sided) and cube"),

  # Hollow box (difference shown as union of walls)
  ("You are given 6 rectangular prisms"
   "A: 20x20x2 at z=-9. B: 20x20x2 at z=9. "
   "C: 20x2x16 at y=-9. D: 20x2x16 at y=9. "
   "E: 2x16x16 at x=-9. F: 2x16x16 at x=9.", """translate([0,0,-9]) cube([20,20,2], center=true);
translate([0,0,9]) cube([20,20,2], center=true);
translate([0,-9,0]) cube([20,2,16], center=true);
translate([0,9,0]) cube([20,2,16], center=true);
translate([-9,0,0]) cube([2,16,16], center=true);
translate([9,0,0]) cube([2,16,16], center=true);""", "Hollow box (6 wall prisms)"),
]

structure = {
  "type": "object",
  "properties": {
    "polyhedron": {
      "type": "object",
      "properties": {
        "vertex": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "xyz": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              }
            },
            "propertyOrdering": ["xyz"],
            "additionalProperties": False,
            "required": ["xyz"]
          }
        },
        "faces": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "vertex": {
                "type": "array",
                "items": {
                  "type": "integer"
                }
              }
            },
            "propertyOrdering": ["vertex"],
            "additionalProperties": False,
            "required": ["vertex"]
          }
        }
      },
      "propertyOrdering": ["vertex", "faces"],
      "additionalProperties": False,
      "required": ["vertex", "faces"]
    }
  },
  "propertyOrdering": ["polyhedron"],
  "additionalProperties": False,
  "required": ["polyhedron"]
}

promptChangeSummary = "Various CSG union problems with different shape combinations."

subpassParamSummary = [tp[2] for tp in testParams]


def prepareSubpassPrompt(index):
  #if index == 1: raise StopIteration  # HACK to save money during dev.
  if index >= len(testParams):
    raise StopIteration
  description, _, _ = testParams[index]
  return promptTemplate.replace("DESCRIPTION", description)


def prepareSubpassReferenceScad(index):
  if index >= len(testParams):
    raise StopIteration
  _, scad_code, _ = testParams[index]
  return f"module reference() {{\n{scad_code}\n}}"


def _cross(a, b):
  """Cross product of two 3D vectors."""
  return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a, b):
  """Dot product of two 3D vectors."""
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
  """Subtract two 3D vectors."""
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _magnitude(v):
  """Magnitude of a 3D vector."""
  return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def _face_normal(vertices, face_indices):
  """Compute face normal using Newell's method for robustness with polygons."""
  n = len(face_indices)
  if n < 3:
    return [0, 0, 0]

  normal = [0.0, 0.0, 0.0]
  for i in range(n):
    v1 = vertices[face_indices[i]]
    v2 = vertices[face_indices[(i + 1) % n]]
    normal[0] += (v1[1] - v2[1]) * (v1[2] + v2[2])
    normal[1] += (v1[2] - v2[2]) * (v1[0] + v2[0])
    normal[2] += (v1[0] - v2[0]) * (v1[1] + v2[1])

  return normal


def _signed_volume_contribution(vertices, face_indices):
  """Compute signed volume contribution of a face (for volume calculation)."""
  if len(face_indices) < 3:
    return 0

  # Triangulate the face and sum contributions
  total = 0
  v0 = vertices[face_indices[0]]
  for i in range(1, len(face_indices) - 1):
    v1 = vertices[face_indices[i]]
    v2 = vertices[face_indices[i + 1]]
    # Signed volume of tetrahedron with origin
    total += _dot(v0, _cross(v1, v2)) / 6.0
  return total


def earlyFailTest(result, subpass):
  """Validate polyhedron before CSG processing."""

  if "polyhedron" not in result:
    return "Missing 'polyhedron' in result"

  poly = result["polyhedron"]

  if "vertex" not in poly or "faces" not in poly:
    return "Polyhedron missing 'vertex' or 'faces'"

  raw_vertices = poly["vertex"]
  raw_faces = poly["faces"]

  # Check for empty mesh
  if len(raw_vertices) == 0:
    return "No vertices provided"
  if len(raw_faces) == 0:
    return "No faces provided"

  # Extract vertex coordinates
  vertices = []
  for i, v in enumerate(raw_vertices):
    if "xyz" not in v:
      return f"Vertex {i} missing 'xyz' field"
    xyz = v["xyz"]
    if len(xyz) != 3:
      return f"Vertex {i} has {len(xyz)} coordinates, expected 3"
    try:
      vertices.append([float(xyz[0]), float(xyz[1]), float(xyz[2])])
    except (ValueError, TypeError):
      return f"Vertex {i} has non-numeric coordinates: {xyz}"

  num_vertices = len(vertices)

  # Extract face indices
  faces = []
  for i, f in enumerate(raw_faces):
    if "vertex" not in f:
      return f"Face {i} missing 'vertex' field"
    indices = f["vertex"]

    # Check for degenerate face (too few vertices)
    if len(indices) < 3:
      return f"Face {i} has only {len(indices)} vertices (minimum 3 required)"

    # Check for invalid indices
    for j, idx in enumerate(indices):
      if not isinstance(idx, int):
        return f"Face {i} vertex {j} is not an integer: {idx}"
      if idx < 0 or idx >= num_vertices:
        return f"Face {i} has invalid vertex index {idx} (valid range: 0-{num_vertices-1})"

    # Check for duplicate vertices in face
    if len(indices) != len(set(indices)):
      return f"Face {i} has duplicate vertex indices: {indices}"

    faces.append(indices)

  # Check for duplicate vertices in the vertex list (exactly same position)
  seen_positions = {}
  for i, v in enumerate(vertices):
    key = (round(v[0], 6), round(v[1], 6), round(v[2], 6))
    if key in seen_positions:
      return f"Duplicate vertex positions: vertex {i} and {seen_positions[key]} at {v}"
    seen_positions[key] = i

  # Check for NaN or Inf values
  for i, v in enumerate(vertices):
    for j, coord in enumerate(v):
      if math.isnan(coord) or math.isinf(coord):
        return f"Vertex {i} has invalid coordinate (NaN or Inf): {v}"

  # Check for outlier points (far from centroid)
  centroid = [
    sum(v[0] for v in vertices) / num_vertices,
    sum(v[1] for v in vertices) / num_vertices,
    sum(v[2] for v in vertices) / num_vertices
  ]
  distances = [_magnitude(_sub(v, centroid)) for v in vertices]
  max_dist = max(distances)
  avg_dist = sum(distances) / len(distances)
  if max_dist > avg_dist * 10 and max_dist > 100:  # 10x average and > 100 units
    outlier_idx = distances.index(max_dist)
    return f"Vertex {outlier_idx} appears to be an outlier: {vertices[outlier_idx]} is {max_dist:.1f} from centroid (avg: {avg_dist:.1f})"

  # Check for degenerate faces (zero area)
  for i, face in enumerate(faces):
    normal = _face_normal(vertices, face)
    area_proxy = _magnitude(normal)
    if area_proxy < 1e-10:
      return f"Face {i} is degenerate (zero or near-zero area)"

  # Edge manifold check: each edge should appear exactly twice (once in each direction)
  # For a watertight mesh with consistent winding
  #
  # NOTE: We collect ALL edge errors before returning so that the failure-mode
  # judge sees the full defect picture.
  edge_count = {}  # (min_idx, max_idx) -> count of directed edges
  directed_edges = {}  # (from, to) -> face index
  winding_errors = []

  for face_idx, face in enumerate(faces):
    n = len(face)
    for i in range(n):
      v1, v2 = face[i], face[(i + 1) % n]
      edge_key = (min(v1, v2), max(v1, v2))
      directed_key = (v1, v2)

      # Track directed edges for winding check
      if directed_key in directed_edges:
        winding_errors.append(
          f"Edge ({v1}, {v2}) appears twice in same direction "
          f"(faces {directed_edges[directed_key]} and {face_idx})")
      directed_edges[directed_key] = face_idx

      edge_count[edge_key] = edge_count.get(edge_key, 0) + 1

  # Check that each edge is shared by exactly 2 faces (watertight)
  boundary_edges = []
  nonmanifold_edges = []
  for edge, count in edge_count.items():
    if count == 1:
      boundary_edges.append(edge)
    elif count > 2:
      nonmanifold_edges.append((edge, count))

  # Check winding consistency: for each undirected edge, we should have
  # exactly one (a,b) and one (b,a) directed edge
  for edge in edge_count.keys():
    v1, v2 = edge
    has_forward = (v1, v2) in directed_edges
    has_backward = (v2, v1) in directed_edges
    if has_forward and has_backward:
      pass  # Good - consistent winding
    elif has_forward or has_backward:
      # Only one direction - this shouldn't happen if edge_count == 2
      pass
    else:
      winding_errors.append(f"Edge {edge} has inconsistent winding order")

  # Report all collected edge errors in one message
  if winding_errors or boundary_edges or nonmanifold_edges:
    parts = []
    if winding_errors:
      parts.append(f"{len(winding_errors)} winding error(s): "
                   + "; ".join(winding_errors))
    if boundary_edges:
      parts.append(f"{len(boundary_edges)} boundary edge(s) (not watertight): "
                   + ", ".join(str(e) for e in boundary_edges))
    if nonmanifold_edges:
      parts.append(f"{len(nonmanifold_edges)} non-manifold edge(s): "
                   + "; ".join(f"{e} used by {c} faces"
                               for e, c in nonmanifold_edges))
    return " | ".join(parts)

  # Calculate signed volume to check for inside-out mesh or zero volume
  total_volume = 0
  for face in faces:
    total_volume += _signed_volume_contribution(vertices, face)

  if abs(total_volume) < 1e-10:
    return "Polyhedron has zero volume (degenerate or flat)"

  # Note: negative volume indicates inside-out winding, but we just warn
  # Some systems use different conventions

  # Check for self-intersecting faces (coplanar check - expensive, simplified)
  # We'll check if any face has vertices that would make it non-planar
  for i, face in enumerate(faces):
    if len(face) > 3:
      # Check planarity - all vertices should be close to the plane defined by first 3
      v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
      normal = _cross(_sub(v1, v0), _sub(v2, v0))
      norm_mag = _magnitude(normal)
      if norm_mag > 1e-10:
        normal = [n / norm_mag for n in normal]
        d = _dot(normal, v0)
        for j in range(3, len(face)):
          vj = vertices[face[j]]
          dist = abs(_dot(normal, vj) - d)
          if dist > 0.01:  # 0.01 unit tolerance
            return f"Face {i} is non-planar: vertex {face[j]} is {dist:.4f} from plane"

  return None  # All checks passed


def resultToScad(result, aiEngineName):
  import scad_format
  scad = """
polyhedron(
      points=[
"""
  for vertex in result["polyhedron"]["vertex"]:
    scad += "    [" + str(vertex["xyz"][0]) + "," + str(vertex["xyz"][1]) + "," + str(
      vertex["xyz"][2]) + "],\n"
  scad += "    ],\n"
  scad += "    faces=[\n"
  for face in result["polyhedron"]["faces"]:
    scad += "    [" + ",".join(map(str, face["vertex"])) + "],\n"
  scad += "    ]\n"
  scad += ");\n"
  return scad_format.format_code("module result(){ " + scad + " }", OpenScad.formatConfig)


highLevelSummary = """
CSG union of polyhedra is very hard without tooling, and hard to do right even with Python.

<br><br>

This test includes 23 different shape combinations: cubes, rectangular prisms, wedges, 
tetrahedra, cylinders (24-gon approximation), hexagonal/octagonal prisms, spheres (24-segment), 
cones, and complex multi-shape unions.

<br><br>

Most LLMs fail to output a closed mesh or correct winding order, 
and this shows up with OpenSCAD throwing errors when it tries to intersect the result
with a reference model.
"""


def postProcessScore(score, subPassIndex):
  if score > 0.95: return 1
  return score
