import math
import random
import OpenScad as vc
import os

tags = ["3D", "Simulation"]

title = "Net Folding - Can a 2D net fold into a 3D polyhedron?"
skip = True
prompt = """
A 'net' is a 2D pattern of connected polygons that can be folded along shared edges to form a 3D polyhedron.

Given the following 2D net laid out on the XY plane with Z=0:

NET_DESCRIPTION

Each face is labeled with a letter. Edges where faces connect are fold lines.

Your task is to specify the final 3D position and orientation of each face after folding the net into a closed 3D shape.

For each face, provide:
- A 3D position (the centroid of the face after folding)
- A normal vector (pointing outward from the closed polyhedron)

The base face 'A' remains fixed at its original position on Z=0 with normal pointing down (-Z).

Rules:
- Adjacent faces in the net must remain connected at their shared edge after folding
- The result must form a closed, watertight polyhedron
- All normals must point outward
"""

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "faces": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": {
            "type": "string"
          },
          "centroid": {
            "type": "array",
            "items": {
              "type": "number"
            },
            "description": "XYZ centroid of the face after folding"
          },
          "normal": {
            "type": "array",
            "items": {
              "type": "number"
            },
            "description": "Outward-facing normal vector"
          }
        },
        "propertyOrdering": ["label", "centroid", "normal"],
        "required": ["label", "centroid", "normal"],
        "additionalProperties": False
      }
    }
  },
  "propertyOrdering": ["reasoning", "faces"],
  "required": ["reasoning", "faces"],
  "additionalProperties": False
}

