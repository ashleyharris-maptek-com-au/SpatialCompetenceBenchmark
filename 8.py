import re
import os
import tempfile
import json
import hashlib
import math
import random
import time
from PIL import Image
from LLMBenchCore.ResultPaths import result_path, report_relpath

# Cache for grading and visualization results
_cache_dir = os.path.join(tempfile.gettempdir(), "8_polynomial_cache")
os.makedirs(_cache_dir, exist_ok=True)


def _get_cache_key(answer: dict, subPass: int, aiEngineName: str) -> str:
  """Generate a cache key from the answer, subPass, and engine name."""
  data = json.dumps(answer, sort_keys=True) + str(subPass) + aiEngineName
  if "SUBPASS_CONFIG_HASHES" in globals() and subPass < len(SUBPASS_CONFIG_HASHES):
    data += SUBPASS_CONFIG_HASHES[subPass]
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
   '#' if f(x,y) > 0
   '.' if f(x,y) <= 0

where f(x,y) is a polynomial of whatever degree you need to solve this. You can include cross terms like x*y, x**2*y, x*y**2, etc.

Return the formula as Python function f(x,y) that uses ONLY:
- arithmetic operations (+, -, *, /)
- powers (**) 
- parentheses for grouping
- integer coordinates x, y
- the words "def" and "return"

Do not use type annotations, casts, conditionals, branches, additional variables, comments or anything else.

You can use the following example as a template:

def f(x, y):
    return x**2 + 3*y**2 - 4*x*y - 145

