import math
import random

skip = True

title = "Mirror Reflection - What do you see in the mirror?"

prompt = """
You are in a room with mirrors on some walls. Objects are placed at various positions.
You are standing at a specific location, looking in a specific direction.

ROOM_DESCRIPTION

For each mirror visible from your position:
1. What objects can you see reflected in that mirror?
2. Where does each object appear to be located (as seen in the mirror)?

Remember: In a mirror, objects appear at the same perpendicular distance behind the mirror 
as they are in front of it. The mirror image is laterally inverted.

For a flat mirror on the YZ plane at X=0:
- An object at (3, 5, 2) appears at (-3, 5, 2) in the mirror
- You can see an object in the mirror if the line from your eye to the mirror image 
  intersects the mirror surface AND doesn't pass through any obstacles.
"""

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "mirrorViews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "mirrorName": {
                        "type": "string"
                    },
                    "visibleObjects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objectName": {
                                    "type": "string"
                                },
                                "apparentPosition": {
                                    "type":
                                    "array",
                                    "items": {
                                        "type": "number"
                                    },
                                    "description":
                                    "Where the object appears to be [x, y, z]"
                                }
                            },
                            "required": ["objectName", "apparentPosition"],
                            "additionalProperties": False
                        }
                    },
                    "canSeeYourself": {
                        "type": "boolean",
                        "description": "Can you see your own reflection?"
                    }
                },
                "required": ["mirrorName", "visibleObjects", "canSeeYourself"],
                "additionalProperties": False
            }
        }
    },
    "propertyOrdering": ["reasoning", "mirrorViews"],
    "required": ["reasoning", "mirrorViews"],
    "additionalProperties": False
}


def reflect_point(point, mirror):
    """Reflect a point across a mirror plane."""
    # Mirror is defined by: normal vector and a point on the plane
    normal = mirror["normal"]
    plane_point = mirror["point"]

    # Vector from plane point to our point
    v = [point[i] - plane_point[i] for i in range(3)]

    # Distance to plane (signed)
    dist = sum(v[i] * normal[i] for i in range(3))

    # Reflected point
    reflected = [point[i] - 2 * dist * normal[i] for i in range(3)]
    return reflected


def line_intersects_plane(p1, p2, plane_point, plane_normal):
    """Check if line from p1 to p2 intersects the plane, return intersection point or None."""
    d = [p2[i] - p1[i] for i in range(3)]
    denom = sum(d[i] * plane_normal[i] for i in range(3))

    if abs(denom) < 1e-9:
        return None  # Line parallel to plane

    w = [p1[i] - plane_point[i] for i in range(3)]
    t = -sum(w[i] * plane_normal[i] for i in range(3)) / denom

    if t < 0 or t > 1:
        return None  # Intersection outside segment

    intersection = [p1[i] + t * d[i] for i in range(3)]
    return intersection


def point_in_mirror_bounds(point, mirror):
    """Check if a point on the mirror plane is within mirror bounds."""
    bounds = mirror.get("bounds", None)
    if bounds is None:
        return True

    # Bounds format: {"x": [min, max], "y": [min, max], "z": [min, max]}
    for axis, (lo, hi) in bounds.items():
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        if not (lo <= point[idx] <= hi):
            return False
    return True


def can_see_in_mirror(viewer_pos, object_pos, mirror):
    """Check if viewer can see object in mirror."""
    # Calculate reflection of object
    reflected_pos = reflect_point(object_pos, mirror)

    # Check if line from viewer to reflected position intersects mirror
    intersection = line_intersects_plane(viewer_pos, reflected_pos,
                                         mirror["point"], mirror["normal"])

    if intersection is None:
        return False, None

    # Check if intersection is within mirror bounds
    if not point_in_mirror_bounds(intersection, mirror):
        return False, None

    return True, reflected_pos


