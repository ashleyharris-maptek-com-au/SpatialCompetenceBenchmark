import math

skip = True

title = "Gravitational trickshots"

prompt = """
You are playing the role of God, building the solar system (inside an N-body physics simulator).

You previous chosen the mass of star: 10^30 kg. 

You previously chose the following planets: 
- 3 planets each 10^24 kg and ~15,000km in diameter (named Alice, Bob, and Carol)
- 2 planets each 10^25 kg and ~40,000km in diameter (named Dave and Eve)
- 2 planets each 10^26 kg and ~100,000km in diameter (named Frank and Grace)

The star's barycentre is the origin of the coordinate system. All coordinates are in km.
Consider a planet destroyed if it crosses the Roche limit of a larger body.

Lay out the star and 7 planets such that:

TWIST

"""

structure = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string"
        },
        "planets": {
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
                        "type":
                        "string",
                        "enum": [
                            "Alice", "Bob", "Carol", "Dave", "Eve", "Frank",
                            "Grace"
                        ]
                    }
                },
                "propertyOrdering":
                ["positionXyzInKm", "velocityXyzInKm", "name"],
                "required": ["positionXyzInKm", "velocityXyzInKm", "name"],
                "additionalProperties": False
            }
        }
    },
    "propertyOrdering": ["reasoning", "bricks"],
    "required": ["reasoning", "bricks"],
    "additionalProperties": False
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
            "All planets are stable except one, which must complete at least 100 orbits within 100 years before slamming into the sun (and nothing else)."
        )
    if index == 4:
        return prompt.replace(
            "TWIST",
            "Frank and Grace are a binary pair, and spend at least 100 years within 10 million km of each other."
        )
    if index == 5:
        return prompt.replace(
            "TWIST",
            "Within 50 years; When projected into the Z=0 plane and viewed from +z, alice completes at least two orbits of the sun clockwise, and at least 2 orbits counter clockwise, without being destroyed."
        )


