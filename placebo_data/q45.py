from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import numpy as np
import random
import math
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import from 45.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
problem45 = importlib.import_module("45")

cachedResult = {}


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
  """
  Solve celestial navigation problem for a given subpass.
  Uses beam search with multiple starting positions to avoid local maxima.
  Time is known exactly, only need to solve for location.
  """
  global cachedResult

  if subPass in cachedResult:
    return cachedResult[subPass]

  # Get subpass parameters from 45.py
  params = problem45.subPassToParams(subPass)
  target_location = params['location']
  observation_time = params['observation_time']
  
  stars = problem45.stars
  magnitudes = problem45.magnitudes
  earth = problem45.earth

  # Build a spatial index of the stars visible at the observation time in 5x5 degree bins
  ref_lat, ref_lon = target_location
  observer = earth + wgs84.latlon(ref_lat, ref_lon)
  astrometric = observer.at(observation_time).observe(stars)
  apparent = astrometric.apparent()
  alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)
  ref_stars = []
  for i in range(len(alt.degrees)):
    if alt.degrees[i] > 0:  # Above horizon
      ref_stars.append((alt.degrees[i], az.degrees[i], magnitudes[i]))
  ref_index = SpatialStarIndex(ref_stars, bin_size=5.0)

  def compute_test_stars(lat, lon):
    """Compute visible stars from a given position at the known time."""
    observer = earth + wgs84.latlon(lat, lon)
    astrometric = observer.at(observation_time).observe(stars)
    apparent = astrometric.apparent()
    alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)
    
    test_stars = []
    for i in range(len(alt.degrees)):
      if alt.degrees[i] > 0:
        test_stars.append((alt.degrees[i], az.degrees[i], magnitudes[i]))
    return test_stars

  def score_guess(lat, lon, mag_threshold):
    """Score a guess position against stars by looking into the bins"""
    test_stars = compute_test_stars(lat, lon)
    return match_star_fields(test_stars, ref_index, mag_threshold=mag_threshold)

  reasoning = ""
  def addReasoning(reason):
    nonlocal reasoning
    reasoning += reason + "\n"
    print(reason)

  addReasoning(f"Exact time: {observation_time.utc_iso()}")

  use_threads = sys.version_info >= (3, 14)
  executor = None
  if use_threads:
    max_workers = min(32, (os.cpu_count() or 1))
    executor = ThreadPoolExecutor(max_workers=max_workers)
    addReasoning(f"Threaded scoring enabled ({max_workers} workers)")

  # BEAM SEARCH: Keep top N candidates to avoid local maxima
  N_BEAMS = 5
  
  # Multi-start: Initialize beams from different starting positions
  initial_positions = [
    (20.0, -160.0),   # Central Pacific
    (0.0, -140.0),    # Near equator, east
    (-30.0, -150.0),  # South Pacific
    (40.0, -170.0),   # North Pacific  
    (-10.0, 170.0),   # West Pacific (near date line)
  ]
  
  # Each beam: (lat, lon, score)
  beams = [(lat, lon, 0.0) for lat, lon in initial_positions]
  
  addReasoning(f"Multi-start beam search with {N_BEAMS} candidates")

  # Progressive schedule: (spatial_range, mag_threshold, iterations, samples_per_beam)
  brightness_schedule = [
    (60.0, 1.0, 20, 150),    # Very coarse
    (40.0, 1.0, 20, 100),
    (25.0, 2.0, 20, 80),
    (15.0, 3.0, 20, 50),
    (8.0, 4.0, 20, 40),
    (4.0, 4.0, 20, 30),
    (2.0, 4.0, 10, 250),
    (1.0, 4.0, 8, 200),
    (0.5, 4.0, 8, 150),
    (0.2, 5.0, 10, 150),
    (0.1, 5.0, 10, 150),
    (0.05, 5.0, 10, 150),
    (0.02, 5.0, 10, 150),
    (0.01, 5.0, 10, 150),
    (0.005, 6.0, 10, 150),
    (0.002, 6.0, 10, 150),
    (0.001, 6.0, 10, 150),
    (0.0005, 6.0, 10, 150),
    (0.0002, 6.0, 10, 150),
    (0.0001, 6.0, 10, 150),
  ]

  # Add fine refinement iterations
  for i in range(20):
    last = brightness_schedule[-1]
    brightness_schedule.append((last[0] * 0.85, last[1], last[2], 50))

  try:
    for hill_size, mag_threshold, max_iterations, samples_per_beam in brightness_schedule:
      # Merge beams that are too close together
      beams = _merge_close_beams(beams, hill_size * 2)
      
      if not beams:
        beams = [(0, -150, 0)]
      
      addReasoning(f"Searching: spatial={hill_size:.4f}°, mag<={mag_threshold}, beams={len(beams)}")

      for iteration in range(max_iterations):
        # Generate all guess positions first (main thread)
        guess_positions = []
        for beam_lat, beam_lon, beam_score in beams:
          # Sample around this beam
          for _ in range(samples_per_beam):
            guess_lat = beam_lat + random.uniform(-hill_size, hill_size)
            guess_lon = beam_lon + random.uniform(-hill_size, hill_size)
            guess_lat = max(-90, min(90, guess_lat))
            guess_lon = ((guess_lon + 180) % 360) - 180
            guess_positions.append((guess_lat, guess_lon))
          # Also include current beam position
          guess_positions.append((beam_lat, beam_lon))

        # Score all positions (threaded only on Python >= 3.14)
        if use_threads and executor is not None:
          def _score_pos(latlon):
            return score_guess(latlon[0], latlon[1], mag_threshold)

          scores = list(executor.map(_score_pos, guess_positions))
          all_candidates = [(lat, lon, score) for (lat, lon), score in zip(guess_positions, scores)]
        else:
          all_candidates = []
          for lat, lon in guess_positions:
            score = score_guess(lat, lon, mag_threshold)
            all_candidates.append((lat, lon, score))

        # Sort and keep top N diverse candidates
        all_candidates.sort(key=lambda x: x[2], reverse=True)
        new_beams = _select_diverse_beams(all_candidates, N_BEAMS, min_distance=hill_size)
        
        # Check if we've converged
        if new_beams and beams:
          if new_beams[0][2] <= beams[0][2] + 0.0005:
            break
        
        beams = new_beams
        
        if beams and beams[0][2] > 0:
          best = beams[0]
          addReasoning(f"  Best: ({best[0]:.4f}, {best[1]:.4f}) score={best[2]:.6f} | {len(beams)} beams")

      # Prune weak beams as we get finer
      if hill_size < 5 and len(beams) > 1:
        best_score = beams[0][2]
        beams = [b for b in beams if b[2] >= best_score * 0.95]
  finally:
    if executor is not None:
      executor.shutdown(wait=True)

  # Final result is the best beam
  if beams:
    lat, lon, best_score = beams[0]
  else:
    lat, lon, best_score = 0, -150, 0
    
  addReasoning(f"Final: ({lat:.4f}, {lon:.4f}) with score {best_score:.4f}")

  result = {"latitude": lat, "longitude": lon}, reasoning
  cachedResult[subPass] = result
  return result


