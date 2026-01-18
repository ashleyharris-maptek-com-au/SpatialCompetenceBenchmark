# Can an AI Navigate via the Stars?

## Abstract

Celestial navigation - determining one's latitude and longitude from observations of stars - is a millennia-old skill now rarely practiced thanks to GPS. We investigate whether modern Large Multimodal Models (LMMs) can revive this art: given a single annotated image of the night sky (with horizon and cardinal directions) and the exact UTC time, can an AI infer its position on Earth? We construct a benchmark of 49 sky observations (7 oceanic locations × 7 dates/times) using a physics-based sky renderer, and evaluate several state-of-the-art LMMs (including ChatGPT-5.2, Google Gemini 3 Pro, Anthropic's Claude Opus 4.5, Alibaba's Qwen VL 235B, Amazon's Nova Premier, XAI's Grok 4, etc.) under different reasoning and tool settings. We also implement a high-accuracy solver as a "human with tools" baseline.

The analytical baseline achieves near-perfect localization (median error ~100 m) under ideal conditions, consistent with prior celestial navigation models. In stark contrast, LMMs without tool-use struggled - typically only guessing the correct hemisphere or quadrant of the globe. Even with chain-of-thought reasoning and web search and code tools enabled, the best LMM achieved passable accuracy on only ~15% of trials. We document common failure modes: improper outputs, hallucinated heuristics (e.g. over-reliance on ambient temperature), inability to resolve faint star patterns due to limited visual resolution, and tool-use sandbox limitations. Our findings highlight that today's LMMs, despite impressive language and vision capabilities, **lack the precise world-model needed for celestial navigation**. Successful localization required explicit computation with an accurate model of Earth's sky - something current LMMs can only partially invoke via tools. These results stress the importance of integrating physical domain knowledge and robust tool-use into world models for solving scientific reasoning tasks.

## Introduction

Long before GPS satellites, mariners determined their ship's position using sextants, star charts, and precise timepieces - the craft of celestial navigation. By measuring star altitudes and using almanac tables, a skilled navigator can fix latitude and longitude to within a few kilometres. Modern research has pushed this accuracy to the order of ~100 meters using automated vision systems and horizon detection. This renewed interest is partly driven by concerns over GPS vulnerability to jamming/spoofing, motivating alternative positioning methods. Determining position from a single night-sky image remains a challenging problem requiring a detailed model of Earth's rotation, star positions, and atmospheric effects. Simultaneously, large multimodal models (LMMs) have emerged that combine language understanding with image processing and tool use. Models like ChatGPT-5.2, Gemini 3, Grok 4, and others have demonstrated the ability to interpret images and perform complex reasoning when augmented with external tools.

Such models have been described as building "world models" - internal representations of the environment - enabling them to solve spatial and temporal reasoning tasks. However, most benchmarks so far focus on everyday images (landmarks, objects) or general QA. Celestial navigation poses a uniquely stringent test of an AI's world model: it requires understanding the correspondence between star configurations and geographic coordinates, essentially inverting an astronomy model. The necessary knowledge (star catalogue positions, Earth's orientation at a given time) is highly precise and unlikely to be fully memorized from text training data. Thus, success may hinge on the model's ability to use tools or calculations - effectively consulting an internal planetarium or ephemeris. In this work, we ask: ***Can advanced LMMs, given a single clear view of the night sky and exact time, figure out where they are on Earth?*** To explore this, we created a benchmark with synthetic "night sky" images generated for known locations and times. We evaluate a range of cutting-edge LMMs under different conditions: direct "one-shot" response, chain-of-thought reasoning, and with code execution tools that give access to astronomical computations. We also compare against an algorithmic solver written by the author.

This study is conducted solely by the author, who developed the entire benchmark, solver implementation, and evaluation framework.

Contributions:

1. We introduce a novel evaluation of world-modelling in LMMs via a realistic celestial navigation task, relevant to safety-critical navigation domains.
2. We present comprehensive results on ~50 test scenarios, covering multiple models and tool-use settings, revealing a significant performance gap between AI and an analytical baseline.
3. We analyse failure modes and discuss why current models fall short, highlighting areas for improvement in multimodal reasoning and tool integration.

## Methods

### Benchmark Design and Data Generation

