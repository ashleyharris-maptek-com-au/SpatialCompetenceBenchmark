import math
import random

skip = True

title = "Gear Train Reasoning - predict rotation directions and speeds"

prompt = """
You are analyzing a gear train system. Gears are circles that mesh together - when one gear turns, 
it causes adjacent (meshing) gears to turn in the opposite direction.

The rotation speed ratio between two meshing gears is inversely proportional to their tooth counts.
If gear A has 20 teeth and gear B has 40 teeth, when A rotates once, B rotates 0.5 times.
When two gears mesh, they rotate in OPPOSITE directions.

GEAR_SYSTEM

The input gear (gear 1) is rotating CLOCKWISE at INPUT_SPEED RPM (rotations per minute).

For each gear in the system, determine:
1. Its rotation direction (clockwise or counterclockwise)
2. Its rotation speed in RPM

Note: A gear with more teeth rotates slower. Two meshing gears rotate in opposite directions.
"""

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "gears": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "gearNumber": {
                        "type": "integer"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["clockwise", "counterclockwise"]
                    },
                    "rpm": {
                        "type": "number"
                    }
                },
                "propertyOrdering": ["gearNumber", "direction", "rpm"],
                "required": ["gearNumber", "direction", "rpm"],
                "additionalProperties": False
            }
        }
    },
    "propertyOrdering": ["reasoning", "gears"],
    "required": ["reasoning", "gears"],
    "additionalProperties": False
}

# Define gear systems
gear_systems = [
    {
        "name":
        "Simple 2-gear",
        "description":
        """
Gear 1: 20 teeth (input gear)
Gear 2: 40 teeth, meshes with Gear 1
""",
        "input_speed":
        100,
        "expected": [
            {
                "gearNumber": 1,
                "direction": "clockwise",
                "rpm": 100
            },
            {
                "gearNumber": 2,
                "direction": "counterclockwise",
                "rpm": 50
            },
        ]
    },
    {
        "name":
        "3-gear chain",
        "description":
        """
Gear 1: 10 teeth (input gear)
Gear 2: 30 teeth, meshes with Gear 1
Gear 3: 15 teeth, meshes with Gear 2
""",
        "input_speed":
        60,
        "expected": [
            {
                "gearNumber": 1,
                "direction": "clockwise",
                "rpm": 60
            },
            {
                "gearNumber": 2,
                "direction": "counterclockwise",
                "rpm": 20
            },
            {
                "gearNumber": 3,
                "direction": "clockwise",
                "rpm": 40
            },
        ]
    },
    {
        "name":
        "4-gear reduction",
        "description":
        """
Gear 1: 12 teeth (input gear)
Gear 2: 48 teeth, meshes with Gear 1
Gear 3: 12 teeth, on SAME SHAFT as Gear 2 (rotates same direction and speed as Gear 2)
Gear 4: 36 teeth, meshes with Gear 3

Note: Gears on the same shaft rotate together at the same speed and direction.
""",
        "input_speed":
        1200,
        "expected": [
            {
                "gearNumber": 1,
                "direction": "clockwise",
                "rpm": 1200
            },
            {
                "gearNumber": 2,
                "direction": "counterclockwise",
                "rpm": 300
            },
            {
                "gearNumber": 3,
                "direction": "counterclockwise",
                "rpm": 300
            },
            {
                "gearNumber": 4,
                "direction": "clockwise",
                "rpm": 100
            },
        ]
    },
    {
        "name":
        "Idler gear system",
        "description":
        """
Gear 1: 24 teeth (input gear)
Gear 2: 24 teeth (idler), meshes with Gear 1
Gear 3: 24 teeth, meshes with Gear 2
Gear 4: 24 teeth, meshes with Gear 3
Gear 5: 24 teeth, meshes with Gear 4

An idler gear reverses direction without changing speed ratio.
""",
        "input_speed":
        200,
        "expected": [
            {
                "gearNumber": 1,
                "direction": "clockwise",
                "rpm": 200
            },
            {
                "gearNumber": 2,
                "direction": "counterclockwise",
                "rpm": 200
            },
            {
                "gearNumber": 3,
                "direction": "clockwise",
                "rpm": 200
            },
            {
                "gearNumber": 4,
                "direction": "counterclockwise",
                "rpm": 200
            },
            {
                "gearNumber": 5,
                "direction": "clockwise",
                "rpm": 200
            },
        ]
    },
    {
        "name":
        "Complex compound gear train",
        "description":
        """
Gear 1: 15 teeth (input gear)
Gear 2: 45 teeth, meshes with Gear 1
Gear 3: 20 teeth, on SAME SHAFT as Gear 2
Gear 4: 60 teeth, meshes with Gear 3
Gear 5: 10 teeth, on SAME SHAFT as Gear 4
Gear 6: 50 teeth, meshes with Gear 5

Calculate the output speed and direction for all gears.
""",
        "input_speed":
        3000,
        "expected": [
            {
                "gearNumber": 1,
                "direction": "clockwise",
                "rpm": 3000
            },
            {
                "gearNumber": 2,
                "direction": "counterclockwise",
                "rpm": 1000
            },
            {
                "gearNumber": 3,
                "direction": "counterclockwise",
                "rpm": 1000
            },
            {
                "gearNumber": 4,
                "direction": "clockwise",
                "rpm": 333.333
            },
            {
                "gearNumber": 5,
                "direction": "clockwise",
                "rpm": 333.333
            },
            {
                "gearNumber": 6,
                "direction": "counterclockwise",
                "rpm": 66.667
            },
        ]
    },
]

