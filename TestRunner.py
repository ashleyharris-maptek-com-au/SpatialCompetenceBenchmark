import subprocess
import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend to avoid tkinter threading issues

import VolumeComparison
from typing import Dict, List, Any, Optional, Set
import os
import base64
import html
import time
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed
from CacheLayer import CacheLayer as cl

try:
  import PIL, numpy, scipy
except ImportError:
  print("WARNIGN: pillow, numpy and scipy are required by some tests. Please install them.")
  exit(1)

global UNSKIP
UNSKIP = False

# Global to track model configs for perfect score propagation
ALL_MODEL_CONFIGS = []


def checkSavedPromptCache(aiEngineName: str, index: int, subPass: int, prompt: str):
  """
  Check if a saved prompt exists and matches the current prompt.
  If so, return the cached result. Otherwise return None.
  
  This is checked BEFORE the CacheLayer to avoid API calls when prompts haven't changed.
  """
  prompt_file = f"results/prompts/{aiEngineName}_{index}_{subPass}.txt"
  result_file = f"results/raw/{aiEngineName}_{index}_{subPass}.txt"

  if not os.path.exists(prompt_file) or not os.path.exists(result_file):
    return None

  if aiEngineName == "Human with tools":
    return None

  try:
    with open(prompt_file, "r", encoding="utf-8") as f:
      saved_prompt = f.read()

    # Compare prompts (strip to handle whitespace differences)
    if saved_prompt.strip() == str(prompt).strip():
      with open(result_file, "r", encoding="utf-8") as f:
        saved_result = f.read()
      print(f"Prompt cache hit for {aiEngineName} Q{index}/S{subPass}")
      # Results are saved with str(result), so use ast.literal_eval to parse
      import ast
      try:
        return ast.literal_eval(saved_result)
      except:
        return saved_result
  except Exception as e:
    print(f"Error checking saved prompt cache: {e}")

  return None


def getCompanyPrefix(model_name: str) -> str:
  """Extract company prefix from model name (part before first '-')."""
  if '-' in model_name:
    return model_name.split('-')[0]
  return model_name


def propogateUpwardsHack(aiEngineName: str, index: int, subPass: int, score: float):
  """
  HACK for development: If a subpass gets a perfect score, propagate the result
  to higher-grade LLMs from the same company.
  
  Same company = same prefix before '-' in model name.
  Higher grade = appears later in ALL_MODEL_CONFIGS list.
  """
  if score < 1.0:
    return

  company_prefix = getCompanyPrefix(aiEngineName)

  # Find current model's position in configs
  current_idx = -1
  for i, cfg in enumerate(ALL_MODEL_CONFIGS):
    if cfg.get('name') == aiEngineName:
      current_idx = i
      break

  if current_idx < 0:
    return

  # Copy results to higher-grade models from same company
  prompt_file = f"results/prompts/{aiEngineName}_{index}_{subPass}.txt"
  result_file = f"results/raw/{aiEngineName}_{index}_{subPass}.txt"
  cot_file = f"results/cot/{aiEngineName}_{index}_{subPass}.txt"

  if not os.path.exists(prompt_file) or not os.path.exists(result_file):
    return

  for i in range(current_idx + 1, len(ALL_MODEL_CONFIGS)):
    other_name = ALL_MODEL_CONFIGS[i].get('name', '')
    other_prefix = getCompanyPrefix(other_name)

    if other_prefix != company_prefix:
      continue

    # Copy files to higher-grade model
    target_prompt = f"results/prompts/{other_name}_{index}_{subPass}.txt"
    target_result = f"results/raw/{other_name}_{index}_{subPass}.txt"
    target_cot = f"results/cot/{other_name}_{index}_{subPass}.txt"

    # Only copy if target doesn't already exist
    if not os.path.exists(target_prompt):
      try:
        import shutil
        shutil.copy(prompt_file, target_prompt)
        shutil.copy(result_file, target_result)
        if os.path.exists(cot_file):
          shutil.copy(cot_file, target_cot)
        print(
          f"Propagated perfect score from {aiEngineName} to {other_name} for Q{index}/S{subPass}")
      except Exception as e:
        print(f"Failed to propagate result: {e}")