"""

GENERATOR_VERSION = "v2"
GRID_IMAGE_THRESHOLD = 40
GRID_IMAGE_TARGET = 320

SUBPASS_CONFIG = [
  {
    "size": 8,
    "seed": 11,
    "fill_ratio": 0.45,
    "freq_limit": 2,
    "blob_count": 3,
    "wave_count": 1,
    "smooth_passes": 2,
    "label": "Small blob cluster"
  },
  {
    "size": 12,
    "seed": 23,
    "fill_ratio": 0.5,
    "freq_limit": 2,
    "blob_count": 4,
    "wave_count": 2,
    "smooth_passes": 2,
    "label": "Smooth corner"
  },
  {
    "size": 24,
    "seed": 37,
    "fill_ratio": 0.38,
    "freq_limit": 2,
    "blob_count": 5,
    "wave_count": 2,
    "smooth_passes": 3,
    "label": "Island just off centre"
  },
  {
    "size": 24,
    "seed": 49,
    "fill_ratio": 0.55,
    "freq_limit": 2,
    "blob_count": 2,
    "wave_count": 1,
    "smooth_passes": 2,
    "label": "Twin islands"
  },
  {
    "size": 48,
    "seed": 61,
    "fill_ratio": 0.42,
    "freq_limit": 3,
    "blob_count": 7,
    "wave_count": 3,
    "smooth_passes": 4,
    "label": "Low-frequency Thumb"
  },
  {
    "size": 64,
    "seed": 73,
    "fill_ratio": 0.45,
    "freq_limit": 3,
    "blob_count": 8,
    "wave_count": 3,
    "smooth_passes": 4,
    "label": "Peanut shape"
  },
  {
    "size": 96,
    "seed": 85,
    "fill_ratio": 0.45,
    "freq_limit": 3,
    "blob_count": 8,
    "wave_count": 3,
    "smooth_passes": 4,
    "label": "Ellipse"
  },
  {
    "size": 50,
    "seed": 86,
    "fill_ratio": 0.3,
    "freq_limit": 8,
    "blob_count": 12,
    "wave_count": 2,
    "smooth_passes": 1,
    "label": "Asteroid"
  },
  {
    "size": 128,
    "seed": 97,
    "fill_ratio": 0.45,
    "freq_limit": 3,
    "blob_count": 8,
    "wave_count": 3,
    "smooth_passes": 4,
    "label": "Hallowean Decoration"
  }
]


def _safe_name(value):
  cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
  return cleaned or "grid"


def _config_hash(config):
  payload = dict(config)
  payload["generator_version"] = GENERATOR_VERSION
  return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


SUBPASS_CONFIG_HASHES = [_config_hash(cfg) for cfg in SUBPASS_CONFIG]
_GRID_CACHE = {}


def _get_subpass_config(index):
  if index < 0 or index >= len(SUBPASS_CONFIG):
    return None
  return SUBPASS_CONFIG[index]


def _get_image_scale(size):
  return max(1, min(8, GRID_IMAGE_TARGET // size))


def _grid_image_path(subpass, kind):
  config_hash = SUBPASS_CONFIG_HASHES[subpass]
  safe_kind = _safe_name(kind)
  return f"results/8_grid_{safe_kind}_{subpass}_{config_hash}.png"


def _grid_lines_to_image(grid_lines):
  size = len(grid_lines)
  img = Image.new("L", (size, size), 255)
  pixels = img.load()
  for y, row in enumerate(grid_lines):
    for x, ch in enumerate(row):
      pixels[x, y] = 0 if ch == "#" else 255
  scale = _get_image_scale(size)
  if scale > 1:
    img = img.resize((size * scale, size * scale), resample=Image.NEAREST)
  return img


def _ensure_grid_image(subpass, grid_lines, kind):
  os.makedirs("results", exist_ok=True)
  path = _grid_image_path(subpass, kind)
  if not os.path.exists(path):
    _grid_lines_to_image(grid_lines).save(path)
  return path


def _generate_field(size, seed, config):
  rng = random.Random(seed)
  blob_count = config.get("blob_count", max(3, size // 12))
  wave_count = config.get("wave_count", max(1, size // 16))
  freq_limit = max(1, min(config.get("freq_limit", 2), 3))
  negative_blob_count = config.get("negative_blob_count", max(1, blob_count // 3))

  blobs = []
  for _ in range(blob_count):
    cx = rng.uniform(0, size - 1)
    cy = rng.uniform(0, size - 1)
    sigma = rng.uniform(size * 0.18, size * 0.38)
    amp = rng.uniform(0.9, 1.6)
    blobs.append((cx, cy, sigma, amp))

  for _ in range(negative_blob_count):
    cx = rng.uniform(0, size - 1)
    cy = rng.uniform(0, size - 1)
    sigma = rng.uniform(size * 0.25, size * 0.5)
    amp = -rng.uniform(0.4, 0.9)
    blobs.append((cx, cy, sigma, amp))

  waves = []
  for _ in range(wave_count):
    fx = rng.randint(1, freq_limit)
    fy = rng.randint(1, freq_limit)
    phase = rng.uniform(0, 2 * math.pi)
    amp = rng.uniform(0.05, 0.12) * (1 if rng.random() > 0.5 else -1)
    waves.append((fx, fy, phase, amp))

  field = []
  for y in range(size):
    row = []
    for x in range(size):
      value = 0.0
      for cx, cy, sigma, amp in blobs:
        dx = x - cx
        dy = y - cy
        value += amp * math.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma))
      for fx, fy, phase, amp in waves:
        value += amp * math.sin((x * fx + y * fy) * 2 * math.pi / size + phase)
      row.append(value)
    field.append(row)
  return field


def _smooth_field(field, passes):
  size = len(field)
  if passes <= 0:
    return field
  for _ in range(passes):
    new_field = []
    for y in range(size):
      row = []
      for x in range(size):
        acc = 0.0
        for dy in (-1, 0, 1):
          ny = min(size - 1, max(0, y + dy))
          for dx in (-1, 0, 1):
            nx = min(size - 1, max(0, x + dx))
            if dx == 0 and dy == 0:
              weight = 4
            elif dx == 0 or dy == 0:
              weight = 2
            else:
              weight = 1
            acc += field[ny][nx] * weight
        row.append(acc / 16.0)
      new_field.append(row)
    field = new_field
  return field


def _generate_grid(config):
  size = config["size"]
  seed = config.get("seed", 0)
  fill_ratio = config.get("fill_ratio", 0.45)
  fill_ratio = max(0.2, min(0.8, fill_ratio))

  field = _generate_field(size, seed, config)
  smooth_passes = config.get("smooth_passes", max(2, size // 12))
  field = _smooth_field(field, smooth_passes)
  values = sorted(v for row in field for v in row)
  threshold_index = int((1 - fill_ratio) * (len(values) - 1))
  threshold = values[threshold_index]

  lines = []
  for y in range(size):
    line = "".join("#" if field[y][x] >= threshold else "." for x in range(size))
    lines.append(line)
  return lines


def _get_grid_for_subpass(subpass):
  if subpass in _GRID_CACHE:
    return _GRID_CACHE[subpass]
  config = _get_subpass_config(subpass)
  if config is None:
    return None
  grid_lines = _generate_grid(config)
  _GRID_CACHE[subpass] = grid_lines
  return grid_lines


def _get_prompt_payload(subpass, grid_lines):
  size = len(grid_lines)
  if size > GRID_IMAGE_THRESHOLD:
    image_path = _ensure_grid_image(subpass, grid_lines, "reference")
    return "(See attached image.)", f"[[image:{image_path}]]"
  return "\n".join(grid_lines), ""


def _build_subpass_summary(subpass, config, grid_lines):
  size = len(grid_lines)
  label = config.get("label")
  header = f"{label} ({size}x{size})" if label else f"{size}x{size}"
  if size > GRID_IMAGE_THRESHOLD:
    return f"{header}<br>See prompt image."
  grid_text = "\n".join(grid_lines)
  return f"{header}<br><pre>{grid_text}</pre>"

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Optional free text for explaining your solution."
    },
    "function": {
      "type": "string",
      "description": "The function defintion as a string. Starting with 'def f(x,y):'"
    }
  },
  "additionalProperties": False,
  "propertyOrdering": ["reasoning", "function"],
  "required": ["reasoning", "function"]
}


def prepareSubpassPrompt(index):
  config = _get_subpass_config(index)
  if config is None:
    raise StopIteration
  grid_lines = _get_grid_for_subpass(index)
  grid_details, image_tag = _get_prompt_payload(index, grid_lines)
  prompt_text = prompt.replace("GRIDSIZE", str(config["size"])).replace("GRIDDETAILS", grid_details)

  if config["size"] > GRID_IMAGE_THRESHOLD:
    prompt_text = prompt_text.replace("'.'", "white")
    prompt_text = prompt_text.replace("'#'", "black")

  if image_tag:
    prompt_text = prompt_text.rstrip() + "\n\n" + image_tag + "\n"
  return prompt_text


subpassParamSummary = [
  _build_subpass_summary(idx, cfg, _get_grid_for_subpass(idx))
  for idx, cfg in enumerate(SUBPASS_CONFIG)
]


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  # Check cache first
  cache_key = _get_cache_key(answer, subPass, aiEngineName)
  cached = _load_from_cache(cache_key, "grade")
  if cached is not None:
    print(f"Using cached grade result for {aiEngineName} subpass {subPass}")
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

  config = _get_subpass_config(subPass)
  if config is None:
    return 0.0, "Invalid subpass"
  gridSize = config["size"]

  if "deff(x,y):" not in answer.replace(" ", ""):

    print("deff(x,y): not in " + answer.replace(" ", ""))

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

  t = time.time()

  grid = _get_grid_for_subpass(subPass)
  score = 0
  errors = []

  getGridTime = time.time() - t
  if (getGridTime > 1):
    print(f"_get_grid_for_subpass took {getGridTime:.2f}s")

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
    makeGridTime = time.time() - t
    if (makeGridTime > 1):
      print(f"Function calling {(y + 1)/(gridSize)*100:.1f}% done")

  getGridTime = time.time() - t
  if (getGridTime > 1):
    print(f"Function calling took {getGridTime:.2f}s")


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
  config = _get_subpass_config(subPass)
  if config is None:
    return "<td>Invalid subpass</td><td>Subpass configuration missing.</td>"
  gridSize = config["size"]
  gridRow = " " * gridSize
  grid = [gridRow] * gridSize

  g = {}
  try:
    exec(answer.strip(), g)
  except Exception as e:
    if len(answer) > 200:
      answer = answer[:200] + "... (truncated)"
    answer_html = answer.replace('\n', '<br/>')
    return f"<td>{answer_html}</td><td>Error evaluating AI-generated python function: {e}</td>"

  if len(answer) > 200:
    answer = answer[:200] + "... (truncated)"

  gRef = _get_grid_for_subpass(subPass)

  try:
    f = g["f"]

    output_lines = []
    mismatch_count = 0
    for y in range(gridSize):
      row_outputs = []
      for x in range(gridSize):
        output = ("#" if f(x, y) > 0 else ".")
        row_outputs.append(output)
        if output == gRef[y][x]:
          display = output
        elif output == ".":
          display = "?"
        else:
          display = "X"
        if display != output:
          mismatch_count += 1
        grid[y] = grid[y][:x] + display + grid[y][x + 1:]
      output_lines.append("".join(row_outputs))

    if gridSize > GRID_IMAGE_THRESHOLD:
      expected_path = _ensure_grid_image(subPass, gRef, "expected")
      output_filename = f"8_grid_output_{_safe_name(aiEngineName)}_{subPass}_{SUBPASS_CONFIG_HASHES[subPass]}.png"
      output_path = result_path(output_filename, aiEngineName)
      _grid_lines_to_image(output_lines).save(output_path)
      return f"""
      <td style='font-size: 14px'><div style='max-width:800px'>
        {answer.replace(chr(10),'<br/>')}
      </div></td><td>
        <div style='display:flex; gap:12px; align-items:flex-start; flex-wrap:wrap;'>
          <div><div>Expected</div><img src='{report_relpath(expected_path, aiEngineName)}' style='max-width:45%'></div>
          <div><div>Output</div><img src='{report_relpath(output_path, aiEngineName)}' style='max-width:45%'></div>
        </div>
        <div>Mismatched cells: {mismatch_count}</div>
      </td>"""

    extraInfo = ""
    if any("?" in row for row in grid):
      extraInfo += "<br/> '?' = '#' was expected, '.' was provided."
    if any("X" in row for row in grid):
      extraInfo += "<br/> 'X' = '.' was expected, '#' was provided."

    gridAndgRef = []
    for y in range(gridSize):
      gridAndgRef.append(grid[y] + " " + gRef[y])

    return f"""
    <td style='font-size: 14px'><div style='max-width:800px'>
      {answer.replace(chr(10),'<br/>')}
    </div></td><td><pre>{'<br/>'.join(gridAndgRef)}</pre><br/>
      {extraInfo}
    </td>"""
  except Exception as e:
    answer_html = answer.replace('\n', '<br/>')
    return f"<td style='font-size: 12px'>{answer_html}</td><td>Error evaluating AI-generated python function: {e}</td>"


highLevelSummary = """
Can the LLM roundtrip a 2D shape through a polynomial?
<br><br>
Shapes are procedurally generated from smooth fields so each subpass features
curves/blobs rather than hardcoded patterns. Larger grids (over 64x64) are
visualized via attached black/white images instead of ASCII art.
"""

if __name__ == "__main__":
  # Test the function with the copied code
  test_answer = {
    'reasoning':
    "I identified the boundary for each y as b(y) where # are for x <= b(y). I interpolated a polynomial p(y) such that p(y) = b(y) + 0.5 at y=0 to 7 using Newton's forward difference formula. To avoid fractions, I worked with r(y) = 2 * p(y), then cleared denominators by multiplying by 1260 (LCM of relevant factorials) to get integer polynomial s(y) = 1260 * r(y). Finally, f(x,y) = s(y) - 2520 * x has the desired sign at integer points (0<=x,y<=7).",
    'function':
    'def f(x, y):\n    return 6300 - 2520 * y + 1260 * (y * (y - 1)) - 105 * (y * (y - 1) * (y - 2) * (y - 3)) + 42 * (y * (y - 1) * (y - 2) * (y - 3) * (y - 4)) - 7 * (y * (y - 1) * (y - 2) * (y - 3) * (y - 4) * (y - 5)) - (y * (y - 1) * (y - 2) * (y - 3) * (y - 4) * (y - 5) * (y - 6)) - 2520 * x'
  }
  print(gradeAnswer(test_answer, 0, "test"))
  result = _resultToNiceReportImpl(test_answer, 0, "test")
  print(result)