def _merge_close_beams(beams, merge_distance):
  """Merge beams that are within merge_distance of each other, keeping the higher-scoring one."""
  if not beams:
    return beams
  
  # Sort by score descending
  sorted_beams = sorted(beams, key=lambda x: x[2], reverse=True)
  merged = []
  
  for beam in sorted_beams:
    lat, lon, score = beam
    # Check if this beam is close to any already-merged beam
    is_close = False
    for m_lat, m_lon, m_score in merged:
      dist = math.sqrt((lat - m_lat)**2 + (lon - m_lon)**2)
      if dist < merge_distance:
        is_close = True
        break
    
    if not is_close:
      merged.append(beam)
  
  return merged


def _select_diverse_beams(candidates, n_beams, min_distance):
  """
  Select top N diverse candidates.
  Ensures selected beams are at least min_distance apart to maintain diversity.
  """
  if not candidates:
    return []
  
  selected = []
  
  for candidate in candidates:
    lat, lon, score = candidate
    
    # Check distance to already selected
    is_diverse = True
    for s_lat, s_lon, s_score in selected:
      dist = math.sqrt((lat - s_lat)**2 + (lon - s_lon)**2)
      if dist < min_distance:
        is_diverse = False
        break
    
    if is_diverse:
      selected.append(candidate)
      if len(selected) >= n_beams:
        break
  
  return selected


if __name__ == "__main__":
  print(get_response(0))
