import sys

sys.path.insert(0, '.')
import importlib
import math
import placebo_data.q22 as q22

importlib.reload(q22)

import importlib.util

spec = importlib.util.spec_from_file_location('grader22', '22.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)

# Test subPass 3 which fails
subPass = 3
result, reasoning = q22.get_response(subPass)
print(f"SubPass {subPass}: {reasoning}")
print(f"Burns: {len(result['engineBurns'])}")
print(f"Rendezvous: {len(result['rendevouses'])}")

# Simulate exactly what the grader does
ORBITS = grader.ORBITS
orbitalParamsAndTimeToCartesian = grader.orbitalParamsAndTimeToCartesian

currentOrbit = list(ORBITS[-1])
currentTime = 0

events = []
for b in result['engineBurns']:
  events.append({"time": b["time"], "type": "burn", "data": b})
for r in result['rendevouses']:
  events.append({"time": r["time"], "type": "rendezvous", "data": r})
events.sort(key=lambda x: x["time"])

for i, event in enumerate(events):
  eventTime = event["time"]
  dt = eventTime - currentTime
  if dt > 0:
    currentOrbit = list(orbitalParamsAndTimeToCartesian(*currentOrbit, dt))
    currentTime = eventTime

  if event["type"] == "burn":
    dv = event["data"]["acceleration"]
    print(f"Event {i}: Burn at T={eventTime:.1f}, dv=[{dv[0]:.3f}, {dv[1]:.3f}, {dv[2]:.3f}]")
    currentOrbit[3] += dv[0]
    currentOrbit[4] += dv[1]
    currentOrbit[5] += dv[2]
    print(
      f"  After burn vel: [{currentOrbit[3]:.3f}, {currentOrbit[4]:.3f}, {currentOrbit[5]:.3f}]")
  elif event["type"] == "rendezvous":
    rend = event["data"]
    rVel = rend["velocity"]
    print(f"Event {i}: Rendezvous at T={eventTime:.1f} with station {rend['station']}")
    print(
      f"  Spacecraft vel: [{currentOrbit[3]:.3f}, {currentOrbit[4]:.3f}, {currentOrbit[5]:.3f}]")
    print(f"  Recorded vel:   [{rVel[0]:.3f}, {rVel[1]:.3f}, {rVel[2]:.3f}]")
    diff = math.sqrt(sum((currentOrbit[3 + i] - rVel[i])**2 for i in range(3)))
    print(f"  Velocity diff: {diff:.3f} km/s")
    if diff > 0.05:
      print("  *** MISMATCH ***")
