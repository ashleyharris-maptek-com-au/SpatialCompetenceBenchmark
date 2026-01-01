import sys

sys.path.insert(0, '.')
from q9 import solve_small_hamilton

# 11x8 grid with blocked cells
cells = set()
for x in range(1, 12):
  for y in range(1, 9):
    cells.add((x, y))

blocked = {(3, 6), (5, 6), (3, 5), (5, 5), (7, 2), (8, 2)}
cells -= blocked

print(f'Testing {len(cells)} cells')
result = solve_small_hamilton(cells)
if result:
  print(f'Found solution with {len(result)} cells!')
else:
  print('No solution found')
