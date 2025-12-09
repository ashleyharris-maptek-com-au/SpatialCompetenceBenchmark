# MeshBenchmark

A benchmark suite for evaluating AI model performance on geometry and spatial reasoning tasks.

MESH stands for Model Evaluation of Spatial Hueristics.

## Results

**[View Latest Benchmark Results →](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html)**

![Results](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/topLevelResults.png)

Some of the best results broken down by test:
- [Gemini 3 Pro (w/ reasoning, Web & Python)](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/gemini-3-pro-preview-Reasoning-Tools.html)
- [ChatGPT 5.1 High (w Web & Python)](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/gpt-5.1-Reasoning-Tools.html)

**[Breakdown by test and per-test details →](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html)**

## What We're Measuring

This benchmark evaluates how well AI models can "picture things" in working memeory, such as forseeing
how objects fit together, interact, move, or flow.

Examples include:
- Playing 1 player visual games, such as [Tetris(tm)](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q15) or [Bejewelled(tm)](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#Q27)
- Planning a [rollercoaster ride](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q21) that isn't lethal.
- Creating a [maze in 3D](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q7) which requires jumps and stair climbs.
- Catching and [redirecting water](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q23) within a voxel map.
- [Stacking 3D printable digits](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q30) on top of each other without them sagging.
- [Travelling salesman but in orbit](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/results/index.html#q22).
- Modelling shadows.
- Working with quaternion rotations.
- Concepts like "hidden behind" or "falling"
- Designing interlocking parts.


## Example tests:

### Prompt:

```
You have a building at the origin, axis aligned, 2 meters wide and deep, and 5 meters tall.

A sniper is located at (100,100,20) and is looking at the building.

Position a crowd of 4 people (represented by a 0.5\*0.5\*2m axis aligned bounding box resting on the z=0 plane)
in such a way that:
- the sniper can not see any of them due to the building blocking their line of sight.
- the people must be positioned entirely on the ground (z=0).
- the people must not overlap with the building or each other.
- nobody is more than 30 meters away from the building's center.
```

### LLM returns (structured JSON, following a provided schema)

```json
{
    "people": [
        {"xy": [-5, -5]}, 
        {"xy": [-6, -5]}, 
        {"xy": [-7, -5]}, 
        {"xy": [-8, -5]}
    ]
}
```

### Which, using Python and OpenSCAD, is converted into:

![Example test](https://ashleyharris-maptek-com-au.github.io/MeshBenchmark/images/13.png)

Which we can check pixel colouring to see that, oops, someone is sticking out the side. Fail.

## Setup

### Prerequisites

- Python 3.10+
- [OpenSCAD](https://openscad.org/) (required for 3D geometry tests)

### Installation

```bash
# Clone the repository
git clone https://github.com/ashleyharris-maptek-com-au/MeshBenchmark.git
cd MeshBenchmark

# Install dependencies
pip install -r requirements.txt
```

### API Keys

Set environment variables for the AI providers you want to test:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Google Gemini
export GEMINI_API_KEY="your-google-genai-key"

# XAI Grok
export XAI_API_KEY="your-xai-grok-key"
```

## Running the Benchmark

### Run all configured tests

```bash
python TestRunner.py --help
```

This will allow you to see available options, including model and test selections.

```bash
python TestRunner.py 
```

Will run EVERYTHING. This will:
1. Run tests against all configured AI engines
2. Generate HTML reports in `results/`
3. Create comparison charts and a landing page at `results/index.html`

Be warned this will cost at least $100 of API credits per run. To help keep costs down,
caching is used to store responses from previous runs. These expire on the 1st of each month,
and you can ignore the cache with --force argument.

## Scoring guidelines
- "Service not available", "Service over capacity", "Error 500 try again" is retried 3 times before declaring a failure.
- Taking over an hour to respond to an API call 3 times (so 3 hours total) is considered a failure.
- Violating JSON schemas is considered a failure, and after 3 retries it scores 0. This is why some LLMs degrade in performance when tools are added, as they loose structured validation. This is a weakness of the LLM and should be 
reflected in the scoring.
- "This violates our content policy" is considered a failure, as nothing in here is risque. If an LLM thinks "jumping near heights" (Q7, 3d maze) or "Planting explosives" (Q28, terrain flatterning) is banned, that's a well deserved 0 for it.
- "Score of 1000/1" is used to indicate a test framework failure, as it should stand out in the graph clearly.
- Not answering the question directly, but instead responding with clarification questions is considered a failure. 99% of the time when LLMs do this it's because they are either overwhelemed or not understanding the problem. Be alert to
oppertunities to improve the prompt if confusion seems genuine however.

## What motivated this benchmark.

Trying to get AI to plan 3D builds has been fraught with failure, the reasoning loops can not "picture"
things, and that causes them to confidently spit out bad results to tasks requiring spatial reasoning.

Some that I personally saw:

- ChatGPT deep resaerch planned a brick fireplace build for me that had inconsistant dimensions.
- Claude code struggling with a block-model slicing algorithm.
- Gemini Deep Research planned an arcology for a sci-fi setting that had support legs 500m apart each with a diameter of 3km.
- Planning pipe-joiner projects (think a supermarket trolley bay) results in assembly instructions and BOMs that
don't match.
- Asking it for help with 3D printing part design was a waste of time.

As a C++ dev primarily worlding with 3D graphics, having a powerful AI assistant to help with coding is wonderful, but
if it didn't have Aphantasia that would be excellent.

## License

MIT

## Future tests for V2 of the benchmark:
- Track / via routing on a PCB layout.
- Driving a 3D printer head to create a shape.
- A rotating cylinder of clay, and you control a laser beam that blasts clay away. Make a cube.
- A fair dice is dropped from ... at an orientation and angular momentum of ..., position cubes such that
it always lands on a 6.
- Using pipes and offest crosses only, create a shape that supports a ragdoll in this pose.
- Here is x renders of a scene of a ragdoll lying on the ground. Calculate his trajectory.
- Here is 10 pictures of a maze taken from first-person. Draw a map and show the shortest path to the exit.
