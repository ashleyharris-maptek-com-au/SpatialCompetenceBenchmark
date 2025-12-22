import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if True:  # Catch-all for any subpass
        # Question 1
        return {
                "pipes": [{"xCentre": 0, "yCentre": 0, "rotationDegrees":
                                      0}, {"xCentre": -2.55, "yCentre": 2.5, "rotationDegrees":
                                                90}, {"xCentre": 2.55, "yCentre": 2.5, "rotationDegrees":
                                                            90}, {"xCentre": -2.55, "yCentre": -2.5, "rotationDegrees": 90},
                                    {"xCentre": 2.55, "yCentre": -2.5, "rotationDegrees": 90}], "Reasoning":
                "This was manually calculated. Half of 10cm is 5cm, so the 10cm wide pipes center is offset by 5cm."
        }, "Placebo thinking... hmmm..."


    return None
