import math, sys,os,random
from textwrap import dedent

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

problem7 = importlib.import_module("7")

testParams = problem7.testParams

def get_response(subPass: int):
    """Get the placebo response for this question."""
    params = testParams[subPass]

    size = params["size"]
    a_height = params["a_height"]
    b_height = params["b_height"]
    required_jumps = params["required_jumps"]
    summary = params["summary"]

    print("Path params:", params)

    # Solve it in 1D to start with:
    if a_height == b_height:
        path = [a_height] * 2
    elif a_height < b_height:
        path = list(range(a_height, b_height + 1))
    else:
        path = list(range(a_height, b_height - 1, -1))

    print("1D path without anything interesting:", path)

    minSize = size * size * 0.2

    # for larger sizes, it's better to have a longer path
    if size >= 15:
        minSize += size * 2
    if size >= 25:
        minSize += size * 2

    while len(path) < minSize:
        # Add random noise in the path. We intentionally don't add values > 7
        # so that 9 can be added to ensure shortcut jumps are not possible.
        pivot = random.randint(1, len(path) - 1)
        path.insert(pivot, random.randint(0, 7))

        # Find any differences > 1 and insert a value between them
        # to make it smooth.
        while True:
            changed = False
            for i in range(len(path) - 1):
                if abs(path[i] - path[i + 1]) > 1:
                    path.insert(i + 1, (path[i] + path[i + 1]) // 2)
                    changed = True
            if not changed:
                break

    print("1D path without jumps:", path)

    # Path is now the minimum length. Now lets add jumps
    jumpsAdded = 0
    while jumpsAdded < required_jumps:
        # Find a random position in the path
        pivot = random.randint(1, len(path) - 2)

        heightBefore = path[pivot - 1]
        heightAfter = path[pivot]

        if heightBefore < 2 or heightAfter < 2:
            # We can't add a jump this close to the ground, try again
            continue

        # Add a jump over the ground
        path.insert(pivot, 0)

        # Now if we were climbing stairs, we need to add the height back in
        if heightBefore != heightAfter:
            path.insert(pivot + 1, heightBefore)

        jumpsAdded += 1
    
    print("1D path with jumps:", path)
    
    path = ["A"] + path + ["B"]

    print("1D path finished:", path)

    grid = [["*"] * size for _ in range(size)]
    
    # Now lay the 1D path out in a serpentine pattern, traveling up and down odd rows only.
    for y in range(0, size, 2):
      if len(path) < size:
        path = [path[0]] * (size - len(path)) + path

      if y % 4 == 0:
        grid[y] = path[0:size]
      else:
        grid[y] = path[0:size][::-1]
      
      if len(path) == size:
        break
      
      # We've used up some of the path, so remove those elements
      # but keep the last element to connect to the next row
      path = path[size -1 :]

      if len(path) == 0: break

      # Now add an extra jump in between the rows
      grid[y+1] = list(grid[y+1])
      jumpOver = 0
      if path[0] > 3:
        jumpOver = path[0] - 2
      if (y) % 4 == 0:
        grid[y+1][-1] = jumpOver
      else:
        grid[y+1][0] = jumpOver

      if path[0] == 0 and path[1] > 1:
        # we just added a 3-wide jump around a corner. whoops.
        # make it a shortcut jump instead.
        if y % 4 == 0:
            grid[y+1][-1] = '*'
            grid[y+1][-2] = 0
        else:
            grid[y+1][0] = '*'
            grid[y+1][1] = 0

    print("Grid after laying out path:")
    for row in grid:
        print(str(" ".join(str(cell) for cell in row)))

    # Now we just need to add random obstacles to fill the grid, taking care that each
    # obsticles height is at least 2 away from all adjacent heights.
    # We do this as a 2 pass process because we only care about being away from the path
    # not away from other obstacles, and if we care about other obsticles with 4 neighbours
    # we could have no valid choices.
    def _cell_value(cell):
        if cell == "A":
            return a_height
        if cell == "B":
            return b_height
        if isinstance(cell, int):
            return cell
        if isinstance(cell, str) and cell.isdigit():
            return int(cell)
        return None

    replacements = {}
    star_positions = []
    for y in range(size):
        for x in range(size):
            if grid[y][x] == "*":
                star_positions.append((x, y))

    for x, y in star_positions:
        neighbor_values = []
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx = x + dx
            ny = y + dy
            if 0 <= nx < size and 0 <= ny < size:
                val = _cell_value(grid[ny][nx])
                if val is not None:
                    neighbor_values.append(val)

        duplicate_floor = None
        if neighbor_values:
            counts = {}
            for neighbor in neighbor_values:
                counts[neighbor] = counts.get(neighbor, 0) + 1
            duplicate_values = [value for value, count in counts.items() if count >= 2]
            if duplicate_values:
                duplicate_floor = max(duplicate_values)

        allowed = [
            value for value in range(10)
            if all(abs(value - neighbor) >= 2 for neighbor in neighbor_values)
            and (duplicate_floor is None or value >= duplicate_floor)
        ]

        if not allowed:
            candidate_pool = range(10)
            if duplicate_floor is not None:
                candidate_pool = range(duplicate_floor, 10)
            if neighbor_values:
                fallback = max(
                    candidate_pool,
                    key=lambda value: min(abs(value - neighbor) for neighbor in neighbor_values)
                )
            else:
                fallback = random.choice(candidate_pool)
            replacements[(x, y)] = fallback
        else:
            replacements[(x, y)] = random.choice(allowed)

    for (x, y), value in replacements.items():
        grid[y][x] = value

    print("Grid after adding obstacles:")
    for row in grid:
        print(str(" ".join(str(cell) for cell in row)))

    out = ""
    for row in grid:
        out += "".join(str(cell) for cell in row) + "\n"
    out = out.strip()

    return out, "This is about 150 lines of python - solves in 1D and then serpentines the path"

    if subPass == 0:
        return dedent("""
                        A5650
                        2B201
                        30150
                        45441
                        91912
                """.strip("\n")), "Placebo thinking... hmmm..."

    if subPass == 1:
        return dedent("""
                A120234145
                9876581206
                8395062907
                9012345094
                7777777777
                4321050432
                7888888888
                0123456029
                9054321096
                314205631B
                """.strip("\n")), "Placebo thinking... hmmm..."

    if subPass == 2:
        return dedent("""
                789321505057893
                21A789032150505
                780932551789320
                175058903217895
                321708950505530
                217859321789035
                217809321750580
                932150505708935
                505217890352170
                085932175809B05
                530217890352178
                095050505302178
                593217893251789
                032178932107893
                505050505052178
                """.strip("\n")), "Placebo thinking... hmmm..."

    if subPass == 3:
        return dedent("""
                A0505050505050505051
                92939798919293979801
                50505050505050505052
                03979891929397989192
                50505050505050505053
                97989192939798919203
                50505050505050505057
                08919293979891929397
                50505050505050505058
                91929397989192939708
                50505050505050505051
                02939798919293979891
                50505050505050505052
                93979891929397989102
                B0505050505050505053
                78123781237812378123
                78123781237812378123
                78123781237812378123
                78123781237812378123
                78123781237812378123
                """.strip("\n")), "Placebo thinking... hmmm..."

    if subPass == 4:
        return dedent("""
                A432234322345432234554322
                7897897897897897897897890
                2234554322345543223455432
                0789789789789789789789789
                2345543345543223455432234
                7897897897897897897897890
                3223455432234554322345554
                0789789789789789789789789
                3455432223455432234554322
                7897897897897897897897890
                2234554322345543223455432
                0789789789789789789789789
                2345543345543223455432234
                7897897897897897897897890
                3223455432234554322345554
                0789789789789789789789789
                3455432223455432234554322
                7897897897897897897897890
                2234554322345543223455432
                0789789789789789789789789
                2345543345543223455432234
                7897897897897897897897890
                3223455432234554322345554
                0789789789789789789789789
                345543222345543223455445B
                """.strip("\n")), "Placebo thinking... hmmm..."

    if subPass == 5:
        return dedent("""
                A43223333344444444443333322222
                778967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                222223333344444444443333322222
                678967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                222223333344444444443333322222
                678967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                222223333344444444443333322222
                678967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                222223333344444444443333322222
                678967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                222223333344444444443333322222
                678967896789678967896789678960
                222223333344444444443333322222
                078967896789678967896789678967
                22222333334444444444333332221B
                678967896789678967896789678967
                678967896789678967896789678967
                678967896789678967896789678967
                678967896789678967896789678967
                678967896789678967896789678967
                """.strip("\n")), "Placebo thinking... hmmm..."


    return None

if __name__ == "__main__":
    print(get_response(1))
