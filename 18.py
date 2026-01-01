title = "Pyamid construction - more bricks than token limits"

prompt = """
A pharoh is building a pyramyd to rest on top of his tomb and protect him for the afterlife. 
He has an army of 100,000 men who are honour bound to assist him in the project.

Pyramids must face north, which is +y, and is centred over the future tomb.

Pharoh has PARAM_A cut large stones, each a 50cm side-length cube.
Each stone needs 10 men to move.

When placed on top of other stones, each stone must have all 4 base
corners sitting in the middle of another stone. Any other arrangements will result in collapse. 
The pyramid does not have any internal voids for this reason.

The final facade will be done with wedges of marble, and the local stonemason requires precise plans to cut 
marble such that each external large stone is covered and the resulting pyamid is smooth.

Generate an OpenSCAD plan showing the tallest pyramid the pharoh can build with his budget
of stone. This plan must be precise with its volume accurate to the milimeter including every step
yet optimised enough to be viewable on the stonemason's CAD software.

Use Metric SI units in all working and in the final OpenSCAD file.

Do not output anything else than the OpenSCAD file, as that will cause compilation errors.
"""


def prepareSubpassPrompt(index):
  if index == 0: return prompt.replace("PARAM_A", "20,000")
  if index == 1: return prompt.replace("PARAM_A", "150,000")
  if index == 2: return prompt.replace("PARAM_A", "600,000")
  if index == 3: return prompt.replace("PARAM_A", "2,500,000")
  raise StopIteration


structure = None

earlyFail = True

promptChangeSummary = """
Hundreds of thousands of stones, then millions. 
The AI needs to merge adjacent stones and work with merged
layers in order to solve this.<br><br>

If it attempts to bruteforce a solution by rendering millions<br>
of bricks as individual cubes, OpenSCAD will either crash from<br>
std::bad_alloc or timeout after 600 seconds, both causing failure.
"""

subpassParamSummary = [
  "20,000 stones (~20m high)", "150,000 stones (~39m high)", "600,000 stones",
  "2,500,000 stones (~100m high / ~200 layers)"
]

referenceScad = ""


def prepareSubpassReferenceScad(index):
  if index == 4: return ""
  stoneCount = 20000 if index == 0 else 150000 if index == 1 else 600000 if index == 2 else 2500000
  scad = ""
  level = 0
  while True:
    level += 1
    stones = level * level
    if stones < stoneCount:
      scad += f"translate([0,0,-{level * 0.5}])  cube([{level * 0.5},{level * 0.5}, 0.5], center=true);\n"
      stoneCount -= stones
    else:
      break

  scad = f"translate([0,0,{level * 0.5}])" + "{\n" + scad + "}\n"

  return "module reference()\n{\n" + scad + "\n}\n"


noMinkowski = True


