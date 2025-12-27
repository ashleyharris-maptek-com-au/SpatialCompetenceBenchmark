import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""

  worldSizes = [10, 30, 40, 50, 100, 300]
  startAltitudes = [5, 9, 19, 48, 95, 250]
  minLengths = [12, 100, 200, 500, 1000, 3000]
  minSpeeds = [5, 8, 12, 15, 20, 25]

  worldSize = worldSizes[subPass]
  startAltitude = startAltitudes[subPass]
  minLength = minLengths[subPass]
  minSpeed = minSpeeds[subPass]

  jerk = [0, 0, 0]
  accel = [0, 0, 0]
  # For spiral mode: use a descending helix with fixed radius
  # Radius chosen so turn rate matches max allowed (stays under 10°)
  center = [worldSize / 2, worldSize / 2]
  helixRadius = max(worldSize * 0.35, 6.5)  # At least 6.5m for safe 9° turns
  # Start at south of center, heading east (tangent to circle)
  pos = [center[0], center[1] - helixRadius, startAltitude]
  # Descent rate: with 9° turns, one lap = 40 segments
  # Need 3m+ Z separation per lap, so 3/40 = 0.075m min per segment
  # Use 0.10 for margin
  # Descent rate varies by world size to reach ground level
  # Larger worlds need slower descent to complete more laps
  descentRate = startAltitude / (minLength * 1.1)  # Reach ground just after min length
  descentRate = max(descentRate, 0.08)  # At least 0.08 for 3m+ clearance per lap
  vel = [1, 0, -descentRate]

  impulses = []
  spiral = True

  if subPass == 0:
    pos = [worldSize, worldSize, startAltitude]
    vel = [-1, -1, -0.51]
    spiral = False
  elif subPass == 1:
    impulses.append([50, 0, 0, -0.2])
    impulses.append([60, 0, 0, 0.8])
    impulses.append([70, 0, 0, -0.5])
  elif subPass == 2:
    vel[2] *= 1.5
  elif subPass == 3:
    impulses.append([10, 0, 0, -0.5])
    impulses.append([60, 0, 0, 1])
  elif subPass == 4:
    vel[2] *= 2

  def vec3_length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

  def vec3_norm(v):
    length = vec3_length(v)
    return [v[0] / length, v[1] / length, v[2] / length]

  def vec3_scale(v, s):
    return [v[0] * s, v[1] * s, v[2] * s]

  def vec3_add(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

  def vec3_cross(v1, v2):
    return [
      v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]
    ]

  def vec3_dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

  # Max angle change per segment is 10 degrees
  maxAngleDegrees = 7.5  # Leave margin for stronger inward drift

  points = []
  trackLength = 0
  while pos[2] > 0.45:  # Stop just above ground to avoid negative Z

    # Spiral steering: simple constant turn rate
    # Creates a predictable inward spiral (involute)
    if spiral:
      # Get current horizontal velocity direction
      velHoriz = [vel[0], vel[1]]
      velHorizLen = math.sqrt(velHoriz[0]**2 + velHoriz[1]**2)
      if velHorizLen > 0.001:
        velHoriz = [velHoriz[0] / velHorizLen, velHoriz[1] / velHorizLen]
      else:
        velHoriz = [1, 0]

      # Turn rate matched to helix radius for circular motion
      # For radius R, turn rate = 1/R radians to maintain circle
      turnRate = 1.0 / helixRadius
      # Cap at 9 degrees to stay under 10 degree limit
      turnRate = min(turnRate, math.radians(9.0))
      cosT = math.cos(turnRate)  # Positive for counter-clockwise (left turn)
      sinT = math.sin(turnRate)
      newVelX = velHoriz[0] * cosT - velHoriz[1] * sinT
      newVelY = velHoriz[0] * sinT + velHoriz[1] * cosT

      vel = [newVelX, newVelY, vel[2]]

    # Now update position with the steered velocity
    vel = vec3_norm(vel)
    delta = vel[:]
    pos2 = vec3_add(pos, delta)

    trackLength += vec3_length(delta)
    points.append(pos2)
    pos = pos2

    # Process impulses (for non-spiral modes)
    if len(impulses) and trackLength > impulses[0][0]:
      i = impulses.pop(0)[1:]
      jerk = vec3_add(jerk, i)

    # Apply jerk -> accel -> vel chain for impulse-based steering
    accel = vec3_add(accel, jerk)
    vel = vec3_add(vel, vec3_scale(accel, 0.1))

    # Decay jerk
    jerkLen = vec3_length(jerk)
    if jerkLen > 0.05:
      jerk = vec3_scale(jerk, 0.7)
    else:
      jerk = [0, 0, 0]

    # Bounds check
    if pos[0] < 0 or pos[0] > worldSize or pos[1] < 0 or pos[1] > worldSize or pos[2] > worldSize:
      print(f"Went out of bounds after {trackLength}m at {pos}")
      break

    if trackLength > 1000000:
      print("Went for over 1000km")
      break

  print("Total Length: ", trackLength)

  return {"trackPoints": points}, ""


if __name__ == "__main__":
  pts = get_response(1)[0]["trackPoints"]
  for p in pts:
    print(f"{p[0]:.2f} {p[1]:.2f} {p[2]:.2f}")
