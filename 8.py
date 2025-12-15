import re
import os
import tempfile
import json
import hashlib

# Cache for grading and visualization results
_cache_dir = os.path.join(tempfile.gettempdir(), "8_polynomial_cache")
os.makedirs(_cache_dir, exist_ok=True)


def _get_cache_key(answer: dict, subPass: int, aiEngineName: str) -> str:
    """Generate a cache key from the answer, subPass, and engine name."""
    data = json.dumps(answer, sort_keys=True) + str(subPass) + aiEngineName
    return hashlib.sha256(data.encode()).hexdigest()


def _load_from_cache(cache_key: str, cache_type: str):
    """Load result from cache if available."""
    cache_file = os.path.join(_cache_dir, f"{cache_type}_{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _save_to_cache(cache_key: str, cache_type: str, result):
    """Save result to cache."""
    cache_file = os.path.join(_cache_dir, f"{cache_type}_{cache_key}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f)
    except IOError:
        pass


title = "Fit a curve to partition 2D ascii patterns via cubic polynomials"

prompt = """

Here is an GRIDSIZExGRIDSIZE grid representing a space partition:

GRIDDETAILS

0, 0 is the top left, x is horizontal, y is vertical. Coordinates are in integers.

Using the formula:

let cell = 

   # if f(x,y) > 0
   . if f(x,y) <= 0

where f(x,y) is a polynomial of whatever degree you need to solve this. You can include cross terms like x*y, x**2*y, x*y**2, etc.

Return the formula as python function f(x,y) that uses ONLY:
- arithmetic operations (+, -, *, /)
- powers (**) 
- parentheses for grouping
- integer coordinates x, y
- the words "def" and "return"

Do not use type annotations, casts, conditionals, branches, additional variables, comments or anything else.

You can use the following example as a template:

def f(x, y):
    return x**2 + 3*y**2 - 4*x*y - 145

DO NOT OUTPUT ANYTHING ELSE THAN THE FUNCTION.
"""

grids = [
    """
###.....
##......
##......
###.....
####....
#####...
#######.
########
""".strip(), """
########....
######......
####........
###.........
###.........
##..........
##..........
#...........
............
............
............
............
""".strip(), """
........................
........................
........................
........................
........................
........................
........................
........................
........................
.....###................
....######..............
....########............
....##########..........
....###########.........
.....############.......
......###########.......
........#######.........
..........###...........
...........#............
........................
........................
........................
........................
........................
""".strip(), """
........
........
...##...
..####..
.######.
.##..##.
##....##
#......#
""".strip(), """
...............................................
...............................................
..................................##...........
.................................####..........
..................................##...........
...............................................
...............................................
...............................................
...............................................
.......##...........##...........##............
......####.........####.........####...........
.......##...........##...........##............
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................##..............
..............................####.............
...............................##..............
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
.....................##........................
....................####.......................
.....................##........................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
...............................................
"""
]

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "Optional free text for explaining your solution."
        },
        "function": {
            "type":
            "string",
            "description":
            "The function defintion as a string. Starting with 'def f(x,y):'"
        }
    },
    "additionalProperties": False,
    "propertyOrdering": ["reasoning", "function"],
    "required": ["reasoning", "function"]
}


def prepareSubpassPrompt(index):
    if index == 0:
        return prompt.replace("GRIDSIZE", "8").replace("GRIDDETAILS", grids[0])
    if index == 1:
        return prompt.replace("GRIDSIZE",
                              "12").replace("GRIDDETAILS", grids[1])
    if index == 2:
        return prompt.replace("GRIDSIZE",
                              "24").replace("GRIDDETAILS", grids[2])
    if index == 3:
        return prompt.replace("GRIDSIZE", "8").replace("GRIDDETAILS", grids[3])
    if index == 4:
        return prompt.replace("GRIDSIZE",
                              "48").replace("GRIDDETAILS", grids[4])
    raise StopIteration


subpassParamSummary = ["<pre>" + g + "</pre>" for g in grids]


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    # Check cache first
    cache_key = _get_cache_key(answer, subPass, aiEngineName)
    cached = _load_from_cache(cache_key, "grade")
    if cached is not None:
        print(
            f"Using cached grade result for {aiEngineName} subpass {subPass}")
        return tuple(cached)

    result = _gradeAnswerImpl(answer, subPass, aiEngineName)
    _save_to_cache(cache_key, "grade", list(result))
    return result


