import math
import random

title = "Balance and Center of Mass - Will it tip over?"

prompt = """
You are analyzing the stability of stacked objects. Each object has a mass and occupies a 
rectangular region in 3D space.

OBJECTS_DESCRIPTION

The bottom object rests on a flat surface (the ground). Objects are stacked on top of each other.
Gravity pulls downward (-Z direction).

Determine:
1. Is the entire stack stable?
2. If not, which object tips first (from bottom to top)?
3. What is the location of the combined center of mass of the entire stack?

Assume uniform density for all objects (center of mass = geometric center).
"""

structure = {
    "type":
    "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "isStable": {
            "type": "boolean"
        },
        "tippingObject": {
            "type":
            "integer",
            "description":
            "Object number that tips first (1-indexed), or 0 if stable"
        },
        "combinedCenterOfMass": {
            "type": "array",
            "items": {
                "type": "number"
            },
            "description": "[x, y, z] of the combined center of mass"
        }
    },
    "propertyOrdering":
    ["reasoning", "isStable", "tippingObject", "combinedCenterOfMass"],
    "required":
    ["reasoning", "isStable", "combinedCenterOfMass", "tippingObject"],
    "additionalProperties":
    False
}


def compute_com(objects):
    """Compute combined center of mass."""
    total_mass = 0
    weighted_pos = [0, 0, 0]

    for obj in objects:
        m = obj["mass"]
        cx = (obj["x_min"] + obj["x_max"]) / 2
        cy = (obj["y_min"] + obj["y_max"]) / 2
        cz = (obj["z_min"] + obj["z_max"]) / 2

        weighted_pos[0] += m * cx
        weighted_pos[1] += m * cy
        weighted_pos[2] += m * cz
        total_mass += m

    if total_mass == 0:
        return [0, 0, 0]

    return [
        weighted_pos[0] / total_mass, weighted_pos[1] / total_mass,
        weighted_pos[2] / total_mass
    ]


def check_stability(objects):
    """Check if stack is stable, return (is_stable, tipping_object_index)."""
    # Check from bottom to top
    for i in range(len(objects)):
        # Get support region (the object below, or ground for first object)
        if i == 0:
            # Ground supports the entire bottom of the object
            support_x_min = objects[i]["x_min"]
            support_x_max = objects[i]["x_max"]
            support_y_min = objects[i]["y_min"]
            support_y_max = objects[i]["y_max"]
        else:
            # Support region is the TOP of the object below
            support_x_min = objects[i - 1]["x_min"]
            support_x_max = objects[i - 1]["x_max"]
            support_y_min = objects[i - 1]["y_min"]
            support_y_max = objects[i - 1]["y_max"]

        # Calculate combined CoM of this object and everything above
        objects_above = objects[i:]
        com = compute_com(objects_above)

        # Check if CoM falls within support region
        if not (support_x_min <= com[0] <= support_x_max
                and support_y_min <= com[1] <= support_y_max):
            return False, i + 1  # 1-indexed

    return True, None


