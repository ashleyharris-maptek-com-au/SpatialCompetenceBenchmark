import sys

sys.path.insert(0, '..')
from q21 import get_response
import importlib.util

spec = importlib.util.spec_from_file_location('q21_grader', '../21.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

for sp in range(6):
  answer, _ = get_response(sp)
  score, reasoning = grader.gradeAnswer(answer, sp, 'test')
  print(f'=== subPass {sp} ===')
  print('Score:', score)
  print('Reasoning:', reasoning[:500])
  print()
print('Score:', score)
print('Reasoning:', reasoning)