def runTest(index: int, aiEngineHook: callable, aiEngineName: str) -> Dict[str, Any]:
  """
    Run a test and return results including score and any generated images.
    
    Returns a dictionary containing:
        - 'average_score': float - average score across all subpasses
        - 'total_score': float - sum of all subpass scores
        - 'subpass_count': int - number of subpasses completed
        - 'subpass_results': list of dicts with individual subpass results
    """
  # load test file, compile it, and get its globals in a map:
  g = {}

  if not os.path.exists(str(index) + ".py"):
    raise StopIteration

  exec(open("" + str(index) + ".py", encoding="utf-8").read(), g)

  if "skip" in g and not UNSKIP:
    return {"average_score": 0, "total_score": 0, "subpass_count": 0, "subpass_results": []}

  prompts = []
  structure = g["structure"]

  if "prepareSubpassPrompt" in g:
    # get the prompt and structure from the globals:
    subPass = 0
    while True:
      try:
        prompts.append(g["prepareSubpassPrompt"](subPass))
        subPass += 1
      except StopIteration:
        break
  else:
    prompts.append(g["prompt"])

  # Helper to run a single prompt and save results
  def run_single_prompt(idx, prompt):
    # Check saved prompt cache first (before CacheLayer)
    cached_result = checkSavedPromptCache(aiEngineName, index, idx, prompt)
    if cached_result is not None:
      if structure is not None:
        if not isinstance(cached_result, dict):
          return {}  # don't crash tests expecting json.
      return cached_result

    try:
      result, chainOfThought = aiEngineHook(prompt, structure, index, idx)
    except Exception as e:
      print("Failed to get result for subpass " + str(idx) + " - " + str(e))
      result = ""
      chainOfThought = ""

    try:
      open("results/raw/" + aiEngineName + "_" + str(index) + "_" + str(idx) + ".txt",
           "w",
           encoding="utf-8").write(str(result))
    except Exception as e:
      print("Failed to save result for subpass " + str(idx) + " - " + str(e))

    try:
      open("results/prompts/" + aiEngineName + "_" + str(index) + "_" + str(idx) + ".txt",
           "w",
           encoding="utf-8").write(str(prompts[idx]))
    except Exception as e:
      print("Failed to save prompt for subpass " + str(idx) + " - " + str(e))

    try:
      open("results/cot/" + aiEngineName + "_" + str(index) + "_" + str(idx) + ".txt",
           "w",
           encoding="utf-8").write(str(chainOfThought))
    except Exception as e:
      print("Failed to save chain of thought for subpass " + str(idx) + " - " + str(e))

    return result

  earlyFail = "earlyFail" in g
  results = [None] * len(prompts)

  if earlyFail and len(prompts) > 1:
    # Run first prompt sequentially
    results[0] = run_single_prompt(0, prompts[0])
  elif "singleThreaded" in g:
    for i, prompt in enumerate(prompts):
      results[i] = run_single_prompt(i, prompt)
  else:
    # Parallelize AI engine calls
    with ThreadPoolExecutor() as executor:
      future_to_index = {
        executor.submit(run_single_prompt, i, prompt): i
        for i, prompt in enumerate(prompts)
      }
      for future in as_completed(future_to_index):
        idx = future_to_index[future]
        results[idx] = future.result()

  # In placebo mode, make sure we test all the grading functions even if the questions are currently
  # too hard for me to create an answer.
  if aiEngineName == "Placebo":
    first_result = next((r for r in results if r is not None), None)
    if first_result is not None:
      results = [r if r is not None else first_result for r in results]

  # Result processing and grading helper
  def process_subpass(subPass, result):
    score = 0
    subpass_data = {"subpass": subPass, "score": 0, "startProcessingTime": time.time()}

    # Check for content violation - always grade as 0
    if isinstance(result, dict) and result.get("__content_violation__"):
      print(f"Content violation for subpass {subPass} - grading as 0")
      subpass_data["score"] = 0
      subpass_data[
        "scoreExplantion"] = f"Content violation: {result.get('reason', 'Policy violation')}"
      subpass_data[
        "output_nice"] = "<strong style='color:red'>FALSE-POSITIVE CONTENT VIOLATION</strong><br>This prompt was blocked by the AI provider's content policy. (LOL. Sad trombone failure sound. Instant 0.)"
      subpass_data["endProcessingTime"] = time.time()
      return 0, subpass_data

    if isinstance(result, dict) and "reasoning" in result:
      subpass_data["reasoning"] = result["reasoning"]
    elif isinstance(result, dict) and "reasoningAndDiscussion" in result:
      subpass_data["reasoningAndDiscussion"] = result["reasoningAndDiscussion"]

    if not result:
      print(f"No answer generated for subpass {subPass}")
      subpass_data["score"] = 0
    elif "resultToImage" in g:
      score, explanation = g["gradeAnswer"](result, subPass, aiEngineName)
      output_path = g["resultToImage"](result, subPass, aiEngineName)
      if "resultToNiceReport" in g:
        subpass_data["output_nice"] = g["resultToNiceReport"](result, subPass, aiEngineName)
      else:
        subpass_data["output_text"] = result
        subpass_data["output_image"] = output_path

      if "getReferenceImage" in g:
        subpass_data["reference_image"] = g["getReferenceImage"](subPass, aiEngineName)
      subpass_data["score"] = score
      subpass_data["scoreExplantion"] = explanation

    elif "referenceScad" in g or "prepareSubpassReferenceScad" in g:
      # Some tests require an OpenSCAD comparison to check if the generated
      # shape closely resembles some reference data.
      comparison_result = VolumeComparison.compareVolumeAgainstOpenScad(index, subPass, result, g)
      score = comparison_result["score"]
      subpass_data["score"] = score
      subpass_data["output_image"] = comparison_result.get("output_image")
      subpass_data["output_mouseover_image"] = comparison_result.get("output_mouseover_image")
      subpass_data["reference_image"] = comparison_result.get("reference_image")
      subpass_data["temp_dir"] = comparison_result.get("temp_dir")
      subpass_data["scoreExplantion"] = comparison_result.get("scoreExplantion")
      subpass_data["output_hyperlink"] = comparison_result.get("output_hyperlink")

    elif "gradeAnswer" in g:
      # Some tests require a custom grading function.

      try:
        score, explanation = g["gradeAnswer"](result, subPass, aiEngineName)
      except Exception as e:
        print("Failed to grade subpass " + str(subPass) + " - " + str(e))
        score = 10000  # This should get attention!
        explanation = "Failed to grade subpass " + str(subPass) + " - " + str(e) + \
            "This is a framework error, not an AI error."

      subpass_data["score"] = score
      subpass_data["scoreExplantion"] = explanation

      if "resultToNiceReport" in g:
        try:
          subpass_data["output_nice"] = g["resultToNiceReport"](result, subPass, aiEngineName)
        except Exception as e:
          print("Failed to generate nice report for subpass " + str(subPass) + " - " + str(e))
          subpass_data["output_nice"] = "Failed to generate nice report for subpass " + str(
            subPass) + " - " + str(e)
      else:
        subpass_data["output_text"] = result

    subpass_data["endProcessingTime"] = time.time()

    # HACK: Propagate perfect scores to higher-grade models from same company
    propogateUpwardsHack(aiEngineName, index, subPass, score)

    return score, subpass_data

  totalScore = 0
  subpass_results = [None] * len(prompts)
  earlyFailTriggered = False

  if earlyFail and len(prompts) > 1:
    # Process first subpass sequentially
    first_score, first_subpass_data = process_subpass(0, results[0])
    totalScore += first_score
    subpass_results[0] = first_subpass_data

    if first_score < 0.5:
      # Early fail: assume all other subpasses will score 0
      earlyFailTriggered = True
      for subPass in range(1, len(prompts)):
        subpass_results[subPass] = {
          "subpass": subPass,
          "score": 0,
          "scoreExplantion": "Skipped due to earlyFail (first subpass scored under 50%)"
        }
    else:
      # First subpass passed, run remaining prompts in parallel
      with ThreadPoolExecutor() as executor:
        future_to_index = {
          executor.submit(run_single_prompt, i, prompts[i]): i
          for i in range(1, len(prompts))
        }
        for future in as_completed(future_to_index):
          idx = future_to_index[future]
          results[idx] = future.result()

      # In placebo mode, fill in missing results
      if aiEngineName == "Placebo":
        first_result = next((r for r in results if r is not None), None)
        if first_result is not None:
          results = [r if r is not None else first_result for r in results]

      # Process remaining subpasses in parallel
      with ThreadPoolExecutor() as executor:
        future_to_subpass = {
          executor.submit(process_subpass, subPass, results[subPass]): subPass
          for subPass in range(1, len(prompts))
        }
        for future in as_completed(future_to_subpass):
          subPass = future_to_subpass[future]
          score, subpass_data = future.result()
          totalScore += score
          subpass_results[subPass] = subpass_data

  elif "singleThreaded" in g:
    for i, result in enumerate(results):
      score, subpass_data = process_subpass(i, result)
      totalScore += score
      subpass_results[i] = subpass_data
  else:
    with ThreadPoolExecutor() as executor:
      future_to_subpass = {
        executor.submit(process_subpass, subPass, result): subPass
        for subPass, result in enumerate(results)
      }
      for future in as_completed(future_to_subpass):
        subPass = future_to_subpass[future]
        score, subpass_data = future.result()
        totalScore += score
        subpass_results[subPass] = subpass_data

  if "extraGradeAnswerRuns" in g:
    extraGradeAnswerRuns = g["extraGradeAnswerRuns"]
    for subPass in extraGradeAnswerRuns:
      subpass_data = {}
      score, explanation = g["gradeAnswer"](results[0], subPass, aiEngineName)
      totalScore += score
      subpass_data["score"] = score
      subpass_data["subpass"] = subPass
      subpass_data["scoreExplantion"] = explanation
      subpass_data["output_nice"] = g["resultToNiceReport"](results[0], subPass, aiEngineName)
      subpass_results.append(subpass_data)

  return {
    "average_score": totalScore / len(results) if results else 0,
    "total_score": max(0, totalScore),
    "subpass_count": len(subpass_results),
    "subpass_results": subpass_results
  }


