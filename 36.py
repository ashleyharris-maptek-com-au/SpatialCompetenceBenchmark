import math
import random
import VolumeComparison as vc
import os

title = "Cross-Section Slicing - What shape results from cutting a 3D object?"

prompt = """
You are given a 3D object and a cutting plane. Determine the 2D shape that results from 
slicing the object with that plane.

OBJECT_DESCRIPTION

PLANE_DESCRIPTION

Describe the resulting 2D cross-section shape by providing its vertices in order (clockwise 
when viewed from the positive side of the cutting plane's normal).

Express all coordinates in the local 2D coordinate system of the cutting plane, where:
- The origin is at the projection of the origin onto the cutting plane
- U-axis and V-axis are as specified for each plane
"""

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "shapeType": {
            "type":
            "string",
            "description":
            "Name of the shape (Prefer single word name of shape with most contraints - eg 'hexagon' over 'polygon', 'rectangle' over 'quadrilateral')"
        },
        "vertices": {
            "type":
            "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "description": "UV coordinates of each vertex"
            },
            "description":
            "For polygonal shapes, list vertices in order. For circles/ellipses, leave empty and provide center and radii instead."
        },
        "center": {
            "type":
            "array",
            "items": {
                "type": "number"
            },
            "description":
            "For circles/ellipses: [u, v] center point. [] For everything else."
        },
        "radii": {
            "type":
            "array",
            "items": {
                "type": "number"
            },
            "description":
            "For circles: [r]. For ellipses: [major_radius, minor_radius]. [] For everything else."
        }
    },
    "propertyOrdering":
    ["reasoning", "shapeType", "vertices", "center", "radii"],
    "required": ["reasoning", "shapeType", "vertices", "center", "radii"],
    "additionalProperties": False
}

# Define slicing problems
problems = [
    {
        "name": "Cube horizontal slice",
        "object": """
A unit cube with corners at (0,0,0) and (1,1,1).
""",
        "plane": """
Cutting plane: Z = 0.5 (horizontal slice through the middle)
U-axis: X direction, V-axis: Y direction
""",
        "expected_type": "square",
        "expected_vertices": [[0, 0], [1, 0], [1, 1], [0, 1]],
        "tolerance": 0.05
    },
    {
        "name": "Cube diagonal slice",
        "object": """
A unit cube with corners at (0,0,0) and (1,1,1).
""",
        "plane": """
Cutting plane: passes through points (0,0,0), (1,1,0), and (0.5,0.5,1)
This is a diagonal slice from one edge to the opposite edge.
U-axis: along the (1,1,0) direction, V-axis: perpendicular, pointing upward
""",
        "expected_type": "rectangle",
        "expected_vertices": [[0, 0], [math.sqrt(2), 0], [math.sqrt(2), 1],
                              [0, 1]],
        "tolerance": 0.1
    },
    {
        "name": "Sphere slice",
        "object": """
A sphere of radius 5 centered at the origin (0,0,0).
""",
        "plane": """
Cutting plane: Z = 3 (horizontal slice 3 units above center)
U-axis: X direction, V-axis: Y direction
""",
        "expected_type": "circle",
        "expected_center": [0, 0],
        "expected_radii": [4],  # sqrt(25-9) = 4
        "tolerance": 0.2
    },
    {
        "name": "Cylinder angled slice",
        "object": """
A cylinder with:
- Radius 2
- Height 10 (from Z=0 to Z=10)
- Centered on the Z axis
""",
        "plane": """
Cutting plane: tilted 45 degrees, passing through (0,0,5)
Normal vector: (0, 1, 1) normalized
U-axis: X direction, V-axis: along the cut slope
""",
        "expected_type": "ellipse",
        "expected_center": [0, 0],
        "expected_radii": [2, 2 * math.sqrt(2)],  # minor=2, major=2*sqrt(2)
        "tolerance": 0.2
    },
    {
        "name":
        "Hexagonal prism slice",
        "object":
        """
A regular hexagonal prism with:
- Hexagon inscribed in circle of radius 2 (flat side to flat side = 2*sqrt(3))
- Height 6 (from Z=0 to Z=6)
- Centered on Z axis with one vertex pointing in +X direction
""",
        "plane":
        """
Cutting plane: Z = 3 (horizontal slice through middle)
U-axis: X direction, V-axis: Y direction
""",
        "expected_type":
        "hexagon",
        "expected_vertices": [[2, 0], [1, math.sqrt(3)], [-1, math.sqrt(3)],
                              [-2, 0], [-1, -math.sqrt(3)], [1,
                                                             -math.sqrt(3)]],
        "tolerance":
        0.15
    },
]