# === SUPER-HARD CHALLENGES ===
# Generate complex gear trains with solver


def solve_gear_train(gears_def, input_speed):
    """
    Solve a gear train defined by connections.
    gears_def: list of dicts with 'teeth', 'meshes_with' (list), 'same_shaft_as' (optional)
    Returns expected results.
    """
    n = len(gears_def)
    rpms = [None] * n
    directions = [None] * n

    # Gear 1 is always input
    rpms[0] = input_speed
    directions[0] = "clockwise"

    # Iteratively solve until all gears are determined
    changed = True
    iterations = 0
    while changed and iterations < 100:
        changed = False
        iterations += 1

        for i, gear in enumerate(gears_def):
            if rpms[i] is not None:
                # This gear is solved, propagate to connected gears

                # Same shaft gears
                if 'same_shaft_as' in gear:
                    j = gear['same_shaft_as'] - 1  # Convert to 0-indexed
                    if rpms[j] is None:
                        rpms[j] = rpms[i]
                        directions[j] = directions[i]
                        changed = True

                # Meshing gears
                for j in gear.get('meshes_with', []):
                    j_idx = j - 1  # Convert to 0-indexed
                    if rpms[j_idx] is None:
                        # Speed ratio = teeth_i / teeth_j
                        rpms[j_idx] = rpms[i] * gears_def[i][
                            'teeth'] / gears_def[j_idx]['teeth']
                        # Opposite direction
                        directions[j_idx] = "counterclockwise" if directions[
                            i] == "clockwise" else "clockwise"
                        changed = True

            # Check if another gear drives this one
            for k, other in enumerate(gears_def):
                if rpms[k] is not None and rpms[i] is None:
                    if i + 1 in other.get('meshes_with', []):
                        rpms[i] = rpms[k] * other['teeth'] / gear['teeth']
                        directions[i] = "counterclockwise" if directions[
                            k] == "clockwise" else "clockwise"
                        changed = True
                    if 'same_shaft_as' in other and other[
                            'same_shaft_as'] == i + 1:
                        rpms[i] = rpms[k]
                        directions[i] = directions[k]
                        changed = True

    return [{
        "gearNumber": i + 1,
        "direction": directions[i],
        "rpm": round(rpms[i], 6)
    } for i in range(n)]


# Complex planetary-style gear system (12 gears)
complex_12_gear = [
    {
        "teeth": 13,
        "meshes_with": [2, 3]
    },  # Gear 1: input, meshes with 2 and 3
    {
        "teeth": 47,
        "meshes_with": [1, 4]
    },  # Gear 2
    {
        "teeth": 31,
        "meshes_with": [1, 5]
    },  # Gear 3
    {
        "teeth": 19,
        "meshes_with": [2],
        "same_shaft_as": 6
    },  # Gear 4, same shaft as 6
    {
        "teeth": 23,
        "meshes_with": [3],
        "same_shaft_as": 7
    },  # Gear 5, same shaft as 7
    {
        "teeth": 41,
        "meshes_with": [8]
    },  # Gear 6
    {
        "teeth": 37,
        "meshes_with": [8]
    },  # Gear 7
    {
        "teeth": 29,
        "meshes_with": [6, 7],
        "same_shaft_as": 9
    },  # Gear 8, same shaft as 9
    {
        "teeth": 17,
        "meshes_with": [10, 11]
    },  # Gear 9
    {
        "teeth": 53,
        "meshes_with": [9, 12]
    },  # Gear 10
    {
        "teeth": 43,
        "meshes_with": [9]
    },  # Gear 11
    {
        "teeth": 61,
        "meshes_with": [10]
    },  # Gear 12: output
]