# Define problems
problems = [
    {
        "name":
        "Simple wall mirror",
        "description":
        """
Room: 10m x 10m x 3m (X: 0-10, Y: 0-10, Z: 0-3)

Mirror: On the wall at X=0, covering Y: 2-8, Z: 0.5-2.5
  - Normal pointing in +X direction

Objects:
- Red Ball at (3, 5, 1)
- Blue Cube at (7, 3, 0.5)
- Green Cone at (5, 8, 1.5)

Your position: (8, 5, 1.5)
Looking direction: toward the mirror (-X direction)
""",
        "mirrors": [{
            "name": "Wall Mirror",
            "point": [0, 0, 0],
            "normal": [1, 0, 0],
            "bounds": {
                "y": [2, 8],
                "z": [0.5, 2.5]
            }
        }],
        "objects": [
            {
                "name": "Red Ball",
                "pos": [3, 5, 1]
            },
            {
                "name": "Blue Cube",
                "pos": [7, 3, 0.5]
            },
            {
                "name": "Green Cone",
                "pos": [5, 8, 1.5]
            },
        ],
        "viewer": [8, 5, 1.5]
    },
    {
        "name":
        "Corner mirrors",
        "description":
        """
Room: 10m x 10m x 3m (X: 0-10, Y: 0-10, Z: 0-3)

Mirror A: On wall at X=0, covering Y: 0-10, Z: 0-3 (full wall)
  - Normal pointing in +X direction
  
Mirror B: On wall at Y=0, covering X: 0-10, Z: 0-3 (full wall)
  - Normal pointing in +Y direction

Objects:
- Statue at (2, 3, 1)
- Lamp at (7, 2, 2)

Your position: (5, 5, 1.5)
Looking toward the corner (toward -X and -Y)
""",
        "mirrors": [{
            "name": "Mirror A",
            "point": [0, 0, 0],
            "normal": [1, 0, 0],
            "bounds": {
                "y": [0, 10],
                "z": [0, 3]
            }
        }, {
            "name": "Mirror B",
            "point": [0, 0, 0],
            "normal": [0, 1, 0],
            "bounds": {
                "x": [0, 10],
                "z": [0, 3]
            }
        }],
        "objects": [
            {
                "name": "Statue",
                "pos": [2, 3, 1]
            },
            {
                "name": "Lamp",
                "pos": [7, 2, 2]
            },
        ],
        "viewer": [5, 5, 1.5]
    },
    {
        "name":
        "Floor mirror",
        "description":
        """
Room: 10m x 10m x 5m

Mirror: On the floor at Z=0, covering X: 3-7, Y: 3-7
  - Normal pointing in +Z direction (upward)

Objects:
- Chandelier at (5, 5, 4) (hanging from ceiling)
- Chair at (4, 6, 0.5)
- Person (you) at standing position

Your position: (5, 4, 1.6) (standing at edge of floor mirror, looking down)
""",
        "mirrors": [{
            "name": "Floor Mirror",
            "point": [0, 0, 0],
            "normal": [0, 0, 1],
            "bounds": {
                "x": [3, 7],
                "y": [3, 7]
            }
        }],
        "objects": [
            {
                "name": "Chandelier",
                "pos": [5, 5, 4]
            },
            {
                "name": "Chair",
                "pos": [4, 6, 0.5]
            },
        ],
        "viewer": [5, 4, 1.6]
    },
    {
        "name":
        "Angled mirror",
        "description":
        """
Room with an angled mirror at 45 degrees.

Mirror: Plane through (5, 0, 0) with normal (0.707, 0.707, 0) - angled 45° between +X and +Y
  - Bounded: Y: 0-5, Z: 0-3

Objects:
- Vase at (2, 2, 1)
- Clock at (8, 1, 2)

Your position: (3, 6, 1.5)
""",
        "mirrors": [{
            "name": "Angled Mirror",
            "point": [5, 0, 0],
            "normal": [0.707, 0.707, 0],
            "bounds": {
                "z": [0, 3]
            }
        }],
        "objects": [
            {
                "name": "Vase",
                "pos": [2, 2, 1]
            },
            {
                "name": "Clock",
                "pos": [8, 1, 2]
            },
        ],
        "viewer": [3, 6, 1.5]
    },
]

# === SUPER-HARD CHALLENGES ===
# Complex multi-mirror setups with many objects


