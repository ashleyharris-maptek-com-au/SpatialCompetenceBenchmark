import math

title = "Tetrahedron Shadow Coverage"

prompt = """
Here is the points and faces of a regular tetrahedron with all sides equal 1, resting on the Z=0 plane and with an edge along the X=0 plane:

polyhedron(
    points = [
        [0, 0, 0],                               // 0
        [1, 0, 0],                               // 1
        [0.5, sqrt(3)/2, 0],                     // 2
        [0.5, sqrt(3)/6, sqrt(2/3)]              // 3 (apex)
    ],
    faces = [
        [0, 2, 1],   // base (oriented outward)
        [0, 1, 3],
        [1, 2, 3],
        [2, 0, 3]
    ],
    convexity = 4
);

We define a 7-part rigid transform of (x,y,z,q0,q1,q2,q3), where q0,q1,q2,q3 is a normalised quaternion, and x, y, z are the translation.
Rotation is defined around the 0,0,0 point (Which is NOT THE CENTRE), and is performed before translation.

We create a scene with mulitple tetrahedra, each with a different transform. Return the transforms of such a scene
such that a shadow projected vertically (onto the Z=0 plane) fully covers PARAM, centered at the origin.

Use as many tetrahedra as you need, scoring is based on shadow coverage, not the number of tetrahedra used.

Score will be deducted for:
- any shadow outside of the square
- reduntant tetrahedra
- non-normalised quaternions
- intersection tetrahedra
"""

structure = {
    "type": "object",
    "properties": {
        "tetrahedrons": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number"
                    },
                    "y": {
                        "type": "number"
                    },
                    "z": {
                        "type": "number"
                    },
                    "q0": {
                        "type": "number"
                    },
                    "q1": {
                        "type": "number"
                    },
                    "q2": {
                        "type": "number"
                    },
                    "q3": {
                        "type": "number"
                    }
                },
                "required": ["x", "y", "z", "q0", "q1", "q2", "q3"],
                "additionalProperties": False
            }
        }
    },
    "required": ["tetrahedrons"],
    "additionalProperties": False
}

subpassParamSummary = [
    """
    Cover a square of side length 4.<br><br>
    
    (Note that the shadow has been linearly extruded to a height of 1 
    to simplify volume comparison)<br><br>

    (Note that a perfect score is possible - the tetrahedrons can't overlap
    in 2D, but they can in 3D, so a right angle can be created by two tetrahedra
    seperated on the Z axis, one rotated 90 degrees.)
    """, "Cover a circle of diameter 4",
    "Cover a square of side length 6, with a hole in the centre of side length 2"
]


def prepareSubpassPrompt(index: int) -> str:
    if index == 0: return prompt.replace("PARAM", "a square of side length 4")
    if index == 1: return prompt.replace("PARAM", "a circle of diameter 4")
    if index == 2:
        return prompt.replace(
            "PARAM",
            "a square of side length 6, with a hole in the centre of side length 2"
        )
    raise StopIteration


referenceScad = """
module reference(){
    translate([0,0,0.5]) cube([4,4,1], center=true);
}
"""


def prepareSubpassReferenceScad(index: int) -> str:
    if index == 0:
        return """
module reference(){
    translate([0,0,0.5]) cube([4,4,1], center=true);
}
"""
    if index == 1:
        return """
module reference(){
    translate([0,0,0.5]) cylinder(r=2, h=1, center=true, $fn=100);
}
"""
    if index == 2:
        return """
module reference(){
  difference() {
    translate([0,0,0.5]) cube([6,6,1], center=true);
    translate([0,0,0.5]) cube([2,2,2], center=true);
  }
}
"""


def quaternionToPitchRollYawInDegrees(q0, q1, q2, q3):
    return [
        math.degrees(
            math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))),
        math.degrees(math.asin(2 * (q0 * q2 - q1 * q3))),
        math.degrees(
            math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3)))
    ]


scadModules = """
module tetrahedron(){
    polyhedron(
        points = [
            [0, 0, 0],                               // 0
            [1, 0, 0],                               // 1
            [0.5, sqrt(3)/2, 0],                     // 2
            [0.5, sqrt(3)/6, sqrt(2/3)]              // 3 (apex)
        ],
        faces = [
            [0, 2, 1],   // base (oriented outward)
            [0, 1, 3],
            [1, 2, 3],
            [2, 0, 3]
        ],
        convexity = 4
    );
  
}
"""


def resultToScad(result):
    try:
        scad = "module result(){ "
        scad += "linear_extrude(height=1){ projection() { minkowski(){cube(0.001); union() { "
        for transform in result["tetrahedrons"]:
            scad += "translate([" + str(transform["x"]) + "," + \
                str(transform["y"]) + "," + str(transform["z"]) + "]) rotate(" + \
            str(quaternionToPitchRollYawInDegrees(transform["q0"], transform["q1"], transform["q2"], transform["q3"])) + ") tetrahedron();\n"

        return scad + "}}}}}\n\n"
    except Exception as e:
        print("Error converting result to SCAD:", e)
        return ""