# Define problems
problems = [
    {
        "name":
        "Simple centered stack",
        "objects": [
            {
                "mass": 10,
                "x_min": 0,
                "x_max": 4,
                "y_min": 0,
                "y_max": 4,
                "z_min": 0,
                "z_max": 2
            },
            {
                "mass": 5,
                "x_min": 1,
                "x_max": 3,
                "y_min": 1,
                "y_max": 3,
                "z_min": 2,
                "z_max": 4
            },
        ],
        "description":
        """
Object 1: Mass 10 kg, occupies region X:[0,4], Y:[0,4], Z:[0,2] (a 4x4x2 block on ground)
Object 2: Mass 5 kg, occupies region X:[1,3], Y:[1,3], Z:[2,4] (a 2x2x2 block centered on top)
"""
    },
    {
        "name":
        "Offset but stable",
        "objects": [
            {
                "mass": 20,
                "x_min": 0,
                "x_max": 6,
                "y_min": 0,
                "y_max": 4,
                "z_min": 0,
                "z_max": 1
            },
            {
                "mass": 5,
                "x_min": 4,
                "x_max": 6,
                "y_min": 1,
                "y_max": 3,
                "z_min": 1,
                "z_max": 3
            },
        ],
        "description":
        """
Object 1: Mass 20 kg, occupies region X:[0,6], Y:[0,4], Z:[0,1] (a 6x4x1 base plate)
Object 2: Mass 5 kg, occupies region X:[4,6], Y:[1,3], Z:[1,3] (a 2x2x2 block offset to one side)
"""
    },
    {
        "name":
        "Overhang - will tip",
        "objects": [
            {
                "mass": 5,
                "x_min": 0,
                "x_max": 2,
                "y_min": 0,
                "y_max": 2,
                "z_min": 0,
                "z_max": 2
            },
            {
                "mass": 10,
                "x_min": 1,
                "x_max": 5,
                "y_min": 0,
                "y_max": 2,
                "z_min": 2,
                "z_max": 3
            },
        ],
        "description":
        """
Object 1: Mass 5 kg, occupies region X:[0,2], Y:[0,2], Z:[0,2] (small base block)
Object 2: Mass 10 kg, occupies region X:[1,5], Y:[0,2], Z:[2,3] (heavier block overhanging significantly)
"""
    },
    {
        "name":
        "Three object tower",
        "objects": [
            {
                "mass": 10,
                "x_min": 0,
                "x_max": 4,
                "y_min": 0,
                "y_max": 4,
                "z_min": 0,
                "z_max": 1
            },
            {
                "mass": 8,
                "x_min": 0.5,
                "x_max": 3.5,
                "y_min": 0.5,
                "y_max": 3.5,
                "z_min": 1,
                "z_max": 2
            },
            {
                "mass": 3,
                "x_min": 1,
                "x_max": 3,
                "y_min": 1,
                "y_max": 3,
                "z_min": 2,
                "z_max": 4
            },
        ],
        "description":
        """
Object 1: Mass 10 kg, occupies region X:[0,4], Y:[0,4], Z:[0,1] (4x4x1 base)
Object 2: Mass 8 kg, occupies region X:[0.5,3.5], Y:[0.5,3.5], Z:[1,2] (3x3x1 middle)
Object 3: Mass 3 kg, occupies region X:[1,3], Y:[1,3], Z:[2,4] (2x2x2 top)
"""
    },
    {
        "name":
        "Asymmetric unstable tower",
        "objects": [
            {
                "mass": 10,
                "x_min": 0,
                "x_max": 3,
                "y_min": 0,
                "y_max": 3,
                "z_min": 0,
                "z_max": 1
            },
            {
                "mass": 5,
                "x_min": 1.5,
                "x_max": 3,
                "y_min": 0,
                "y_max": 3,
                "z_min": 1,
                "z_max": 2
            },
            {
                "mass": 20,
                "x_min": 2,
                "x_max": 4,
                "y_min": 0.5,
                "y_max": 2.5,
                "z_min": 2,
                "z_max": 4
            },
        ],
        "description":
        """
Object 1: Mass 10 kg, occupies region X:[0,3], Y:[0,3], Z:[0,1] (3x3x1 base)
Object 2: Mass 5 kg, occupies region X:[1.5,3], Y:[0,3], Z:[1,2] (offset to right side)
Object 3: Mass 20 kg, occupies region X:[2,4], Y:[0.5,2.5], Z:[2,4] (heavy block extending past base)
"""
    },
]

# === SUPER-HARD CHALLENGES ===
# Complex multi-object stacks with varying densities and precarious balance