def generate_mirror_problem(num_mirrors, num_objects, seed):
    """Generate a random mirror problem."""
    random.seed(seed)

    room_size = 20

    mirrors = []
    # Generate mirrors on different walls/surfaces
    wall_options = [
        {
            "point": [0, 0, 0],
            "normal": [1, 0, 0],
            "axis_bounds": ["y", "z"]
        },  # X=0 wall
        {
            "point": [room_size, 0, 0],
            "normal": [-1, 0, 0],
            "axis_bounds": ["y", "z"]
        },  # X=max wall
        {
            "point": [0, 0, 0],
            "normal": [0, 1, 0],
            "axis_bounds": ["x", "z"]
        },  # Y=0 wall
        {
            "point": [0, room_size, 0],
            "normal": [0, -1, 0],
            "axis_bounds": ["x", "z"]
        },  # Y=max wall
        {
            "point": [0, 0, 0],
            "normal": [0, 0, 1],
            "axis_bounds": ["x", "y"]
        },  # Floor
    ]

    used_walls = random.sample(range(len(wall_options)),
                               min(num_mirrors, len(wall_options)))

    for i, wall_idx in enumerate(used_walls):
        wall = wall_options[wall_idx]
        bounds = {}
        for axis in wall["axis_bounds"]:
            lo = random.uniform(2, 8)
            hi = random.uniform(lo + 3, min(lo + 10, room_size - 2))
            bounds[axis] = [lo, hi]

        mirrors.append({
            "name": f"Mirror {chr(65+i)}",
            "point": wall["point"],
            "normal": wall["normal"],
            "bounds": bounds
        })

    # Generate random objects
    objects = []
    object_names = [
        "Sphere", "Cube", "Pyramid", "Cylinder", "Cone", "Torus", "Vase",
        "Lamp", "Chair", "Table", "Plant", "Statue", "Clock", "Book", "Box",
        "Ball"
    ]

    for i in range(num_objects):
        name = f"{object_names[i % len(object_names)]} {i+1}"
        pos = [
            random.uniform(2, room_size - 2),
            random.uniform(2, room_size - 2),
            random.uniform(0.5, 4)
        ]
        objects.append({"name": name, "pos": pos})

    viewer = [
        random.uniform(5, room_size - 5),
        random.uniform(5, room_size - 5), 1.6
    ]

    return mirrors, objects, viewer


def format_mirror_description(mirrors, objects, viewer, room_size=20):
    """Format a mirror problem as description text."""
    desc = f"\nRoom: {room_size}m x {room_size}m x 5m\n\n"

    for mirror in mirrors:
        desc += f"{mirror['name']}: "
        if mirror["normal"] == [1, 0, 0]:
            desc += "On wall at X=0"
        elif mirror["normal"] == [-1, 0, 0]:
            desc += f"On wall at X={room_size}"
        elif mirror["normal"] == [0, 1, 0]:
            desc += "On wall at Y=0"
        elif mirror["normal"] == [0, -1, 0]:
            desc += f"On wall at Y={room_size}"
        elif mirror["normal"] == [0, 0, 1]:
            desc += "On floor at Z=0"
        else:
            desc += f"Plane with normal {mirror['normal']}"

        bounds_str = ", ".join(f"{k.upper()}: [{v[0]:.1f}, {v[1]:.1f}]"
                               for k, v in mirror["bounds"].items())
        desc += f", covering {bounds_str}\n"

    desc += "\nObjects:\n"
    for obj in objects:
        desc += f"- {obj['name']} at ({obj['pos'][0]:.1f}, {obj['pos'][1]:.1f}, {obj['pos'][2]:.1f})\n"

    desc += f"\nYour position: ({viewer[0]:.1f}, {viewer[1]:.1f}, {viewer[2]:.1f})\n"

    return desc


# Generate hard problems
hard_mirror_data = [
    (3, 8, 99901),  # 3 mirrors, 8 objects
    (4, 12, 99902),  # 4 mirrors, 12 objects  
    (5, 15, 99903),  # 5 mirrors, 15 objects
]

for num_m, num_o, seed in hard_mirror_data:
    mirrors, objects, viewer = generate_mirror_problem(num_m, num_o, seed)
    problems.append({
        "name":
        f"{num_m} mirrors, {num_o} objects - HARD",
        "description":
        format_mirror_description(mirrors, objects, viewer),
        "mirrors":
        mirrors,
        "objects":
        objects,
        "viewer":
        viewer
    })