# === SUPER-HARD CHALLENGES ===
# Complex shapes requiring computational geometry


def compute_torus_slice(R, r, plane_z):
    """
    Compute cross-section of a torus sliced by horizontal plane.
    R = major radius (center of tube to center of torus)
    r = minor radius (tube radius)
    plane_z = height of cutting plane
    """
    # For a torus centered at origin with axis along Z:
    # If |plane_z| < r, the slice is two circles (or figure-8 at z=0)
    # If |plane_z| > r, no intersection

    if abs(plane_z) >= r:
        return None, None, None

    # Distance from tube center to slice
    d = abs(plane_z)
    # Radius of each circular cross-section
    slice_r = math.sqrt(r**2 - d**2)

    # Centers of the two circles
    center1 = [R, 0]
    center2 = [-R, 0]

    return "two_circles", [center1, center2], [slice_r, slice_r]


def compute_cone_slice(apex, base_center, base_radius, plane_normal,
                       plane_point):
    """
    Compute conic section from slicing a cone.
    Returns type (circle, ellipse, parabola, hyperbola) and parameters.
    """
    # Simplified: for a cone along Z axis with apex at origin
    # Slicing at angle determines conic type

    # This is complex - return pre-computed for specific cases
    return None


def compute_stellated_octahedron_slice(plane_z):
    """
    Slice through a stellated octahedron (stella octangula).
    This is two interpenetrating tetrahedra.
    """
    # At z=0, the cross-section is a hexagram (Star of David)
    if abs(plane_z) < 0.01:
        # Regular hexagram with vertices alternating between inner and outer
        outer_r = 1.0
        inner_r = outer_r / 2
        vertices = []
        for i in range(12):
            angle = i * math.pi / 6
            r = outer_r if i % 2 == 0 else inner_r
            vertices.append([r * math.cos(angle), r * math.sin(angle)])
        return "hexagram", vertices

    return None, None


def compute_mobius_band_slice():
    """
    Conceptual - a Möbius band sliced produces interesting topology.
    """
    pass