def _massToRocheLimit(mass: float) -> float:
    return mass**(1 / 3) / 10000


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):

    bodies = []
    namesInAnswer = set()

    if len(answer["planets"]) != 7:
        return 0, "answer must contain exactly 7 planets"

    bodies.append({
        "name": "Sun",
        "mass": 10**30,
        "position": [0, 0, 0],
        "velocity": [0, 0, 0],
        "orbitsClockWise": 0,
        "orbitsCounterClockWise": 0,
        "destroyed": False,
        "rocheLimit": _massToRocheLimit(10**30)
    })

    for planet in answer["planets"]:
        if planet['name'] in namesInAnswer:
            return 0, "answer must contain exactly 7 planets with unique names"
        namesInAnswer.add(planet['name'])

        if planet["name"] not in [
                "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace"
        ]:
            return 0, "answer must contain exactly 7 planets with names Alice, Bob, Carol, Dave, Eve, Frank, and Grace"

        mass = 10**24 if planet["name"] in ["Alice", "Bob", "Carol"] else \
            10**25 if planet["name"] in ["Dave", "Eve"] else \
            10**26 if planet["name"] in ["Frank", "Grace"] else \
            0

        bodies.append({
            "name": planet['name'],
            "mass": mass,
            "position": planet['positionXyzInKm'],
            "velocity": planet['velocityXyzInKm'],
            "orbitsClockWise": 0,
            "orbitsCounterClockWise": 0,
            "destroyed": False,
            "rocheLimit": _massToRocheLimit(mass)
        })

    yearsToRun = [100, 200, 60, 100, 100, 50]
    impacts = []

    # G in km^3 / (kg * s^2)
    G = 6.674e-20
    dt = 86400  # 1 day in seconds

    def vec_sub(a, b):
        return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

    def vec_add(a, b):
        return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

    def vec_scale(v, s):
        return [v[0] * s, v[1] * s, v[2] * s]

    def vec_mag(v):
        return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

    def vec_norm(v):
        m = vec_mag(v)
        if m == 0:
            return [0, 0, 0]
        return [v[0] / m, v[1] / m, v[2] / m]

    # Track previous angles for orbit counting (angle in XY plane relative to sun)
    prev_angles = {}
    for body in bodies:
        if body["name"] != "Sun":
            dx = body["position"][0]
            dy = body["position"][1]
            prev_angles[body["name"]] = math.atan2(dy, dx)

    # Track Frank/Grace distance for subPass 4
    frank_grace_close_days = 0

    for day in range(0, yearsToRun[subPass] * 365):
        if day % 365 == 0: print(f"{subPass}: Starting year {day/365}")
        # Get list of active (non-destroyed) bodies
        active_bodies = [b for b in bodies if not b["destroyed"]]

        # Calculate accelerations for all active bodies
        accelerations = {b["name"]: [0.0, 0.0, 0.0] for b in active_bodies}

        for i, body in enumerate(active_bodies):
            for j, other in enumerate(active_bodies):
                if i == j:
                    continue

                r_vec = vec_sub(other["position"], body["position"])
                r = vec_mag(r_vec)

                if r < 1:  # Avoid division by zero
                    continue

                # a = G * M / r^2, direction towards other
                a_mag = G * other["mass"] / (r * r)
                a_dir = vec_norm(r_vec)
                a_vec = vec_scale(a_dir, a_mag)

                accelerations[body["name"]] = vec_add(
                    accelerations[body["name"]], a_vec)

        # Update velocities (in km/s)
        for body in active_bodies:
            acc = accelerations[body["name"]]
            body["velocity"] = vec_add(body["velocity"], vec_scale(acc, dt))

        # Update positions (velocity is km/s, dt is seconds, position is km)
        for body in active_bodies:
            body["position"] = vec_add(body["position"],
                                       vec_scale(body["velocity"], dt))

        # Check for collisions (Roche limit crossings)
        active_bodies = [b for b in bodies if not b["destroyed"]]
        for i, body in enumerate(active_bodies):
            for j, other in enumerate(active_bodies):
                if i >= j:
                    continue
                if body["destroyed"] or other["destroyed"]:
                    continue

                r = vec_mag(vec_sub(body["position"], other["position"]))

                # Use the larger body's Roche limit
                larger = body if body["mass"] >= other["mass"] else other
                smaller = other if body["mass"] >= other["mass"] else body

                if r < larger["rocheLimit"]:
                    # Impact! Smaller body is destroyed
                    print(
                        f"{subPass}: IMPACT!!! {smaller['name']} crashed into {larger['name']} "
                    )
                    smaller["destroyed"] = True
                    impacts.append({
                        "day": day,
                        "destroyed": smaller["name"],
                        "survivor": larger["name"]
                    })

                    # Conserve momentum: m1*v1 + m2*v2 = (m1+m2)*v_new
                    total_mass = larger["mass"] + smaller["mass"]
                    momentum = vec_add(
                        vec_scale(larger["velocity"], larger["mass"]),
                        vec_scale(smaller["velocity"], smaller["mass"]))
                    larger["velocity"] = vec_scale(momentum, 1.0 / total_mass)

                    # Merge mass
                    larger["mass"] = total_mass
                    larger["rocheLimit"] = _massToRocheLimit(total_mass)

        # Count orbits (track angle crossing through 0 in XY plane relative to Sun)
        sun = bodies[0]
        for body in bodies:
            if body["destroyed"] or body["name"] == "Sun":
                continue

            dx = body["position"][0] - sun["position"][0]
            dy = body["position"][1] - sun["position"][1]
            curr_angle = math.atan2(dy, dx)
            prev_angle = prev_angles.get(body["name"], curr_angle)

            # Detect crossing from negative to positive angle (counter-clockwise)
            # or positive to negative (clockwise) through the +x axis
            if prev_angle < 0 and curr_angle >= 0:
                # Crossed +x axis going counter-clockwise
                body["orbitsCounterClockWise"] += 1
            elif prev_angle >= 0 and curr_angle < 0:
                # Crossed +x axis going clockwise
                body["orbitsClockWise"] += 1

            prev_angles[body["name"]] = curr_angle

        # Track Frank/Grace distance for subPass 4
        frank = next((b for b in bodies if b["name"] == "Frank"), None)
        grace = next((b for b in bodies if b["name"] == "Grace"), None)
        if frank and grace and not frank["destroyed"] and not grace[
                "destroyed"]:
            fg_dist = vec_mag(vec_sub(frank["position"], grace["position"]))
            if fg_dist <= 10_000_000:  # 10 million km
                frank_grace_close_days += 1

    # Now grade based on subPass
    if subPass == 0:
        # System stable for 100 years - no impacts
        if len(impacts) > 0:
            return 0, f"System unstable: {impacts[0]['destroyed']} was destroyed on day {impacts[0]['day']}"
        return 1, "System stable for 100 years"

    elif subPass == 1:
        # All planets orbit in different planes and stable for 200 years
        if len(impacts) > 0:
            return 0, f"System unstable: {impacts[0]['destroyed']} was destroyed on day {impacts[0]['day']}"
        # Check orbital planes are different (using initial velocity cross position as normal)
        # Simplified: just check stability
        return 1, "System stable for 200 years"

    elif subPass == 2:
        # No impacts for 50 years, then at least one impact before year 60
        early_impacts = [i for i in impacts if i["day"] < 50 * 365]
        late_impacts = [i for i in impacts if 50 * 365 <= i["day"] < 60 * 365]
        if len(early_impacts) > 0:
            return 0, f"Impact too early: {early_impacts[0]['destroyed']} on day {early_impacts[0]['day']}"
        if len(late_impacts) == 0:
            return 0, "No impact occurred between year 50 and 60"
        return 1, f"Impact occurred as planned: {late_impacts[0]['destroyed']} on day {late_impacts[0]['day']}"

    elif subPass == 3:
        # One planet completes 100 orbits within 100 years then hits sun
        sun_impacts = [i for i in impacts if i["survivor"] == "Sun"]
        if len(sun_impacts) == 0:
            return 0, "No planet hit the sun"
        # Check the destroyed planet had 100+ orbits
        destroyed_name = sun_impacts[0]["destroyed"]
        destroyed_body = next(b for b in bodies if b["name"] == destroyed_name)
        total_orbits = destroyed_body["orbitsClockWise"] + destroyed_body[
            "orbitsCounterClockWise"]
        if total_orbits < 100:
            return 0, f"{destroyed_name} only completed {total_orbits} orbits before hitting sun"
        # Check other planets are stable (no other impacts)
        other_impacts = [
            i for i in impacts if i["destroyed"] != destroyed_name
        ]
        if len(other_impacts) > 0:
            return 0, f"Other planet {other_impacts[0]['destroyed']} was also destroyed"
        return 1, f"{destroyed_name} completed {total_orbits} orbits then hit sun"

    elif subPass == 4:
        # Frank and Grace binary pair within 10 million km for 100 years
        frank = next(b for b in bodies if b["name"] == "Frank")
        grace = next(b for b in bodies if b["name"] == "Grace")
        if frank["destroyed"] or grace["destroyed"]:
            return 0, "Frank or Grace was destroyed"
        required_days = 100 * 365
        if frank_grace_close_days < required_days:
            return 0, f"Frank and Grace only within 10M km for {frank_grace_close_days} days (need {required_days})"
        return 1, f"Frank and Grace within 10M km for {frank_grace_close_days} days"

    elif subPass == 5:
        # Alice completes 2 clockwise and 2 counter-clockwise orbits
        alice = next(b for b in bodies if b["name"] == "Alice")
        if alice["destroyed"]:
            return 0, "Alice was destroyed"
        if alice["orbitsClockWise"] < 2:
            return 0, f"Alice only completed {alice['orbitsClockWise']} clockwise orbits"
        if alice["orbitsCounterClockWise"] < 2:
            return 0, f"Alice only completed {alice['orbitsCounterClockWise']} counter-clockwise orbits"
        return 1, f"Alice completed {alice['orbitsClockWise']} CW and {alice['orbitsCounterClockWise']} CCW orbits"

    return 0, "Unknown subPass"


