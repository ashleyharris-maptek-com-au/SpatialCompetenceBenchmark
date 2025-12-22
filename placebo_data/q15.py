import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if True:  # Catch-all for any subpass
        # A rather poor tetris run:

        def block(x):
            b = [
                    {"translationCount": x, "rotationCount": 3},
                    {"translationCount": x + 1, "rotationCount": 1},
            ]
            b.extend(b)
            b.extend(b)
            return b

        basicBlocks = block(0) + block(2) + block(4) + block(6) + block(8)

        if subPass == 1:
            basicBlocks.extend([
                    {"translationCount": 13, "rotationCount": 2},
                    {"translationCount": 10, "rotationCount": 0},
            ] * 6)
            basicBlocks.extend(block(14))

        if subPass >= 2:
            basicBlocks.extend(block(10))
            basicBlocks.extend(block(12))
            basicBlocks.extend(block(14))
            basicBlocks.extend(block(16))
            basicBlocks.extend(block(18))

        if subPass >= 3:
            basicBlocks.extend(block(20))
            basicBlocks.extend(block(22))
            basicBlocks.extend(block(24))
            basicBlocks.extend(block(26))
            basicBlocks.extend(block(28))
            basicBlocks.extend(block(30))
            basicBlocks.extend(block(32))
            basicBlocks.extend(block(34))
            basicBlocks.extend(block(36))
            basicBlocks.extend(block(38))

        return {"moves": basicBlocks}, "Placebo thinking... hmmm..."


    return None