# 15-gear compound reduction system
complex_15_gear = [
    {
        "teeth": 11,
        "meshes_with": [2]
    },  # Gear 1: input
    {
        "teeth": 67,
        "meshes_with": [1],
        "same_shaft_as": 3
    },
    {
        "teeth": 13,
        "meshes_with": [4]
    },
    {
        "teeth": 71,
        "meshes_with": [3],
        "same_shaft_as": 5
    },
    {
        "teeth": 17,
        "meshes_with": [6]
    },
    {
        "teeth": 59,
        "meshes_with": [5],
        "same_shaft_as": 7
    },
    {
        "teeth": 19,
        "meshes_with": [8]
    },
    {
        "teeth": 53,
        "meshes_with": [7],
        "same_shaft_as": 9
    },
    {
        "teeth": 23,
        "meshes_with": [10]
    },
    {
        "teeth": 47,
        "meshes_with": [9],
        "same_shaft_as": 11
    },
    {
        "teeth": 29,
        "meshes_with": [12]
    },
    {
        "teeth": 43,
        "meshes_with": [11],
        "same_shaft_as": 13
    },
    {
        "teeth": 31,
        "meshes_with": [14]
    },
    {
        "teeth": 41,
        "meshes_with": [13],
        "same_shaft_as": 15
    },
    {
        "teeth": 37,
        "meshes_with": [14]
    },  # Gear 15: output
]

# 10-gear branching system with reconvergence
complex_10_gear_branch = [
    {
        "teeth": 20,
        "meshes_with": [2, 3, 4]
    },  # Gear 1: input splits to 3 branches
    {
        "teeth": 60,
        "meshes_with": [1],
        "same_shaft_as": 5
    },
    {
        "teeth": 40,
        "meshes_with": [1],
        "same_shaft_as": 6
    },
    {
        "teeth": 80,
        "meshes_with": [1],
        "same_shaft_as": 7
    },
    {
        "teeth": 15,
        "meshes_with": [8]
    },
    {
        "teeth": 25,
        "meshes_with": [9]
    },
    {
        "teeth": 10,
        "meshes_with": [10]
    },
    {
        "teeth": 45,
        "meshes_with": [5]
    },  # These should have specific ratios
    {
        "teeth": 50,
        "meshes_with": [6]
    },
    {
        "teeth": 40,
        "meshes_with": [7]
    },
]

gear_systems.extend([
    {
        "name": "12-gear planetary-style system - HARD",
        "description": """
A complex 12-gear system with branching paths and reconvergence:

Gear 1: 13 teeth (input gear), meshes with Gears 2 AND 3 (power splits)
Gear 2: 47 teeth, meshes with Gears 1 and 4
Gear 3: 31 teeth, meshes with Gears 1 and 5
Gear 4: 19 teeth, meshes with Gear 2, SAME SHAFT as Gear 6
Gear 5: 23 teeth, meshes with Gear 3, SAME SHAFT as Gear 7
Gear 6: 41 teeth, meshes with Gear 8
Gear 7: 37 teeth, meshes with Gear 8
Gear 8: 29 teeth, meshes with Gears 6 and 7, SAME SHAFT as Gear 9 (paths reconverge)
Gear 9: 17 teeth, meshes with Gears 10 and 11
Gear 10: 53 teeth, meshes with Gears 9 and 12
Gear 11: 43 teeth, meshes with Gear 9
Gear 12: 61 teeth, meshes with Gear 10 (final output)

Note: When power splits and reconverges, the gear ratios must be compatible.
Calculate RPM and direction for all 12 gears.
""",
        "input_speed": 10000,
        "expected": solve_gear_train(complex_12_gear, 10000)
    },
    {
        "name": "15-gear extreme reduction - HARD",
        "description": """
A 15-gear compound reduction train achieving massive speed reduction:

Gear 1: 11 teeth (input)
Gear 2: 67 teeth, meshes with Gear 1, SAME SHAFT as Gear 3
Gear 3: 13 teeth, meshes with Gear 4
Gear 4: 71 teeth, meshes with Gear 3, SAME SHAFT as Gear 5
Gear 5: 17 teeth, meshes with Gear 6
Gear 6: 59 teeth, meshes with Gear 5, SAME SHAFT as Gear 7
Gear 7: 19 teeth, meshes with Gear 8
Gear 8: 53 teeth, meshes with Gear 7, SAME SHAFT as Gear 9
Gear 9: 23 teeth, meshes with Gear 10
Gear 10: 47 teeth, meshes with Gear 9, SAME SHAFT as Gear 11
Gear 11: 29 teeth, meshes with Gear 12
Gear 12: 43 teeth, meshes with Gear 11, SAME SHAFT as Gear 13
Gear 13: 31 teeth, meshes with Gear 14
Gear 14: 41 teeth, meshes with Gear 13, SAME SHAFT as Gear 15
Gear 15: 37 teeth, meshes with Gear 14 (output)

This is a 7-stage compound reduction. Calculate RPM for all gears.
""",
        "input_speed": 100000,
        "expected": solve_gear_train(complex_15_gear, 100000)
    },
    {
        "name": "10-gear branching system - HARD",
        "description": """
A 10-gear system where power branches and each branch has different reduction:

Gear 1: 20 teeth (input), meshes with Gears 2, 3, AND 4 simultaneously
Gear 2: 60 teeth, meshes with Gear 1, SAME SHAFT as Gear 5
Gear 3: 40 teeth, meshes with Gear 1, SAME SHAFT as Gear 6
Gear 4: 80 teeth, meshes with Gear 1, SAME SHAFT as Gear 7
Gear 5: 15 teeth, meshes with Gear 8
Gear 6: 25 teeth, meshes with Gear 9
Gear 7: 10 teeth, meshes with Gear 10
Gear 8: 45 teeth, meshes with Gear 5
Gear 9: 50 teeth, meshes with Gear 6
Gear 10: 40 teeth, meshes with Gear 7

Each branch has different total reduction ratios.
Calculate RPM and direction for all 10 gears.
""",
        "input_speed": 6000,
        "expected": solve_gear_train(complex_10_gear_branch, 6000)
    },
])