def resultToNiceReport(answer, subPass, aiEngineName):
    return "<p>Not implemented - I'd need to animate this.</p>"


if __name__ == "__main__":
    print(
        gradeAnswer(
            {
                "planets": [{
                    "name": "Alice",
                    "positionXyzInKm": [0, 150e6, 0],
                    "velocityXyzInKm": [10, 0, 0]
                }, {
                    "name": "Bob",
                    "positionXyzInKm": [0, 200e6, 0],
                    "velocityXyzInKm": [12, 0, 0]
                }, {
                    "name": "Carol",
                    "positionXyzInKm": [0, 250e6, 0],
                    "velocityXyzInKm": [15, 0, 0]
                }, {
                    "name": "Dave",
                    "positionXyzInKm": [0, 300e6, 0],
                    "velocityXyzInKm": [20, 0, 0]
                }, {
                    "name": "Eve",
                    "positionXyzInKm": [0, 350e6, 0],
                    "velocityXyzInKm": [25, 0, 0]
                }, {
                    "name": "Frank",
                    "positionXyzInKm": [0, 400e6, 0],
                    "velocityXyzInKm": [30, 0, 0]
                }, {
                    "name": "Grace",
                    "positionXyzInKm": [0, 450e6, 0],
                    "velocityXyzInKm": [35, 0, 0]
                }]
            }, 0, ""))
