skip = True

title = "Solar system sandbox"

prompt = """
You are playing the role of God, and are building the solar system inside.

Mass of star: 10^30 kg. Consider a planet destroyed if it passes within 10 million km.

Planets: 
- 3 planets each 10^24 kg and ~15,000km in diameter (named Alice, Bob, and Carol)
- 2 planets each 10^25 kg and ~40,000km in diameter (named Dave and Eve)
- 2 planets each 10^26 kg and ~100,000km in diameter (named Frank and Grace)

The star's centre is the origin of the coordinate system. All coordinates are in km.

Lay out a star and 7 planets such that:

TWIST

"""

structure = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "positionXyzInKm": {
                "type": "array",
                "items": {
                    "type": "number"
                }
            },
            "velocityXyzInKm": {
                "type": "array",
                "items": {
                    "type": "number"
                }
            },
            "name": {
                "type": "string"
            }
        },
        "propertyOrdering": ["positionXyzInKm", "velocityXyzInKm", "name"],
        "required": ["positionXyzInKm", "velocityXyzInKm", "name"],
        "additionalProperties": False
    }
}


def prepareSubpassPrompt(index: int) -> str:
    if index == 0:
        return prompt.replace(
            "TWIST",
            "The system is stable for at least 100 years of simulated N-body physics."
        )
    if index == 1:
        return prompt.replace(
            "TWIST",
            "All planets orbit in different planes and the system is stable for at least 200 years of simulated N-body physics."
        )
    if index == 2:
        return prompt.replace(
            "TWIST",
            "No impacts occur for at least 50 years of simulated N-body physics, and then at least one impact occurs before the 60th year."
        )
    if index == 3:
        return prompt.replace(
            "TWIST",
            "All planets are stable except one, which must complete at least 100 orbits before slamming into the sun (and nothing else)."
        )
    if index == 4:
        return prompt.replace(
            "TWIST",
            "Frank and Grace are a binary pair, and spend at least 100 years within 10 million km"
        )
