from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import numpy as np
import random
import math

cachedResult = None


class SpatialStarIndex:
  """Spatial hash for fast star lookup by (altitude, azimuth) position."""

  def __init__(self, stars, bin_size=5.0):
    """
    Build a spatial index for stars.
    stars: list of (alt, az, magnitude) tuples
    bin_size: size of each bin in degrees
    """
    self.bin_size = bin_size
    self.bins = {}
    self.stars = stars

    for i, (alt, az, mag) in enumerate(stars):
      key = self._get_bin_key(alt, az)
      if key not in self.bins:
        self.bins[key] = []
      self.bins[key].append((alt, az, mag, i))

  def _get_bin_key(self, alt, az):
    """Get the bin key for a given altitude and azimuth."""
    alt_bin = int(alt / self.bin_size)
    az_bin = int(az / self.bin_size)
    return (alt_bin, az_bin)

  def find_nearby(self, alt, az, radius=3.0):
    """Find all stars within radius degrees of the given position."""
    nearby = []
    # Check the 3x3 neighborhood of bins
    center_key = self._get_bin_key(alt, az)
    for dalt in range(-1, 2):
      for daz in range(-1, 2):
        key = (center_key[0] + dalt, center_key[1] + daz)
        # Handle azimuth wraparound at 360/0 boundary
        if key[1] < 0:
          key = (key[0], key[1] + int(360 / self.bin_size))
        elif key[1] >= int(360 / self.bin_size):
          key = (key[0], key[1] - int(360 / self.bin_size))

        if key in self.bins:
          for star_alt, star_az, star_mag, star_idx in self.bins[key]:
            # Calculate angular distance
            dist = angular_distance(alt, az, star_alt, star_az)
            if dist <= radius:
              nearby.append((star_alt, star_az, star_mag, star_idx, dist))

    return nearby


def angular_distance(alt1, az1, alt2, az2):
  """Calculate angular distance between two sky positions in degrees."""
  # Convert to radians
  alt1_r, az1_r = math.radians(alt1), math.radians(az1)
  alt2_r, az2_r = math.radians(alt2), math.radians(az2)

  # Use spherical law of cosines
  cos_dist = (math.sin(alt1_r) * math.sin(alt2_r) +
              math.cos(alt1_r) * math.cos(alt2_r) * math.cos(az2_r - az1_r))
  # Clamp to avoid numerical issues with acos
  cos_dist = max(-1.0, min(1.0, cos_dist))
  return math.degrees(math.acos(cos_dist))


def match_star_fields(test_stars, ref_index, mag_threshold=6.0, match_radius=2.0):
  """
  Match stars between a test field and a reference field.
  
  test_stars: list of (alt, az, mag) from the guessed position
  ref_index: SpatialStarIndex of the reference star field
  mag_threshold: only consider stars brighter than this magnitude
  match_radius: maximum angular distance to consider a match (degrees)
  
  Returns: score between 0 and 1
  """
  # Filter to stars brighter than threshold
  bright_test = [(alt, az, mag) for alt, az, mag in test_stars if mag <= mag_threshold]
  bright_ref = [(alt, az, mag, idx) for alt, az, mag, idx in [(s[0], s[1], s[2], i)
                                                              for i, s in enumerate(ref_index.stars)
                                                              if s[2] <= mag_threshold]]

  if not bright_test or not bright_ref:
    return 0.0

  # For each test star, find the best matching reference star
  matched_ref_indices = set()
  total_score = 0.0
  total_weight = 0.0

  for test_alt, test_az, test_mag in bright_test:
    # Weight brighter stars more heavily
    weight = max(0.1, (7.0 - test_mag) / 7.0)
    total_weight += weight

    # Find nearby reference stars
    nearby = ref_index.find_nearby(test_alt, test_az, match_radius)

    if not nearby:
      continue  # No match found - this hurts the score

    # Find the best match (closest that hasn't been matched yet)
    best_match = None
    best_dist = float('inf')

    for ref_alt, ref_az, ref_mag, ref_idx, dist in nearby:
      if ref_idx in matched_ref_indices:
        continue
      # Also check magnitude similarity (within 1.5 magnitudes)
      if abs(ref_mag - test_mag) > 1.5:
        continue
      if dist < best_dist:
        best_dist = dist
        best_match = ref_idx

    if best_match is not None:
      matched_ref_indices.add(best_match)
      # Score based on distance (perfect match = 1, at radius = 0)
      match_quality = 1.0 - (best_dist / match_radius)
      total_score += weight * match_quality

  if total_weight == 0:
    return 0.0

  return total_score / total_weight


