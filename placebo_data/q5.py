import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        # Question 5 subpass 0
        return {
                'maze':
                dedent("""
                        ################
                        #A..#...#.....##
                        ###.#.#.#.###.##
                        # #...#.#.# #.##
                        # #####.#.# #.##
                        #.....#...#...##
                        #.###.#####.####
                        #..B#...#...# ##
                        #######.#.### ##
                        #.......#.....##
                        #.###########.##
                        #.....#.......##
                        # ###.#.########
                        #   #...      ##
                        ################
                        ################
                                """).strip()
        }, "Placebo thinking... hmmm..."

    if True:  # Catch-all for any subpass
        sizes = [16, 32, 64, 128]
        size = sizes[subPass]
        grid = [list("#" * size) for _ in range(size)]
        x_min, x_max = 1, size - 2
        y_min, y_max = 1, size - 2

        path = []
        y = y_min
        go_right = True
        while y <= y_max:
            if go_right:
                for x in range(x_min, x_max + 1):
                    path.append((x, y))
                if y + 2 <= y_max:
                    path.append((x_max, y + 1))
                    path.append((x_max, y + 2))
            else:
                for x in range(x_max, x_min - 1, -1):
                    path.append((x, y))
                if y + 2 <= y_max:
                    path.append((x_min, y + 1))
                    path.append((x_min, y + 2))
            y += 2
            go_right = not go_right

        for (x, y) in path:
            grid[y][x] = "."
        if path:
            ax, ay = path[0]
            bx, by = path[-1]
            grid[ay][ax] = "A"
            grid[by][bx] = "B"

        maze = "\n".join("".join(row) for row in grid)
        return {"maze": maze}, "Placebo thinking... hmmm..."


    return None
