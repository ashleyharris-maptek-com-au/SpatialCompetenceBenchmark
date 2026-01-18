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
  import LLMBenchCore.CacheLayer as cl, re, scad_format

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
    from LLMBenchCore.AiEngineGoogleGemini import GeminiEngine
    engine = GeminiEngine("gemini-2.5-flash-lite", False, False)
    cacheLayer = cl(engine.configAndSettingsHash, engine.AIHook, "gemini-2.5-flash-lite")

    def answerQuestion(q: str) -> dict:
      return cacheLayer.AIHook(q, structure, -1, -1)[0]

  else:
    from LLMBenchCore.AiEngineOpenAiChatGPT import OpenAIEngine
    engine = OpenAIEngine("gpt-5-nano", False, False)
    cacheLayer = cl(engine.configAndSettingsHash, engine.AIHook, "gpt-5-nano")

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
  if "primitiveCount" in inspectionResult and inspectionResult["primitiveCount"] > 1000:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("Aborting due to " + str(inspectionResult["primitiveCount"]) + " parts!")
    return "module result(){linear_extrude(0.1) text(\"Aborting due to " + str(
      inspectionResult["primitiveCount"]) + " parts!\");}"
  elif "primitiveCount" in inspectionResult and inspectionResult["primitiveCount"] > 200:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("This is dubious and might break your machine, but we'll try.")
  elif "primitiveCount" in inspectionResult:
    print("AI estimation of primitive count: " + str(inspectionResult["primitiveCount"]))
    print("Seems safe to continue.")
  else:
    return "module result(){linear_extrude(0.1) text(\"LLM failed to "\
      "estimate part count.\\nCheck both OpenAI and Gemini API tokens!\");}"

  if result.count("```") == 2:
    result = re.split(r"```[^\n]*\n?", result)[1]
    # Also remove the closing ``` marker
    if result.rstrip().endswith("```"):
      result = result.rstrip()[:-3]

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
```openscad
// Pharaoh's Pyramid Construction Plans
// Specifications:
//   - 20,000 stones available (500mm cubes)
//   - 19,019 stones used
//   - 38 layers
//   - Height: 19,000mm (19 meters)
//   - Base: 19,000mm × 19,000mm square
//   - Orientation: North face aligned with +Y axis

stone_size = 500; // millimeters
n_base = 38;      // base layer is 38×38 stones

// Smooth marble facade (final external surface)
module smooth_pyramid() {
    base = n_base * stone_size;    // 19,000mm
    height = n_base * stone_size;  // 19,000mm
    
    polyhedron(
        points = [
            [-base/2, -base/2, 0],  // 0: Southwest corner
            [base/2, -base/2, 0],   // 1: Southeast corner
            [base/2, base/2, 0],    // 2: Northeast corner
            [-base/2, base/2, 0],   // 3: Northwest corner
            [0, 0, height]          // 4: Apex
        ],
        faces = [
            [0,1,2,3],  // Base
            [0,1,4],    // South face
            [1,2,4],    // East face
            [2,3,4],    // North face (+Y)
            [3,0,4]     // West face
        ]
    );
}

// Internal stepped stone structure
module stepped_pyramid() {
    for (L = [0:n_base-1]) {
        layer_size = n_base - L;
        translate([0, 0, L * stone_size + stone_size/2])
            cube([layer_size * stone_size, layer_size * stone_size, stone_size], center=true);
    }
}

// Render marble facade
color("white", 1.0)  
    smooth_pyramid();

// Render internal structure
color("sandybrown", 0.4) 
    stepped_pyramid();
```
  """, "claude-opus-4-5"))