# Add computed hard problems
problems.extend([
    {
        "name": "Torus horizontal slice - HARD",
        "object": """
A torus (donut shape) with:
- Major radius R = 5 (distance from center of torus to center of tube)
- Minor radius r = 2 (radius of the tube)
- Centered at origin with axis along Z
""",
        "plane": """
Cutting plane: Z = 1 (horizontal slice above center)
U-axis: X direction, V-axis: Y direction
""",
        "expected_type": "two_circles",
        "expected_center": [[5, 0], [-5, 0]],  # Two circle centers
        "expected_radii": [math.sqrt(3), math.sqrt(3)],  # sqrt(4-1) for each
        "tolerance": 0.2
    },
    {
        "name":
        "Cube maximum hexagon slice - HARD",
        "object":
        """
A cube with vertices at (±1, ±1, ±1), centered at origin.
""",
        "plane":
        """
Cutting plane: passes through (1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)
This plane is perpendicular to the (1,1,1) diagonal.
Normal vector: (1,1,1) normalized = (0.577, 0.577, 0.577)
U-axis: (1,-1,0) normalized, V-axis: (1,1,-2) normalized
""",
        "expected_type":
        "hexagon",
        "expected_vertices": [[math.sqrt(2), 0],
                              [math.sqrt(2) / 2,
                               math.sqrt(6) / 2],
                              [-math.sqrt(2) / 2,
                               math.sqrt(6) / 2], [-math.sqrt(2), 0],
                              [-math.sqrt(2) / 2, -math.sqrt(6) / 2],
                              [math.sqrt(2) / 2, -math.sqrt(6) / 2]],
        "tolerance":
        0.25
    },
    {
        "name": "Cone diagonal slice (ellipse) - HARD",
        "object": """
A cone with:
- Apex at (0, 0, 10)
- Base circle of radius 5 at Z = 0, centered on Z axis
- Height 10
""",
        "plane": """
Cutting plane: tilted 30 degrees from horizontal, passing through (0, 0, 5)
Normal vector: (0, sin(30°), cos(30°)) = (0, 0.5, 0.866)
The plane cuts the cone at an angle less steep than the cone's side, producing an ellipse.
U-axis: X direction, V-axis: along the tilted plane's slope
""",
        "expected_type": "ellipse",
        "expected_center": [0, 0],
        # At height 5, cone radius = 2.5. Tilted cut creates ellipse.
        "expected_radii": [2.5, 2.5 / math.cos(math.radians(30))],
        "tolerance": 0.3
    },
    {
        "name":
        "Intersecting cylinders slice - HARD",
        "object":
        """
Two perpendicular cylinders, both radius 3:
- Cylinder A: axis along Z, centered at origin
- Cylinder B: axis along X, centered at origin

The solid is the INTERSECTION of these two cylinders (a Steinmetz solid).
""",
        "plane":
        """
Cutting plane: Z = 2 (horizontal slice)
U-axis: X direction, V-axis: Y direction

Note: At this height, the cross-section is bounded by:
- Cylinder A contributes: circle of radius 3 centered at origin
- Cylinder B contributes: two vertical lines at X = ±sqrt(9-4) = ±sqrt(5)

The intersection creates a shape bounded by circular arcs and straight lines.
""",
        "expected_type":
        "lens",
        "expected_vertices": [[math.sqrt(5), math.sqrt(4)], [0, 3],
                              [-math.sqrt(5), math.sqrt(4)],
                              [-math.sqrt(5), -math.sqrt(4)], [0, -3],
                              [math.sqrt(5), -math.sqrt(4)]],
        "tolerance":
        0.3
    },
    {
        "name":
        "Twisted prism slice - HARD",
        "object":
        """
A twisted triangular prism:
- Base: equilateral triangle with vertices at (2,0,0), (-1,√3,0), (-1,-√3,0)
- Top: same triangle but rotated 60° around Z axis at height Z=6
- The prism is linearly twisted between base and top

Vertices:
Bottom (Z=0): (2,0,0), (-1,1.732,0), (-1,-1.732,0)
Top (Z=6): (-2,0,6), (1,1.732,6), (1,-1.732,6)
""",
        "plane":
        """
Cutting plane: Z = 3 (horizontal slice at half height)
At this height, the triangle has rotated 30° from the base position.
U-axis: X direction, V-axis: Y direction
""",
        "expected_type":
        "triangle",
        "expected_vertices":
        [[2 * math.cos(math.radians(30)), 2 * math.sin(math.radians(30))],
         [2 * math.cos(math.radians(150)), 2 * math.sin(math.radians(150))],
         [2 * math.cos(math.radians(270)), 2 * math.sin(math.radians(270))]],
        "tolerance":
        0.2
    },
    {
        "name":
        "Dodecahedron slice - HARD",
        "object":
        """
A regular dodecahedron (12 pentagonal faces) with:
- Center at origin
- Vertices at distance φ² from origin where φ = (1+√5)/2 ≈ 1.618
- One face has normal pointing in +Z direction
""",
        "plane":
        """
Cutting plane: Z = 0 (through the center)
U-axis: X direction, V-axis: Y direction

The cross-section through the center of a dodecahedron, 
perpendicular to a face-to-face axis, is a regular decagon (10 sides).
""",
        "expected_type":
        "decagon",
        "expected_vertices": [[
            1.618 * math.cos(i * math.pi / 5),
            1.618 * math.sin(i * math.pi / 5)
        ] for i in range(10)],
        "tolerance":
        0.3
    },
])

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Different 3D objects and cutting planes"