def generate_tower_problem(num_objects, seed):
    """Generate a random tower stacking problem."""
    random.seed(seed)

    objects = []
    current_z = 0

    # Start with a base
    base_size = random.uniform(3, 6)
    objects.append({
        "mass": random.uniform(5, 20),
        "x_min": 0,
        "x_max": base_size,
        "y_min": 0,
        "y_max": base_size,
        "z_min": 0,
        "z_max": random.uniform(0.5, 2)
    })
    current_z = objects[0]["z_max"]

    for i in range(1, num_objects):
        prev = objects[i - 1]
        prev_cx = (prev["x_min"] + prev["x_max"]) / 2
        prev_cy = (prev["y_min"] + prev["y_max"]) / 2

        # Random size (generally getting smaller)
        size_x = random.uniform(1, (prev["x_max"] - prev["x_min"]) * 0.9)
        size_y = random.uniform(1, (prev["y_max"] - prev["y_min"]) * 0.9)
        height = random.uniform(0.5, 2)

        # Random offset from center (this creates instability potential)
        offset_x = random.uniform(-1.5, 1.5)
        offset_y = random.uniform(-1.5, 1.5)

        cx = prev_cx + offset_x
        cy = prev_cy + offset_y

        objects.append({
            "mass": random.uniform(2, 15),
            "x_min": cx - size_x / 2,
            "x_max": cx + size_x / 2,
            "y_min": cy - size_y / 2,
            "y_max": cy + size_y / 2,
            "z_min": current_z,
            "z_max": current_z + height
        })
        current_z += height

    return objects


def format_objects_description(objects):
    """Format objects list as description string."""
    desc = ""
    for i, obj in enumerate(objects):
        desc += f"\nObject {i+1}: Mass {obj['mass']:.1f} kg, occupies region "
        desc += f"X:[{obj['x_min']:.2f},{obj['x_max']:.2f}], "
        desc += f"Y:[{obj['y_min']:.2f},{obj['y_max']:.2f}], "
        desc += f"Z:[{obj['z_min']:.2f},{obj['z_max']:.2f}]"
    return desc


# Generate hard problems with 8, 10, and 12 objects
hard_problems_data = [
    (8, 77701),
    (10, 77702),
    (12, 77703),
]

for num_obj, seed in hard_problems_data:
    objs = generate_tower_problem(num_obj, seed)
    problems.append({
        "name": f"{num_obj}-object tower - HARD",
        "objects": objs,
        "description": format_objects_description(objs)
    })

# Add a specific challenging cantilever problem
problems.append({
    "name":
    "Complex cantilever with counterweight - HARD",
    "objects": [
        {
            "mass": 50,
            "x_min": 0,
            "x_max": 8,
            "y_min": 0,
            "y_max": 4,
            "z_min": 0,
            "z_max": 1
        },
        {
            "mass": 30,
            "x_min": 6,
            "x_max": 8,
            "y_min": 0.5,
            "y_max": 3.5,
            "z_min": 1,
            "z_max": 3
        },
        {
            "mass": 5,
            "x_min": 7,
            "x_max": 11,
            "y_min": 1,
            "y_max": 3,
            "z_min": 3,
            "z_max": 4
        },
        {
            "mass": 25,
            "x_min": 9,
            "x_max": 12,
            "y_min": 0.5,
            "y_max": 3.5,
            "z_min": 4,
            "z_max": 6
        },
        {
            "mass": 100,
            "x_min": -2,
            "x_max": 1,
            "y_min": 0,
            "y_max": 4,
            "z_min": 1,
            "z_max": 2
        },
        {
            "mass": 15,
            "x_min": 10,
            "x_max": 14,
            "y_min": 1,
            "y_max": 3,
            "z_min": 6,
            "z_max": 8
        },
        {
            "mass": 8,
            "x_min": 11,
            "x_max": 15,
            "y_min": 1.2,
            "y_max": 2.8,
            "z_min": 8,
            "z_max": 9
        },
        {
            "mass": 3,
            "x_min": 13,
            "x_max": 16,
            "y_min": 1.5,
            "y_max": 2.5,
            "z_min": 9,
            "z_max": 10
        },
    ],
    "description":
    """
Object 1: Mass 50 kg, X:[0,8], Y:[0,4], Z:[0,1] (large base plate)
Object 2: Mass 30 kg, X:[6,8], Y:[0.5,3.5], Z:[1,3] (support pillar on right)
Object 3: Mass 5 kg, X:[7,11], Y:[1,3], Z:[3,4] (horizontal beam extending right)
Object 4: Mass 25 kg, X:[9,12], Y:[0.5,3.5], Z:[4,6] (heavy block on beam)
Object 5: Mass 100 kg, X:[-2,1], Y:[0,4], Z:[1,2] (counterweight on left, resting on base)
Object 6: Mass 15 kg, X:[10,14], Y:[1,3], Z:[6,8] (extending further right)
Object 7: Mass 8 kg, X:[11,15], Y:[1.2,2.8], Z:[8,9] (more extension)
Object 8: Mass 3 kg, X:[13,16], Y:[1.5,2.5], Z:[9,10] (tip of cantilever)

This is a cantilever structure with a heavy counterweight. Is it balanced?
"""
})