def resultToScad(result, aiEngineName):
  import CacheLayer as cl, re, scad_format

  structure = {
    "type": "object",
    "properties": {
      "primitiveCount": {
        "type": "integer",
        "description": "How many 'things'' are processed in this script?"
      }
    },
    "required": ["primitiveCount"],
    "additionalProperties": False,
    "propertyOrdering": ["primitiveCount"]
  }

  if "gpt" in aiEngineName:
    from AiEngineGoogleGemini import GeminiEngine
    engine = GeminiEngine("gemini-2.5-flash-lite", False, False)
    cacheLayer = cl.CacheLayer(engine.configAndSettingsHash, engine.AIHook, "gemini-2.5-flash-lite")

    def answerQuestion(q: str) -> dict:
      return cacheLayer.AIHook(q, structure, -1, -1)[0]

  else:
    from AiEngineOpenAiChatGPT import OpenAIEngine
    engine = OpenAIEngine("gpt-5-nano", False, False)
    cacheLayer = cl.CacheLayer(engine.configAndSettingsHash, engine.AIHook, "gpt-5-nano")

    def answerQuestion(q: str) -> dict:
      return cacheLayer.AIHook(q, structure, -1, -1)[0]

  prompt = """
Your job is to determine how many primitives are processed in a script.

Eg:
```
for (i = [0:10])
{
  difference()
  {
    cube(1);
    cube(0.9);
  }
} 
```
Would process 20 cubes, so you'd say it processes 20 primitives. 2 in each loop.

```
module b()
{
  for (i = [0:10])
  {
    for (j = [0:10])
    {
      translate([i,j,0]) sphere(1);
    }
  }
}

foo = 10;
for (k = [0:foo]) b();
```
Would process 1000 spheres, (3 loops of 10) so 1000 primitives.

Exact precision is not required here, magnitude is what is important.

How many primitives are processed in this below script?

-------------------------------------------------------------------------------
""" + result

  inspectionResult = answerQuestion(prompt)

  if inspectionResult["primitiveCount"] > 1000:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("Aborting due to " + str(inspectionResult["primitiveCount"]) + " parts!")
    return "module result(){linear_extrude(0.1) text(\"Aborting due to " + str(
      inspectionResult["primitiveCount"]) + " parts!\");}"
  elif inspectionResult["primitiveCount"] > 200:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("This is dubious and might break your machine, but we'll try.")
  else:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("Seems safe to continue.")

  if result.count("```") == 2:
    result = re.split(r"```[^\n]*\n")[1]

  # We need to extract things that can't be nested inside module result():
  # 1. Module definitions: module name(...) { ... }
  # 2. Function definitions: function name(...) = ...;
  # 3. Top-level variable assignments: name = value; (not inside braces)

  extracted = []
  remaining = result

  # Extract module definitions by matching balanced braces
  module_pattern = re.compile(r'module\s+\w+\s*\([^)]*\)\s*\{')

  while True:
    match = module_pattern.search(remaining)
    if not match:
      break

    start = match.start()
    brace_start = match.end() - 1
    depth = 1
    pos = brace_start + 1

    while pos < len(remaining) and depth > 0:
      if remaining[pos] == '{':
        depth += 1
      elif remaining[pos] == '}':
        depth -= 1
      pos += 1

    if depth == 0:
      extracted.append(remaining[start:pos])
      remaining = remaining[:start] + remaining[pos:]
    else:
      break

  # Extract function definitions: function name(...) = ...;
  func_pattern = re.compile(r'function\s+\w+\s*\([^)]*\)\s*=[^;]*;')
  for match in func_pattern.finditer(remaining):
    extracted.append(match.group())
  remaining = func_pattern.sub('', remaining)

  # Extract top-level variable assignments (not inside braces)
  # Process line by line, tracking brace depth
  lines = remaining.split('\n')
  top_level_lines = []
  inside_lines = []
  brace_depth = 0

  var_assign_pattern = re.compile(r'^\s*(\w+)\s*=\s*[^;]+;\s*(//.*)?$')

  for line in lines:
    # Count braces to track depth (simple approach - doesn't handle strings/comments perfectly)
    open_braces = line.count('{')
    close_braces = line.count('}')

    # If we're at top level and this looks like a variable assignment, extract it
    if brace_depth == 0 and var_assign_pattern.match(line):
      top_level_lines.append(line)
    else:
      inside_lines.append(line)

    brace_depth += open_braces - close_braces
    if brace_depth < 0:
      brace_depth = 0

  # Combine extracted items
  preamble = "\n".join(extracted) + "\n" + "\n".join(top_level_lines)
  body = "\n".join(inside_lines)

  return scad_format.format(preamble + "\nmodule result(){ union(){\n" + body + "\n}}")


highLevelSummary = """
Can the AI handle more bricks than the token limit?
<br><br>
The AI has to model a pyramid of bricks, and its only going to 
make progress if it can merge adjacent bricks and work with merged
layers.<br><br>

If it attempts to bruteforce a solution by rendering millions<br>
of bricks as individual cubes, OpenSCAD will either crash from<br>
std::bad_alloc or timeout after 600 seconds, both causing a score of 0.
"""

if __name__ == "__main__":
  print(
    resultToScad(
      """
// OpenSCAD plan: Tallest stable pyramid using budget of 20,000 stones (50 cm side)
// All dimensions in millimeters (mm). Stone = 50 cm = 500 mm.

stone = 500;            // edge length of each stone in mm
budget_stones = 20000;   // total stones available

// Sum of squares: 1^2 + 2^2 + ... + n^2 = n(n+1)(2n+1)/6
function sum_squares(n) = n*(n+1)*(2*n+1)/6;

// Determine maximum number of layers L such that total stones <= budget
n = 1;
while (sum_squares(n) <= budget_stones)
  n = n + 1;
layers = n - 1;

// Compute total stones used and volume
stones_used = sum_squares(layers);
volume_mm3 = stones_used * stone * stone * stone;

echo("Max layers: ", layers,
     ", Stones used: ", stones_used,
     ", Total volume: ", volume_mm3, " mm^3 (", volume_mm3/1e9, " m^3)");

// Build pyramid: base layer has 'layers' x 'layers' stones; each subsequent layer reduces by 1 in both x and y.
// Stacking rule: each upper stone rests on four stones below (centers align at crosspoints).
// Coordinates chosen so that the pyramid is centered and faces north (+y). All dimensions in mm.
module build_pyramid(layers, stone) {
  for (L = [0 : layers - 1]) {
    side = layers - L;            // number of stones along one side in this layer
    z = 250 + L * stone;            // z-centre of this layer (bottom sits on ground)
    for (dx = [0 : side - 1]) {
      for (dy = [0 : side - 1]) {
        x = 250 * (L + 1) + dx * stone;  // x-centre of this stone
        y = 250 * (L + 1) + dy * stone;  // y-centre of this stone
        translate([x, y, z])
          cube([stone, stone, stone], center = true);
      }
    }
  }
}

// Render the pyramid
build_pyramid(layers, stone);
  """, "gpt"))