subpassParamSummary = [s["name"] for s in gear_systems]
promptChangeSummary = "Progressively more complex gear trains"


def prepareSubpassPrompt(index: int) -> str:
    if index >= len(gear_systems):
        raise StopIteration
    system = gear_systems[index]
    p = prompt.replace("GEAR_SYSTEM", system["description"])
    p = p.replace("INPUT_SPEED", str(system["input_speed"]))
    return p


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    system = gear_systems[subPass]
    expected = system["expected"]

    gears = answer.get("gears", [])
    if not gears:
        return 0, "No gears provided"

    gear_dict = {}
    for g in gears:
        num = g.get("gearNumber", 0)
        gear_dict[num] = g

    total_score = 0
    max_score = len(expected) * 2  # 1 for direction, 1 for rpm
    details = []

    for exp in expected:
        num = exp["gearNumber"]
        if num not in gear_dict:
            details.append(f"Missing gear {num}")
            continue

        g = gear_dict[num]

        # Check direction
        if g.get("direction", "").lower() == exp["direction"]:
            total_score += 1
            details.append(f"Gear {num} direction OK")
        else:
            details.append(
                f"Gear {num} direction wrong (got {g.get('direction')}, expected {exp['direction']})"
            )

        # Check RPM (within 1% tolerance)
        expected_rpm = exp["rpm"]
        actual_rpm = g.get("rpm", 0)
        if abs(actual_rpm - expected_rpm) <= max(0.01 * expected_rpm, 0.1):
            total_score += 1
            details.append(f"Gear {num} RPM OK ({actual_rpm:.2f})")
        else:
            details.append(
                f"Gear {num} RPM wrong (got {actual_rpm:.2f}, expected {expected_rpm:.2f})"
            )

    score = total_score / max_score if max_score > 0 else 0
    return score, "<br>".join(details)


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    gears = answer.get("gears", [])

    html = "<table border='1'><tr><th>Gear</th><th>Direction</th><th>RPM</th></tr>"

    for g in sorted(gears, key=lambda x: x.get("gearNumber", 0)):
        html += f"<tr><td>{g.get('gearNumber', '?')}</td>"
        html += f"<td>{g.get('direction', '?')}</td>"
        html += f"<td>{g.get('rpm', '?'):.2f}</td></tr>"

    html += "</table>"

    # Add expected for comparison
    system = gear_systems[subPass]
    html += "<br><b>Expected:</b><table border='1'><tr><th>Gear</th><th>Direction</th><th>RPM</th></tr>"
    for exp in system["expected"]:
        html += f"<tr><td>{exp['gearNumber']}</td>"
        html += f"<td>{exp['direction']}</td>"
        html += f"<td>{exp['rpm']:.2f}</td></tr>"
    html += "</table>"

    return html


highLevelSummary = """
Tests mechanical reasoning about gear trains.
<br><br>
Key concepts:
<ul>
<li>Meshing gears rotate in opposite directions</li>
<li>Speed ratio = inverse of tooth count ratio</li>
<li>Gears on the same shaft rotate together</li>
<li>Compound gear trains multiply ratios</li>
</ul>
This tests whether an LLM can trace cause-and-effect through a mechanical system.
"""