# Add specific challenging scenarios
problems.append({
    "name":
    "Hall of mirrors (parallel mirrors) - HARD",
    "description":
    """
Room: 10m x 20m x 3m

Mirror A: Full wall at X=0 (Y: 0-20, Z: 0-3), normal pointing +X
Mirror B: Full wall at X=10 (Y: 0-20, Z: 0-3), normal pointing -X

These parallel mirrors create infinite reflections!

Objects:
- Red Sphere at (3, 10, 1.5)
- Blue Cube at (7, 10, 1)
- Green Pyramid at (5, 5, 0.5)
- Yellow Cylinder at (5, 15, 2)
- Purple Cone at (2, 8, 1)
- Orange Torus at (8, 12, 1.5)

Your position: (5, 10, 1.6)

Note: For this problem, only consider FIRST-ORDER reflections (direct reflections, not reflections of reflections).
""",
    "mirrors": [
        {
            "name": "Mirror A",
            "point": [0, 0, 0],
            "normal": [1, 0, 0],
            "bounds": {
                "y": [0, 20],
                "z": [0, 3]
            }
        },
        {
            "name": "Mirror B",
            "point": [10, 0, 0],
            "normal": [-1, 0, 0],
            "bounds": {
                "y": [0, 20],
                "z": [0, 3]
            }
        },
    ],
    "objects": [
        {
            "name": "Red Sphere",
            "pos": [3, 10, 1.5]
        },
        {
            "name": "Blue Cube",
            "pos": [7, 10, 1]
        },
        {
            "name": "Green Pyramid",
            "pos": [5, 5, 0.5]
        },
        {
            "name": "Yellow Cylinder",
            "pos": [5, 15, 2]
        },
        {
            "name": "Purple Cone",
            "pos": [2, 8, 1]
        },
        {
            "name": "Orange Torus",
            "pos": [8, 12, 1.5]
        },
    ],
    "viewer": [5, 10, 1.6]
})

problems.append({
    "name":
    "Corner cube (3 perpendicular mirrors) - HARD",
    "description":
    """
A corner cube reflector formed by three perpendicular mirrors meeting at origin:

Mirror X: YZ plane at X=0 (Y: 0-10, Z: 0-5), normal +X
Mirror Y: XZ plane at Y=0 (X: 0-10, Z: 0-5), normal +Y  
Mirror Z: XY plane at Z=0 (X: 0-10, Y: 0-10), normal +Z (floor)

Objects placed in the positive octant:
- Sphere A at (2, 3, 2)
- Cube B at (5, 2, 1)
- Pyramid C at (3, 6, 3)
- Cylinder D at (7, 7, 1.5)
- Cone E at (4, 4, 4)
- Lamp F at (8, 3, 2.5)
- Vase G at (2, 8, 1)
- Chair H at (6, 5, 0.5)

Your position: (5, 5, 1.6)

For each mirror, determine which objects you can see reflected.
""",
    "mirrors": [
        {
            "name": "Mirror X",
            "point": [0, 0, 0],
            "normal": [1, 0, 0],
            "bounds": {
                "y": [0, 10],
                "z": [0, 5]
            }
        },
        {
            "name": "Mirror Y",
            "point": [0, 0, 0],
            "normal": [0, 1, 0],
            "bounds": {
                "x": [0, 10],
                "z": [0, 5]
            }
        },
        {
            "name": "Mirror Z",
            "point": [0, 0, 0],
            "normal": [0, 0, 1],
            "bounds": {
                "x": [0, 10],
                "y": [0, 10]
            }
        },
    ],
    "objects": [
        {
            "name": "Sphere A",
            "pos": [2, 3, 2]
        },
        {
            "name": "Cube B",
            "pos": [5, 2, 1]
        },
        {
            "name": "Pyramid C",
            "pos": [3, 6, 3]
        },
        {
            "name": "Cylinder D",
            "pos": [7, 7, 1.5]
        },
        {
            "name": "Cone E",
            "pos": [4, 4, 4]
        },
        {
            "name": "Lamp F",
            "pos": [8, 3, 2.5]
        },
        {
            "name": "Vase G",
            "pos": [2, 8, 1]
        },
        {
            "name": "Chair H",
            "pos": [6, 5, 0.5]
        },
    ],
    "viewer": [5, 5, 1.6]
})

# Pre-compute expected answers
for prob in problems:
    expected_views = []
    for mirror in prob["mirrors"]:
        view = {
            "mirrorName": mirror["name"],
            "visibleObjects": [],
            "canSeeYourself": False
        }

        # Check each object
        for obj in prob["objects"]:
            visible, reflected = can_see_in_mirror(prob["viewer"], obj["pos"],
                                                   mirror)
            if visible:
                view["visibleObjects"].append({
                    "objectName":
                    obj["name"],
                    "apparentPosition": [round(r, 2) for r in reflected]
                })

        # Check if can see self
        can_see_self, self_reflected = can_see_in_mirror(
            prob["viewer"], prob["viewer"], mirror)
        view["canSeeYourself"] = can_see_self

        expected_views.append(view)

    prob["expected"] = expected_views

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Various mirror configurations"