def _rotate_by_quaternion(point, q0, q1, q2, q3):
    """Rotate a point by a quaternion (q0 is scalar/w component)."""
    # Using quaternion rotation: p' = q * p * q^-1
    px, py, pz = point
    # For unit quaternion, q^-1 = conjugate
    # Simplified rotation formula:
    t0 = 2 * (q1 * pz - q3 * px + q2 * py)
    t1 = 2 * (q2 * pz - q1 * py + q3 * px)
    t2 = 2 * (q3 * pz - q2 * px + q1 * py)
    return [
        px + q0 * t0 + q2 * t2 - q3 * t1, py + q0 * t1 + q3 * t0 - q1 * t2,
        pz + q0 * t2 + q1 * t1 - q2 * t0
    ]


def _get_tetrahedron_vertices(t):
    """Get transformed vertices of a tetrahedron."""
    # Base tetrahedron vertices (from scad definition)
    base_verts = [[0, 0, 0], [1, 0, 0], [0.5, math.sqrt(3) / 2, 0],
                  [0.5, math.sqrt(3) / 6,
                   math.sqrt(2 / 3)]]
    verts = []
    for v in base_verts:
        rv = _rotate_by_quaternion(v, t["q0"], t["q1"], t["q2"], t["q3"])
        verts.append([rv[0] + t["x"], rv[1] + t["y"], rv[2] + t["z"]])
    return verts


def _tetrahedrons_intersect(a, b):
    """Check if two tetrahedrons intersect using Separating Axis Theorem."""
    verts_a = _get_tetrahedron_vertices(a)
    verts_b = _get_tetrahedron_vertices(b)

    def cross(u, v):
        return [
            u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]
        ]

    def sub(p1, p2):
        return [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]

    def dot(u, v):
        return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

    def get_face_normals(verts):
        faces = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]]
        normals = []
        for f in faces:
            e1 = sub(verts[f[1]], verts[f[0]])
            e2 = sub(verts[f[2]], verts[f[0]])
            normals.append(cross(e1, e2))
        return normals

    def get_edges(verts):
        edge_pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        return [sub(verts[e[1]], verts[e[0]]) for e in edge_pairs]

    def project(verts, axis):
        dots = [dot(v, axis) for v in verts]
        return min(dots), max(dots)

    def separated_on_axis(axis, verts_a, verts_b):
        if abs(dot(axis, axis)) < 1e-10:  # Degenerate axis
            return False
        min_a, max_a = project(verts_a, axis)
        min_b, max_b = project(verts_b, axis)
        return max_a < min_b or max_b < min_a

    # Test face normals of A and B
    for normal in get_face_normals(verts_a) + get_face_normals(verts_b):
        if separated_on_axis(normal, verts_a, verts_b):
            return False

    # Test cross products of edges
    edges_a = get_edges(verts_a)
    edges_b = get_edges(verts_b)
    for ea in edges_a:
        for eb in edges_b:
            axis = cross(ea, eb)
            if separated_on_axis(axis, verts_a, verts_b):
                return False

    return True  # No separating axis found, they intersect


def validatePostVolume(result, score, resultVolume, referenceVolume,
                       intersectionVolume, differenceVolume):
    tetrahedrons = result["tetrahedrons"]
    for tetrahedron in tetrahedrons:
        if abs(tetrahedron["q0"]**2 + tetrahedron["q1"]**2 +
               tetrahedron["q2"]**2 + tetrahedron["q3"]**2 - 1) > 0.01:
            return score * 0.25, "Quaternion is not normalised. 75% penalty."

    for i, a in enumerate(tetrahedrons):
        for j, b in enumerate(tetrahedrons):
            if i < j and _tetrahedrons_intersect(a, b):
                return score * 0.5, f"Tetrahedrons {i} and {j} intersect. 50% penalty."

    return score, ""


def postProcessScore(score, subPassIndex):
    if subPassIndex == 1:
        return min(1, score / 0.9)  # Circle is impossible to cover.
    return score


highLevelSummary = """
Creating 2D shapes with regular tetrahedrons isn't something that appears in much
training data, because, why on earth would you want to do that?
<br><br>

Perfect scores are possible for the square and holed square (a single tetrahedron
can make a shadow that casts to a perfect square, but care needs to be taken to avoid intersection 
as you can't tile the plane with them all at the same z level).

<br><br>

Note that multiple rings of tetrahedra stacked in z and projected to z can
approximate a cricle very precisely, pixel perfect even.
"""
