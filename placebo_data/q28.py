import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if True:  # Catch-all for any subpass
        g = {}
        exec(open("28.py").read(), g)
        sizes = g["sizes"]
        size = sizes[subPass]

        heightMap = g["heightMaps"][subPass]

        averageHeight = sum(map(sum, heightMap)) / (size * size)

        blasts = []
        for x in range(size):
            for y in range(size):
                if heightMap[x][y] > averageHeight + 1:
                    blasts.append({"x": x, "y": y, "z": heightMap[x][y] - averageHeight})

        blasts.sort(key=lambda b: b["z"], reverse=False)

        return {"blasts": blasts}, "Blast our way up the hillsides from the middle"


    return None
