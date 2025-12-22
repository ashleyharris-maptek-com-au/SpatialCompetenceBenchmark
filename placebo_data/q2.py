import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        return {
                "bricks": [{"Centroid": [0, 48, 4.8], "RotationDegrees":
                                        0}, {"Centroid": [0, -48, 4.8], "RotationDegrees":
                                                  0}, {"Centroid": [0, 64, 4.8], "RotationDegrees":
                                                            0}, {"Centroid": [0, -64, 4.8], "RotationDegrees":
                                                                      0}, {"Centroid": [32, 32, 4.8], "RotationDegrees":
                                                                                0}, {"Centroid": [32, 48, 4.8], "RotationDegrees":
                                                                                          0}, {"Centroid": [32, -32, 4.8], "RotationDegrees": 0},
                                      {"Centroid": [32, -48, 4.8], "RotationDegrees":
                                        0}, {"Centroid": [-32, 32, 4.8], "RotationDegrees":
                                                  0}, {"Centroid": [-32, 48, 4.8], "RotationDegrees":
                                                            0}, {"Centroid": [-32, -32, 4.8], "RotationDegrees":
                                                                      0}, {"Centroid": [-32, -48, 4.8], "RotationDegrees":
                                                                                0}, {"Centroid": [64, 0, 4.8], "RotationDegrees":
                                                                                          0}, {"Centroid": [-64, 0, 4.8], "RotationDegrees": 0},
                                      {"Centroid": [64, 16, 4.8], "RotationDegrees":
                                        0}, {"Centroid": [64, -16, 4.8], "RotationDegrees":
                                                  0}, {"Centroid": [-64, 16, 4.8], "RotationDegrees":
                                                            0}, {"Centroid": [-64, -16, 4.8], "RotationDegrees":
                                                                      0}, {"Centroid": [48, 0, 14.4], "RotationDegrees":
                                                                                90}, {"Centroid": [-48, 0, 14.4], "RotationDegrees": 90},
                                      {"Centroid": [64, 0, 14.4], "RotationDegrees":
                                        90}, {"Centroid": [-64, 0, 14.4], "RotationDegrees":
                                                    90}, {"Centroid": [32, 32, 14.4], "RotationDegrees":
                                                                90}, {"Centroid": [32, -32, 14.4], "RotationDegrees":
                                                                            90}, {"Centroid": [-32, 32, 14.4], "RotationDegrees": 90},
                                      {"Centroid": [-32, -32, 14.4], "RotationDegrees":
                                        90}, {"Centroid": [48, 32, 14.4], "RotationDegrees":
                                                    90}, {"Centroid": [48, -32, 14.4], "RotationDegrees":
                                                                90}, {"Centroid": [-48, 32, 14.4], "RotationDegrees":
                                                                            90}, {"Centroid": [-48, -32, 14.4], "RotationDegrees":
                                                                                        90}, {"Centroid": [0, 64, 14.4], "RotationDegrees": 90},
                                      {"Centroid": [0, -64, 14.4], "RotationDegrees":
                                        90}, {"Centroid": [16, 64, 14.4], "RotationDegrees":
                                                    90}, {"Centroid": [16, -64, 14.4], "RotationDegrees":
                                                                90}, {"Centroid": [-16, 64, 14.4], "RotationDegrees":
                                                                            90}, {"Centroid": [-16, -64, 14.4], "RotationDegrees":
                                                                                        90}, {"Centroid": [0, 32, 24.0], "RotationDegrees": 0},
                                      {"Centroid": [0, -32, 24.0], "RotationDegrees":
                                        0}, {"Centroid": [0, 48, 24.0], "RotationDegrees":
                                                  0}, {"Centroid": [0, -48, 24.0], "RotationDegrees":
                                                            0}, {"Centroid": [0, 64, 24.0], "RotationDegrees":
                                                                      0}, {"Centroid": [0, -64, 24.0], "RotationDegrees":
                                                                                0}, {"Centroid": [32, 0, 24.0], "RotationDegrees":
                                                                                          0}, {"Centroid": [-32, 0, 24.0], "RotationDegrees": 0},
                                      {"Centroid": [32, 16, 24.0], "RotationDegrees":
                                        0}, {"Centroid": [32, -16, 24.0], "RotationDegrees":
                                                  0}, {"Centroid": [-32, 16, 24.0], "RotationDegrees":
                                                            0}, {"Centroid": [-32, -16, 24.0], "RotationDegrees":
                                                                      0}, {"Centroid": [32, 32, 24.0], "RotationDegrees":
                                                                                0}, {"Centroid": [32, -32, 24.0], "RotationDegrees": 0},
                                      {"Centroid": [-32, 32, 24.0], "RotationDegrees":
                                        0}, {"Centroid": [-32, -32, 24.0], "RotationDegrees":
                                                  0}, {"Centroid": [32, 48, 24.0], "RotationDegrees":
                                                            0}, {"Centroid": [32, -48, 24.0], "RotationDegrees":
                                                                      0}, {"Centroid": [-32, 48, 24.0], "RotationDegrees":
                                                                                0}, {"Centroid": [-32, -48, 24.0], "RotationDegrees":
                                                                                          0}, {"Centroid": [64, 0, 24.0], "RotationDegrees": 0},
                                      {"Centroid": [-64, 0, 24.0], "RotationDegrees":
                                        0}, {"Centroid": [32, 0, 33.6], "RotationDegrees":
                                                  90}, {"Centroid": [-32, 0, 33.6], "RotationDegrees":
                                                              90}, {"Centroid": [48, 0, 33.6], "RotationDegrees":
                                                                          90}, {"Centroid": [-48, 0, 33.6], "RotationDegrees":
                                                                                      90}, {"Centroid": [0, 32, 33.6], "RotationDegrees": 90},
                                      {"Centroid": [0, -32, 33.6], "RotationDegrees":
                                        90}, {"Centroid": [16, 32, 33.6], "RotationDegrees":
                                                    90}, {"Centroid": [16, -32, 33.6], "RotationDegrees":
                                                                90}, {"Centroid": [-16, 32, 33.6], "RotationDegrees":
                                                                            90}, {"Centroid": [-16, -32, 33.6], "RotationDegrees": 90
                                                                                        }, {"Centroid": [32, 32, 33.6], "RotationDegrees": 90},
                                      {"Centroid": [32, -32, 33.6], "RotationDegrees":
                                        90}, {"Centroid": [-32, 32, 33.6], "RotationDegrees":
                                                    90}, {"Centroid": [-32, -32, 33.6], "RotationDegrees":
                                                                90}, {"Centroid": [48, 32, 33.6], "RotationDegrees":
                                                                            90}, {"Centroid": [48, -32, 33.6], "RotationDegrees": 90
                                                                                        }, {"Centroid": [-48, 32, 33.6], "RotationDegrees": 90},
                                      {"Centroid": [-48, -32, 33.6], "RotationDegrees":
                                        90}, {"Centroid": [0, 0, 43.2], "RotationDegrees":
                                                    0}, {"Centroid": [0, 16, 43.2], "RotationDegrees":
                                                              0}, {"Centroid": [0, -16, 43.2], "RotationDegrees":
                                                                        0}, {"Centroid": [0, 32, 43.2], "RotationDegrees":
                                                                                  0}, {"Centroid": [0, -32, 43.2], "RotationDegrees":
                                                                                            0}, {"Centroid": [0, 48, 43.2], "RotationDegrees": 0},
                                      {"Centroid": [0, -48, 43.2], "RotationDegrees":
                                        0}, {"Centroid": [32, 0, 43.2], "RotationDegrees":
                                                  0}, {"Centroid": [-32, 0, 43.2], "RotationDegrees":
                                                            0}, {"Centroid": [32, 16, 43.2], "RotationDegrees":
                                                                      0}, {"Centroid": [32, -16, 43.2], "RotationDegrees":
                                                                                0}, {"Centroid": [-32, 16, 43.2], "RotationDegrees": 0},
                                      {"Centroid": [-32, -16, 43.2], "RotationDegrees":
                                        0}, {"Centroid": [32, 32, 43.2], "RotationDegrees":
                                                  0}, {"Centroid": [32, -32, 43.2], "RotationDegrees":
                                                            0}, {"Centroid": [-32, 32, 43.2], "RotationDegrees":
                                                                      0}, {"Centroid": [-32, -32, 43.2], "RotationDegrees":
                                                                                0}, {"Centroid": [0, 0, 52.8], "RotationDegrees": 90},
                                      {"Centroid": [16, 0, 52.8], "RotationDegrees":
                                        90}, {"Centroid": [-16, 0, 52.8], "RotationDegrees":
                                                    90}, {"Centroid": [32, 0, 52.8], "RotationDegrees":
                                                                90}, {"Centroid": [-32, 0, 52.8], "RotationDegrees":
                                                                            90}, {"Centroid": [0, 32, 52.8], "RotationDegrees": 90},
                                      {"Centroid": [0, -32, 52.8], "RotationDegrees":
                                        90}, {"Centroid": [16, 32, 52.8], "RotationDegrees":
                                                    90}, {"Centroid": [16, -32, 52.8], "RotationDegrees":
                                                                90}, {"Centroid": [-16, 32, 52.8], "RotationDegrees":
                                                                            90}, {"Centroid": [-16, -32, 52.8], "RotationDegrees": 90
                                                                                        }, {"Centroid": [32, 32, 52.8], "RotationDegrees": 90},
                                      {"Centroid": [32, -32, 52.8], "RotationDegrees":
                                        90}, {"Centroid": [-32, 32, 52.8], "RotationDegrees":
                                                    90}, {"Centroid": [-32, -32, 52.8], "RotationDegrees":
                                                                90}, {"Centroid": [0, 0, 62.4], "RotationDegrees":
                                                                            0}, {"Centroid": [0, 16, 62.4], "RotationDegrees":
                                                                                      0}, {"Centroid": [0, -16, 62.4], "RotationDegrees": 0}],
                "Reasoning":
                "I generated this from the Gemini 2.5 pro API playground while developing the test. It's a bit 'meh'"
        }, "Placebo thinking... hmmm..."

    if subPass == 1:

        bricks = []

        for x in range(-120, 120, 32):
            for y in range(-120, 120, 16):
                for zBy10 in range(48, 1300, 96):
                    z = zBy10 / 10
                    dist = math.sqrt(x * x + y * y + z * z)
                    if dist > 80 and dist < 110:
                        bricks.append({"Centroid": [x, y, z], "RotationDegrees": 0})

        return {
                "bricks": bricks,
        }, ""

    if subPass == 2:

        bricks = []

        for x in range(-200, 200, 32):
            for y in range(-200, 200, 16):
                for zBy10 in range(48, 2000, 96):
                    z = zBy10 / 10
                    dist = math.sqrt(x * x + y * y + z * z)
                    if dist > 150 and dist < 170:
                        bricks.append({"Centroid": [x, y, z], "RotationDegrees": 0})

        return {
                "bricks": bricks,
        }, ""


    return None