# Add a precarious balance problem
problems.append({
    "name":
    "Precarious multi-branch balance - HARD",
    "objects": [
        {
            "mass": 100,
            "x_min": 0,
            "x_max": 10,
            "y_min": 0,
            "y_max": 10,
            "z_min": 0,
            "z_max": 0.5
        },
        {
            "mass": 20,
            "x_min": 0,
            "x_max": 2,
            "y_min": 4,
            "y_max": 6,
            "z_min": 0.5,
            "z_max": 4
        },
        {
            "mass": 20,
            "x_min": 8,
            "x_max": 10,
            "y_min": 4,
            "y_max": 6,
            "z_min": 0.5,
            "z_max": 4
        },
        {
            "mass": 15,
            "x_min": 4,
            "x_max": 6,
            "y_min": 0,
            "y_max": 2,
            "z_min": 0.5,
            "z_max": 3
        },
        {
            "mass": 15,
            "x_min": 4,
            "x_max": 6,
            "y_min": 8,
            "y_max": 10,
            "z_min": 0.5,
            "z_max": 3
        },
        {
            "mass": 50,
            "x_min": -1,
            "x_max": 3,
            "y_min": 3.5,
            "y_max": 6.5,
            "z_min": 4,
            "z_max": 5
        },
        {
            "mass": 45,
            "x_min": 7,
            "x_max": 11,
            "y_min": 3.5,
            "y_max": 6.5,
            "z_min": 4,
            "z_max": 5
        },
        {
            "mass": 30,
            "x_min": 3,
            "x_max": 7,
            "y_min": -1,
            "y_max": 3,
            "z_min": 3,
            "z_max": 4
        },
        {
            "mass": 35,
            "x_min": 3,
            "x_max": 7,
            "y_min": 7,
            "y_max": 11,
            "z_min": 3,
            "z_max": 4
        },
        {
            "mass": 10,
            "x_min": -2,
            "x_max": 0,
            "y_min": 4,
            "y_max": 6,
            "z_min": 5,
            "z_max": 7
        },
        {
            "mass": 12,
            "x_min": 10,
            "x_max": 12,
            "y_min": 4,
            "y_max": 6,
            "z_min": 5,
            "z_max": 7
        },
    ],
    "description":
    """
Object 1: Mass 100 kg, X:[0,10], Y:[0,10], Z:[0,0.5] (large 10x10 base plate)
Object 2: Mass 20 kg, X:[0,2], Y:[4,6], Z:[0.5,4] (left pillar)
Object 3: Mass 20 kg, X:[8,10], Y:[4,6], Z:[0.5,4] (right pillar)
Object 4: Mass 15 kg, X:[4,6], Y:[0,2], Z:[0.5,3] (front pillar)
Object 5: Mass 15 kg, X:[4,6], Y:[8,10], Z:[0.5,3] (back pillar)
Object 6: Mass 50 kg, X:[-1,3], Y:[3.5,6.5], Z:[4,5] (heavy block on left pillar, overhanging left)
Object 7: Mass 45 kg, X:[7,11], Y:[3.5,6.5], Z:[4,5] (heavy block on right pillar, overhanging right)
Object 8: Mass 30 kg, X:[3,7], Y:[-1,3], Z:[3,4] (heavy block on front pillar, overhanging front)
Object 9: Mass 35 kg, X:[3,7], Y:[7,11], Z:[3,4] (heavy block on back pillar, overhanging back)
Object 10: Mass 10 kg, X:[-2,0], Y:[4,6], Z:[5,7] (extension on left side)
Object 11: Mass 12 kg, X:[10,12], Y:[4,6], Z:[5,7] (extension on right side)

Multiple overhanging loads in different directions. Is the combined system stable?
"""
})

