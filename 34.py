import math
import random
import VolumeComparison as vc
import os

skip = True

title = "Net Folding - Can a 2D net fold into a 3D polyhedron?"

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

ASCII view (Y increases upward):
    F
    E
  D A B C

This folds into a unit cube centered at (0.5, 0.5, 0.5).
""",
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

When folded, forms a tetrahedron with A as base sitting on Z=0.
""",
        "expected_faces": {
            "A": {
                "centroid": [1, math.sqrt(3) / 3, 0],
                "normal": [0, 0, -1]
            },
            "B": {
                "centroid": [1, math.sqrt(3) / 3 - 0.5,
                             math.sqrt(2 / 3)],
                "normal": [0, -math.sqrt(2 / 3),
                           math.sqrt(1 / 3)]
            },
            "C": {
                "centroid": [1.5,
                             math.sqrt(3) / 3 + 0.25,
                             math.sqrt(2 / 3)],
                "normal":
                [math.sqrt(2 / 3),
                 math.sqrt(1 / 6),
                 math.sqrt(1 / 3)]
            },
            "D": {
                "centroid": [0.5,
                             math.sqrt(3) / 3 + 0.25,
                             math.sqrt(2 / 3)],
                "normal":
                [-math.sqrt(2 / 3),
                 math.sqrt(1 / 6),
                 math.sqrt(1 / 3)]
            },
        },
        "tolerance": 0.2
    },
    {
        "name": "Octahedron net",
        "description": """
An octahedron net consisting of 8 equilateral triangles arranged in a strip:

     D E F G
    A B C H

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
A net for a rectangular box of dimensions 2 (length) x 1 (width) x 1 (height):

Face A: Rectangle 2x1 at origin - BASE (bottom of box)
Face B: Rectangle 1x1 attached to left edge of A (folds up to become left end)
Face C: Rectangle 1x1 attached to right edge of A (folds up to become right end)  
Face D: Rectangle 2x1 attached to top edge of A (folds up to become back)
Face E: Rectangle 2x1 attached to top edge of D (folds over to become top)
Face F: Rectangle 2x1 attached to bottom edge of A (folds up to become front)

      E
      D
  B   A   C
      F

When folded: box with A at bottom (Z=0), centered at (1, 0.5, 0.5)
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


def compute_icosahedron_net():
    """Generate an icosahedron net with 20 triangular faces and compute expected positions."""
    # Golden ratio
    phi = (1 + math.sqrt(5)) / 2

    # Icosahedron vertices (normalized to unit edge length)
    scale = 1 / (2 * math.sin(2 * math.pi / 5))
    vertices = [[0, 1, phi], [0, -1, phi], [0, 1, -phi], [0, -1, -phi],
                [1, phi, 0], [-1, phi, 0], [1, -phi, 0], [-1, -phi, 0],
                [phi, 0, 1], [-phi, 0, 1], [phi, 0, -1], [-phi, 0, -1]]
    vertices = [[v[i] * scale for i in range(3)] for v in vertices]

    # Icosahedron faces (20 triangles)
    faces_idx = [[0, 1, 8], [0, 8, 4], [0, 4, 5], [0, 5, 9], [0, 9, 1],
                 [1, 6, 8], [8, 6, 10], [8, 10, 4], [4, 10, 2], [4, 2, 5],
                 [5, 2, 11], [5, 11, 9], [9, 11, 7], [9, 7, 1], [1, 7, 6],
                 [3, 6, 7], [3, 7, 11], [3, 11, 2], [3, 2, 10], [3, 10, 6]]

    expected = {}
    labels = "ABCDEFGHIJKLMNOPQRST"

    for i, face in enumerate(faces_idx):
        v0, v1, v2 = [vertices[j] for j in face]
        centroid = [(v0[k] + v1[k] + v2[k]) / 3 for k in range(3)]

        # Normal = cross product of two edges, pointing outward
        e1 = [v1[k] - v0[k] for k in range(3)]
        e2 = [v2[k] - v0[k] for k in range(3)]
        normal = [
            e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2],
            e1[0] * e2[1] - e1[1] * e2[0]
        ]
        mag = math.sqrt(sum(n**2 for n in normal))
        normal = [n / mag for n in normal]

        # Ensure normal points outward (away from origin)
        if sum(centroid[k] * normal[k] for k in range(3)) < 0:
            normal = [-n for n in normal]

        expected[labels[i]] = {
            "centroid": [round(c, 4) for c in centroid],
            "normal": [round(n, 4) for n in normal]
        }

    return expected


def compute_dodecahedron_net():
    """Generate a dodecahedron net with 12 pentagonal faces."""
    phi = (1 + math.sqrt(5)) / 2

    # Dodecahedron vertices
    vertices = []
    # Cube vertices
    for i in [-1, 1]:
        for j in [-1, 1]:
            for k in [-1, 1]:
                vertices.append([i, j, k])
    # Rectangle vertices
    for i in [-1, 1]:
        for j in [-1, 1]:
            vertices.append([0, i / phi, j * phi])
            vertices.append([i / phi, j * phi, 0])
            vertices.append([i * phi, 0, j / phi])

    # Scale to unit edge
    edge_len = 2 / phi
    vertices = [[v[i] / edge_len for i in range(3)] for v in vertices]

    # Dodecahedron faces (12 pentagons) - computing face centroids
    expected = {}
    labels = "ABCDEFGHIJKL"

    # Face normals point toward these directions (normalized)
    face_normals = [[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1], [-1, 1, 1],
                    [-1, 1, -1], [-1, -1, 1], [-1, -1, -1], [0, phi, 1 / phi],
                    [0, phi, -1 / phi], [0, -phi, 1 / phi],
                    [0, -phi, -1 / phi]]

    for i, normal in enumerate(face_normals):
        mag = math.sqrt(sum(n**2 for n in normal))
        normal = [n / mag for n in normal]

        # Centroid is at distance from origin
        dist = phi**2 / math.sqrt(3)
        centroid = [normal[k] * dist / edge_len for k in range(3)]

        expected[labels[i]] = {
            "centroid": [round(c, 4) for c in centroid],
            "normal": [round(n, 4) for n in normal]
        }

    return expected


def compute_truncated_tetrahedron_net():
    """Truncated tetrahedron: 4 triangles + 4 hexagons = 8 faces."""
    # Vertices of truncated tetrahedron
    a = math.sqrt(8)
    vertices = [[3, 1, 1], [1, 3, 1], [1, 1, 3], [-3, -1, 1], [-1, -3, 1],
                [-1, -1, 3], [-3, 1, -1], [-1, 3, -1], [-1, 1, -3],
                [3, -1, -1], [1, -3, -1], [1, -1, -3]]
    scale = 1 / math.sqrt(8)
    vertices = [[v[i] * scale for i in range(3)] for v in vertices]

    expected = {}

    # Triangle faces (at original tetrahedron vertices)
    tri_centroids = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]]
    for i, c in enumerate(tri_centroids):
        mag = math.sqrt(sum(x**2 for x in c))
        dist = math.sqrt(3) * scale * 3
        centroid = [x / mag * dist for x in c]
        normal = [x / mag for x in c]
        expected[chr(65 + i)] = {
            "centroid": [round(x, 4) for x in centroid],
            "normal": [round(x, 4) for x in normal]
        }

    # Hexagon faces (at original tetrahedron faces)
    hex_normals = [[1, 1, -1], [1, -1, 1], [-1, 1, 1], [-1, -1, -1]]
    for i, n in enumerate(hex_normals):
        mag = math.sqrt(sum(x**2 for x in n))
        normal = [x / mag for x in n]
        dist = math.sqrt(3) * scale * 2
        centroid = [normal[k] * dist for k in range(3)]
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
A net for a regular icosahedron with 20 equilateral triangle faces.

The net is arranged as a strip of triangles that folds into the icosahedron:

Row 1:    A   C   E   G   I
Row 2:  B   D   F   H   J
Row 3:    K   M   O   Q   S
Row 4:  L   N   P   R   T

Face A: Base triangle at origin, normal pointing -Z after folding
Faces B-T: Connected in sequence, alternating orientation

All triangles have edge length 1.
The final icosahedron should be centered roughly at origin.

Note: The icosahedron has vertices at permutations of (0, ±1, ±φ) where φ = (1+√5)/2 ≈ 1.618
""",
        "expected_faces": compute_icosahedron_net(),
        "tolerance": 0.3
    },
    {
        "name": "Dodecahedron net (12 faces) - HARD",
        "description": """
A net for a regular dodecahedron with 12 regular pentagon faces.

The net layout (pentagons labeled A through L):

        A
      B C D
    E   F   G
      H I J
        K
        L

Face A: Top pentagon, after folding has normal pointing roughly toward (+1,+1,+1)
Face L: Bottom pentagon, normal pointing roughly toward (-1,-1,-1)
Faces B-K: Form the middle band

All pentagons are regular with edge length 1.
The dodecahedron vertices lie at corners of three mutually perpendicular golden rectangles.

Note: φ = (1+√5)/2 ≈ 1.618 (golden ratio)
Vertices include (±1, ±1, ±1) and cyclic permutations of (0, ±1/φ, ±φ)
""",
        "expected_faces": compute_dodecahedron_net(),
        "tolerance": 0.35
    },
    {
        "name": "Truncated Tetrahedron net (8 faces) - HARD",
        "description": """
A truncated tetrahedron has 8 faces: 4 equilateral triangles and 4 regular hexagons.

The net layout:

      A (triangle)
    E   F (hexagons)
  B       C (triangles)  
    G   H (hexagons)
      D (triangle)

Triangles A, B, C, D are at the truncated vertices of the original tetrahedron.
Hexagons E, F, G, H replace the original tetrahedron faces.

Triangle edge length: 1
Hexagon edge length: 1

After folding:
- Face A has centroid near (0.612, 0.612, 0.612) with normal toward (+1,+1,+1)
- Face D has centroid near (0.612, -0.612, -0.612) with normal toward (+1,-1,-1)
- Hexagons connect between triangles

The truncated tetrahedron is formed by cutting off each vertex of a tetrahedron 
at 1/3 of the edge length.
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
                f"Face {label} centroid wrong (dist={dist:.3f}, expected {exp_c})"
            )

        # Check normal (should be parallel, same direction)
        exp_n = normalize(exp["normal"])
        norm_n = normalize(normal)
        dot = sum(a * b for a, b in zip(norm_n, exp_n))
        if dot > 0.9:  # Within ~25 degrees
            total_score += 1
            details.append(f"Face {label} normal OK (dot={dot:.3f})")
        else:
            details.append(
                f"Face {label} normal wrong (dot={dot:.3f}, expected {exp_n})")

    score = total_score / max_score if max_score > 0 else 0
    return score, "<br>".join(details)


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    faces = answer.get("faces", [])

    scad_content = "union() {\n"

    colors = [
        "red", "green", "blue", "yellow", "cyan", "magenta", "orange", "purple"
    ]

    for i, face in enumerate(faces):
        centroid = face.get("centroid", [0, 0, 0])
        normal = face.get("normal", [0, 0, 1])
        label = face.get("label", str(i))
        color = colors[i % len(colors)]

        # Draw a small cube at centroid
        scad_content += f'  color("{color}") translate([{centroid[0]}, {centroid[1]}, {centroid[2]}]) sphere(0.1);\n'

        # Draw normal as a line
        end = [centroid[j] + normal[j] * 0.3 for j in range(3)]
        scad_content += f'  color("{color}") hull() {{\n'
        scad_content += f'    translate([{centroid[0]}, {centroid[1]}, {centroid[2]}]) sphere(0.02);\n'
        scad_content += f'    translate([{end[0]}, {end[1]}, {end[2]}]) sphere(0.02);\n'
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
