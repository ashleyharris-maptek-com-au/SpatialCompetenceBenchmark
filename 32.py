skip = True

title = "Essay section"

highLevelSummary = """
This gets an LLM to write an essay or report, and then uses another LLM to grade it against
expected discoverys and insights. This relies on an LLM to be good enough to read an essay
and answer a simple question about it - most are good enough for this.

For each essay topic, the marking guide contains a list of 'good' and 'bad' ideas.
- For mentioning a 'good' idea, an LLM gets +0.5
- For recommending a 'good' idea, an LLM gets another +0.5.
- For mentioning a 'bad' idea and recommending it, an LLM gets - 1.
- For mentioning a 'bad' idea and recommending against it, an LLM gets +1
- Score is graded as a fraction out of len(good) + len(bad), clamped at 0.
"""

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

Write a report suggesting all potential optimisations for this file format, both wise and
unwise, and justify your chocies for which to adopt.
""",
    "good": [
        "Chunk or otherwise split the data in in a coherent way?",
        "Seperate the arrays of RGBA image data from the arrays of beam data (ideally within chunk)?",
        "Optimisation for flat surfaces when encountered?",
        "Store in polar form when possible?",
        "Store fixed resolution angle data tightly packed - using bit packing to 20-bits?",
        "Store beam strenghths at 12-bits or better. Eg 2 returns-per-3-bytes, or deltas?"
        "Optimise for 0 or 1 returns, with secondary being rare but handled?",
        "Store secondary beam impacts as a delta from the first return?",
        "Store x data less freqeuntly than y, as scanlines are running vertically?",
        "Realise the vertical scanlines are fractionally tilted, and stores that speed?",
        "Compress the image data using any establish image compression algorithm?",
        "Post process the file through a common compression algorithm like zlib, zstd, lzma2 or algorithmic coding?",
        "Use a streaming / block based compression algorithm to allow fast seeking of the file?",
        "Store y implicitly or as a delta from expected?",
        "Allow image data to be stored for missing beams?",
        "Store a thumbnail, low res preview, or part of the data at the start to allow for fast load or preview?"
        "Optimise for the common case when ranges of adjacent beams are likely similar?",
        "When motion happens, store the path seperately to keep polar form?",
        "Store like data with like data, ie structure of arrays is better than array of structures?"
    ],
    "bad": [
        "Store data in cartessian coordinates?",
        "Voxelise the data?",
        "Store distances in meters, or floating point seconds?",
    ]
}]

structure = None


def prepareSubpassPrompt(index):
    if index == len(questions): raise StopIteration

    return questions[index]["question"]


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
    return 0, "NYI"


def resultToNiceReport(answer, subPass, aiEngineName):
    return "<p>NYI</p>"
