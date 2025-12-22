import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        return {
                "hole": {"transform": [math.sqrt(0.25),
                                                              math.sqrt(0.25),
                                                              math.sqrt(0.25),
                                                              math.sqrt(0.5)]}, "solid": {"transform": [0, 0, 0, 1]}
        }, "Placebo thinking... hmmm..."


    return None
