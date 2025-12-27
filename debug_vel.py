import sys

sys.path.insert(0, '.')
import importlib
import placebo_data.q22 as q22

importlib.reload(q22)

import importlib.util

spec = importlib.util.spec_from_file_location('grader22', '22.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

# Test multiple subPasses
for subPass in range(6):
  numStations = grader.MISSION_LENGTHS[subPass]
  print(f"\nSubPass {subPass} ({numStations} stations):")
  try:
    result, reasoning = q22.get_response(subPass)
    score, grade_reason = grader._gradeAnswerImpl(result, subPass, 'Test')
    print(f"Score: {score:.3f} - {grade_reason.strip().split(chr(10))[0]}")
  except Exception as e:
    print(f"Error: {e}")