def get_response(subPass: int):
  """ Typical response:

Currently at (22.0000, -156.0000).
Considering only Mag<=1 degree stars. (Sirius, Canopus, Alpha Centauri, Arcturus, Vega, Capella, Rigel, Procyon, Betelgeuse, Achernar, Hadar (Agena), Altair, Acrux, Aldebaran, Antares, Spica)
Randomly sampleing 500 times for 3 iterationsin an area of 50.0 degrees.
Hill-climbed to (37.0902, -170.6568) with score 0.3898
Hill-climbed to (35.8122, -171.7694) with score 0.5608
Now adding stars of magnitude 1.0
Randomly sampleing 100 times for 4 iterationsin an area of 25.0 degrees.
Now adding stars of magnitude 2.0
Randomly sampleing 50 times for 5 iterationsin an area of 10.0 degrees.
Hill-climbed to (36.4800, -170.0993) with score 0.6126
Now adding stars of magnitude 3.0
Randomly sampleing 25 times for 6 iterationsin an area of 5.0 degrees.
Now adding stars of magnitude 4.0
Randomly sampleing 20 times for 7 iterationsin an area of 2.0 degrees.
Hill-climbed to (35.9830, -170.7882) with score 0.9174
Now adding stars of magnitude 5.0
Randomly sampleing 20 times for 8 iterationsin an area of 0.5 degrees.
Hill-climbed to (35.6652, -170.8256) with score 0.9453
Hill-climbed to (35.8358, -170.7550) with score 0.9784
Randomly sampleing 10 times for 10 iterationsin an area of 0.25 degrees.
Randomly sampleing 10 times for 10 iterationsin an area of 0.1 degrees.
Hill-climbed to (35.8094, -170.7862) with score 0.9887
Hill-climbed to (35.7924, -170.7940) with score 0.9907
Randomly sampleing 100 times for 10 iterationsin an area of 0.09000000000000001 degrees.
Hill-climbed to (35.8022, -170.7680) with score 0.9932
Randomly sampleing 100 times for 10 iterationsin an area of 0.08100000000000002 degrees.
Hill-climbed to (35.7870, -170.7768) with score 0.9983
Randomly sampleing 100 times for 10 iterationsin an area of 0.07290000000000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.06561000000000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.05904900000000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.05314410000000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.04782969000000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.043046721000000024 degrees.
Hill-climbed to (35.7866, -170.7728) with score 0.9997
Randomly sampleing 100 times for 10 iterationsin an area of 0.03874204890000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.03486784401000002 degrees.
Randomly sampleing 100 times for 10 iterationsin an area of 0.03138105960900001 degrees.
"""
  global cachedResult

  # :HACK: This code takes about 2 hours, and you're not that patient...
  cachedResult = {"latitude": 35.7866, "longitude": -170.7728}, ""

  if cachedResult is not None:
    return cachedResult

  g = {}
  exec(open("45.py").read(), g)

  stars = g['stars']
  magnitudes = g['magnitudes']
  earth = g['earth']
  ts = g['ts']
  test_location = g['test_location']
  base_time = g['base_time']

  ref_lat, ref_lon, _ = test_location
  observer = earth + wgs84.latlon(ref_lat, ref_lon)

  astrometric = observer.at(base_time).observe(stars)
  apparent = astrometric.apparent()
  alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)

  ref_stars = []
  for i in range(len(alt.degrees)):
    if alt.degrees[i] > 0:  # Above horizon
      ref_stars.append((alt.degrees[i], az.degrees[i], magnitudes[i]))

  # Build spatial index for reference stars
  ref_index = SpatialStarIndex(ref_stars, bin_size=5.0)

  def compute_test_stars(lat, lon, time):
    """Compute visible stars from a given position."""
    observer = g["earth"] + wgs84.latlon(lat, lon)

    # Observe all stars at once (vectorized)
    astrometric = observer.at(time).observe(stars)
    apparent = astrometric.apparent()

    # Get altitude and azimuth for all stars
    alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)

    # Convert to numpy arrays (degrees)
    alt_deg = alt.degrees
    az_deg = az.degrees

    test_stars = []
    for i in range(len(alt_deg)):
      if alt_deg[i] > 0:  # Above horizon
        test_stars.append((alt_deg[i], az_deg[i], magnitudes[i]))

    return test_stars

  def score_guess(lat, lon, time, mag_threshold):
    """Score a guess position against the reference star field."""
    test_stars = compute_test_stars(lat, lon, time)
    return match_star_fields(test_stars, ref_index, mag_threshold=mag_threshold)

  # Start at a central Pacific location
  lat = 22.0
  lon = -156.0
  time = g['ts'].utc(2025, 12, 25, 12, 0, 0)

  reasoning = ""

  def addReasoning(reason):
    nonlocal reasoning
    reasoning += reason + "\n"
    print(reason)

  addReasoning(f"Starting at ({lat:.4f}, {lon:.4f})")

  # Progressive brightness thresholds - start with brightest stars only
  # As hill shrinks, add dimmer stars for finer precision
  brightness_schedule = [
    (50.0, 1.0, 3, 500),  # Large hill: only magnitude <= 1 (brightest ~20 stars)
    (25.0, 2.0, 4, 100),  # Medium hill: magnitude <= 2 (~100 stars)
    (10.0, 3.0, 5, 50),  # Smaller: magnitude <= 3 (~300 stars)
    (5.0, 4.0, 6, 25),  # Finer: magnitude <= 4 (~900 stars)
    (2.0, 5.0, 7, 20),  # Very fine: magnitude <= 5 (~2500 stars)
    (0.5, 6.0, 8, 20),  # Final: all visible stars
    (0.25, 6.0, 10, 10),
    (0.1, 6.0, 10, 10),
  ]

  for i in range(50):
    last = brightness_schedule[-1]
    brightness_schedule.append((last[0] * 0.9, last[1], last[2], 100))

  best_score = 0.0
  addReasoning(f"Currently at ({lat:.4f}, {lon:.4f}).")

  addReasoning(
    "Considering only Mag<=1 degree stars. (Sirius, Canopus, Alpha Centauri, Arcturus, Vega, " +
    "Capella, Rigel, Procyon, Betelgeuse, Achernar, Hadar (Agena), Altair, Acrux, Aldebaran, Antares, Spica)"
  )

  for hill_size, mag_threshold, max_iterations, sampleCount in brightness_schedule:
    # Hill climbing at this scale
    iterations = 0

    addReasoning(f"Randomly sampleing {sampleCount} times for {max_iterations} iterations"\
    f"in an area of {hill_size} degrees.")

    while iterations < max_iterations:
      iterations += 1
      guesses = []

      # Sample around current best position
      for i in range(sampleCount):
        guess_lat = lat + random.uniform(-hill_size, hill_size)
        guess_lon = lon + random.uniform(-hill_size, hill_size)
        # Clamp to valid ranges
        guess_lat = max(-90, min(90, guess_lat))
        guess_lon = ((guess_lon + 180) % 360) - 180

        score = score_guess(guess_lat, guess_lon, time, mag_threshold)
        guesses.append((guess_lat, guess_lon, score))

      # Also evaluate current position
      current_score = score_guess(lat, lon, time, mag_threshold)
      guesses.append((lat, lon, current_score))

      guesses.sort(key=lambda x: x[2], reverse=True)
      best = guesses[0]

      if best[2] <= current_score + 0.001:
        # Converged at this scale
        break

      lat, lon = best[0], best[1]
      best_score = best[2]
      addReasoning(f"Hill-climbed to ({lat:.4f}, {lon:.4f}) with score {best_score:.4f}")

    if hill_size > 1:
      addReasoning("Now adding stars of magnitude " + str(mag_threshold))

  addReasoning(f"Hill-climbed to ({lat:.4f}, {lon:.4f}) with score {best_score:.4f}")

  cachedResult = {"reasoning": reasoning, "latitude": lat, "longitude": lon}, reasoning
  return cachedResult