def prepareSubpassPrompt(index: int) -> str:

    if index >= len(problems):
        raise StopIteration
    prob = problems[index]
    p = prompt.replace("OBJECT_DESCRIPTION", prob["object"])
    p = p.replace("PLANE_DESCRIPTION", prob["plane"])
    return p


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    prob = problems[subPass]
    tolerance = prob["tolerance"]

    shape_type = answer.get("shapeType", "").lower()
    expected_type = prob["expected_type"].lower()

    # Check shape type (partial credit for close matches)
    type_score = 0
    if shape_type == expected_type:
        type_score = 1
    elif shape_type in expected_type or expected_type in shape_type:
        type_score = 0.5

    # Check geometry
    geom_score = 0
    details = [
        f"Shape type: {shape_type} (expected {expected_type}) - {type_score:.1f} pts"
    ]

    if expected_type in ["circle", "ellipse"]:
        # Check center and radii
        exp_center = prob.get("expected_center", [0, 0])
        exp_radii = prob.get("expected_radii", [1])

        center = answer.get("center", [0, 0])
        radii = answer.get("radii", [1])

        if not isinstance(center, list) or len(center) < 2:
            center = [0, 0]
        if not isinstance(radii, list) or len(radii) < 1:
            radii = [1]

        center_dist = math.sqrt((center[0] - exp_center[0])**2 +
                                (center[1] - exp_center[1])**2)
        if center_dist <= tolerance:
            geom_score += 0.5
            details.append(f"Center OK: {center}")
        else:
            details.append(f"Center wrong: {center} (expected {exp_center})")

        # Check radii (allow any order for ellipse)
        radii_sorted = sorted(radii)
        exp_sorted = sorted(exp_radii)

        radii_match = True
        for r, e in zip(radii_sorted, exp_sorted):
            if abs(r - e) > tolerance:
                radii_match = False
                break

        if radii_match:
            geom_score += 0.5
            details.append(f"Radii OK: {radii}")
        else:
            details.append(f"Radii wrong: {radii} (expected {exp_radii})")

    else:
        # Check vertices for polygonal shapes
        vertices = answer.get("vertices", [])
        exp_vertices = prob.get("expected_vertices", [])

        if len(vertices) != len(exp_vertices):
            details.append(
                f"Wrong vertex count: {len(vertices)} (expected {len(exp_vertices)})"
            )
        else:
            # Try to match vertices (allowing for rotation/starting point)
            best_match = 0
            n = len(exp_vertices)

            for offset in range(n):
                for direction in [1, -1]:  # Try both winding orders
                    matches = 0
                    for i, exp_v in enumerate(exp_vertices):
                        idx = (offset + i * direction) % n
                        if idx < len(vertices):
                            v = vertices[idx]
                            if isinstance(v, list) and len(v) >= 2:
                                dist = math.sqrt((v[0] - exp_v[0])**2 +
                                                 (v[1] - exp_v[1])**2)
                                if dist <= tolerance:
                                    matches += 1
                    best_match = max(best_match, matches)

            geom_score = best_match / n if n > 0 else 0
            details.append(f"Matched {best_match}/{n} vertices")

    total_score = (type_score + geom_score) / 2
    return total_score, "<br>".join(details)


def generate_3d_object_scad(prob):
    """Generate OpenSCAD code for the 3D object in the problem."""
    name = prob["name"].lower()

    if "cube" in name and "unit" in prob["object"].lower():
        if "±1" in prob["object"]:
            # Cube centered at origin with vertices at ±1
            return "translate([-1,-1,-1]) cube([2,2,2]);"
        else:
            # Unit cube at origin
            return "cube([1,1,1]);"

    elif "sphere" in name:
        # Extract radius from problem
        if "radius 5" in prob["object"]:
            return "$fn=64; sphere(r=5);"
        return "$fn=64; sphere(r=1);"

    elif "cylinder" in name:
        if "radius 2" in prob["object"].lower(
        ) and "height 10" in prob["object"].lower():
            return "$fn=64; cylinder(r=2, h=10);"
        return "$fn=64; cylinder(r=1, h=5);"

    elif "hexagonal prism" in name:
        # Regular hexagonal prism, radius 2, height 6
        return "$fn=6; cylinder(r=2, h=6);"

    elif "torus" in name:
        # Torus with R=5, r=2
        return "$fn=64; rotate_extrude() translate([5,0,0]) circle(r=2);"

    elif "cone" in name:
        # Cone with apex at (0,0,10), base radius 5 at z=0
        return "$fn=64; cylinder(r1=5, r2=0, h=10);"

    elif "intersecting cylinders" in name or "steinmetz" in name.lower():
        # Steinmetz solid - intersection of two perpendicular cylinders
        return """$fn=64;
intersection() {
    cylinder(r=3, h=20, center=true);
    rotate([0,90,0]) cylinder(r=3, h=20, center=true);
}"""

    elif "twisted prism" in name:
        # Twisted triangular prism - approximate with linear_extrude and twist
        return """$fn=32;
linear_extrude(height=6, twist=60) 
    polygon(points=[[2,0], [-1,1.732], [-1,-1.732]]);"""

    elif "dodecahedron" in name:
        # Approximate dodecahedron using OpenSCAD's polyhedron or hull
        phi = 1.618
        return f"""$fn=32;
// Dodecahedron approximation
scale([{phi},{phi},{phi}]) {{
    hull() {{
        for(i=[0:4]) rotate([0,0,i*72]) translate([1.17,0,0.85]) sphere(r=0.3);
        for(i=[0:4]) rotate([0,0,i*72+36]) translate([1.17,0,-0.85]) sphere(r=0.3);
        translate([0,0,1.4]) sphere(r=0.3);
        translate([0,0,-1.4]) sphere(r=0.3);
    }}
}}"""

    # Default cube
    return "cube([1,1,1]);"


