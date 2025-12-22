import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        return {
                "tetrahedra": [
                        {
                                "x": -1.500000, "y": 2.598076, "z": 0.000000, "q0": 0.000000, "q1": 0.000000, "q2":
                                0.000000, "q3": 1.000000
                        },
                ]
        }, "Placebo thinking... hmmm..."


    return None
