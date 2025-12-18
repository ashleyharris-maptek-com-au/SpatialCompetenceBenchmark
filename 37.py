import math
import random
import itertools

skip = True

title = "Mental Rotation - Identify which 3D shapes are rotations of each other"

prompt = """
You are shown multiple 3D objects made of connected unit cubes (like 3D Tetris pieces).
Each object is described by listing the (x, y, z) coordinates of its unit cubes.

Your task is to identify which objects are the SAME shape, just rotated differently in 3D space.
Two shapes are considered the same if one can be rotated (but NOT reflected/mirrored) to match the other.

Objects to analyze:

OBJECTS_DESCRIPTION

Group the objects by their underlying shape. Return groups where each group contains 
object numbers that are rotations of each other.
"""

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "groups": {
            "type": "array",
            "items": {
                "type":
                "array",
                "items": {
                    "type": "integer"
                },
                "description":
                "List of object numbers that are rotations of each other"
            }
        }
    },
    "propertyOrdering": ["reasoning", "groups"],
    "required": ["reasoning", "groups"],
    "additionalProperties": False
}


def rotate_shape_90(cubes, axis):
    """Rotate a shape 90 degrees around the given axis."""
    result = []
    for x, y, z in cubes:
        if axis == 'x':
            result.append((x, -z, y))
        elif axis == 'y':
            result.append((z, y, -x))
        elif axis == 'z':
            result.append((-y, x, z))
    return result


def normalize_shape(cubes):
    """Translate shape so minimum coordinates are at origin."""
    if not cubes:
        return tuple()
    min_x = min(c[0] for c in cubes)
    min_y = min(c[1] for c in cubes)
    min_z = min(c[2] for c in cubes)
    normalized = tuple(
        sorted((x - min_x, y - min_y, z - min_z) for x, y, z in cubes))
    return normalized


def get_all_rotations(cubes):
    """Get all 24 possible rotations of a shape."""
    rotations = set()
    current = list(cubes)

    # 24 rotations: 6 faces can face up, 4 rotations each
    for _ in range(4):  # Rotations around Z
        for _ in range(4):  # Rotations around X
            rotations.add(normalize_shape(current))
            current = rotate_shape_90(current, 'x')
        current = rotate_shape_90(current, 'z')

    # Also try rotations starting from Y-up
    current = rotate_shape_90(list(cubes), 'x')
    for _ in range(4):
        rotations.add(normalize_shape(current))
        current = rotate_shape_90(current, 'y')

    current = rotate_shape_90(
        rotate_shape_90(rotate_shape_90(list(cubes), 'x'), 'x'), 'x')
    for _ in range(4):
        rotations.add(normalize_shape(current))
        current = rotate_shape_90(current, 'y')

    return rotations


def shapes_are_same_rotation(shape1, shape2):
    """Check if two shapes are rotations of each other."""
    rotations1 = get_all_rotations(shape1)
    norm2 = normalize_shape(shape2)
    return norm2 in rotations1


# Define base shapes and their rotations
base_shapes = [
    # L-tetromino in 3D
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0)],
    # T-tetromino
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0)],
    # S-tetromino (chiral - has mirror that's different)
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0)],
    # 3D L-shape
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)],
    # Straight line
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)],
    # 2x2 square
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)],
    # 3D corner
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
]


def generate_problem(num_objects, num_shapes, seed):
    """Generate a problem with objects that may be rotations of each other."""
    random.seed(seed)

    # Pick which base shapes to use
    shapes_to_use = random.sample(range(len(base_shapes)),
                                  min(num_shapes, len(base_shapes)))

    objects = []
    true_groups = {i: [] for i in range(len(shapes_to_use))}

    for obj_id in range(num_objects):
        # Pick a random shape
        shape_idx = random.randint(0, len(shapes_to_use) - 1)
        base = base_shapes[shapes_to_use[shape_idx]]

        # Apply random rotation
        current = list(base)
        for _ in range(random.randint(0, 10)):
            axis = random.choice(['x', 'y', 'z'])
            current = rotate_shape_90(current, axis)

        # Apply random translation
        offset = (random.randint(0,
                                 5), random.randint(0,
                                                    5), random.randint(0, 5))
        current = [(x + offset[0], y + offset[1], z + offset[2])
                   for x, y, z in current]

        objects.append(current)
        true_groups[shape_idx].append(obj_id + 1)  # 1-indexed

    # Convert to list of groups (only non-empty, sorted)
    groups = [sorted(g) for g in true_groups.values() if len(g) > 0]
    groups.sort(key=lambda x: x[0] if x else 0)

    return objects, groups


problems = [
    {
        "num_objects": 4,
        "num_shapes": 2,
        "seed": 42
    },
    {
        "num_objects": 6,
        "num_shapes": 3,
        "seed": 123
    },
    {
        "num_objects": 8,
        "num_shapes": 3,
        "seed": 456
    },
    {
        "num_objects": 10,
        "num_shapes": 4,
        "seed": 789
    },
    {
        "num_objects": 12,
        "num_shapes": 5,
        "seed": 101112
    },
]

# === SUPER-HARD CHALLENGES ===
# More complex shapes with more cubes, and chiral pairs