def prepareSubpassPrompt(index: int) -> str:
    if index >= len(problems):
        raise StopIteration
    return prompt.replace("ROOM_DESCRIPTION", problems[index]["description"])


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    prob = problems[subPass]
    expected = prob["expected"]

    views = answer.get("mirrorViews", [])
    if not views:
        return 0, "No mirror views provided"

    total_score = 0
    max_points = 0
    details = []

    for exp_view in expected:
        mirror_name = exp_view["mirrorName"]

        # Find matching answer
        ans_view = None
        for v in views:
            if v.get("mirrorName", "").lower() == mirror_name.lower():
                ans_view = v
                break

        if ans_view is None:
            details.append(f"Missing view for {mirror_name}")
            max_points += len(exp_view["visibleObjects"]) + 1
            continue

        # Check visible objects
        exp_objects = {
            o["objectName"]: o["apparentPosition"]
            for o in exp_view["visibleObjects"]
        }
        ans_objects = {
            o.get("objectName", ""): o.get("apparentPosition", [])
            for o in ans_view.get("visibleObjects", [])
        }

        for obj_name, exp_pos in exp_objects.items():
            max_points += 1
            if obj_name in ans_objects:
                ans_pos = ans_objects[obj_name]
                if isinstance(ans_pos, list) and len(ans_pos) >= 3:
                    dist = math.sqrt(
                        sum((ans_pos[i] - exp_pos[i])**2 for i in range(3)))
                    if dist <= 1.0:  # Allow 1m tolerance
                        total_score += 1
                        details.append(
                            f"{mirror_name}: {obj_name} position OK")
                    else:
                        partial = max(0, 1 - dist / 5)
                        total_score += partial
                        details.append(
                            f"{mirror_name}: {obj_name} position off by {dist:.1f}m"
                        )
                else:
                    details.append(
                        f"{mirror_name}: {obj_name} invalid position format")
            else:
                details.append(f"{mirror_name}: Missing {obj_name}")

        # Check wrong objects (should not be visible)
        for obj_name in ans_objects:
            if obj_name not in exp_objects and obj_name:
                details.append(
                    f"{mirror_name}: {obj_name} incorrectly listed as visible")
                total_score -= 0.5

        # Check can see yourself
        max_points += 1
        if ans_view.get("canSeeYourself") == exp_view["canSeeYourself"]:
            total_score += 1
            details.append(f"{mirror_name}: canSeeYourself correct")
        else:
            details.append(f"{mirror_name}: canSeeYourself wrong")

    score = max(0, total_score / max_points) if max_points > 0 else 0
    return min(1, score), "<br>".join(details)


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    prob = problems[subPass]

    html = "<b>Problem:</b><br>"
    html += prob["description"].replace("\n", "<br>")

    html += "<br><br><b>Your answer:</b><br>"
    for view in answer.get("mirrorViews", []):
        html += f"<b>{view.get('mirrorName', '?')}</b>:<br>"
        html += f"  Can see yourself: {view.get('canSeeYourself', '?')}<br>"
        for obj in view.get("visibleObjects", []):
            html += f"  - {obj.get('objectName', '?')} at {obj.get('apparentPosition', '?')}<br>"

    html += "<br><b>Expected:</b><br>"
    for view in prob["expected"]:
        html += f"<b>{view['mirrorName']}</b>:<br>"
        html += f"  Can see yourself: {view['canSeeYourself']}<br>"
        for obj in view["visibleObjects"]:
            html += f"  - {obj['objectName']} at {obj['apparentPosition']}<br>"

    return html


highLevelSummary = """
Tests understanding of mirror reflections in 3D space.
<br><br>
Key concepts:
<ul>
<li>Reflection creates a virtual image at equal distance behind the mirror</li>
<li>Line of sight must intersect the mirror surface</li>
<li>Mirror bounds limit what can be seen</li>
<li>Multiple mirrors create multiple viewpoints</li>
</ul>
This spatial reasoning skill is essential for understanding optics, 
room layout, and many puzzle types.
"""
