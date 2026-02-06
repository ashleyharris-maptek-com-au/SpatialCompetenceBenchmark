title = "Essay section"
skip = True
questions = [{
  'question':
  """
We are designing a file format for 3D data that's the result of a laser scan used by to
survey infastructure, buildings, streets, and other parts of modern life.

The laser scanner consists of two rotating mirrors, one high speed (600rpm) that sweeps
vertically, returns data from -80 degrees to + 80 degrees, and one slow speed that
rotates in arcs up to a full 360 degrees, and as slow as 1rph. 

The laser beam will impact objects in the scene and, for each beam, return an unknown
number of returns. 
- Laser beams that shoot off into the atmosphere do not return.
- Beams that hit a solid object respond with a signal value, representing the
  albedo and normal of the impacted surface.
- Beams can return multiple hits, when impacting surfaces like glass, water, fog,
  foilage, mirrors, dust, smoke, etc.

Image data is also captured in RGBA format using a spherical mirror mounted on the
same axis as the laser scanner, each 2x2 cell of beams contains 1 or more pixels
of RGB data.

Scanner position is fixed 90% of the time, but it can be mounted to a moving 
vechile for rapid data acquisition and the origin is kept updated via GPS.

A/D encoder resolution is 12 bits for returned beam signal strength, 16ghz for times,
and 20 bits for azimuth and elevation angles. Data loss within these limits is acceptable,
and desirable for compression. Data loss exceeding this limits is not desirable.

The user can set the capture rates based on their needs for speed vs quality. On board computer is quite powerful
and for the purpose of this exercise has infinite processing capability.

We're design a file format that can store this data as optimally as possible. Since the
file is immutable once written, care should be taken to ensure that the file is
as compact as possible. Optimising for typical use cases is what will help us get
an edge over the competition. Scan files can be expected to be 100s of millions of beams,
with 100s of billions not being unheard of.

Write a report of at least 300 words suggesting all potential optimisations for this file format, both wise and
unwise, and justify your chocies for which to adopt.
""",
  "good": [
    "Chunk or otherwise split the data in in a coherent way?",
    "Seperate the arrays of RGBA image data from the arrays of beam data (ideally within chunk)?",
    "Optimisation for flat surfaces when encountered?", "Store in polar form when possible?",
    "Store fixed resolution angle data tightly packed - using bit packing to 20-bits?",
    "Store beam strenghths at 12-bits or better. Eg 2 returns-per-3-bytes, or deltas?",
    "Optimise for 0 or 1 returns, with secondary being rare but handled?",
    "Store secondary beam impacts as a delta from the first return?",
    "Store x data less freqeuntly than y, as scanlines are running vertically?",
    "Realise the vertical scanlines are fractionally tilted, and stores that speed?",
    "Compress the image data using any establish image compression algorithm?",
    "Post process the file through a common compression algorithm like zlib, zstd, lzma2 or algorithmic coding?",
    "Use a streaming / block based compression algorithm to allow fast seeking of the file?",
    "Store y implicitly or as a delta from expected?",
    "Allow image data to be stored for missing beams?",
    "Store a thumbnail, low res preview, or part of the data at the start to allow for fast load or preview?",
    "Optimise for the common case when ranges of adjacent beams are likely similar?",
    "When motion happens, store the path seperately to keep polar form?",
    "Store like data with like data, ie structure of arrays is better than array of structures?"
  ],
  "bad": [
    "Store data in cartessian coordinates?",
    "Voxelise the data?",
    "Store distances in meters?",
    "Store distances in floating point seconds?",
    "Per-beam variable-length record structure?",
  ]
}]

structure = None


def prepareSubpassPrompt(index):
  if index == len(questions): raise StopIteration

  return questions[index]["question"]


grading = [[None]]


