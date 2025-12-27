import math, itertools
import os
import sys

# Add parent directory to path to import from 22.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EARTH_RADIUS = 6371
MIN_ALTITUDE = 100


def get_response(subPass: int):
  """Get the placebo response for this question."""

  # Import functions from 22.py
  g = {}
  parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  exec(open(os.path.join(parent_dir, "22.py"), "r", encoding="utf-8").read(), g)

  lambert_solve = g["lambert_solve"]
  orbitalParamsAndTimeToCartesian = g["orbitalParamsAndTimeToCartesian"]
  get_orbital_elements = g["get_orbital_elements"]
  general_transfer_delta_v = g["general_transfer_delta_v"]
  ORBITS = g["ORBITS"]
  MISSION_LENGTHS = g["MISSION_LENGTHS"]
  MU = g["MU"]

  def is_orbit_valid(orbit):
    """Check if orbit doesn't crash into Earth or escape."""
    orb_elem = get_orbital_elements(*orbit)
    if orb_elem is None:
      return False  # Hyperbolic/parabolic
    _, _, periapsis, apoapsis, _ = orb_elem
    if periapsis - EARTH_RADIUS < MIN_ALTITUDE:
      return False  # Would crash
    if apoapsis - EARTH_RADIUS > 1_000_000:
      return False  # Too high
    return True

  def find_best_transfer(source_orbit, source_time, target_initial_orbit, target_station_idx):
    """
    Find the best transfer from source orbit at source_time to target station.
    Returns (departure_time, arrival_time, dv1_vec, dv2_vec, total_dv, arrival_orbit) or None.
    """
    best = None
    best_dv = float('inf')

    # Get orbital period of source for search range
    source_elem = get_orbital_elements(*source_orbit)
    if source_elem:
      source_period = source_elem[4]
    else:
      source_period = 5400  # Default ~90 min LEO

    target_elem = get_orbital_elements(*target_initial_orbit)
    if target_elem:
      target_period = target_elem[4]
    else:
      target_period = 5400

    # Search over departure times (minimum 1s offset to avoid overlapping with previous arrival)
    min_offset = 1 if source_time > 0 else 0  # Prevent same-time burns
    dep_steps = max(16, int(source_period * 3 / 300))  # At least every 300 seconds
    for dep_idx in range(dep_steps):
      dep_offset = min_offset + int(source_period * 3 * dep_idx / dep_steps)
      dep_time = source_time + dep_offset

      # Propagate source to departure time
      if dep_offset > 0:
        source_at_dep = orbitalParamsAndTimeToCartesian(*source_orbit, dep_offset)
      else:
        source_at_dep = list(source_orbit)

      # Search over TOFs (0.3 to 4 target orbital periods)
      for tof_factor in [
          0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0
      ]:
        tof = target_period * tof_factor

        # Propagate target to arrival time
        arrival_time = dep_time + tof
        target_at_arr = orbitalParamsAndTimeToCartesian(*target_initial_orbit, arrival_time)

        # Try Lambert solve
        for prograde in [True, False]:
          try:
            result = lambert_solve(source_at_dep[0:3], target_at_arr[0:3], tof, MU, prograde)
          except (OverflowError, ValueError, ZeroDivisionError):
            continue
          if result is None:
            continue

          v1_transfer, v2_transfer = result

          # Calculate delta-v vectors
          dv1 = [v1_transfer[i] - source_at_dep[3 + i] for i in range(3)]
          dv2 = [target_at_arr[3 + i] - v2_transfer[i] for i in range(3)]

          dv1_mag = math.sqrt(sum(x * x for x in dv1))
          dv2_mag = math.sqrt(sum(x * x for x in dv2))
          total_dv = dv1_mag + dv2_mag

          # Reject burns that are too large (would likely cause problems)
          if dv1_mag > 8.0 or dv2_mag > 8.0:
            continue

          if total_dv >= best_dv:
            continue

          # Check orbit validity after departure burn
          post_burn1_orbit = list(source_at_dep)
          post_burn1_orbit[3] += dv1[0]
          post_burn1_orbit[4] += dv1[1]
          post_burn1_orbit[5] += dv1[2]

          if not is_orbit_valid(post_burn1_orbit):
            continue

          # Check orbit validity after arrival burn (should match target orbit)
          post_burn2_orbit = list(target_at_arr)
          # After arrival burn, velocity should match target - check it's valid
          if not is_orbit_valid(post_burn2_orbit):
            continue

          # Propagate to verify actual arrival velocity
          post_burn1_state = list(source_at_dep)
          post_burn1_state[3] = v1_transfer[0]
          post_burn1_state[4] = v1_transfer[1]
          post_burn1_state[5] = v1_transfer[2]

          actual_arrival = orbitalParamsAndTimeToCartesian(*post_burn1_state, tof)

          # Compute actual dv2 based on propagated arrival velocity
          actual_dv2 = [target_at_arr[3 + i] - actual_arrival[3 + i] for i in range(3)]
          actual_dv2_mag = math.sqrt(sum(x * x for x in actual_dv2))

          # Recompute total with actual dv2
          actual_total_dv = dv1_mag + actual_dv2_mag

          if actual_dv2_mag > 8.0 or actual_total_dv >= best_dv:
            continue

          # Verify arrival position matches target (grader requires < 0.5km)
          pos_error = math.sqrt(sum((actual_arrival[i] - target_at_arr[i])**2 for i in range(3)))
          if pos_error > 0.5:
            continue

          best_dv = actual_total_dv
          # Return actual spacecraft state after arrival burn
          actual_post_burn = list(actual_arrival)
          actual_post_burn[3] += actual_dv2[0]
          actual_post_burn[4] += actual_dv2[1]
          actual_post_burn[5] += actual_dv2[2]
          best = (dep_time, arrival_time, dv1, actual_dv2, actual_total_dv, actual_post_burn)

    return best

  # Starting orbit is the last one in ORBITS array
  startOrbit = ORBITS[-1]
  numStations = MISSION_LENGTHS[subPass]
  stationOrbits = ORBITS[0:numStations]

  # Find optimal ordering using clustering approach for scalability

  def get_transfer_dv(from_orbit, to_orbit):
    """Get delta-v for transfer using the proper orbital mechanics function."""
    try:
      result = general_transfer_delta_v(from_orbit[0:3], from_orbit[3:6], to_orbit[0:3],
                                        to_orbit[3:6])
      if result is None:
        return float('inf')
      return result[2]  # total delta-v
    except (OverflowError, ValueError, ZeroDivisionError):
      return float('inf')

  def classify_orbit(orbit):
    """Classify orbit by altitude band and inclination."""
    elem = get_orbital_elements(*orbit)
    if elem is None:
      return (0, 0)  # fallback
    sma, ecc, peri, apo, period = elem

    # Altitude band (0=LEO, 1=MEO, 2=GEO, 3=HEO)
    avg_alt = (peri + apo) / 2 - EARTH_RADIUS
    if avg_alt < 2000:
      alt_band = 0  # LEO
    elif avg_alt < 20000:
      alt_band = 1  # MEO
    elif avg_alt < 40000:
      alt_band = 2  # GEO
    else:
      alt_band = 3  # HEO

    # Inclination from orbital elements (approximate from state vector)
    r = orbit[0:3]
    v = orbit[3:6]
    h = [r[1] * v[2] - r[2] * v[1], r[2] * v[0] - r[0] * v[2], r[0] * v[1] - r[1] * v[0]]
    h_mag = math.sqrt(sum(x * x for x in h))
    if h_mag > 0:
      inc = math.acos(h[2] / h_mag) * 180 / math.pi
    else:
      inc = 0

    # Inclination band (0=equatorial, 1=low-inc, 2=mid-inc, 3=polar/sun-sync)
    if inc < 15:
      inc_band = 0
    elif inc < 45:
      inc_band = 1
    elif inc < 75:
      inc_band = 2
    else:
      inc_band = 3

    return (alt_band, inc_band)

  def find_best_path_clustered(stations, start_orbit):
    """Find path using brute force for small sets, greedy for larger."""
    if len(stations) <= 6:
      # Small enough for brute force
      best_dv = float('inf')
      best_path = None
      for ordering in itertools.permutations(stations):
        current = start_orbit
        dv = 0
        for s in ordering:
          dv += get_transfer_dv(current, stationOrbits[s])
          current = stationOrbits[s]
        if dv < best_dv:
          best_dv = dv
          best_path = list(ordering)
      return best_path if best_path else list(stations)

    # For larger sets, use greedy nearest-neighbor with multiple starts
    best_path = None
    best_total_dv = float('inf')

    for first_station in stations:
      path = [first_station]
      remaining = set(stations) - {first_station}
      current = stationOrbits[first_station]
      total_dv = get_transfer_dv(start_orbit, current)

      while remaining:
        # Find nearest unvisited station
        next_station = min(remaining, key=lambda s: get_transfer_dv(current, stationOrbits[s]))
        dv = get_transfer_dv(current, stationOrbits[next_station])
        total_dv += dv
        path.append(next_station)
        remaining.remove(next_station)
        current = stationOrbits[next_station]

      if total_dv < best_total_dv:
        best_total_dv = total_dv
        best_path = path

    return best_path

  bestPath = find_best_path_clustered(list(range(numStations)), startOrbit)
  bestDeltaV = sum(
    get_transfer_dv(startOrbit if i == 0 else stationOrbits[bestPath[i - 1]], stationOrbits[
      bestPath[i]]) for i in range(len(bestPath)))

  # Now compute actual burns and rendezvous for the best path
  burns = []
  rdx = []

  currentOrbit = list(startOrbit)
  currentTime = 0.0

  for destination in bestPath:
    targetOrbit = stationOrbits[destination]

    transfer = find_best_transfer(currentOrbit, currentTime, targetOrbit, destination)

    # If transfer failed, try fallback: direct transfer with longer search
    if transfer is None:
      # Fallback: try a simple 1-orbit transfer at various departure times
      source_elem = get_orbital_elements(*currentOrbit)
      target_elem = get_orbital_elements(*targetOrbit)
      source_period = source_elem[4] if source_elem else 5400
      target_period = target_elem[4] if target_elem else 5400

      best_fallback = None
      best_fallback_dv = float('inf')

      min_offset = 1 if currentTime > 0 else 0  # Prevent same-time burns
      for dep_mult in range(20):  # Try 20 departure times
        dep_offset = min_offset + int(source_period * dep_mult / 10)
        dep_time = currentTime + dep_offset

        if dep_offset > 0:
          source_at_dep = orbitalParamsAndTimeToCartesian(*currentOrbit, dep_offset)
        else:
          source_at_dep = list(currentOrbit)

        for tof_mult in range(1, 20):  # Try various TOFs
          tof = target_period * tof_mult / 5
          arrival_time = dep_time + tof
          target_at_arr = orbitalParamsAndTimeToCartesian(*targetOrbit, arrival_time)

          for prograde in [True, False]:
            try:
              result = lambert_solve(source_at_dep[0:3], target_at_arr[0:3], tof, MU, prograde)
            except:
              continue
            if result is None:
              continue

            v1_transfer, v2_transfer = result
            dv1 = [v1_transfer[i] - source_at_dep[3 + i] for i in range(3)]
            dv1_mag = math.sqrt(sum(x * x for x in dv1))

            # Propagate to get actual arrival velocity
            post_burn1 = list(source_at_dep)
            post_burn1[3:6] = v1_transfer
            try:
              actual_arr = orbitalParamsAndTimeToCartesian(*post_burn1, tof)
            except:
              continue

            dv2 = [target_at_arr[3 + i] - actual_arr[3 + i] for i in range(3)]
            dv2_mag = math.sqrt(sum(x * x for x in dv2))
            total_dv = dv1_mag + dv2_mag

            # Validate post-burn orbits
            if dv1_mag > 15 or dv2_mag > 15:
              continue  # Burns too large

            post_burn1_orbit = list(source_at_dep)
            post_burn1_orbit[3] += dv1[0]
            post_burn1_orbit[4] += dv1[1]
            post_burn1_orbit[5] += dv1[2]
            if not is_orbit_valid(post_burn1_orbit):
              continue

            # Check position error (grader requires < 0.5km)
            pos_err = math.sqrt(sum((actual_arr[i] - target_at_arr[i])**2 for i in range(3)))
            if pos_err > 0.5:
              continue

            if total_dv < best_fallback_dv:
              best_fallback_dv = total_dv
              # Return actual spacecraft state after arrival burn
              actual_post_burn = list(actual_arr)
              actual_post_burn[3] += dv2[0]
              actual_post_burn[4] += dv2[1]
              actual_post_burn[5] += dv2[2]
              best_fallback = (dep_time, arrival_time, dv1, dv2, total_dv, actual_post_burn)

      transfer = best_fallback

    if transfer is None:
      continue  # Last resort: skip this station

    dep_time, arr_time, dv1, dv2, total_dv, _ = transfer

    # Departure burn
    burns.append({"time": dep_time, "acceleration": list(dv1)})

    # Arrival burn
    burns.append({"time": arr_time, "acceleration": list(dv2)})

    # Simulate exactly what the grader does to compute spacecraft state
    # Propagate to departure time
    dt_to_dep = dep_time - currentTime
    if dt_to_dep > 0:
      currentOrbit = list(orbitalParamsAndTimeToCartesian(*currentOrbit, dt_to_dep))

    # Apply departure burn
    currentOrbit[3] += dv1[0]
    currentOrbit[4] += dv1[1]
    currentOrbit[5] += dv1[2]

    # Propagate to arrival time
    tof = arr_time - dep_time
    if tof > 0:
      currentOrbit = list(orbitalParamsAndTimeToCartesian(*currentOrbit, tof))

    # Apply arrival burn
    currentOrbit[3] += dv2[0]
    currentOrbit[4] += dv2[1]
    currentOrbit[5] += dv2[2]

    currentTime = arr_time

    # Record rendezvous with the simulated spacecraft state
    rdx.append({
      "position": list(currentOrbit[0:3]),
      "velocity": list(currentOrbit[3:6]),
      "time": arr_time,
      "station": destination
    })

  # Calculate actual total delta-v
  total_dv_used = sum(math.sqrt(sum(b["acceleration"][i]**2 for i in range(3))) for b in burns)
  reasoning = f"Path: start -> {' -> '.join(map(str, bestPath))}. Total delta-v: {total_dv_used:.3f} km/s"

  return {"reasoning": reasoning, "engineBurns": burns, "rendevouses": rdx}, reasoning
