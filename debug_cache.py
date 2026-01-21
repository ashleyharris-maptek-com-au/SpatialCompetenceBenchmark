import sys

sys.path.insert(0, 'placebo_data')
from q9 import get_blocked_cells, find_cached_subproblems_in_puzzle, format_cells_ascii_art

blocked = get_blocked_cells(5)
print('Blocked cells:', sorted(blocked))

all_cells = {(x, y) for x in range(1, 17) for y in range(1, 17)} - blocked
matches = find_cached_subproblems_in_puzzle(all_cells, blocked, 16)

print(f'\nFound {len(matches)} cache matches:')
for i, (cells, blocked_subset, solution) in enumerate(matches):
  print(f'\nMatch {i}: {len(cells)} cells')
  print(f'  Blocked in pattern: {sorted(blocked_subset)}')
  xs = [c[0] for c in cells]
  ys = [c[1] for c in cells]
  print(f'  x range: {min(xs)}-{max(xs)}, y range: {min(ys)}-{max(ys)}')
  print('  Pattern visualization:')
  print(format_cells_ascii_art(cells, blocked_subset, 16))