# Pre-compute expected answers
for prob in problems:
    is_stable, tipping = check_stability(prob["objects"])
    prob["is_stable"] = is_stable
    prob["tipping_object"] = tipping
    prob["com"] = compute_com(prob["objects"])

subpassParamSummary = [p["name"] for p in problems]
promptChangeSummary = "Various stacking configurations testing stability"


def prepareSubpassPrompt(index: int) -> str:

    if index >= len(problems):
        raise StopIteration
    return prompt.replace("OBJECTS_DESCRIPTION",
                          problems[index]["description"])


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    prob = problems[subPass]

    score = 0
    details = []

    # Check stability prediction (worth 0.4)
    is_stable = answer.get("isStable", None)
    if is_stable == prob["is_stable"]:
        score += 0.4
        details.append(f"Stability correct: {is_stable}")
    else:
        details.append(
            f"Stability wrong: got {is_stable}, expected {prob['is_stable']}")

    # Check tipping object (worth 0.3) - only if unstable
    if not prob["is_stable"]:
        tipping = answer.get("tippingObject", None)
        if tipping == prob["tipping_object"]:
            score += 0.3
            details.append(f"Tipping object correct: {tipping}")
        else:
            details.append(
                f"Tipping object wrong: got {tipping}, expected {prob['tipping_object']}"
            )
    else:
        # If stable, no tipping object needed
        score += 0.3

    # Check center of mass (worth 0.3)
    com = answer.get("combinedCenterOfMass", [0, 0, 0])
    expected_com = prob["com"]

    if isinstance(com, list) and len(com) >= 3:
        dist = math.sqrt(sum((a - b)**2 for a, b in zip(com, expected_com)))
        tolerance = 0.5  # Allow 0.5 unit error

        if dist <= tolerance:
            score += 0.3
            details.append(f"CoM correct: {com}")
        else:
            # Partial credit
            partial = max(0, 0.3 * (1 - dist / 3))
            score += partial
            details.append(
                f"CoM off by {dist:.2f}: got {com}, expected {expected_com}")
    else:
        details.append(f"Invalid CoM format: {com}")

    return score, "<br>".join(details)