def generate_cutting_plane_scad(prob, scale=10):
    """Generate OpenSCAD code for the cutting plane visualization."""
    name = prob["name"].lower()
    plane_desc = prob["plane"].lower()

    # Parse plane from description
    if "z = 0.5" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},0.5]) cube([{scale*2},{scale*2},0.01]);"
    elif "z = 3" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},3]) cube([{scale*2},{scale*2},0.01]);"
    elif "z = 1" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},1]) cube([{scale*2},{scale*2},0.01]);"
    elif "z = 2" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},2]) cube([{scale*2},{scale*2},0.01]);"
    elif "z = 0" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},0]) cube([{scale*2},{scale*2},0.01]);"
    elif "z = 5" in plane_desc:
        return f"color([1,0,0,0.3]) translate([-{scale},-{scale},5]) cube([{scale*2},{scale*2},0.01]);"
    elif "diagonal" in plane_desc or "(1,1,1)" in plane_desc:
        # Diagonal plane through cube
        return f"color([1,0,0,0.3]) rotate([35.26,0,45]) translate([-{scale},-{scale},0]) cube([{scale*2},{scale*2},0.01]);"
    elif "tilted 45" in plane_desc or "tilted 30" in plane_desc:
        angle = 45 if "45" in plane_desc else 30
        return f"color([1,0,0,0.3]) translate([0,0,5]) rotate([{angle},0,0]) translate([-{scale},-{scale},0]) cube([{scale*2},{scale*2},0.01]);"

    # Default horizontal plane at z=0.5
    return f"color([1,0,0,0.3]) translate([-{scale},-{scale},0.5]) cube([{scale*2},{scale*2},0.01]);"