# Extended base shapes for hard problems - larger and more complex
hard_base_shapes = [
    # 5-cube L in 3D
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 1, 1)],
    # 5-cube T in 3D
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, 0, 1)],
    # 5-cube S (chiral)
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 1, 1)],
    # 5-cube S mirror (chiral pair)
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],
    # 6-cube complex
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 1, 1), (2, 2, 1)],
    # 6-cube zigzag
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0), (2, 1, 1), (2, 2, 1)],
    # 7-cube helix-like
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 2, 1),
     (0, 2, 2)],
    # 7-cube branched
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, -1, 0), (1, 0, 1),
     (1, 0, -1)],
    # 8-cube cube corner missing
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1),
     (0, 1, 1)],
    # 8-cube staircase
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0), (2, 1, 1), (2, 2, 1),
     (3, 2, 1), (3, 2, 2)],
]


def generate_hard_problem(num_objects, num_shapes, seed, use_hard_shapes=True):
    """Generate a harder problem with larger shapes."""
    random.seed(seed)

    shapes = hard_base_shapes if use_hard_shapes else base_shapes
    shapes_to_use = random.sample(range(len(shapes)),
                                  min(num_shapes, len(shapes)))

    objects = []
    true_groups = {i: [] for i in range(len(shapes_to_use))}

    for obj_id in range(num_objects):
        shape_idx = random.randint(0, len(shapes_to_use) - 1)
        base = shapes[shapes_to_use[shape_idx]]

        # Apply random rotations
        current = list(base)
        for _ in range(random.randint(0, 15)):
            axis = random.choice(['x', 'y', 'z'])
            current = rotate_shape_90(current, axis)

        # Apply random translation with larger range
        offset = (random.randint(-3,
                                 8), random.randint(-3,
                                                    8), random.randint(-3, 8))
        current = [(x + offset[0], y + offset[1], z + offset[2])
                   for x, y, z in current]

        objects.append(current)
        true_groups[shape_idx].append(obj_id + 1)

    groups = [sorted(g) for g in true_groups.values() if len(g) > 0]
    groups.sort(key=lambda x: x[0] if x else 0)

    return objects, groups


# Add hard problems
problems.extend([
    {
        "num_objects": 16,
        "num_shapes": 6,
        "seed": 999001,
        "hard": True
    },
    {
        "num_objects": 20,
        "num_shapes": 7,
        "seed": 999002,
        "hard": True
    },
    {
        "num_objects": 25,
        "num_shapes": 8,
        "seed": 999003,
        "hard": True
    },
])

# Pre-generate all problems
generated_problems = []
for p in problems:
    if p.get("hard", False):
        objects, groups = generate_hard_problem(p["num_objects"],
                                                p["num_shapes"], p["seed"])
    else:
        objects, groups = generate_problem(p["num_objects"], p["num_shapes"],
                                           p["seed"])
    generated_problems.append({
        "objects": objects,
        "groups": groups,
        "num_objects": p["num_objects"]
    })

subpassParamSummary = [
    f"{p['num_objects']} objects, {p['num_shapes']} unique shapes"
    for p in problems
]
promptChangeSummary = "Increasing number of objects and unique shapes"


def prepareSubpassPrompt(index: int) -> str:
    if index >= len(generated_problems):
        raise StopIteration

    prob = generated_problems[index]

    desc = ""
    for i, obj in enumerate(prob["objects"]):
        desc += f"\nObject {i+1}: cubes at " + ", ".join(f"({x},{y},{z})"
                                                         for x, y, z in obj)

    return prompt.replace("OBJECTS_DESCRIPTION", desc)


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    prob = generated_problems[subPass]
    expected_groups = prob["groups"]

    given_groups = answer.get("groups", [])
    if not given_groups:
        return 0, "No groups provided"

    # Normalize groups (sort each group, then sort groups by first element)
    def normalize_groups(groups):
        normalized = [sorted(g) for g in groups if g]
        normalized.sort(key=lambda x: x[0] if x else 0)
        return normalized

    given_norm = normalize_groups(given_groups)
    expected_norm = normalize_groups(expected_groups)

    # Check for exact match
    if given_norm == expected_norm:
        return 1.0, "Perfect match!"

    # Partial scoring: count correctly grouped pairs
    def get_pairs(groups):
        pairs = set()
        for g in groups:
            for i, a in enumerate(g):
                for b in g[i + 1:]:
                    pairs.add((min(a, b), max(a, b)))
        return pairs

    expected_pairs = get_pairs(expected_norm)
    given_pairs = get_pairs(given_norm)

    correct = len(expected_pairs & given_pairs)
    total = len(expected_pairs)

    # Also penalize wrong pairs
    wrong = len(given_pairs - expected_pairs)

    score = (correct - 0.5 * wrong) / total if total > 0 else 0
    score = max(0, min(1, score))

    return score, f"Correct pairs: {correct}/{total}, Wrong pairs: {wrong}<br>Expected: {expected_norm}<br>Got: {given_norm}"


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    prob = generated_problems[subPass]

    html = "<b>Objects:</b><br>"
    for i, obj in enumerate(prob["objects"]):
        html += f"Object {i+1}: {obj}<br>"

    html += "<br><b>Your groups:</b><br>"
    for g in answer.get("groups", []):
        html += f"{g}<br>"

    html += "<br><b>Expected groups:</b><br>"
    for g in prob["groups"]:
        html += f"{g}<br>"

    return html


highLevelSummary = """
Mental rotation is a core spatial reasoning ability - recognizing that two objects are 
the same shape despite being shown from different orientations.
<br><br>
This test presents multiple 3D polycube shapes and asks the LLM to group those that are 
rotations of each other (but NOT mirror images).
<br><br>
Key challenges:
<ul>
<li>Mentally rotating 3D coordinates</li>
<li>Distinguishing rotations from reflections (chiral shapes)</li>
<li>Handling multiple comparison groups simultaneously</li>
</ul>
This mirrors classic spatial ability tests used in psychology research.
"""