def generate_stack_scad(prob):
    """Generate OpenSCAD code for stack visualization."""
    objects = prob["objects"]

    # Generate distinct colors for each object
    colors = [
        [0.8, 0.3, 0.3],  # red
        [0.3, 0.8, 0.3],  # green
        [0.3, 0.3, 0.8],  # blue
        [0.8, 0.8, 0.3],  # yellow
        [0.8, 0.3, 0.8],  # magenta
        [0.3, 0.8, 0.8],  # cyan
        [0.9, 0.6, 0.3],  # orange
        [0.6, 0.3, 0.9],  # purple
        [0.3, 0.9, 0.6],  # teal
        [0.9, 0.5, 0.5],  # pink
        [0.5, 0.7, 0.5],  # light green
        [0.5, 0.5, 0.7],  # light blue
    ]

    scad = "// Stack visualization\n"
    scad += "$fn = 32;\n"

    # Draw ground plane
    all_x = [obj["x_min"]
             for obj in objects] + [obj["x_max"] for obj in objects]
    all_y = [obj["y_min"]
             for obj in objects] + [obj["y_max"] for obj in objects]
    ground_margin = 2
    ground_x_min = min(all_x) - ground_margin
    ground_x_max = max(all_x) + ground_margin
    ground_y_min = min(all_y) - ground_margin
    ground_y_max = max(all_y) + ground_margin

    scad += f"// Ground plane\n"
    scad += f"color([0.6, 0.6, 0.6]) translate([{ground_x_min}, {ground_y_min}, -0.1]) "
    scad += f"cube([{ground_x_max - ground_x_min}, {ground_y_max - ground_y_min}, 0.1]);\n"

    # Draw each object as a box
    for i, obj in enumerate(objects):
        color = colors[i % len(colors)]
        x_size = obj["x_max"] - obj["x_min"]
        y_size = obj["y_max"] - obj["y_min"]
        z_size = obj["z_max"] - obj["z_min"]

        scad += f"// Object {i+1} (mass={obj['mass']}kg)\n"
        scad += f"color([{color[0]}, {color[1]}, {color[2]}, 0.8]) "
        scad += f"translate([{obj['x_min']}, {obj['y_min']}, {obj['z_min']}]) "
        scad += f"cube([{x_size}, {y_size}, {z_size}]);\n"

        # Add label at center of object
        cx = (obj["x_min"] + obj["x_max"]) / 2
        cy = (obj["y_min"] + obj["y_max"]) / 2
        cz = (obj["z_min"] + obj["z_max"]) / 2
        scad += f"color([1, 1, 1]) translate([{cx}, {cy}, {cz}]) "
        scad += f"linear_extrude(0.01) text(\"{i+1}\", size={min(x_size, y_size, z_size)*0.5}, halign=\"center\", valign=\"center\");\n"

    # Draw center of mass as a small sphere
    com = prob["com"]
    scad += f"// Combined Center of Mass\n"
    scad += f"color([1, 0, 0]) translate([{com[0]}, {com[1]}, {com[2]}]) sphere(r=0.2);\n"

    # Draw vertical line from CoM down to ground
    scad += f"color([1, 0, 0, 0.5]) translate([{com[0]}, {com[1]}, 0]) cylinder(r=0.05, h={com[2]});\n"

    return scad


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    import VolumeComparison as vc
    import os

    prob = problems[subPass]

    # Generate visualization
    vis_html = ""
    try:
        scad = generate_stack_scad(prob)
        output_path = f"results/38_{subPass}_{aiEngineName}_stack.png"

        # Calculate camera position for side view
        objects = prob["objects"]
        all_x = [obj["x_min"]
                 for obj in objects] + [obj["x_max"] for obj in objects]
        all_y = [obj["y_min"]
                 for obj in objects] + [obj["y_max"] for obj in objects]
        all_z = [obj["z_min"]
                 for obj in objects] + [obj["z_max"] for obj in objects]

        center_x = (min(all_x) + max(all_x)) / 2
        center_y = (min(all_y) + max(all_y)) / 2
        center_z = (min(all_z) + max(all_z)) / 2

        extent = max(
            max(all_x) - min(all_x),
            max(all_y) - min(all_y),
            max(all_z) - min(all_z))
        cam_dist = extent * 2

        # Side view - looking from +Y direction with slight angle
        camera_arg = f"--camera={center_x},{center_y - cam_dist},{center_z + cam_dist/2},{center_x},{center_y},{center_z}"
        vc.render_scadText_to_png(scad, output_path, cameraArg=camera_arg)
        vis_html = f'<img src="{os.path.basename(output_path)}" />'
    except Exception as e:
        vis_html = f"<i>Visualization error: {e}</i>"

    # Text content in left column
    html = "<td><b>Your answer:</b><br>"
    html += f"Is Stable: {answer.get('isStable', 'not provided')}<br>"
    html += f"Tipping Object: {answer.get('tippingObject', 'not provided')}<br>"
    html += f"Center of Mass: {answer.get('combinedCenterOfMass', 'not provided')}<br>"

    html += "<br><b>Expected:</b><br>"
    html += f"Is Stable: {prob['is_stable']}<br>"
    html += f"Tipping Object: {prob['tipping_object']}<br>"
    html += f"Center of Mass: {[round(c, 2) for c in prob['com']]}<br>"

    html += f"</td><td>{vis_html}</td>"

    return html


highLevelSummary = """
Tests understanding of physical stability and center of mass.
<br><br>
Key physics concepts:
<ul>
<li>Center of mass is at the geometric center for uniform density objects</li>
<li>Combined CoM is the weighted average of individual CoMs</li>
<li>A stack tips when combined CoM falls outside the support footprint</li>
<li>Heavier objects on top have larger effect on combined CoM</li>
</ul>
This is crucial for robotics, construction, and any physical manipulation task.
"""