def _gradeAnswerImpl(answer: dict, subPass: int, aiEngineName: str):
    answer = answer["function"]
    validPass = answer
    validPass = validPass.replace("def", "").strip()
    validPass = validPass.replace("f", "").strip()
    validPass = validPass.replace("return", "").strip()
    validPass = validPass.replace("x", "").strip()
    validPass = validPass.replace("y", "").strip()
    validPass = validPass.replace("e", "").strip()  # Allow sci notation

    if re.search(r'[A-Za-z]', validPass):
        return 0.0, f"Invalid characters in answer: {answer}. It contained \"{validPass}\". Score is 0"

    gridSize = 8 if subPass == 0 else 12 if subPass == 1 else 24 if subPass == 2 else 8 if subPass == 3 else 48

    if "def f(x,y):" not in answer.replace(", ", ""):
        return 0.0, f"Invalid function signature in answer: {answer}. It must contain \"def f(x, y):\". Score is 0"

    if "return" not in answer:
        return 0.0, f"Invalid function signature in answer: {answer}. It must contain \"return\". Score is 0"

    if re.search(R"return [^x]*x", answer) == None:
        return 0.0, "Invalid function - must use x in it's return calculation"

    if re.search(R"return [^y]*y", answer) == None:
        return 0.0, "Invalid function - must use y in it's return calculation"

    g = {}
    try:
        exec(answer.strip(), g)
    except Exception as e:
        return 0.0, f"Error evaluating AI-generated python function: {e}"

    f = g["f"]

    grid = grids[subPass].splitlines()
    score = 0
    errors = []

    generatedHashes = 0

    for y in range(gridSize):
        for x in range(gridSize):
            try:
                p = f(x, y)  # use the evaluated function
                if p > 0:
                    generatedHashes += 1
                    if grid[y][x] == "#":
                        score += 1
                else:
                    if grid[y][x] == ".":
                        score += 1
            except Exception as e:
                errors.append(f"Error evaluating f({x}, {y}): {e}")
                continue

    if generatedHashes == 0 or generatedHashes == gridSize * gridSize:
        return 0.0, f"Output was uniformly valued"

    final_score = score / (gridSize * gridSize)
    reasoning = f"Grid size: {gridSize}, matched {score}/{gridSize*gridSize} cells"
    if errors:
        reasoning += f"\n{len(errors)} evaluation errors occurred"

    if final_score < 0.75:
        final_score = 0

    # Penalize "close but not quite right" answers a bit.
    final_score = final_score**4

    return final_score, reasoning


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str):
    # Check cache first
    cache_key = _get_cache_key(answer, subPass, aiEngineName)
    cached = _load_from_cache(cache_key, "report")
    if cached is not None:
        print(f"Using cached report for {aiEngineName} subpass {subPass}")
        return cached

    result = _resultToNiceReportImpl(answer, subPass, aiEngineName)
    _save_to_cache(cache_key, "report", result)
    return result


def _resultToNiceReportImpl(answer: dict, subPass: int, aiEngineName: str):
    answer = answer["function"]
    gridSize = 8 if subPass == 0 else 12 if subPass == 1 else 24 if subPass == 2 else 8 if subPass == 3 else 48
    gridRow = " " * gridSize
    grid = [gridRow] * gridSize

    g = {}
    try:
        exec(answer.strip(), g)
    except Exception as e:
        return f"<td>{answer.replace('\n','<br/>')}</td><td>Error evaluating AI-generated python function: {e}</td>"

    try:
        f = g["f"]

        for y in range(gridSize):
            for x in range(gridSize):
                grid[y] = grid[y][:x] + ("#" if f(x, y) > 0 else
                                         ".") + grid[y][x + 1:]

        return f"<td style='font-size: 8px'><div style='max-width:800px'>{answer.replace('\n','<br/>')}</div></td><td><pre>{'<br/>'.join(grid)}</pre></td>"
    except Exception as e:
        return f"<td>{answer.replace('\n','<br/>')}</td><td>Error evaluating AI-generated python function: {e}</td>"


highLevelSummary = """
Can the LLM roundtrip a 2D shape through a polynomial?
<br><br>
Some of these are simple cubics, others require hundreds of terms including
cross terms.
"""
