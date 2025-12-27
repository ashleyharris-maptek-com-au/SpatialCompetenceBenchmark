import sys

sys.path.insert(0, '.')
import importlib
import placebo_data.q22 as q22

importlib.reload(q22)

import importlib.util

spec = importlib.util.spec_from_file_location('grader22', '22.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

# Test subPass 4 and 5 (8 and 10 stations - previously used greedy)
for subPass in [4, 5]:
  print(f"\n=== SubPass {subPass} ({grader.MISSION_LENGTHS[subPass]} stations) ===")
  try:
    result, reasoning = q22.get_response(subPass)
    print(f"Solver: {reasoning}")
    score, grade_reason = grader._gradeAnswerImpl(result, subPass, 'Placebo')
    print(f"Score: {score:.3f}")
    print(f"Grader: {grade_reason.strip()}")
  except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