# Define nets as adjacency + 2D layout
# Net 0: Cube cross net
nets = [
  {
    "name": "Cube (cross net)",
    "description": """
Face A: Square at (0,0) to (1,1) - this is the BASE (bottom)
Face B: Square at (1,0) to (2,1) - connected to A on the right (east side of A)
Face C: Square at (2,0) to (3,1) - connected to B on the right
Face D: Square at (0,1) to (1,2) - connected to A on the top (north side of A)
Face E: Square at (1,1) to (2,2) - connected to B on top AND D on right
Face F: Square at (1,2) to (2,3) - connected to E on top

""",
    #ASCII view (Y increases upward):
    #    F
    #    E
    #  D A B C
    #
    #This folds into a unit cube centered at (0.5, 0.5, 0.5).
    "expected_faces": {
      "A": {
        "centroid": [0.5, 0.5, 0],
        "normal": [0, 0, -1]
      },
      "B": {
        "centroid": [1, 0.5, 0.5],
        "normal": [1, 0, 0]
      },
      "C": {
        "centroid": [0.5, 0.5, 1],
        "normal": [0, 0, 1]
      },
      "D": {
        "centroid": [0.5, 1, 0.5],
        "normal": [0, 1, 0]
      },
      "E": {
        "centroid": [0, 0.5, 0.5],
        "normal": [-1, 0, 0]
      },
      "F": {
        "centroid": [0.5, 0, 0.5],
        "normal": [0, -1, 0]
      },
    },
    "tolerance": 0.15
  },
  {
    "name": "Tetrahedron net",
    "description": """
A regular tetrahedron net with equilateral triangles of side length 2:

Face A: Equilateral triangle with vertices at (0,0), (2,0), (1, sqrt(3)) - BASE
Face B: Triangle attached to edge (0,0)-(2,0) of A, folding downward in Y
Face C: Triangle attached to edge (2,0)-(1,sqrt(3)) of A, on the right
Face D: Triangle attached to edge (0,0)-(1,sqrt(3)) of A, on the left
""",
    #When folded, forms a tetrahedron with A as base sitting on Z=0.
    "expected_faces": {
      "A": {
        "centroid": [1, math.sqrt(3) / 3, 0],
        "normal": [0, 0, -1]
      },
      "B": {
        "centroid": [1, math.sqrt(3) / 3 - 0.5, math.sqrt(2 / 3)],
        "normal": [0, -math.sqrt(2 / 3), math.sqrt(1 / 3)]
      },
      "C": {
        "centroid": [1.5, math.sqrt(3) / 3 + 0.25, math.sqrt(2 / 3)],
        "normal": [math.sqrt(2 / 3), math.sqrt(1 / 6),
                   math.sqrt(1 / 3)]
      },
      "D": {
        "centroid": [0.5, math.sqrt(3) / 3 + 0.25, math.sqrt(2 / 3)],
        "normal": [-math.sqrt(2 / 3), math.sqrt(1 / 6),
                   math.sqrt(1 / 3)]
      },
    },
    "tolerance": 0.2
  },
  {
    "name": "Octahedron net",
    "description": """
8 equilateral triangles arranged in a 2-strip:

Face A: Triangle at base-left
Face B: Triangle sharing edge with A (to its right)
Face C: Triangle sharing edge with B
Face H: Triangle sharing edge with C
Face D: Triangle above A
Face E: Triangle above B
Face F: Triangle above C  
Face G: Triangle above H (rightmost top)

All triangles have side length 1.
When folded, A stays as base with normal pointing -Z.
""",
    "expected_faces": {
      "A": {
        "centroid": [0.5, 0.289, 0],
        "normal": [0, 0, -1]
      },
      "B": {
        "centroid": [0, 0.289, 0.408],
        "normal": [-0.816, -0.333, 0.471]
      },
      "C": {
        "centroid": [0.5, -0.289, 0.816],
        "normal": [0, -0.943, 0.333]
      },
      "D": {
        "centroid": [0.5, 0.866, 0.408],
        "normal": [0, 0.943, 0.333]
      },
      "E": {
        "centroid": [0, 0.577, 0.816],
        "normal": [-0.816, 0.333, 0.471]
      },
      "F": {
        "centroid": [0.5, 0.289, 1.224],
        "normal": [0, 0, 1]
      },
      "G": {
        "centroid": [1, 0.577, 0.816],
        "normal": [0.816, 0.333, 0.471]
      },
      "H": {
        "centroid": [1, 0.289, 0.408],
        "normal": [0.816, -0.333, 0.471]
      },
    },
    "tolerance": 0.25
  },
  {
    "name": "Rectangular box net (2x1x1)",
    "description": """
Face A: Rectangle 2x1 at origin - BASE 
Face B: Rectangle 1x1 attached to left edge of A 
Face C: Rectangle 1x1 attached to right edge of A 
Face D: Rectangle 2x1 attached to top edge of A 
Face E: Rectangle 2x1 attached to top edge of D 
Face F: Rectangle 2x1 attached to bottom edge of A
""",
    "expected_faces": {
      "A": {
        "centroid": [1, 0.5, 0],
        "normal": [0, 0, -1]
      },
      "B": {
        "centroid": [0, 0.5, 0.5],
        "normal": [-1, 0, 0]
      },
      "C": {
        "centroid": [2, 0.5, 0.5],
        "normal": [1, 0, 0]
      },
      "D": {
        "centroid": [1, 1, 0.5],
        "normal": [0, 1, 0]
      },
      "E": {
        "centroid": [1, 0.5, 1],
        "normal": [0, 0, 1]
      },
      "F": {
        "centroid": [1, 0, 0.5],
        "normal": [0, -1, 0]
      },
    },
    "tolerance": 0.15
  },
]

# === SUPER-HARD CHALLENGES ===
# These require a solver to compute the expected answers


