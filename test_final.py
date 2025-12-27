import sys

sys.path.insert(0, '.')
import importlib
import placebo_data.q22 as q22

importlib.reload(q22)

import importlib.util

spec = importlib.util.spec_from_file_location('grader22', '22.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

print('Testing all subPasses:')
total_score = 0
for subPass in range(6):
  result, reasoning = q22.get_response(subPass)
  score, _ = grader._gradeAnswerImpl(result, subPass, 'Test')
  total_score += score
  print(f'  SubPass {subPass}: {score:.3f}')
print(f'Total Score: {total_score:.1f}/6')
