import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        return {
                "voxels":
                [{"xyz": [0, 0, 0]}, {"xyz": [0, 0, 1]}, {"xyz": [0, 0, 2]}, {"xyz": [0, 0, 3]},
                  {"xyz": [0, 0, 4]}, {"xyz": [0, 0, 5]}, {"xyz": [0, 1, 0]}, {"xyz": [0, 1, 1]},
                  {"xyz": [0, 1, 2]}, {"xyz": [0, 1, 3]}, {"xyz": [0, 1, 4]}, {"xyz": [0, 1, 5]},
                  {"xyz": [0, 2, 0]}, {"xyz": [0, 2, 1]}, {"xyz": [0, 2, 2]}, {"xyz": [0, 2, 3]},
                  {"xyz": [0, 2, 4]}, {"xyz": [0, 3, 3]}, {"xyz": [0, 4, 4]}, {"xyz": [0, 5, 5]},
                  {"xyz": [1, 0, 1]}, {"xyz": [1, 1, 2]}, {"xyz": [1, 2, 3]}, {"xyz": [1, 3, 4]},
                  {"xyz": [1, 4, 5]}, {"xyz": [1, 5, 0]}, {"xyz": [2, 0, 2]}, {"xyz": [2, 1, 3]},
                  {"xyz": [2, 2, 4]}, {"xyz": [2, 3, 5]}, {"xyz": [2, 4, 0]}, {"xyz": [2, 5, 1]},
                  {"xyz": [3, 0, 3]}, {"xyz": [3, 1, 4]}, {"xyz": [3, 2, 5]}, {"xyz": [3, 3, 0]},
                  {"xyz": [3, 4, 1]}, {"xyz": [3, 5, 2]}, {"xyz": [4, 0, 4]}, {"xyz": [4, 1, 5]}, {
                          "xyz": [4, 2, 0]
                  }, {"xyz": [4, 3, 1]}, {"xyz": [4, 4, 2]}, {"xyz": [4, 5, 3]}, {"xyz": [5, 0, 5]},
                  {"xyz": [5, 1, 0]}, {"xyz": [5, 2, 1]}, {"xyz": [5, 3, 2]}, {"xyz":
                                                                                                                                            [5, 4,
                                                                                                                                              3]}, {"xyz": [5, 5, 4]}]
        }, "Placebo thinking... hmmm..."

    if True:  # Catch-all for any subpass
        sizes = [6, 8, 12, 16, 24, 24]
        counts = [50, 100, 200, 400, 1000, 500]
        size = sizes[subPass]
        count = counts[subPass]
        voxels = []

        for y in range(size):
            for x in range(size):
                for z in range(size):
                    if x + y + z % size == 0:
                        if subPass == 5 and "7" in str(x + y + z): continue
                        voxels.append({"xyz": [x, y, z]})

        while len(voxels) < count:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            z = random.randint(0, size - 1)
            if subPass == 5 and "7" in str(x + y + z): continue
            element = {"xyz": [x, y, z]}
            if element not in voxels:
                voxels.append(element)

        return {"voxels": voxels}, "Placebo thinking... hmmm..."


    return None