def rotation_matrix_from_vectors(vec_from, vec_to):
  """Compute rotation matrix that rotates vec_from to vec_to."""
  # Normalize inputs
  a = vec_from
  b = vec_to
  mag_a = math.sqrt(sum(x**2 for x in a))
  mag_b = math.sqrt(sum(x**2 for x in b))
  a = [x / mag_a for x in a]
  b = [x / mag_b for x in b]

  # Cross product (rotation axis)
  v = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

  # Dot product (cosine of angle)
  c = sum(a[i] * b[i] for i in range(3))

  # Handle parallel/anti-parallel cases
  if c > 0.9999:
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
  if c < -0.9999:
    # 180 degree rotation - find perpendicular axis
    if abs(a[0]) < 0.9:
      perp = [0, -a[2], a[1]]
    else:
      perp = [-a[2], 0, a[0]]
    mag = math.sqrt(sum(x**2 for x in perp))
    perp = [x / mag for x in perp]
    # Rotation by 180 degrees around perp
    return [[2 * perp[0]**2 - 1, 2 * perp[0] * perp[1], 2 * perp[0] * perp[2]],
            [2 * perp[0] * perp[1], 2 * perp[1]**2 - 1, 2 * perp[1] * perp[2]],
            [2 * perp[0] * perp[2], 2 * perp[1] * perp[2], 2 * perp[2]**2 - 1]]

  # Rodrigues' rotation formula
  s = math.sqrt(sum(x**2 for x in v))
  kmat = [[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]

  # R = I + K + K^2 * (1-c)/s^2
  factor = (1 - c) / (s * s)
  k2 = [[sum(kmat[i][k] * kmat[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

  rot = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
  for i in range(3):
    for j in range(3):
      rot[i][j] = (1 if i == j else 0) + kmat[i][j] + k2[i][j] * factor

  return rot


def apply_rotation(rot_matrix, vec):
  """Apply a 3x3 rotation matrix to a 3D vector."""
  return [sum(rot_matrix[i][j] * vec[j] for j in range(3)) for i in range(3)]


def compute_icosahedron_net():
  """Generate an icosahedron net with 20 triangular faces and compute expected positions.
    Rotated so Face A has normal pointing -Z and sits on Z=0 plane."""
  # Golden ratio
  phi = (1 + math.sqrt(5)) / 2

  # Icosahedron vertices (normalized to unit edge length)
  scale = 1 / (2 * math.sin(2 * math.pi / 5))
  vertices = [[0, 1, phi], [0, -1, phi], [0, 1, -phi], [0, -1, -phi], [1, phi, 0], [-1, phi, 0],
              [1, -phi, 0], [-1, -phi, 0], [phi, 0, 1], [-phi, 0, 1], [phi, 0, -1], [-phi, 0, -1]]
  vertices = [[v[i] * scale for i in range(3)] for v in vertices]

  # Icosahedron faces (20 triangles)
  faces_idx = [[0, 1, 8], [0, 8, 4], [0, 4, 5], [0, 5, 9], [0, 9, 1], [1, 6, 8], [8, 6, 10],
               [8, 10, 4], [4, 10, 2], [4, 2, 5], [5, 2, 11], [5, 11, 9], [9, 11, 7], [9, 7, 1],
               [1, 7, 6], [3, 6, 7], [3, 7, 11], [3, 11, 2], [3, 2, 10], [3, 10, 6]]

  # First pass: compute Face A's normal to determine rotation
  v0, v1, v2 = [vertices[j] for j in faces_idx[0]]
  centroid_a = [(v0[k] + v1[k] + v2[k]) / 3 for k in range(3)]
  e1 = [v1[k] - v0[k] for k in range(3)]
  e2 = [v2[k] - v0[k] for k in range(3)]
  normal_a = [
    e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]
  ]
  mag = math.sqrt(sum(n**2 for n in normal_a))
  normal_a = [n / mag for n in normal_a]
  if sum(centroid_a[k] * normal_a[k] for k in range(3)) < 0:
    normal_a = [-n for n in normal_a]

  # Compute rotation matrix to align normal_a with [0, 0, -1]
  target = [0, 0, -1]
  rot_matrix = rotation_matrix_from_vectors(normal_a, target)

  # Apply rotation to all vertices
  rotated_vertices = [apply_rotation(rot_matrix, v) for v in vertices]

  # Translate so Face A centroid is on Z=0
  v0r, v1r, v2r = [rotated_vertices[j] for j in faces_idx[0]]
  centroid_a_rot = [(v0r[k] + v1r[k] + v2r[k]) / 3 for k in range(3)]
  z_offset = centroid_a_rot[2]
  rotated_vertices = [[v[0], v[1], v[2] - z_offset] for v in rotated_vertices]

  expected = {}
  labels = "ABCDEFGHIJKLMNOPQRST"

  for i, face in enumerate(faces_idx):
    v0, v1, v2 = [rotated_vertices[j] for j in face]
    centroid = [(v0[k] + v1[k] + v2[k]) / 3 for k in range(3)]

    # Normal = cross product of two edges, pointing outward
    e1 = [v1[k] - v0[k] for k in range(3)]
    e2 = [v2[k] - v0[k] for k in range(3)]
    normal = [
      e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]
    ]
    mag = math.sqrt(sum(n**2 for n in normal))
    normal = [n / mag for n in normal]

    # Ensure normal points outward (away from origin for most, but check dot with centroid)
    # For rotated shape, origin may not be inside, so use original logic
    if sum(centroid[k] * normal[k] for k in range(3)) < 0:
      normal = [-n for n in normal]

    expected[labels[i]] = {
      "centroid": [round(c, 4) for c in centroid],
      "normal": [round(n, 4) for n in normal]
    }

  return expected


def compute_dodecahedron_net():
  """Generate a dodecahedron net with 12 pentagonal faces.
    Rotated so Face A has normal pointing -Z and sits on Z=0 plane."""
  phi = (1 + math.sqrt(5)) / 2

  # Face normals point toward these directions (normalized)
  face_normals_raw = [[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1], [-1, 1, 1], [-1, 1, -1],
                      [-1, -1, 1], [-1, -1, -1], [0, phi, 1 / phi], [0, phi, -1 / phi],
                      [0, -phi, 1 / phi], [0, -phi, -1 / phi]]

  # Scale to unit edge
  edge_len = 2 / phi

  # Face A's original normal
  normal_a = face_normals_raw[0]
  mag = math.sqrt(sum(n**2 for n in normal_a))
  normal_a = [n / mag for n in normal_a]

  # Compute rotation matrix to align normal_a with [0, 0, -1]
  target = [0, 0, -1]
  rot_matrix = rotation_matrix_from_vectors(normal_a, target)

  expected = {}
  labels = "ABCDEFGHIJKL"

  # First compute Face A's centroid after rotation to determine z offset
  dist = phi**2 / math.sqrt(3)
  centroid_a_orig = [normal_a[k] * dist / edge_len for k in range(3)]
  centroid_a_rot = apply_rotation(rot_matrix, centroid_a_orig)
  z_offset = centroid_a_rot[2]

  for i, normal_raw in enumerate(face_normals_raw):
    mag = math.sqrt(sum(n**2 for n in normal_raw))
    normal_orig = [n / mag for n in normal_raw]

    # Centroid is at distance from origin
    centroid_orig = [normal_orig[k] * dist / edge_len for k in range(3)]

    # Apply rotation
    centroid = apply_rotation(rot_matrix, centroid_orig)
    normal = apply_rotation(rot_matrix, normal_orig)

    # Translate so Face A is on Z=0
    centroid[2] -= z_offset

    expected[labels[i]] = {
      "centroid": [round(c, 4) for c in centroid],
      "normal": [round(n, 4) for n in normal]
    }

  return expected


def compute_truncated_tetrahedron_net():
  """Truncated tetrahedron: 4 triangles + 4 hexagons = 8 faces.
    Rotated so Face A has normal pointing -Z and sits on Z=0 plane."""
  scale = 1 / math.sqrt(8)

  # Triangle faces (at original tetrahedron vertices)
  tri_normals_raw = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]]
  # Hexagon faces (at original tetrahedron faces)
  hex_normals_raw = [[1, 1, -1], [1, -1, 1], [-1, 1, 1], [-1, -1, -1]]

  # Face A's original normal is [1,1,1]
  normal_a = [1, 1, 1]
  mag = math.sqrt(sum(n**2 for n in normal_a))
  normal_a = [n / mag for n in normal_a]

  # Compute rotation matrix to align normal_a with [0, 0, -1]
  target = [0, 0, -1]
  rot_matrix = rotation_matrix_from_vectors(normal_a, target)

  # Compute Face A's centroid before rotation to determine z offset
  dist_tri = math.sqrt(3) * scale * 3
  centroid_a_orig = [normal_a[k] * dist_tri for k in range(3)]
  centroid_a_rot = apply_rotation(rot_matrix, centroid_a_orig)
  z_offset = centroid_a_rot[2]

  expected = {}

  # Triangle faces
  for i, n_raw in enumerate(tri_normals_raw):
    mag = math.sqrt(sum(x**2 for x in n_raw))
    normal_orig = [x / mag for x in n_raw]
    centroid_orig = [normal_orig[k] * dist_tri for k in range(3)]

    centroid = apply_rotation(rot_matrix, centroid_orig)
    normal = apply_rotation(rot_matrix, normal_orig)
    centroid[2] -= z_offset

    expected[chr(65 + i)] = {
      "centroid": [round(x, 4) for x in centroid],
      "normal": [round(x, 4) for x in normal]
    }

  # Hexagon faces
  dist_hex = math.sqrt(3) * scale * 2
  for i, n_raw in enumerate(hex_normals_raw):
    mag = math.sqrt(sum(x**2 for x in n_raw))
    normal_orig = [x / mag for x in n_raw]
    centroid_orig = [normal_orig[k] * dist_hex for k in range(3)]

    centroid = apply_rotation(rot_matrix, centroid_orig)
    normal = apply_rotation(rot_matrix, normal_orig)
    centroid[2] -= z_offset

    expected[chr(69 + i)] = {
      "centroid": [round(x, 4) for x in centroid],
      "normal": [round(x, 4) for x in normal]
    }

  return expected


# Add super-hard nets
nets.extend([
  {
    "name": "Icosahedron net (20 faces) - HARD",
    "description": """
The net is arranged as a strip of equalateral triangles:

```
Row 1:    A   C   E   G   I
Row 2:  B   D   F   H   J
Row 3:    K   M   O   Q   S
Row 4:  L   N   P   R   T
```

Face A: Base triangle at origin, normal pointing -Z after folding
Faces B-T: Connected in sequence, alternating orientation

All triangles have edge length 1.
""",
    "expected_faces": compute_icosahedron_net(),
    "tolerance": 0.3
  },
  {
    "name": "Dodecahedron net (12 faces) - HARD",
    "description": """
The net layout (12 regular pentagons labeled A through L):

```
        A
      B C D
    E   F   G
      H I J
        K
        L
```

All pentagons are regular with edge length 1.
""",
    "expected_faces": compute_dodecahedron_net(),
    "tolerance": 0.35
  },
  {
    "name": "Truncated Tetrahedron net (8 faces) - HARD",
    "description": """
8 faces: 4 equilateral triangles and 4 regular hexagons.

The net layout:

```
      A (triangle)
    E   F (hexagons)
  B       C (triangles)  
    G   H (hexagons)
      D (triangle)
```

Triangle edge length: 1
Hexagon edge length: 1

""",
    "expected_faces": compute_truncated_tetrahedron_net(),
    "tolerance": 0.3
  },
])

subpassParamSummary = [n["name"] for n in nets]

promptChangeSummary = "Different polyhedra nets of increasing complexity"


def prepareSubpassPrompt(index: int) -> str:
  if index >= len(nets):
    raise StopIteration
  return prompt.replace("NET_DESCRIPTION", nets[index]["description"])


def normalize(v):
  mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
  if mag < 1e-9:
    return [0, 0, 0]
  return [v[0] / mag, v[1] / mag, v[2] / mag]


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  net = nets[subPass]
  expected = net["expected_faces"]
  tolerance = net["tolerance"]

  faces = answer.get("faces", [])
  if not faces:
    return 0, "No faces provided"

  face_dict = {}
  for f in faces:
    label = f.get("label", "")
    face_dict[label] = f

  total_score = 0
  max_score = len(expected) * 2  # 1 point for centroid, 1 for normal
  details = []

  for label, exp in expected.items():
    if label not in face_dict:
      details.append(f"Missing face {label}")
      continue

    face = face_dict[label]
    centroid = face.get("centroid", [0, 0, 0])
    normal = face.get("normal", [0, 0, 1])

    # Check centroid
    exp_c = exp["centroid"]
    dist = math.sqrt(sum((a - b)**2 for a, b in zip(centroid, exp_c)))
    if dist <= tolerance:
      total_score += 1
      details.append(f"Face {label} centroid OK (dist={dist:.3f})")
    else:
      details.append(
        f"Face {label} centroid wrong (dist={dist:.3f}, given {centroid}, expected {exp_c})")

    # Check normal (should be parallel, same direction)
    exp_n = normalize(exp["normal"])
    norm_n = normalize(normal)
    dot = sum(a * b for a, b in zip(norm_n, exp_n))
    if dot > 0.9:  # Within ~25 degrees
      total_score += 1
      details.append(f"Face {label} normal OK (dot={dot:.3f})")
    else:
      details.append(f"Face {label} normal wrong (dot={dot:.3f}, given {norm_n}, expected {exp_n})")

  if len(details) > 4:
    details = details[0:4] + [f"... (truncated {len(details) - 4} more)"]

  score = total_score / max_score if max_score > 0 else 0
  return score, "<br>".join(details)


def get_face_shape_info(subPass):
  """Return (num_sides, circumradius) for faces in each net type."""
  if subPass == 0:  # Cube
    return {"default": (4, 0.5 / math.cos(math.pi / 4))}  # squares, side=1
  elif subPass == 1:  # Tetrahedron
    return {"default": (3, 2 / math.sqrt(3))}  # triangles, side=2
  elif subPass == 2:  # Octahedron
    return {"default": (3, 1 / math.sqrt(3))}  # triangles, side=1
  elif subPass == 3:  # Rectangular box 2x1x1
    return {
      "A": (4, 1.118),  # 2x1 rectangle
      "B": (4, 0.707),  # 1x1 square
      "C": (4, 0.707),
      "D": (4, 1.118),
      "E": (4, 1.118),
      "F": (4, 1.118),
      "default": (4, 0.707)
    }
  elif subPass == 4:  # Icosahedron
    return {"default": (3, 1 / math.sqrt(3))}  # triangles, side=1
  elif subPass == 5:  # Dodecahedron
    return {"default": (5, 0.851)}  # pentagons, side=1
  elif subPass == 6:  # Truncated tetrahedron
    return {
      "A": (3, 1 / math.sqrt(3)),  # triangles
      "B": (3, 1 / math.sqrt(3)),
      "C": (3, 1 / math.sqrt(3)),
      "D": (3, 1 / math.sqrt(3)),
      "E": (6, 1.0),  # hexagons
      "F": (6, 1.0),
      "G": (6, 1.0),
      "H": (6, 1.0),
      "default": (4, 0.5)
    }
  return {"default": (4, 0.5)}


def generate_face_polygon(centroid, normal, num_sides, radius):
  """Generate vertices for a regular polygon at centroid, perpendicular to normal."""
  # Normalize the normal
  n = normal
  mag = math.sqrt(sum(x**2 for x in n))
  if mag < 1e-9:
    n = [0, 0, 1]
  else:
    n = [x / mag for x in n]

  # Find two perpendicular vectors in the plane
  if abs(n[2]) < 0.9:
    up = [0, 0, 1]
  else:
    up = [1, 0, 0]

  # u = up x n (normalized)
  u = [up[1] * n[2] - up[2] * n[1], up[2] * n[0] - up[0] * n[2], up[0] * n[1] - up[1] * n[0]]
  mag_u = math.sqrt(sum(x**2 for x in u))
  u = [x / mag_u for x in u]

  # v = n x u
  v = [n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0]]

  # Generate polygon vertices
  vertices = []
  for i in range(num_sides):
    angle = 2 * math.pi * i / num_sides + math.pi / num_sides  # offset for flat edge at bottom
    px = centroid[0] + radius * (math.cos(angle) * u[0] + math.sin(angle) * v[0])
    py = centroid[1] + radius * (math.cos(angle) * u[1] + math.sin(angle) * v[1])
    pz = centroid[2] + radius * (math.cos(angle) * u[2] + math.sin(angle) * v[2])
    vertices.append([px, py, pz])

  return vertices


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
  faces = answer.get("faces", [])
  shape_info = get_face_shape_info(subPass)

  scad_content = "union() {\n"

  colors = [[1, 0, 0], [0, 0.8, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1], [1, 0.5, 0],
            [0.5, 0, 1], [0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.8, 0.8, 0.8]]

  for i, face in enumerate(faces):
    centroid = face.get("centroid", [0, 0, 0])
    normal = face.get("normal", [0, 0, 1])
    label = face.get("label", str(i))
    color = colors[i % len(colors)]

    # Get shape info for this face
    if label in shape_info:
      num_sides, radius = shape_info[label]
    else:
      num_sides, radius = shape_info.get("default", (4, 0.5))

    # Generate polygon vertices
    verts = generate_face_polygon(centroid, normal, num_sides, radius)

    # Draw the face as a thin polyhedron
    scad_content += f'  color([{color[0]}, {color[1]}, {color[2]}, 0.7]) {{\n'

    # Create polygon points for OpenSCAD
    pts_str = ", ".join([f"[{v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f}]" for v in verts])

    # Extrude slightly along normal for visibility
    thickness = 0.02
    back_verts = [[v[j] - normal[j] * thickness for j in range(3)] for v in verts]
    back_pts_str = ", ".join([f"[{v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f}]" for v in back_verts])

    all_pts = f"[{pts_str}, {back_pts_str}]"

    # Build faces for the polyhedron
    n = num_sides
    top_face = list(range(n))
    bottom_face = list(range(2 * n - 1, n - 1, -1))
    side_faces = [[i, (i + 1) % n, (i + 1) % n + n, i + n] for i in range(n)]

    faces_str = f"[{top_face}, {bottom_face}"
    for sf in side_faces:
      faces_str += f", {sf}"
    faces_str += "]"

    scad_content += f'    polyhedron(points={all_pts}, faces={faces_str});\n'
    scad_content += f'  }}\n'

    # Draw normal as a line (arrow)
    end = [centroid[j] + normal[j] * 0.4 for j in range(3)]
    scad_content += f'  color([{color[0]}, {color[1]}, {color[2]}]) hull() {{\n'
    scad_content += f'    translate([{centroid[0]}, {centroid[1]}, {centroid[2]}]) sphere(0.03, $fn=12);\n'
    scad_content += f'    translate([{end[0]}, {end[1]}, {end[2]}]) sphere(0.015, $fn=12);\n'
    scad_content += f'  }}\n'

  scad_content += "}\n"

  os.makedirs("results", exist_ok=True)
  output_path = f"results/34_Visualization_{aiEngineName}_subpass{subPass}.png"
  vc.render_scadText_to_png(scad_content, output_path)

  return f'<img src="{os.path.basename(output_path)}" alt="Net Folding Visualization" style="max-width: 100%;">'


highLevelSummary = """
Can an LLM mentally fold a 2D net into a 3D polyhedron?
<br><br>
This is a classic spatial reasoning test used in IQ assessments. The LLM must:
<ul>
<li>Understand how 2D faces connect at fold lines</li>
<li>Visualize the 3D result of folding operations</li>
<li>Calculate correct positions and orientations for each face</li>
</ul>
Starting with simple cube nets and progressing to more complex polyhedra.
"""