#### Test Locations and Times

We selected 7 ocean locations in the Pacific, far from large landmasses (to avoid trivial clues like coastline patterns). Their latitudes ranged from about 56°S to 53°N (both hemispheres) and longitudes ranged across the Pacific (roughly 130°E to 170°W). To represent different seasons and sky orientations, we chose 7 observation times spanning dates in November-December 2025 at various UTC hours. Each location-time pair defines a unique celestial sphere orientation. In total this yields $7\times7 = 49$ distinct test cases.

#### Sky Image Generation

For each test case, we rendered a full hemispherical sky image (zenith-centered) using an accurate astronomically-driven simulator. We used the Hipparcos star catalogue (≤6.0 apparent magnitude) and JPL DE421 ephemerides for planets. The rendering code computes the exact altitude and azimuth of every visible star and major planet as seen from the given latitude/longitude and time (accounting for Earth's rotation, axial tilt, gravitational lensing, and refraction adjusting for temperature and barometric pressure). Stars are plotted as filled circles with brightness and radius scaled by their magnitude (dimmer stars appear smaller/fainter). The projection is stereographic, as if captured with a fisheye lens, with the horizon drawn as a green circle and cardinal directions (N,S,E,W) labelled at the edges. Figure 1 shows an example sky image from the dataset. Each image is $8192\times8192$ pixels (~65 megapixels) to ensure even faint stars (mag 5-6) are visible when zoomed; our images contain on the order of 2500 stars visible, matching a human eye at peak performance. Planetary bodies (e.g. Venus, Jupiter), as well as the moon are also drawn if above the horizon, in distinct colours and proportionally sized ellipses. The image is oriented such that north is up and east is right, matching conventional azimuth bearings. We thus provide the model with a rich and information-complete view of the night sky, analogous to what a skilled navigator would see with a labelled star chart. Along with the image, we supply the exact date and time in UTC as text.

#### Prompt to LMMs

The query posed to models is a short scenario: "You are a navigator on a ship in the middle of the Pacific Ocean. Your GPS has failed, but you can see the stars clearly..." and instructs the model to determine latitude and longitude from the attached sky image. The prompt explicitly notes that the image is oriented (zenith at center, north at top) and gives some environmental context: e.g. "dawn is far away and has been dark for hours" (to indicate it's the middle of the night), and "TEMP degrees Celsius outside" (inserting a temperature value that corresponds to that location's typical climate). It also includes a sentence about visible planets: e.g. "Jupiter and Saturn are visible" or "No planets nor the moon are visible." This extra information was provided to mimic what a human might note (bright celestial bodies can be helpful reference points). All this text is concatenated, and the sky image is attached in the model's multimodal input. The model must output its answer in a structured JSON format with two keys: "latitude" and "longitude", given as numbers (in decimal degrees).

### Models Evaluated

We evaluated a slate of advanced LMMs available in late 2025, spanning multiple AI labs and differing scales, under various inference modes:

**GPT-5 family (OpenAI)**: We tested 5 models from OpenAI: gpt-5-nano, gpt-5-mini, gpt-5.1, gpt-5.2 and gpt-5.2-pro (build 2025-12-11).
**Gemini family (Google)**: We tested 3 models from Google: gemini-2.5-flash-lite, gemini-2.5-flash, and gemini-3-pro-preview (release November 2025).
**Anthropic Claude family (Anthropic)**: We tested 2 models from Anthropic: claude-sonnet-4.5 and claude-opus-4.5.
**Grok family (XAI)**: We tested 3 models from Grok AI: grok-2-vision-1212, grok-4-1-fast, and grok-4-0709
**Qwen family (Alibaba)**: We tested 2 models from Alibaba : qwen3-32b-v1:0 and qwen.qwen3-vl-235b-a22b.
**Llama family (Meta)**: We tested 2 models from Meta: llama3-70b and llama3-1-405b.
**Mistral family (Mistral AI)**: We tested mistral-large-3-675b-instruct
**Nova family (Amazon):** We tested 3 models from Amazon: nova-lite, nova-pro, and nova-premier

These models accept image+text input and generate text. We invoked each model in a standard completion mode (direct answer) and a "HighReasoning" mode where the model is allowed to produce chain-of-thought (CoT) reasoning (which is hidden from the final answer) to reason step-by-step, and this was set to the maximum allowed in their respective API documentation. Additionally, -Reasoning-Tools mode allowed the model to execute Python code via a sandbox (to perform calculations or image analysis), and search /browse the internet.

For each model and mode, we attempted the full suite of 49 test cases. However, to manage cost and time, we employed an early-stopping heuristic during testing: if a model performed very poorly on the first 3 cases (average score below 0.20, essentially failing to get even hemispheres correct), we halted further runs for that model to conserve resources. In such cases, only 3 data points were collected. Models that showed at least minimal proficiency proceeded to solve all 49 cases.

### Analytical Baseline (the "Human with tools" LMM)

In addition to the LMMs, we implemented a deterministic solver to serve as an upper-bound benchmark. This solver uses a multi-step algorithm that mimics how a novice navigator with access to computational tools might approach the problem.

1. Pre-calculation: Starting with a coarse grid (2° cells) covering plausible areas (the scenario says "middle of Pacific Ocean", which we interpret as roughly 40°S-50°N, 100°E-100°W for initial guess space), for every star potentially visible, the solver pre-calculates the altitude/azimuth angle at which it would be visible at the given temperature, pressure, time, and coordinates. This allows for fast linear interpolation later. This calculation takes about 15 minutes, is written in mildly optimised single threaded python, and produces about 350mb of data.

2. Star Detection: The solver reads the generated sky image and identifies star positions and brightness. We applied image processing (thresholding and connected-component labelling using SciPy) to extract the pixel coordinates of each star in the image, converting back to altitude/azimuth angles. This yields a list of observed stars with their alt-az positions and approximate magnitudes. This process was surprisingly accurate, often to an arcminute, with the exception of errors caused by adjacent or overlapping bodies / stars.

3. Grid search. For each grid point (2°x2°), we compare the ~20 brightest stars in our hypothetical sky against what was decoded from the image, using a 5° binned grid for fast lookup. We score based on distance error between stars of the same magnitude, calculating a simple average error.

4. Beam walk. The we select the best-matching 100 grid points and search around them with finer spacing,
sampling dozens of points within a few degrees of the best-matching grid points. We repeat this process,
discard, gradually discarding the worst-matching beams, adding dimmer stars, and shrinking our random search radius.

5. Hill climb. Finally, run a local optimization (hill-climbing) to converge to a precise coordinate, we also switch our scoring heuristic to allow discarding of a few outliers (as image-decode introduces a few false stars) stopping when adding stars no longer improves the match or the step size becomes very small (~.00001°)

6. Output: The solver yields the latitude/longitude that best fits the observed sky. We found this method typically converged within 10 minutes.

This baseline effectively has complete knowledge of the physics (it uses the same star catalogue used to create the image) - representing what is achievable if one perfectly "understands" the problem and has sufficient computation. It achieved very high accuracy, as we will show. The author developed this solver and verification code from scratch, ensuring that the evaluation is fair and that the ground truth is known precisely.

### Evaluation Metrics

We evaluate model answers primarily by geographic error and a derived score. Given the model's guessed latitude and longitude, we compute the great-circle distance to the true location (using the haversine formula). We also break down error into latitude error (degrees) and longitude error, and note if the guess got the hemisphere (N vs S) correct and the "side" of the prime meridian/international date line (E vs W) correct. The performance is summarized with a score from 0.0 to 1.0 defined as follows:

+0.1 for correct hemisphere (N/S).
+0.1 for correct East/West half (relative to 0° or 180° meridian).
+0.1 for latitude error < 10°,
+0.1 for longitude error < 10°.

If all above four are correct (score = 0.4 so far), then additional credit is assigned on a log-scale of the great-circle distance error: an error < 10 km yields a full 1.0 score, <100 km → 0.9, <1000 km → 0.8, <10,000 km → 0.7, <~half Earth (20,000 km) → 0.6. In essence, a model gets 0.4 for nailing the right general quadrant of the globe, and the remaining 0.6 is scaled by how close within that quadrant the guess is (with 1.0 meaning essentially a direct hit within ~10 km).

This scoring system reflects the task's difficulty - even a rough placement on the correct side of Earth earns 0.2-0.3, while 0.8+ indicates near-exact position. We report aggregate statistics like average score, full success rate (score=1.0), and median error distance for each model. All results were logged to a CSV file for analysis, including each model's guess and errors for every test case.

## Results

### Baseline Solver Accuracy

The "Human with tools" baseline performed exceedingly well. It successfully localized all 49/49 test cases to essentially near-perfect accuracy (often sub-kilometer error). The median great-circle error was 0.06 km (about 60 meters), and 75% of cases were solved within 200 m. In 48 out of 49 cases, the solver's error was below 10 km, giving it a score of 1.0 on those; in one difficult case with fewer visible stars, it achieved ~15 km error, scoring 0.9. Overall the baseline's average score was 0.984, essentially demonstrating that the benchmark is solvable with precise computations. This aligns with prior work in astronomical navigation which reported ~100 m accuracy under good conditions. We thus treat this solver's outputs as ground-truth for evaluating the LMMs - it confirms that the information present in the image + time is sufficient to yield an unambiguous fix in all cases.

### LMM Performance Overview

Table 1 summarizes the performance of selected LMMs on the benchmark. We report the average score, the percentage of test cases with full success (score = 1.0, i.e. error < ~10 km), and the median error distance. Models are grouped by family and whether they had tool use enabled.

Table 1. Performance of AI models on 49 celestial navigation cases. (LMM = large multimodal model; "CoT" = chain-of-thought reasoning allowed; "Tools" = code execution tools enabled. All models received the same sky image and time info.)

Model & Setting | Avg. Score (0-1) | Full Success (100% correct) | Median Error (km)
--- | --- | --- | ---
Human (solver baseline) | 0.984 | 98% (48/49) | 0.06 km
GPT-5.2 LMM + CoT + Tools | 0.64 | 14% (≈7/49) | 254 km
GPT-5.2 LMM + CoT (no tools) | 0.24 | 2% (1/49) | 3,484 km
GPT-5.1 LMM + CoT + Tools | 0.44 | 0% (0/49) | 2,505 km
GPT-5.1 LMM + CoT (no tools) | 0.24 | 2% (1/49) | 3,164 km
GPT-5-mini LMM + CoT + Tools | 0.29 | 2% (≈1/49) | 4,723 km
GPT-5-nano (no reasoning, no tools) | 0.10 | 0% | 6,397 km
Google Gemini-3 (preview) + Tools | 0.50 | 0% (0/49) | 643 km
Google Gemini-2.5 + Tools | 0.20 | 0% | 5,117 km
Anthropic Claude-Opus + Tools | 0.25 | 0% | 3,182 km
Anthropic Claude-Opus (no tools) | 0.20 | 0% | 3,476 km
Qwen-VL 22B + Tools | 0.18 | 0% | 5,198 km

(Other models not shown had score <0.2 and 0% success.)

The median error is the 50th percentile great-circle distance error across all attempts (lower is better). Several clear trends emerge from these results:

No model approaches human/solver accuracy. The best LMM (GPT-5.2 with tools) achieves an average score of 0.64, which is far below the baseline's 0.98. In terms of distance, GPT-5.2+Tools had a median error of ~254 km - four orders of magnitude larger than the baseline's median 0.06 km. Figure 2 (a) shows the distribution of errors: even the best model only occasionally comes close (its best-case errors were on the order of 5-10 km, but worst-case were thousands of km off).

Tool use dramatically improves performance (for those models able to use it). For instance, GPT-5.2 without tools (only reasoning) averaged 0.24 score, vs 0.64 with tools - a substantial jump. It also went from only 1 successful case (out of 49) to about 7 successes with tool assistance. A similar boost is seen for GPT-5.1 (0.24 → 0.44 avg). This validates the hypothesis that external computation is necessary: when the LMM can call Python functions to help solve geometry or parse the star field, it does better. However, even with tools, the performance is a fraction of the baseline's. The tools clearly helped prevent complete failures but did not guarantee full accuracy (most tool-using models still had many errors of hundreds of km).

Larger models outperform smaller ones (within the same family/condition). GPT-5.2 > GPT-5.1 > GPT-5-mini > GPT-5-nano in descending order of size correlate with descending performance. GPT-5-nano (a very small model) was essentially guessing (avg score 0.1, often just outputting something like "0°N, 170°W" for lack of knowledge). The smallest models often didn't even get hemisphere right more than chance. Meanwhile GPT-5.2 (presumably with tens of billions of params and trained on multimodal data) had the best intuition and was the only one to sometimes pinpoint the location exactly. This suggests that model scale and training are crucial for any non-trivial success in this task - smaller models simply lack the factual or reasoning capacity needed.

GPT 5.2-pro does not have the capability to execute code, explaining why 5.2-pro performed worse than 5.2. It did have access to web browser, which it was able to use to find web tools for calculating planet positions and was able to use that guesstimate effectively.

Differences across AI providers: Among non-OpenAI models, we observe some competence but generally lower. Google's Gemini-3 preview with tools scored around 0.5, indicating it was able to narrow down location to a few hundred km on those attempts (it notably got one case ~120 km away, score 0.8). Gemini was observed executing code that seemed to run until timing out. Anthropic's Claude-opus with tools managed ~0.25 average, better than chance but no perfect fixes. Alibaba's Qwen-VL (22B) was around 0.18, barely above the threshold of not failing early. These discrepancies could stem from differences in vision capabilities or training: OpenAI's models might have seen more astronomy knowledge in training or have better fine-grained image understanding. None of the non-GPT models achieved any score=1.0 cases in our evaluation.

"High reasoning" (chain-of-thought) vs direct: We gave all models the ability to produce intermediate reasoning text. Interestingly, this alone (without code tools) did not dramatically improve accuracy for most. It helped slightly in some cases (e.g., GPT-5.1 got one answer fully correct in HighReasoning mode whereas it got none in strict mode). But generally, without actual computation or external knowledge, the reasoning often led the model to qualitatively correct conclusions (like correctly identifying a constellation or deducing the hemisphere) but still insufficient for precise coordinates. In other words, a model might reason "I see the Big Dipper low on the horizon, so I'm likely in the northern mid-latitudes," which is true and earns partial credit, but that alone can't yield a specific longitude and latitude. Score-wise, many reasoning-enabled runs ended with 0.2-0.3 (correct hemisphere and maybe roughly right latitude band) but not beyond. This suggests that while chain-of-thought is necessary for complex tasks, it must be coupled with either retrieval or calculation to solve a problem requiring numerical precision or extensive factual recall.

To better visualize performance, Figure 2(b) plots cumulative distribution of error distances for three representative models vs the baseline. The baseline (Human with tools) curve jumps to 100% of cases solved within ~20 km. GPT-5.2+Tools (best LMM) rises more slowly: about 20% of its cases are within 50 km, ~50% under 500 km, and then it plateaus (some outliers around 4000+ km error). GPT-5.2 without tools lags further, with the majority of its guesses over 1000 km off. This illustrates that current LMMs, even the best, frequently make order-of-magnitude larger errors than a dedicated solver.

## Qualitative Analysis of Model Behaviours

We inspected transcripts and outputs from the LMMs to understand how and why they failed. Several consistent failure modes and challenges were observed:

### Broken or Non-Compliant Output

Many models struggled to produce a clean JSON with just latitude/longitude. Often, they would insert commentary or degree symbols, or format numbers incorrectly, leading to invalid answers. We used 'structured output' where available as an LLM feature, but this was not always supported or was
incompatible with tooling. We used published workarounds where possible (including function calling and
two-pass prompting). We were forgiving of these errors, allowing LLMs to retry up to 3 times, however many failed 3 times in a row getting a 0.

Examples:

> {"latitude": -35.0, 0000, "longitude": -160.00000}

> {"latitude": 15, **longitude": -155}

> {"latitude": -25,longitude": -115}

### Answering with "Do you want me to solve this?"

Many models CoT would realise they were unable to answer the problem, were running short on reasoning time, and would phrase their failure as asking permission to solve the problem. Text to the effect of "I should ask the user 'Would you like me to conduct a thorough analysis of this image to find your location?'" would often appear in the CoT of a struggling model. This would result in the 'answer' being prepared for the user being a request to answer the question, and then struggling to fit such a question into 2 number fields.

Any competent human, upon seeing the format required for their answer is not free text, would realise that yes, they should try to answer it. Nobody writes "Do you want me to look in a dictionary?" in really small print to answer a crossword puzzle with space for 4 letters.

### Heuristic Guessing and Hallucinations

Without the ability to truly calculate positions, models often resorted to heuristic guesses or outright fabrications. A common example was misinterpreting the provided temperature (included for accurate atmospheric refraction modelling) as latitude information. The model essentially hallucinated a climate heuristic ("warm night implies low latitude") and overruled the star data, leading to large latitude errors.

"Middle of the ocean" was also sometimes taken literally, with CoT devoted to finding the
exact middle point of the pacific ocean. At least one session a LMM threw away a decent calculation
because the result was 200km away from the Kamchatka peninsula, and that wasn't 'the middle of the ocean' enough.

### Constellation focus

Anthropic and OpenAI model's CoT both included discussion of constellations visible in the image, often correctly identifying them, however this was not a useful aspect of the problem. The models were not able to use the constellations to calculate positions, and instead would often use them as a basis for heuristic guessing or hallucination.

Assuming (incorrectly) that either Polaris or Southern Cross must be always visible confused at least 1 test case. There was a test location (at 11.1° south) in which Polaris was permanently below the horizon, and the Southern Cross was below the horizon for half the night, resulting in neither being visible.

Other models incorrectly identified constellations leadingly to wildly incorrect guesses. Polaris was "seen" from the southern hemisphere. The "Southern Cross" was seen from 52° north but the LLM was unable to locate its corresponding pointer pair (needed in conjunction with the cross for finding the south celestial pole, not relevant to this task, but mentioned frequently in star navigation courses.)

The models likely never saw such dense star charts during training. Without explicit astrometry calculations, these identifications did not translate to precise coordinates.

### Limited Visual Resolution and Overload

We experimented with image resolutions from 256x256 to 16384x16384 (250 megapixels) before settling on 8192x8192 for the test. Amazon Bedrock (hosting Nova, Mistral, Llama, and Qwen) capped image sizes at 16000x16000, and Anthropic and XAI capped image sizes at 8000x8000. The reference solver showed no decrease in accuracy when moving from 16384 to 8192, but accuracy did start to drop when moving to a 4192x4192 image. So 8192x8192 was used for the final test (except for Anthropic and XAI, who got the largest possible 8000x8000). The images were attached as base-64 encoded PNG files, ensuring that JPEG artifacts did not affect the results.

Handling an 8192×8192 image tests the limit of these models. OpenAI models, under default settings, would complain about "only a thumbnail being attached" until `"detail": "high"` was added to the input parameters, as it's default behavior was to down-sample the data.

A few times CoT included comments like "I can't see any stars", or they'd spend significant time trying to fine-tune the contrast of the image. A reasonable explanation for this is that the image was down-sampled or recompressed within the model, perhaps with a fast or non-linear interpolation algorithm that loses fine detail.

The effect of this "resolution bottleneck" was that some models might only pick up the brightest few stars. For instance, gpt-5-mini was observed attempting to solve the problem entirely based on the position of a single planet (typically Jupiter). The baseline solver, by contrast, used all ~2500 stars. This highlights a core limitation: general vision models are not designed for images containing thousands of tiny points. This is a different style of problem to most computer vision processing, typically fine details are noise, like specs of dust or JPEG artifacts that complicate object recognition, where as in this case fine detail and the pattern it makes is information contained in the image.

### Inadequate Longitudinal Reasoning

Even models that correctly deduced latitude often struggled with longitude. This is unsurprising - determining longitude from stars requires knowing the time and recognizing some timing offset (e.g. comparing observed star positions to where they'd be at Greenwich). We did give the exact UTC time to the models. In principle, if a model identified a particular star and noted it is at X azimuth at this UTC, it could deduce longitude. But doing so needs either memory of star rise times or calculation.

Traces of this reasoning was observed within the CoT - many seemed to be recalling observations and
formulas for where celestial bodies would be at given times, however the information was either incorrect or the formulas were incorrectly used (without tooling), as it did not give the correct longitude.

### Faulty Guardrails

ChatGPT 5.2 (Reasoning + Tools) failed 2/49 tests due to "your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt". This scored itself a well deserved 0, as nothing in the question was even close to a violation of their policies.

The author has attempted a number of other benchmarking tasks and submitted hundreds of unrelated puzzles to LLMs/LMMs, and this faulty guardrail random failure behavior is not unique to celestial navigation. The prompts that trigger this behavior are locked out of the benchmark execution framework and blocked from ever being retried to avoid account suspension.

### Python sandbox limitations

Models were observed fighting against their restrictive enclosures. When scipy wasn't available, they'd try to install it from pip. When that failed, they'd try things like `os.system("pip install scipy")` or web searching for the package to download it. They would try to install `skyfield`, and lament that library's unavailability. Their python scripts did not have web access while running, so they couldn't use code that lazily downloaded star maps.

Watching the CoT, the best approaches were the ones that were solved iteratively - the model ran some code, got some feedback, and refined it. Gemini 3 Pro was observed using python to generate histograms and scatter plots, viewing them internally (never showing them to the user), and then using that to iteratively refine its answer.

This suggests that iterative tool feedback might be necessary to solve such tasks reliably. The author didn't single-shot write the reference solver, it was an iterative process. Likewise the best models refined and improved their code iteratively, however their attention span was limited, all but Gemini 3 gave up within an hour.

Gemini 3 did occasionally write code that seemed to run for over 3 hours, at least according to the CoT. Grok 4 was observed running code that timed out at XAI's limit of 45 minutes.

### Summary

In summary, the LMMs fell short because they lack an internal precise model of the celestial sphere and their general reasoning was not enough to compensate. The baseline solver essentially had a perfect world model of the problem (the physics and data of star positions) and could apply it, whereas the LMMs have a statistical approximation of a world model learned from data, which proved insufficient here.

World Models and Knowledge: A true world model (in the sense of Ha & Schmidhuber, 2018) would entail an AI having an internal simulation of how the environment (night sky) is generated from state (lat, lon, time). The LMMs tested might have some latent knowledge - for example, they know Polaris is only visible in the north and roughly that its altitude equals latitude. But they do not explicitly store the positions of thousands of stars or the algorithms of spherical astronomy. That kind of knowledge is niche and highly numerical - likely beyond the capacity of any to memorize from text. Our results highlight that LMMs still rely on tools for such specialized knowledge.

This aligns with the concept behind Toolformer and related research: by extending LMs with tools (calculators, external models), we can solve tasks they otherwise get wrong. Indeed, GPT-5.2 with tools was the only model to sometimes "build" a correct world model on the fly (through code). This suggests a possible path forward: if we want LMMs to robustly handle scientific tasks like celestial navigation, we should integrate domain APIs or modules (e.g., an ephemeris calculator) and train the LMM when to call them. In our case, calls to an astronomy library or a learned star-identification network could dramatically improve accuracy. The challenge is that this requires meticulous coordination - something current systems struggle with, as seen in our logs where models attempted but often misused the tools.

Multimodal Reasoning Complexity: Celestial navigation is an intersection of vision, language, math, and world knowledge. The model must interpret an image, possibly convert visual features to a symbolic form (star angles), recall or derive relationships (star angle to lat/lon), and output a numeric answer. This is more complex than typical vision-language tasks like captioning or object recognition. It is closer to visual problem solving. In the realm of AI tasks, it is somewhat analogous to the game GeoGuessr (guess location from street view) but arguably harder because the visual cues are entirely astronomical. Even humans require training to do this (most people cannot look at a random star field and instantly know where they are). Humans use tools - sextant, tables - to systematically get a fix. Our LMMs similarly needed tools. So, one could say this task is at the frontier of what we might expect general AI to do without explicit training. It's unsurprising they struggled, yet it's telling that even models with hundreds of billions of parameters and seemingly broad knowledge didn't come close to solving it directly.

Comparison to Prior ML Approaches: Previous works have applied deep learning to navigation or geolocation from images. For example, Google's PlaNet CNN was able to predict where a photo was taken by learning from millions of geotagged images. However, PlaNet relied on recognizable terrestrial cues (buildings, vegetation, etc.), and it treated the task as classification into geographic cells. Our problem is different: the night sky looks similar across vast areas (e.g., anywhere along a given latitude will see the same stars just rotated horizontally). It requires fine regression, not classification. A more directly related prior project is by Tozzi & Metz (2020), who trained a deep network to output latitude/longitude from synthetic sky images (with known time). They reported some success using a specialized CNN+LSTM model and a custom loss for haversine error, achieving on the order of tens of km accuracy on simulated data. Their approach, however, was a bespoke supervised model - essentially giving the network a structured way to learn the mapping from star patterns to coordinates. In contrast, our LMMs were not explicitly trained for this task (there is no indication any of them saw similar data in training).

One outcome of our work could be that targeted training or fine-tuning is necessary for LMMs to master such tasks. Perhaps an LMM fine-tuned on astronomy QA and star charts could perform better. Indeed, there are efforts like AstroLLaVA that adapt vision-language models to scientific domains. We did not test a domain-specialized model here (none exists yet for this exact problem), but that would be an interesting future experiment.

Failure Modes and Robustness: The issues of JSON formatting and sandbox limits might seem like "mundane" problems, but they are critical in practice. In an applied setting (say, an AI assistant helping with navigation), a malformed answer is as bad as a wrong answer. Our evaluation penalized those strictly. This reveals that when pushing models to their limits, their reliability suffers - they may break format or produce nonsense when unsure. Several of our tested models did output clearly nonsense coordinates at times (e.g., one gave latitude 0.0, longitude 180.0 for multiple cases - essentially saying "somewhere on equator at the Date Line" as a default guess). Such behavior is analogous to an untrained person shrugging - the model gave a placeholder or repeated guess because it was flummoxed. To be fair, we did not explicitly ask for a confidence estimate; our prompt said "if uncertain, guessing is acceptable." They all guessed, often with false confidence. A practical system should indicate uncertainty (e.g., "I'm not sure, maybe around 20°N, 150°W, plus or minus 1000 km").

## Conclusion

We presented a comprehensive evaluation of whether a large multimodal AI can achieve accurate positioning using the stars, essentially testing its internal world model of astronomy and its ability to use tools. Our findings lead to a clear answer: ***not yet***. While an algorithm with full knowledge can solve the task to meter-level precision, today's LMMs fall far short, often only identifying broad regions (hemisphere or continent-scale) correctly. The best model with extensive reasoning and tooling succeeded in a handful of cases, demonstrating a glimmer of potential but also inconsistency. These results highlight several challenges and research opportunities. First, improving the integration of hard scientific knowledge into LMMs - either through training (so the model inherently knows star catalogues) or through better tool use - is crucial. The task exemplifies a case where an AI's parametric knowledge is insufficient and it must reliably leverage external computations. Progress in frameworks that allow LMMs to call specialized models (as in HuggingGPT) will be key to tackling such problems. Second, visual processing limitations need addressing. An LMM that could ingest a high-res image or at least detect tiny features (perhaps by dynamically zooming or using an external vision module) would perform better. Our experiment suggests current vision front-ends are a bottleneck for astronomy-like imagery, so developing adaptive resolution or domain-specific perception could enhance multimodal reasoning. Output discipline let many models down, even a brilliant chain-of-thought is wasted if the final answer is malformed or the model doesn't admit when it's unsure. Techniques for aligning models to give well-calibrated and format-correct responses should accompany any increases in reasoning power.

Asking an AI to navigate by the stars proved to be a revealing stress test. It requires the AI to have a fairly detailed model of the world's physical law (celestial mechanics) and to apply it - a tall order for current systems trained mostly on internet text and images. Our study shows that with the help of tools, we can coax partially correct behavior from state-of-the-art models, but consistent sub-kilometre accuracy remains out of reach in 2026.

## Acknowledgments

The author is solely responsible for the entirety of this work, including the development of the sky simulation, baseline solver, and evaluation software. Thanks to the open-source community for libraries like Skyfield (astronomy) and the contributors of the LMMs evaluated. This research received no external funding.

## Citations

HuggingGPT: Leveraging LLMs to Solve Complex AI Tasks with Hugging Face Models - InfoQ

<https://www.infoq.com/news/2023/04/hugginggpt-complex-ai-tasks/>

[1602.05314] PlaNet - Photo Geolocation with Convolutional Neural Networks

<https://arxiv.org/abs/1602.05314>

AstroLLaVA: Towards the Unification of Astronomical Data ... - arXiv

<https://arxiv.org/html/2504.08583v1>