def generate_cross_section_scad(answer, prob):
    """Generate OpenSCAD code for the 2D cross-section result."""
    shape_type = answer.get("shapeType", "").lower()
    vertices = answer.get("vertices", [])
    center = answer.get("center", [0, 0])
    radii = answer.get("radii", [1])

    scad = "$fn=64;\n"

    if shape_type in ["circle"] and radii:
        r = radii[0] if radii else 1
        cx, cy = center if len(center) >= 2 else [0, 0]
        scad += f"translate([{cx},{cy},0]) circle(r={r});"

    elif shape_type in ["ellipse"] and radii:
        rx = radii[0] if len(radii) > 0 else 1
        ry = radii[1] if len(radii) > 1 else rx
        cx, cy = center if len(center) >= 2 else [0, 0]
        scad += f"translate([{cx},{cy},0]) scale([{rx},{ry},1]) circle(r=1);"

    elif shape_type == "two_circles" and radii:
        # Two circles for torus slice
        centers = answer.get("center", [[5, 0], [-5, 0]])
        if isinstance(centers[0], list):
            for i, c in enumerate(centers):
                r = radii[i] if i < len(radii) else radii[0]
                scad += f"translate([{c[0]},{c[1]},0]) circle(r={r});\n"
        else:
            r = radii[0] if radii else 1
            scad += f"translate([5,0,0]) circle(r={r});\n"
            scad += f"translate([-5,0,0]) circle(r={r});\n"

    elif vertices and len(vertices) >= 3:
        # Polygon from vertices
        pts = ", ".join(f"[{v[0]},{v[1]}]" for v in vertices
                        if isinstance(v, list) and len(v) >= 2)
        if pts:
            scad += f"polygon(points=[{pts}]);"

    else:
        # Fallback - just a small square
        scad += "square([0.5, 0.5], center=true);"

    return scad


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    prob = problems[subPass]
    shape_type = answer.get("shapeType", "unknown")

    html = f"<b>Shape type:</b> {shape_type}<br>"

    if "center" in answer:
        html += f"<b>Center:</b> {answer['center']}<br>"
    if "radii" in answer:
        html += f"<b>Radii:</b> {answer['radii']}<br>"
    if "vertices" in answer:
        html += f"<b>Vertices:</b><br>"
        for i, v in enumerate(answer["vertices"]):
            html += f"  {i}: {v}<br>"

    # Generate 3D visualization with cutting plane
    try:
        object_scad = generate_3d_object_scad(prob)
        plane_scad = generate_cutting_plane_scad(prob)

        # Determine appropriate scale for the plane
        name = prob["name"].lower()
        if "sphere" in name or "torus" in name:
            scale = 8
        elif "cylinder" in name or "cone" in name:
            scale = 5
        else:
            scale = 3

        full_scad = f"""// 3D Object with cutting plane
color([0.5, 0.7, 1.0, 0.7]) {{
{object_scad}
}}
{plane_scad}
"""

        output_3d = f"results/36_{subPass}_{aiEngineName}_3d.png"
        vc.render_scadText_to_png(full_scad, output_3d)
        html += f'<br><b>3D Object with Cutting Plane:</b><br><img src="{os.path.basename(output_3d)}" /><br>'

        # Generate 2D cross-section visualization
        cross_section_scad = generate_cross_section_scad(answer, prob)

        # Also show expected cross-section for comparison
        expected_scad = "$fn=64;\n"
        exp_type = prob.get("expected_type", "").lower()

        if exp_type in ["circle", "ellipse"]:
            exp_center = prob.get("expected_center", [0, 0])
            exp_radii = prob.get("expected_radii", [1])
            if exp_type == "circle":
                expected_scad += f"color([0,1,0,0.5]) translate([{exp_center[0]},{exp_center[1]},0]) circle(r={exp_radii[0]});"
            else:
                rx = exp_radii[0]
                ry = exp_radii[1] if len(exp_radii) > 1 else rx
                expected_scad += f"color([0,1,0,0.5]) translate([{exp_center[0]},{exp_center[1]},0]) scale([{rx},{ry},1]) circle(r=1);"
        elif exp_type == "two_circles":
            exp_centers = prob.get("expected_center", [[5, 0], [-5, 0]])
            exp_radii = prob.get("expected_radii", [1, 1])
            for i, c in enumerate(exp_centers):
                r = exp_radii[i] if i < len(exp_radii) else exp_radii[0]
                expected_scad += f"color([0,1,0,0.5]) translate([{c[0]},{c[1]},0]) circle(r={r});\n"
        else:
            exp_vertices = prob.get("expected_vertices", [])
            if exp_vertices:
                pts = ", ".join(f"[{v[0]},{v[1]}]" for v in exp_vertices)
                expected_scad += f"color([0,1,0,0.5]) polygon(points=[{pts}]);"

        # Combine answer (red) and expected (green) cross-sections
        combined_2d = f"""// Cross-section comparison: Red=Answer, Green=Expected
color([1,0,0,0.7]) linear_extrude(height=0.1) {{
{cross_section_scad}
}}
translate([0,0,-0.1]) {{
{expected_scad.replace('color([0,1,0,0.5])', 'color([0,1,0,0.7]) linear_extrude(height=0.1)')}
}}
"""

        output_2d = f"results/36_{subPass}_{aiEngineName}_cross_section.png"
        vc.render_scadText_to_png(combined_2d,
                                  output_2d,
                                  cameraArg="--camera=0,0,10,0,0,0")
        html += f'<br><b>Cross-Section (Red=Answer, Green=Expected):</b><br><img src="{os.path.basename(output_2d)}" /><br>'

    except Exception as e:
        html += f"<br><i>Visualization error: {e}</i><br>"

    return html


highLevelSummary = """
Tests the ability to mentally slice 3D objects and predict the resulting 2D cross-section.
<br><br>
This is a fundamental spatial reasoning skill:
<ul>
<li>Horizontal slices through regular solids</li>
<li>Diagonal/angled cuts</li>
<li>Understanding how circles become ellipses when cylinders are cut at angles</li>
<li>Recognizing that cube diagonals create rectangles</li>
</ul>
Used in medical imaging, manufacturing, and architecture.
"""