def runAllTests(aiEngineHook: callable, aiEngineName: str, test_filter: Optional[Set[int]] = None):
  """
    Run all tests for an AI engine.
    
    Args:
        aiEngineHook: The AI engine hook function
        aiEngineName: Name of the AI engine
        test_filter: Optional set of test indices to run. If None, runs all tests.
    """
  # Create results directory and subdirectories
  os.makedirs("results", exist_ok=True)
  os.makedirs("results/raw", exist_ok=True)
  os.makedirs("results/prompts", exist_ok=True)
  os.makedirs("results/cot", exist_ok=True)

  # Create a results file for the html results of this engines test run
  results_file = open("results/" + aiEngineName + ".html", "w", buffering=1, encoding="utf-8")
  results_file.write("<html>\n<head>\n<style>\n")
  results_file.write("""
:root {
    --bg-color: #ffffff;
    --text-color: #333;
    --text-secondary: #666;
    --border-color: #ddd;
    --header-bg: #4CAF50;
    --header-text: white;
    --test-header-bg: #45a049;
    --prompt-bg: #f9f9f9;
    --subpass-bg: #ffffff;
    --img-border: #ccc;
    --score-good: #228B22;
    --score-bad: #dc3545;
}
@media screen and (prefers-color-scheme: dark) {
    :root {
        --bg-color: #1a1a1a;
        --text-color: #e0e0e0;
        --text-secondary: #aaa;
        --border-color: #444;
        --header-bg: #2d5a2d;
        --header-text: #e0e0e0;
        --test-header-bg: #3d6a3d;
        --prompt-bg: #2a2a2a;
        --subpass-bg: #1f1f1f;
        --img-border: #555;
        --score-good: #4CAF50;
        --score-bad: #ff6b6b;
    }
    a[href] { color: #55f}
}
body { background-color: var(--bg-color); color: var(--text-color); }
table { border-collapse: collapse; width: 100%; margin: 20px 0; }
th, td { border: 1px solid var(--border-color); padding: 12px; text-align: left; vertical-align: top; }
th { background-color: var(--header-bg); color: var(--header-text); }
.test-header { background-color: var(--test-header-bg); font-weight: bold; }
.prompt-row { background-color: var(--prompt-bg); font-style: italic; }
.subpass-row { background-color: var(--subpass-bg); }
img { max-width: 100%; height: auto; border: 1px solid var(--img-border); }
.score-good { color: var(--score-good); font-weight: bold; }
.score-bad { color: var(--score-bad); font-weight: bold; }
h1 { color: var(--text-color); }
h2 { color: var(--text-secondary); margin-top: 30px; }
""")
  results_file.write("</style>\n<meta charset='UTF-8'/> </head>\n<body>\n")
  results_file.write("<h1>Benchmark Results for " + aiEngineName + "</h1>\n")
  results_file.write("<table>\n")

  testIndex = 1
  overall_total_score = 0
  overall_max_score = 0
  per_question_scores = {}  # {question_num: {"title": str, "score": float, "max": int}}

  longestProcessor = (None, None), 0

  while True:
    print("\n" + "=" * 60)
    print(f"TEST {testIndex} START")
    print("=" * 60)

    try:
      if not os.path.exists(str(testIndex) + ".py"):
        break
      test_result = {}
      # Load test metadata
      test_globals = {}
      exec(open(str(testIndex) + ".py", encoding="utf-8").read(), test_globals)

      test_was_run = test_filter is None or testIndex in test_filter
      if test_was_run:
        test_result = runTest(testIndex, aiEngineHook, aiEngineName)
      else:
        test_result = {"total_score": 0, "subpass_count": 0, "subpass_results": []}

      current_test_index = testIndex
      testIndex += 1

      # Calculate max score for this test (1 point per subpass)
      max_score = test_result['subpass_count']
      overall_total_score += test_result['total_score']
      overall_max_score += max_score

      # Track per-question scores (only for tests that were actually run)
      if test_was_run:
        question_title = test_globals.get("title", f"Test {current_test_index}")
        per_question_scores[current_test_index] = {
          "title": question_title,
          "score": test_result['total_score'],
          "max": max_score
        }

    except StopIteration:
      break

    # Console output
    print(f"Score: {test_result['total_score']:.2f} / {max_score}")
    print(f"Subpasses Completed: {test_result['subpass_count']}")
    print("\nSubpass Details:")

    for subpass in test_result['subpass_results']:
      print(f"  Subpass {subpass['subpass']}: Score = {subpass['score']:.4f}")
      #print(subpass)
      if 'endProcessingTime' in subpass and 'startProcessingTime' in subpass:
        timeTaken = subpass['endProcessingTime'] - subpass['startProcessingTime']
        if timeTaken > longestProcessor[1]:
          longestProcessor = ((testIndex, subpass['subpass']), timeTaken)

    print("\n" + "=" * 60)
    print(f"TEST {testIndex-1} COMPLETED!")
    print("=" * 60)

    # HTML output

    # Header row: Test name, number of subpasses, score
    test_name = f"Test {testIndex-1}"

    # Extract test purpose from title or prompt (first line)
    test_purpose = ""
    if "title" in test_globals:
      test_purpose = test_globals["title"]
    elif "prompt" in test_globals:
      prompt_lines = test_globals["prompt"].strip().split("\n")
      test_purpose = prompt_lines[0] if prompt_lines else "No description available"
    else:
      test_purpose = "Unnamed test"

    score_class = "score-good" if test_result['total_score'] >= max_score * 0.7 else "score-bad"

    results_file.write("  <tr class='test-header'>\n")
    results_file.write(
      f"    <th colspan=3><a name='q{testIndex-1}'>{test_name}: {test_purpose}</a></th>\n")
    results_file.write(
      f"    <th class='{score_class}'>Score: {test_result['total_score']:.2f} / {max_score}</th>\n")
    results_file.write("  </tr>\n")

    # Prompt row: Typical prompt and how it changes
    results_file.write("  <tr class='prompt-row'>\n")
    results_file.write(
      "    <td colspan='3'><div style='overflow-x: auto;height: 200px;'><strong>Typical Prompt:</strong><br>"
    )

    def handlePromptImages(prompt: str) -> str:
      if "[[image:" not in prompt:
        return prompt

      while "[[image:results/" in prompt:
        prompt = prompt.replace("[[image:results/", "[[image:")

      return prompt.replace("[[image:", "<img src='").replace("]]", "' width='200px'>")

    if "prepareSubpassPrompt" in test_globals:
      # Show first subpass prompt
      try:
        first_prompt = test_globals["prepareSubpassPrompt"](0)
        results_file.write(handlePromptImages(first_prompt).replace("\n", "<br>"))
      except:
        results_file.write("Dynamic prompt generation")
    elif "prompt" in test_globals:
      prompt_text = test_globals["prompt"].strip()
      results_file.write(handlePromptImages(prompt_text).replace("\n", "<br>"))
    else:
      results_file.write("No prompt available")

    results_file.write("</div></td>\n")
    results_file.write("    <td><strong>Prompt Changes:</strong><br>")

    if "promptChangeSummary" in test_globals:
      results_file.write(test_globals["promptChangeSummary"])
    elif "prepareSubpassPrompt" in test_globals:
      results_file.write("Prompt parameters change between subpasses (increasing difficulty)")
    else:
      results_file.write("Prompt remains constant")

    results_file.write("</td>\n")
    results_file.write("  </tr>\n")

    # Subpass rows
    for subpass in test_result['subpass_results']:
      results_file.write("  <tr class='subpass-row'>\n")

      # Subpass overview
      results_file.write(f"    <td rowspan=2><strong>Subpass {subpass['subpass']}</strong><br>")

      if "subpassParamSummary" in test_globals and subpass['subpass'] < len(
          test_globals["subpassParamSummary"]):
        results_file.write(
          f"Parameters: {test_globals['subpassParamSummary'][subpass['subpass']]}<br>")
      elif "prepareSubpassPrompt" in test_globals:
        try:
          subpass_prompt = test_globals["prepareSubpassPrompt"](subpass['subpass'])
          # Extract parameters from prompt
          results_file.write("Parameters: ")
          if "PARAM_" in subpass_prompt:
            results_file.write("(modified from base prompt)")
          else:
            results_file.write("(see typical prompt)")
        except:
          results_file.write("Subpass configuration")
      else:
        results_file.write("Same as typical prompt")

      results_file.write("<a href=\"prompts/" + aiEngineName + "_" + str(testIndex - 1) + "_" +
                         str(subpass['subpass']) + ".txt\">View exact prompt</a><br>")
      results_file.write("<a href=\"raw/" + aiEngineName + "_" + str(testIndex - 1) + "_" +
                         str(subpass['subpass']) + ".txt\">View raw AI output</a><br>")
      results_file.write("<a href=\"cot/" + aiEngineName + "_" + str(testIndex - 1) + "_" +
                         str(subpass['subpass']) + ".txt\">View chain of thought</a><br>")

      if "highLevelSummary" in test_globals and subpass['subpass'] == 0:
        results_file.write(test_globals['highLevelSummary'])

      results_file.write("</td>\n")

      if "reasoning" in subpass:
        results_file.write(
          f"<td colspan=2><div style='overflow-y: auto;max-height: 100px;'><strong>AI Reasoning: </strong>{html.escape(subpass['reasoning'])}</div></td>"
        )
      else:
        results_file.write("<td colspan=2></td>")

      # Score
      score_class = "score-good" if subpass['score'] >= 0.7 else "score-bad"
      results_file.write(
        f"    <td rowspan=2class='{score_class}'><strong>{subpass['score']:.4f}</strong>")

      if "scoreExplantion" in subpass:
        results_file.write(
          "<br><div style='font-size: 12px; font-style: italic; color: #666; margin-left: 20px; overflow-x: auto; max-width:200px;'>"
          + subpass['scoreExplantion'].replace("\n", "<br>") + "</div>")

      results_file.write("</td>\n")
      results_file.write("  </tr>\n")

      # Images
      if 'output_image' in subpass and subpass['output_image']:
        # Actual image
        results_file.write("    <td>")

        if "output_hyperlink" in subpass and subpass['output_hyperlink']:
          results_file.write(f"<a href='{subpass['output_hyperlink']}'>")
        if ('output_mouseover_image' in subpass and subpass['output_mouseover_image']
            and os.path.exists(subpass['output_mouseover_image'])
            and os.path.exists(subpass['output_image'])):
          with open(subpass['output_image'], 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
          with open(subpass['output_mouseover_image'], 'rb') as img_file:
            img_data2 = base64.b64encode(img_file.read()).decode('utf-8')

          results_file.write(f"""
                    <img src='data:image/png;base64,{img_data}' 
                      data-mouseout='data:image/png;base64,{img_data}'
                      data-mouseover='data:image/png;base64,{img_data2}'
                      alt='Output' onmouseover="this.src=this.dataset.mouseover" onmouseout="this.src=this.dataset.mouseout">
                    """)

        elif os.path.exists(subpass['output_image']):
          try:
            with open(subpass['output_image'], 'rb') as img_file:
              img_data = base64.b64encode(img_file.read()).decode('utf-8')
              results_file.write(f"<img src='data:image/png;base64,{img_data}' alt='Output'>")
          except:
            results_file.write(f"<a href='../{subpass['output_image']}'>View Output Image</a>")
        else:
          results_file.write("Image not found")

        if "output_hyperlink" in subpass and subpass['output_hyperlink']:
          results_file.write(f"</a>")
        results_file.write("</td>\n")

        # Reference image
        results_file.write("    <td>")
        if 'reference_image' in subpass and subpass['reference_image'] and os.path.exists(
            subpass['reference_image']):
          try:
            with open(subpass['reference_image'], 'rb') as img_file:
              img_data = base64.b64encode(img_file.read()).decode('utf-8')
              results_file.write(f"<img src='data:image/png;base64,{img_data}' alt='Reference'>")
          except:
            results_file.write(
              f"<a href='../{subpass['reference_image']}'>View Reference Image</a>")
        else:
          results_file.write("No reference image")
        results_file.write("</td>\n")
      elif "output_nice" in subpass:
        # Nice preformatted output, if it contains table cells just display as is:
        if "</td><td>" in subpass["output_nice"]:
          results_file.write(subpass["output_nice"])
        else:
          results_file.write("    <td colspan='2'>" + subpass["output_nice"] + "</td>\n")
      elif "output_text" in subpass:
        # Text output only
        results_file.write(
          "    <td colspan='2'><pre style='max-width: 1000px; overflow-x: auto;'>" +
          html.escape(str(subpass["output_text"])) + "</pre></td>\n")
      else:
        # No images for this test type
        results_file.write("    <td>N/A (LLM did not answer)</td>\n")
        results_file.write("    <td>N/A (Test forfeited)</td>\n")

  # Overall summary
  results_file.write("<h2>Overall Summary</h2>\n")
  results_file.write("<table>\n")
  results_file.write("  <tr class='test-header'>\n")
  results_file.write("    <th>Total Tests</th>\n")
  results_file.write("    <th>Overall Score</th>\n")
  results_file.write("    <th>Percentage</th>\n")
  results_file.write("  </tr>\n")
  results_file.write("  <tr>\n")
  results_file.write(f"    <td>{testIndex - 1}</td>\n")
  results_file.write(f"    <td>{overall_total_score:.2f} / {overall_max_score}</td>\n")
  percentage = (overall_total_score / overall_max_score * 100) if overall_max_score > 0 else 0
  results_file.write(f"    <td>{percentage:.1f}%</td>\n")
  results_file.write("  </tr>\n")
  results_file.write("</table>\n")

  results_file.write("</body>\n</html>\n")
  results_file.close()

  print("\n" + "=" * 60)
  print("BENCHMARK COMPLETE")
  print("=" * 60)
  print(f"Total Score: {overall_total_score:.2f} / {overall_max_score} ({percentage:.1f}%)")
  print(f"Results saved to: results/{aiEngineName}.html")
  print("=" * 60)

  scores = {}

  if not os.path.exists("results/results.txt"):
    with open("results/results.txt", "w", encoding="utf-8") as f:
      f.write("\n")

  with open("results/results.txt", "r", encoding="utf-8") as f:
    for line in f:
      if ":" in line:
        scores[line.split(":")[0].strip()] = line.split(":")[1].strip()

  if test_filter is None:
    # Don't overwrite scores if we're running a subset of tests.
    scores[aiEngineName] = overall_total_score / overall_max_score if overall_max_score > 0 else 0

  with open("results/results.txt", "w", encoding="utf-8") as f:
    for key, value in sorted(scores.items(), key=lambda item: float(item[1]), reverse=True):
      f.write(f"{key}: {value}\n")

  # Save per-question results to JSON
  import json
  per_question_file = "results/results_by_question.json"
  all_per_question = {}
  if os.path.exists(per_question_file):
    with open(per_question_file, "r", encoding="utf-8") as f:
      try:
        all_per_question = json.load(f)
      except:
        all_per_question = {}

  # Merge with existing data for this engine (don't overwrite other questions)
  if aiEngineName not in all_per_question:
    all_per_question[aiEngineName] = {}
  for q_num, q_data in per_question_scores.items():
    all_per_question[aiEngineName][str(q_num)] = q_data

  with open(per_question_file, "w", encoding="utf-8") as f:
    json.dump(all_per_question, f, indent=2)

  # Generate a summary page of the results, suitable for use as a github landing page,
  # including a big graph of the results by engine name

  import matplotlib.pyplot as plt
  import pandas as pd

  df = pd.read_csv("results/results.txt", sep=":", header=None, names=["Engine", "Score"])

  di = df.to_dict()
  for i in range(df.shape[0]):
    e = di["Engine"][i]

    e = e.replace("-HighReasoning", "+R")
    e = e.replace("-Reasoning-Tools", "+RT")
    e = e.replace("-bedrock", "")
    di["Engine"][i] = e

  df = df.from_dict(di)

  # Use horizontal bar chart for better label readability
  fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.5)))
  ax.barh(df["Engine"], df["Score"], color='#1f77b4')
  ax.set_xlabel("Score")
  ax.set_ylabel("")
  ax.set_title("Mesh Benchmark Results")
  ax.invert_yaxis()  # Highest score at top
  plt.tight_layout()
  plt.savefig("results/topLevelResults.png", dpi=600)
  plt.close()

  # Generate per-question graphs
  question_graphs = {}  # {question_num: {"title": str, "filename": str}}

  # Get all question numbers from all engines
  all_questions = set()
  for engine_data in all_per_question.values():
    all_questions.update(int(q) for q in engine_data.keys())

  for q_num in sorted(all_questions):
    q_str = str(q_num)
    # Collect scores for this question from all engines
    engine_scores = []
    question_title = f"Question {q_num}"
    max_score = 1

    for engine_name, engine_data in all_per_question.items():
      if q_str in engine_data:
        q_data = engine_data[q_str]
        question_title = q_data.get("title", question_title)
        max_score = q_data.get("max", 1)
        score = q_data.get("score", 0)
        # Normalize to percentage of max
        normalized = score / max_score if max_score > 0 else 0
        engine_scores.append((engine_name, normalized))

    if not engine_scores:
      continue

    # Sort by score descending
    engine_scores.sort(key=lambda x: x[1], reverse=True)
    engines = [e[0] for e in engine_scores]
    scores_list = [e[1] for e in engine_scores]

    # Generate graph
    fig, ax = plt.subplots(figsize=(10, max(3, len(engines) * 0.4)))
    ax.barh(engines, scores_list, color='#667eea')
    ax.set_xlabel("Score (normalized)")
    ax.set_ylabel("")
    ax.set_title(f"Q{q_num}: {question_title}")
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    plt.tight_layout()

    filename = f"question_{q_num}.png"
    plt.savefig(f"results/{filename}", dpi=150)
    plt.close()

    best_engine, best_score = engine_scores[0] if engine_scores else ("", 0)
    if best_engine == "Human with tools":
      best_engine, best_score = engine_scores[1] if len(engine_scores) > 1 else ("", 0)

    humanScore = [e[1] for e in engine_scores if e[0] == "Human with tools"][0]

    question_graphs[q_num] = {
      "title": question_title,
      "filename": filename,
      "max": max_score,
      "best_engine": best_engine,
      "human_score": humanScore,
      "best_pct": best_score * 100
    }

  # Generate index.html landing page
  with open("results/index.html", "w", encoding="utf-8") as index_file:
    index_file.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mesh Benchmark Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .graph-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .graph-container h2 {
            color: #333;
        }
        .graph-container img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        .results-table {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background-color: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .score-cell {
            font-weight: bold;
            font-size: 1.1em;
        }
        .score-high {
            color: #10b981;
        }
        .score-medium {
            color: #f59e0b;
        }
        .score-low {
            color: #ef4444;
        }
        a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        a:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-best {
            background-color: #dcfce7;
            color: #166534;
        }
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            .graph-container, .results-table {
                background: #16213e;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .graph-container h2 {
                color: #e0e0e0;
            }
            td {
                border-bottom-color: #2a2a4a;
            }
            tr:hover {
                background-color: #1f2b4a;
            }
            .footer {
                color: #888;
            }
            a {
                color: #8b9fea;
            }
            .badge-best {
                background-color: #1a4d2e;
                color: #6ee7a0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Mesh Benchmark Results</h1>
        <p class="subtitle">Model Evaluation of Spatial Hueristics.</p>
        <p>Can LLMs use internal visualisation or spatial reasoning to solve problems?</p>
    </div>
    
    <div class="graph-container">
        <h2 style="margin-top: 0;">Performance Overview</h2>
        <img src="topLevelResults.png" alt="Benchmark Results Graph">
    </div>
    
    <div class="results-table">
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Engine Name</th>
                    <th>Score</th>
                    <th>Percentage</th>
                    <th>Detailed Results</th>
                </tr>
            </thead>
            <tbody>
""")

    # Sort engines by score (descending)
    sorted_engines = sorted(scores.items(), key=lambda x: float(x[1]), reverse=True)
    best_score = float(sorted_engines[0][1]) if sorted_engines else 0

    for rank, (engine_name, score) in enumerate(sorted_engines, 1):
      score_float = float(score)
      percentage = score_float * 100

      # Determine score class
      if percentage >= 70:
        score_class = "score-high"
      elif percentage >= 40:
        score_class = "score-medium"
      else:
        score_class = "score-low"

      # Add best badge
      badge = '<span class="badge badge-best">BEST</span>' if rank == 1 else ''

      index_file.write(f"""                <tr>
                    <td><strong>#{rank}</strong></td>
                    <td>{html.escape(engine_name)}{badge}</td>
                    <td class="score-cell {score_class}">{score_float:.4f}</td>
                    <td class="{score_class}">{percentage:.1f}%</td>
                    <td><a href="{html.escape(engine_name)}.html">View Details →</a></td>
                </tr>
""")

    index_file.write("""            </tbody>
        </table>
    </div>
""")

    # Add per-question sections
    if question_graphs:
      index_file.write("""
    <div class="graph-container">
        <h2 style="margin-top: 0;">Results by Question</h2>
    </div>
""")
      for q_num in sorted(question_graphs.keys()):
        # load test file, compile it, and get its globals in a map:
        g = {}

        if not os.path.exists(str(q_num) + ".py"):
          raise StopIteration

        exec(open("" + str(q_num) + ".py", encoding="utf-8").read(), g)

        if question_graphs[q_num]['human_score']:
          humanRatio = question_graphs[q_num]['best_pct'] /\
            (question_graphs[q_num]['human_score'] * 100)
          humanCompare = "No Data"
          if humanRatio < 0.3:
            humanCompare = "<p style='color:#0f0'> Human is considerably better</p>"
          elif humanRatio < 0.9:
            humanCompare = "<p style='color:#0f0'> Human is better</p>"
          elif humanRatio < 0.99:
            humanCompare = "<p style='color:#0f0'> Human is marginally better</p>"
          elif humanRatio < 1.01:
            if question_graphs[q_num]['human_score'] == 0:
              humanCompare = "<p style='color:#ff0'>Niether human nor AI have solved this.</p>"
            elif question_graphs[q_num]['human_score'] == 1:
              humanCompare = "<p style='color:#ff0'> Human and the best AI have both mastered this.</p>"
            else:
              humanCompare = "<p style='color:#ff0'> Human and the best AI are equal.</p>"
          elif humanRatio < 1.5:
            humanCompare = f"<p style='color:#f00'> The best AI is marginally better. Human scored {question_graphs[q_num]['human_score'] * 100:.1f}% </p>"
          else:
            humanCompare = f"<p style='color:#f00'> The best AI is considerably better. Human scored {question_graphs[q_num]['human_score'] * 100:.1f}%</p>"
        else:
          if question_graphs[q_num]['best_pct'] == 0:
            humanCompare = "<p style='color:#ff0'>Niether human nor AI have solved this.</p>"
          else:
            humanCompare = "<p style='color:#f00'> The best AI is considerably better, human scored 0 or hasn't attempted.</p>"

        q_data = question_graphs[q_num]
        index_file.write(f"""
    <div class="graph-container" id="q{q_num}">
        <img src="../images/{q_num}.png" style="float:right; max-width:400px">
        <a name="q{q_num}"><h2 style="margin-top: 0;color:#fff">Q{q_num}: {html.escape(q_data['title'])}</h2></a>
        {g.get("highLevelSummary","")}
        <p style='clear:both'><strong>Best result:</strong> <a href="{html.escape(q_data['best_engine'])}.html#q{q_num}">{html.escape(q_data['best_engine'])}</a> ({q_data['best_pct']:.1f}%)</p>
        {humanCompare}
        <details>
            <summary style="cursor:pointer; color:#667eea;">Click to show comparison graph</summary>
            <img src="{q_data['filename']}" alt="Question {q_num} Results" style="margin-top:10px;">
        </details>
    </div>
""")

    index_file.write("""
    <div class="footer">
        <p>Generated automatically by TestRunner.py</p>
        <p>Last updated: """ + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                     """</p>
    </div>
</body>
</html>
""")

  print(f"Landing page saved to: results/index.html")
  print(f"Longest processing time: {longestProcessor[1]} seconds for test {longestProcessor[0]}")


def get_all_model_configs():
  """
    Returns a list of all available model configurations.
    Each config is a dict with: name, engine_module, configure_args, env_key
    """
  configs = []

  # Human with tools (Placebo)
  configs.append({
    "name": "Human with tools",
    "engine": "placebo",
    "env_key": None,  # Always available
  })

  # OpenAI models
  openai_base_models = ["gpt-5-nano", "gpt-5-mini", "gpt-5.1", "gpt-5.2"]
  for model in openai_base_models:
    configs.append({
      "name": model,
      "engine": "openai",
      "base_model": model,
      "reasoning": False,
      "tools": False,
      "env_key": "OPENAI_API_KEY"
    })
    configs.append({
      "name": f"{model}-HighReasoning",
      "engine": "openai",
      "base_model": model,
      "reasoning": 10,
      "tools": False,
      "env_key": "OPENAI_API_KEY"
    })
    configs.append({
      "name": f"{model}-Reasoning-Tools",
      "engine": "openai",
      "base_model": model,
      "reasoning": 10,
      "tools": True,
      "env_key": "OPENAI_API_KEY"
    })

  # Gemini models
  gemini_base_models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview"]
  for model in gemini_base_models:
    configs.append({
      "name": model,
      "engine": "gemini",
      "base_model": model,
      "reasoning": False,
      "tools": False,
      "env_key": "GEMINI_API_KEY"
    })
    configs.append({
      "name": f"{model}-HighReasoning",
      "engine": "gemini",
      "base_model": model,
      "reasoning": 10,
      "tools": False,
      "env_key": "GEMINI_API_KEY"
    })
    configs.append({
      "name": f"{model}-Reasoning-Tools",
      "engine": "gemini",
      "base_model": model,
      "reasoning": 10,
      "tools": True,
      "env_key": "GEMINI_API_KEY"
    })

  # XAI/Grok models. These are a bit weird with their reasoning support.

  configs.append({
    "name": "grok-2-vision-1212",
    "engine": "xai",
    "base_model": "grok-2-vision-1212",
    "reasoning": False,
    "tools": False,
    "env_key": "XAI_API_KEY"
  })
  configs.append({
    "name": "grok-4-1-fast-non-reasoning",
    "engine": "xai",
    "base_model": "grok-4-1-fast-non-reasoning",
    "reasoning": False,
    "tools": False,
    "env_key": "XAI_API_KEY"
  })
  configs.append({
    "name": "grok-4-1-fast-reasoning",
    "engine": "xai",
    "base_model": "grok-4-1-fast-reasoning",
    "reasoning": 10,
    "tools": False,
    "env_key": "XAI_API_KEY"
  })
  configs.append({
    "name": "grok-4-0709-HighReasoning",
    "engine": "xai",
    "base_model": "grok-4-0709",
    "reasoning": 10,
    "tools": False,
    "env_key": "XAI_API_KEY"
  })
  configs.append({
    "name": "grok-4-0709",
    "engine": "xai",
    "base_model": "grok-4-0709",
    "reasoning": False,
    "tools": False,
    "env_key": "XAI_API_KEY"
  })

  # Anthropic models
  anthropic_base_models = ["claude-sonnet-4-5", "claude-opus-4-5"]
  for model in anthropic_base_models:
    configs.append({
      "name": model,
      "engine": "anthropic",
      "base_model": model,
      "reasoning": False,
      "tools": False,
      "env_key": "ANTHROPIC_API_KEY"
    })
    configs.append({
      "name": f"{model}-HighReasoning",
      "engine": "anthropic",
      "base_model": model,
      "reasoning": 10,
      "tools": False,
      "env_key": "ANTHROPIC_API_KEY"
    })
    configs.append({
      "name": f"{model}-Reasoning-Tools",
      "engine": "anthropic",
      "base_model": model,
      "reasoning": 10,
      "tools": True,
      "env_key": "ANTHROPIC_API_KEY"
    })

  # Amazon Bedrock models (Qwen, Llama, Mistral, etc.)
  # Qwen3 models on Bedrock
  bedrock_qwen_models = [
    ("qwen3-32B", "qwen.qwen3-32b-v1:0"),
    ("qwen3-VL-235B-22B", "qwen.qwen3-vl-235b-a22b"),
  ]
  for name, model_id in bedrock_qwen_models:
    configs.append({
      "name": name,
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": False,
      "tools": False,
      "region": "us-east-1",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

  # Llama models on Bedrock
  bedrock_llama_models = [
    ("llama3-70b-bedrock", "meta.llama3-70b-instruct-v1:0"),
    ("llama3-1-405b-bedrock", "meta.llama3-1-405b-instruct-v1:0"),
  ]
  for name, model_id in bedrock_llama_models:
    configs.append({
      "name": name,
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": False,
      "tools": False,
      "region": "us-west-2",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

  # Mistral models on Bedrock
  bedrock_mistral_models = [
    ("mistral-large-bedrock", "mistral.mistral-large-2402-v1:0"),
  ]
  for name, model_id in bedrock_mistral_models:
    configs.append({
      "name": name,
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": False,
      "tools": False,
      "region": "us-east-1",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

  nova_models = [("nova-lite", "amazon.nova-lite-v1:0"), ("nova-pro", "amazon.nova-pro-v1:0"),
                 ("nova-premier", "us.amazon.nova-premier-v1:0")]

  # Add Nova models to configs
  for name, model_id in nova_models:
    configs.append({
      "name": name,
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": False,
      "tools": False,
      "region": "us-east-1",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

    configs.append({
      "name": name + "-HighReasoning",
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": 10,
      "tools": False,
      "region": "us-east-1",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

    # With tools (code interpreter + web grounding)
    configs.append({
      "name": name + "-Reasoning-Tools",
      "engine": "bedrock",
      "base_model": model_id,
      "reasoning": False,
      "tools": True,
      "region": "us-east-1",
      "env_key": "AWS_ACCESS_KEY_ID"
    })

  return configs


def run_model_config(config: dict, test_filter: Optional[Set[int]] = None):
  """Run tests for a single model configuration."""
  name = config["name"]
  engine = config["engine"]

  # Check if required API key is available
  env_key = config.get("env_key")
  if env_key and not os.environ.get(env_key):
    print(f"Skipping {name}: {env_key} not set")
    return

  if engine == "placebo":
    import AiEnginePlacebo
    runAllTests(AiEnginePlacebo.PlaceboAIHook, name, test_filter)

  elif engine == "openai":
    import AiEngineOpenAiChatGPT
    AiEngineOpenAiChatGPT.Configure(config["base_model"], config["reasoning"], config["tools"])
    cacheLayer = cl(AiEngineOpenAiChatGPT.configAndSettingsHash,
                    AiEngineOpenAiChatGPT.ChatGPTAIHook, name)
    runAllTests(cacheLayer.AIHook, name, test_filter)

  elif engine == "gemini":
    import AiEngineGoogleGemini
    AiEngineGoogleGemini.Configure(config["base_model"], config["reasoning"], config["tools"])
    cacheLayer = cl(AiEngineGoogleGemini.configAndSettingsHash, AiEngineGoogleGemini.GeminiAIHook,
                    name)
    runAllTests(cacheLayer.AIHook, name, test_filter)

  elif engine == "xai":
    import AiEngineXAIGrok
    AiEngineXAIGrok.Configure(config["base_model"], config["reasoning"], config["tools"])
    cacheLayer = cl(AiEngineXAIGrok.configAndSettingsHash, AiEngineXAIGrok.GrokAIHook, name)
    runAllTests(cacheLayer.AIHook, name, test_filter)

  elif engine == "anthropic":
    import AiEngineAnthropicClaude
    AiEngineAnthropicClaude.Configure(config["base_model"], config["reasoning"], config["tools"])
    cacheLayer = cl(AiEngineAnthropicClaude.configAndSettingsHash,
                    AiEngineAnthropicClaude.ClaudeAIHook, name)
    runAllTests(cacheLayer.AIHook, name, test_filter)

  elif engine == "bedrock":
    import AiEngineAmazonBedrock
    AiEngineAmazonBedrock.Configure(config["base_model"], config["reasoning"], config["tools"],
                                    config.get("region", "us-east-1"))
    cacheLayer = cl(AiEngineAmazonBedrock.configAndSettingsHash,
                    AiEngineAmazonBedrock.BedrockAIHook, name)
    runAllTests(cacheLayer.AIHook, name, test_filter)


def parse_test_filter(test_arg: str) -> Set[int]:
  """Parse test filter argument into a set of test indices."""
  tests = set()
  for part in test_arg.split(","):
    part = part.strip()
    if "-" in part:
      start, end = part.split("-", 1)
      tests.update(range(int(start), int(end) + 1))
    else:
      tests.add(int(part))
  return tests


def run_setup():
  """
  Execute all test files (1.py, 2.py, ...) to download and build reference data.
  This triggers any asset downloads, reference model builds, etc. without running AI tests.
  """
  print("=" * 60)
  print("SETUP MODE: Building reference data and downloading assets")
  print("=" * 60)

  test_index = 1
  successful = 0
  failed = 0

  while True:
    test_file = f"{test_index}.py"
    if not os.path.exists(test_file):
      break

    print(f"\n[{test_index}] Loading {test_file}...")

    try:
      # Execute the test file to trigger any module-level setup
      test_globals = {}
      exec(open(test_file, encoding="utf-8").read(), test_globals)

      # Get test title if available
      title = test_globals.get("title", f"Test {test_index}")
      print(f"    Title: {title}")

      # If there's a setup function, call it
      if "setup" in test_globals:
        print(f"    Running setup()...")
        test_globals["setup"]()

      # If there's reference data generation, trigger it
      if "prepareSubpassReferenceScad" in test_globals:
        print(f"    Building OpenSCAD reference models...")
        subpass = 0
        while True:
          try:
            out = test_globals["prepareSubpassReferenceScad"](subpass)
            subpass += 1
            if out is None or out == "":
              break
          except StopIteration:
            break
          except Exception as e:
            print(f"    Warning: Reference build for subpass {subpass} failed: {e}")
            break
        print(f"    Built {subpass} reference models")

      successful += 1
      print(f"    ✓ OK")

    except Exception as e:
      print(f"    ✗ Error: {e}")
      failed += 1

    test_index += 1

  print("\n" + "=" * 60)
  print(f"SETUP COMPLETE: {successful} tests loaded, {failed} failed")
  print("=" * 60)

  if failed > 0:
    print(f"\nWarning: {failed} test(s) had errors during setup.")
    print("Some reference data may not be available.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run AI benchmark tests",
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog="""
Examples:
  python TestRunner.py                          # Run all tests on all available models
  python TestRunner.py --setup                  # Download/build reference data (run first!)
  python TestRunner.py --parallel               # Run all models in parallel
  python TestRunner.py --list-models            # List all available model names
  python TestRunner.py -t 1,2,3                 # Run only tests 1, 2, 3
  python TestRunner.py -t 5-10                  # Run tests 5 through 10
  python TestRunner.py -m gpt-5-nano            # Run only gpt-5-nano model
  python TestRunner.py -m "gpt-5-nano,gpt-5.1"  # Run multiple specific models
  python TestRunner.py -m "nova-*"              # Run all models matching wildcard pattern
  python TestRunner.py -m "*-HighReasoning"     # Run all HighReasoning variants
  python TestRunner.py -t 1 -m gpt-5-nano       # Run test 1 on gpt-5-nano only
  python TestRunner.py --force -m gpt-5-nano    # Re-run without using cached AI responses
        """)
  parser.add_argument(
    "-t",
    "--tests",
    type=str,
    help="Comma-separated list of test indices or ranges (e.g., '1,2,3' or '5-10' or '1,5-10,15')")
  parser.add_argument(
    "-m",
    "--models",
    type=str,
    help=
    "Comma-separated list of model names or patterns with wildcards (* and ?) to run (use --list-models to see available names)"
  )
  parser.add_argument("--list-models",
                      action="store_true",
                      help="List all available model names and exit")
  parser.add_argument("--force",
                      action="store_true",
                      help="Bypass AI response cache (still saves new responses to cache)")

  parser.add_argument("--offline",
                      action="store_true",
                      help="Only used cached results. Do not make any API calls.")

  parser.add_argument("--unskip", action="store_true", help="Run tests that are currently skipped.")

  parser.add_argument("--parallel", action="store_true", help="Run all models in parallel")

  parser.add_argument(
    "--setup",
    action="store_true",
    help=
    "Download and build all reference data without running tests. Execute all test files to trigger asset downloads/builds."
  )

  args = parser.parse_args()

  # Set force refresh flag in CacheLayer
  if args.force:
    import CacheLayer
    CacheLayer.FORCE_REFRESH = True
    print("Force mode: AI response cache will be bypassed (new responses still cached)")

  if args.offline:
    import CacheLayer
    CacheLayer.OFFLINE_MODE = True
    print("Offline mode: No API calls will be made, cache only.")

  if args.unskip: UNSKIP = True

  # Handle --setup mode: execute all test files to build reference data
  if args.setup:
    run_setup()
    exit(0)

  # Populate global for perfect score propagation hack
  all_configs = get_all_model_configs()
  ALL_MODEL_CONFIGS.clear()
  ALL_MODEL_CONFIGS.extend(all_configs)

  if args.parallel:
    if args.models: print("--parallel and --model aren't compatable")
    import sys
    args = sys.argv[1:]
    args.remove("--parallel")

    tasks = []
    for config in all_configs:
      tasks.append(subprocess.Popen([sys.executable, __file__, "-m", config["name"], *args]))
    for task in tasks:
      task.wait()
    exit(0)

  if args.list_models:
    print("Available models:")
    for config in all_configs:
      env_key = config.get("env_key")
      available = "✓" if (env_key is None or os.environ.get(env_key)) else f"✗ (needs {env_key})"
      print(f"  {available} {config['name']}")
    exit(0)

  # Parse test filter
  test_filter = None
  if args.tests:
    test_filter = parse_test_filter(args.tests)
    print(f"Running tests: {sorted(test_filter)}")

  # Parse model filter with wildcard support
  model_filter = None
  if args.models:
    import fnmatch
    all_model_names = [c["name"] for c in all_configs]
    patterns = [m.strip() for m in args.models.split(",")]
    matched_models = set()

    for pattern in patterns:
      # Check if pattern contains wildcards
      if '*' in pattern or '?' in pattern:
        matches = [
          name for name in all_model_names if fnmatch.fnmatch(name.lower(), pattern.lower())
        ]
        if not matches:
          print(f"Warning: Pattern '{pattern}' did not match any models")
        matched_models.update(matches)
      else:
        # Exact match (case-insensitive)
        exact_match = next((name for name in all_model_names if name.lower() == pattern.lower()),
                           None)
        if exact_match:
          matched_models.add(exact_match)
        else:
          print(f"Error: Model '{pattern}' not found. Use --list-models to see available models.")

    if not matched_models:
      print("No models matched. Exiting.")
      import sys
      sys.exit(1)

    model_filter = matched_models
    print(f"Running models: {sorted(model_filter)}")

  # Run selected configurations
  for config in all_configs:
    if model_filter and config["name"] not in model_filter:
      continue
    run_model_config(config, test_filter)