def gradeAnswer(answer: str, subPass: int, aiEngineName: str):
  import LLMBenchCore.CacheLayer as cl

  print(answer)

  if len(answer) < 1500:
    return 0, "Answer was too short. Expected at least 1500 characters for a 500 word report."

  structure = {
    "type": "object",
    "properties": {
      "mentioned": {
        "type": "boolean",
        "description": "Whether the idea was mentioned"
      },
      "recommended": {
        "type":
        "boolean",
        "description":
        "Whether the idea was recommended as a good idea (true) or rejected as a bad idea (false). "
      }
    },
    "required": ["mentioned", "recommended"],
    "additionalProperties": False,
    "propertyOrdering": ["mentioned", "recommended"]
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

  grading[subPass] = []
  recommendedGoodIdeas = 0
  mentionedGoodIdeas = 0
  recommendedBadIdeas = 0
  mentionedBadIdeas = 0

  for idea in questions[subPass]["good"] + questions[subPass]["bad"]:
    prompt = "Read the following report: ```" + answer + "\n```\n\n" + \
        "According to that report: Is the idea '" + idea + "' mentioned, and is it recommended?" + """

An idea can be considered recommended even if that recomendation is classed as future work, not urgent, 
optional, or conditional on the readers own experimentation.


An idea can be considered mentioned even if exact keywords don't appear, so long as there is evidence 
the idea was considered.

If you are unsure, answer False, False."""

    result = answerQuestion(prompt)

    if "mentioned" not in result or "recommended" not in result:
      print("WARNING: Grading while offline / missing grader AI. Inaccurate grading.")
      grading[subPass].append({
        "idea": idea,
        "mentioned": False,
        "recommended": False,
        "goodIdea": idea in questions[subPass]["good"],
        "scoreDelta": 0
      })

    grading[subPass].append({
      "idea": idea,
      "mentioned": result["mentioned"] if "mentioned" in result else False,
      "recommended": result["recommended"] if "recommended" in result else False,
      "goodIdea": idea in questions[subPass]["good"],
      "scoreDelta": 0
    })

    if grading[subPass][-1]["goodIdea"]:
      if grading[subPass][-1]["recommended"]:
        grading[subPass][-1]["scoreDelta"] = 1
        recommendedGoodIdeas += 1
      elif "mentioned" in grading[subPass][-1] and grading[subPass][-1]["mentioned"]:
        grading[subPass][-1]["scoreDelta"] = 0.5
        mentionedGoodIdeas += 1
    else:
      if grading[subPass][-1]["recommended"]:
        grading[subPass][-1]["scoreDelta"] = -1
        recommendedBadIdeas += 1
      elif "mentioned" in grading[subPass][-1] and grading[subPass][-1]["mentioned"]:
        grading[subPass][-1]["scoreDelta"] = 1
        mentionedBadIdeas += 1

    print(grading[subPass][-1])

  score = 0
  for g in grading[subPass]:
    score += g["scoreDelta"]

  return score / len(
    questions[subPass]["good"] + questions[subPass]["bad"]
  ), f"{recommendedGoodIdeas} recommended good ideas, {mentionedGoodIdeas} mentioned good ideas, {recommendedBadIdeas} recommended bad ideas, {mentionedBadIdeas} mentioned bad ideas."


def resultToNiceReport(answer, subPass, aiEngineName):
  table = "<table><tr><th>Idea</th><th>Mentioned or Recommended</th><th>Scorecard</th></tr>"
  for grades in grading[subPass]:
    table += "<tr>"
    table += "<td>" + grades["idea"] + "</td> "
    if grades["goodIdea"] and grades["recommended"]:
      table += "<td style='color: green;'>Good Idea Recommended</td> "
    elif grades["goodIdea"] and grades["mentioned"]:
      table += "<td style='color: yellow;'>Good Idea Mentioned but not recommended</td> "
    elif not grades["goodIdea"] and grades["recommended"]:
      table += "<td style='color: red;'>Bad Idea Recommended</td> "
    elif not grades["goodIdea"] and grades["mentioned"]:
      table += "<td style='color: green;'>Bad Idea Mentioned and NOT recommended</td> "
    else:
      table += "<td style='color: yellow;'>Not mentioned</td> "
    table += "<td>" + str(grades["scoreDelta"]) + "</td>"
    table += "</tr>"
  table += "</table>"

  return table


highLevelSummary = """
This gets an LLM to write an essay or report, and then uses another LLM to grade it against
expected discoverys and insights. This relies on an LLM to be good enough to read an essay
and answer a simple question about it - most are good enough for this.<br><br>

For each essay topic, the marking guide contains a list of 'good' and 'bad' ideas.<ul>
<li>For mentioning a 'good' idea, an LLM gets +0.5</li>
<li>For recommending a 'good' idea, an LLM gets another +0.5.</li>
<li>For mentioning a 'bad' idea and recommending it, an LLM gets - 1.</li>
<li>For mentioning a 'bad' idea and recommending against it, an LLM gets +1</li>
<li>Score is graded as a fraction out of len(good) + len(bad), clamped at 0.</li>
</ul><br><br>

Icon was made by ChatGPT 5.2, and I think it's just cringy enough to be hilarous.
"""
