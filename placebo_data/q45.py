# Appendix 3 - solver of skyfield image.

import subprocess
import time
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import numpy as np
import random
import math
import sys
import os
import json
import tempfile
from enum import Enum
import PIL.Image

PIL.Image.MAX_IMAGE_PIXELS = 268435456

# Add parent directory to path to import from 45.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

problem45 = importlib.import_module("45")

# Persistent cache directory - one file per subpass to avoid race conditions
_CACHE_DIR = os.path.join(tempfile.gettempdir(), "q45_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


def _load_cached_result(subPass):
  """Load cached result for a specific subpass."""
  cache_file = os.path.join(_CACHE_DIR, f"{subPass}.json")
  if os.path.exists(cache_file):
    try:
      with open(cache_file, 'r') as f:
        return json.load(f)
    except (json.JSONDecodeError, IOError):
      return None
  return None


def _save_cached_result(subPass, result):
  """Save cached result for a specific subpass."""
  cache_file = os.path.join(_CACHE_DIR, f"{subPass}.json")
  try:
    with open(cache_file, 'w') as f:
      json.dump(result, f)
  except IOError:
    pass


# Grid cache directory
_GRID_CACHE_DIR = os.path.join(tempfile.gettempdir(), "q45_grid_cache")
os.makedirs(_GRID_CACHE_DIR, exist_ok=True)


def _get_grid_cache_path(observation_time_iso, grid_params):
  """Get cache file path for a grid with given time and parameters."""
  # Create a hash of the grid parameters for the filename
  param_str = f"{grid_params['lat_min']}_{grid_params['lat_max']}_{grid_params['spacing']}"
  # Sanitize the ISO time string for use in filename
  time_str = observation_time_iso.replace(":", "-").replace(".", "-")
  return os.path.join(_GRID_CACHE_DIR, f"grid_{time_str}_{param_str}.npz")


def _load_cached_grid(observation_time_iso, grid_params):
  """Load cached star grid from disk if available."""
  cache_path = _get_grid_cache_path(observation_time_iso, grid_params)
  if os.path.exists(cache_path):
    try:
      print(f"Loading cached grid from {cache_path}...")
      data = np.load(cache_path, allow_pickle=True)
      grid = {}
      keys = data['keys']
      alts = data['alts']
      azs = data['azs']
      for i, key in enumerate(keys):
        grid[tuple(key)] = (alts[i], azs[i])
      print(f"Loaded {len(grid)} grid points from cache")
      return grid
    except Exception as e:
      print(f"Failed to load grid cache: {e}")
      return None
  return None


def _save_cached_grid(observation_time_iso, grid_params, star_grid):
  """Save star grid to disk cache."""
  cache_path = _get_grid_cache_path(observation_time_iso, grid_params)
  try:
    keys = list(star_grid.keys())
    alts = [star_grid[k][0] for k in keys]
    azs = [star_grid[k][1] for k in keys]
    np.savez(cache_path, keys=keys, alts=alts, azs=azs)
    print(f"Saved grid cache to {cache_path}")
  except Exception as e:
    print(f"Failed to save grid cache: {e}")


class StarIndexMode(Enum):
  """Mode for building the star index."""
  EXACT = "exact"  # Use exact star positions from Skyfield
  IMAGE = "image"  # Detect stars from the rendered image
  IMAGE_AND_EXACT = "image_and_exact"  # Compare both methods


def detect_stars_from_image(image_path: str):
  """
  Detect stars from a rendered sky image and return their alt/az/magnitude.
  
  Uses the reverse of the stereographic projection used in rendering:
  - center = img_size // 2
  - scale = img_size / 2.2
  - r = scale * (90 - alt) / 90  =>  alt = 90 * (1 - r/scale)
  - x = center + r * sin(az_rad)
  - y = center - r * cos(az_rad)
  - brightness = 255 * (7 - mag) / 7  =>  mag = 7 * (1 - brightness/255)
  
  Returns: list of (alt, az, magnitude) tuples
  """
  img = PIL.Image.open(image_path)
  img_array = np.array(img)
  img_size = img.width

  center = img_size // 2
  scale = img_size / 2.2

  # Convert to grayscale using the same formula as rendering (R and G are equal, B is 0.9*R)
  # We'll use the red channel as it has the full brightness value
  if len(img_array.shape) == 3:
    gray = img_array[:, :, 0].astype(np.float32)
  else:
    gray = img_array.astype(np.float32)

  # Threshold to find bright pixels (stars have brightness > ~20 for mag 6)
  # Background is (0, 0, 10) so threshold above that
  threshold = 15
  binary = gray > threshold

  # Find connected components (each star is a blob)
  from scipy import ndimage
  labeled, num_features = ndimage.label(binary)

  print(f"label done, {num_features} found")

  # Get bounding box slices for all labels at once - O(pixels) not O(labels*pixels)
  object_slices = ndimage.find_objects(labeled)

  detected_stars = []

  for label_idx in range(1, num_features + 1):
    slices = object_slices[label_idx - 1]  # find_objects is 0-indexed
    if slices is None:
      continue

    # Extract small sub-regions for this blob
    y_slice, x_slice = slices
    sub_labeled = labeled[slices]
    sub_gray = gray[slices]

    # Create mask only for the small sub-region
    blob_mask = sub_labeled == label_idx
    blob_brightness = sub_gray[blob_mask]

    if len(blob_brightness) == 0:
      continue

    total_brightness = np.sum(blob_brightness)
    if total_brightness == 0:
      continue

    # Get local coordinates within the sub-region
    local_coords = np.where(blob_mask)
    local_y = local_coords[0]
    local_x = local_coords[1]

    # Convert to global coordinates
    y_offset = y_slice.start
    x_offset = x_slice.start

    # Weighted centroid (in global coordinates)
    centroid_y = y_offset + np.sum(local_y * blob_brightness) / total_brightness
    centroid_x = x_offset + np.sum(local_x * blob_brightness) / total_brightness

    # Peak brightness (for magnitude estimation)
    peak_brightness = np.max(blob_brightness)

    # Estimate radius from blob size
    blob_radius = np.sqrt(len(blob_brightness) / np.pi)

    # Skip very large blobs (likely planets or artifacts like cardinal direction text)
    if blob_radius > 15:
      continue

    # Skip blobs near the edges (cardinal direction text)
    if centroid_x < 50 or centroid_x > img_size - 50:
      if abs(centroid_y - center) < 50:
        continue
    if centroid_y < 50 or centroid_y > img_size - 50:
      if abs(centroid_x - center) < 50:
        continue

    # Reverse stereographic projection
    dx = centroid_x - center
    dy = center - centroid_y  # Note: y is inverted
    r = math.sqrt(dx * dx + dy * dy)

    # Skip if outside the horizon circle
    if r > scale:
      continue

    # Calculate altitude: r = scale * (90 - alt) / 90
    alt = 90.0 * (1.0 - r / scale)

    # Calculate azimuth: theta where x = r*sin(theta), y = r*cos(theta)
    if r > 0:
      az = math.degrees(math.atan2(dx, dy))
      if az < 0:
        az += 360.0
    else:
      az = 0.0

    # Estimate magnitude from brightness: brightness = 255 * (7 - mag) / 7
    # mag = 7 * (1 - brightness / 255)
    mag_from_brightness = 7.0 * (1.0 - peak_brightness / 255.0)

    # Also use radius as a secondary magnitude estimate, BUT only if radius > 1.5
    # The rendering clamps radius to max(1, ...) so radius=1 could be any mag from ~4.7 to 7
    # radius = max(1, int(3 * (7 - mag) / 7)) => mag = 7 - radius * 7 / 3
    if blob_radius > 1.5:
      mag_from_radius = 7.0 - blob_radius * 7.0 / 3.0
      # Weight towards brightness (more reliable)
      estimated_mag = 0.7 * mag_from_brightness + 0.3 * mag_from_radius
    else:
      # For small blobs (radius clamped to 1), use brightness only
      estimated_mag = mag_from_brightness

    estimated_mag = max(-2.0, min(7.0, estimated_mag))  # Clamp to reasonable range

    detected_stars.append((alt, az, estimated_mag))

  return detected_stars


def compare_star_indices(exact_index, image_index, addReasoning=None):
  """
  Compare exact and image-based star indices and report discrepancies.
  Uses closest distance matching to avoid cross-matching nearby stars.
  """
  if addReasoning is None:
    addReasoning = print

  exact_stars = exact_index.stars
  image_stars = image_index.stars

  addReasoning(f"Exact index: {len(exact_stars)} stars")
  addReasoning(f"Image index: {len(image_stars)} stars")

  # Match stars between the two indices
  matched = 0
  unmatched = 0
  unmatchedDetails = []
  total_alt_error = 0.0
  total_az_error = 0.0
  total_mag_error = 0.0

  # Track which image stars have been matched to avoid double-matching
  matched_image_stars = set()

  # Sort exact stars by brightness (brightest first) for better matching
  sorted_exact = sorted([(alt, az, mag) for alt, az, mag in exact_stars if mag <= 6.0],
                        key=lambda x: x[2])

  for exact_alt, exact_az, exact_mag in sorted_exact:
    nearby = image_index.find_nearby(exact_alt, exact_az, radius=0.2)
    available = [(alt, az, mag, idx, dist) for alt, az, mag, idx, dist in nearby
                 if idx not in matched_image_stars]

    if not available:
      # Find closest match in image index by DISTANCE (not magnitude)
      nearby = image_index.find_nearby(exact_alt, exact_az, radius=2)

      # Filter out already-matched image stars and sort by distance
      available = [(alt, az, mag, idx, dist) for alt, az, mag, idx, dist in nearby
                   if idx not in matched_image_stars]

    if not available:
      unmatched += 1
      unmatchedDetails.append((exact_alt, exact_az, exact_mag))
      continue

    # Pick closest by distance
    best_match = min(available, key=lambda x: x[4])  # x[4] is dist
    img_alt, img_az, img_mag, img_idx, dist = best_match

    matched_image_stars.add(img_idx)

    alt_err = abs(exact_alt - img_alt)
    az_err = abs(exact_az - img_az)
    # Handle azimuth wraparound
    if az_err > 180:
      az_err = 360 - az_err
    mag_err = abs(exact_mag - img_mag)

    if alt_err > 0.5 or az_err > 0.5 or mag_err > 0.5:
      print(f"  Mismatch: exact=({exact_alt:.3f}, {exact_az:.3f}, {exact_mag:.3f}) "
            f"vs image=({img_alt:.3f}, {img_az:.3f}, {img_mag:.3f}) dist={dist:.3f}°")

    matched += 1
    total_alt_error += alt_err
    total_az_error += az_err
    total_mag_error += mag_err

  if matched > 0:
    addReasoning(f"Matched {matched} stars, {unmatched} unmatched")
    addReasoning(f"  Avg alt error: {total_alt_error / matched:.4f}°")
    addReasoning(f"  Avg az error: {total_az_error / matched:.4f}°")
    addReasoning(f"  Avg mag error: {total_mag_error / matched:.4f}")
  else:
    addReasoning("No stars matched between exact and image indices!")

  for alt, az, mag in unmatchedDetails:
    print(f"  Star not in image: ({alt:.3f}, {az:.3f}, {mag:.3f})")

  return matched, total_alt_error, total_az_error, total_mag_error


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
    # Check the 3x3 neighbourhood of bins
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


def match_star_fields(test_stars,
                      ref_index,
                      mag_threshold=6.0,
                      match_radius=0.5,
                      outlier_percentile=0.0):
  """
  Score how well test_stars match the reference star field.
  
  test_stars: list of (alt, az, mag) from the guessed position
  ref_index: SpatialStarIndex of the reference star field
  mag_threshold: only consider stars brighter than this magnitude
  match_radius: maximum angular distance to consider a match (degrees)
  outlier_percentile: exclude the worst X% of matches (0-100). Use >0 for fine stages
                      to make scoring robust to misidentified stars.
  
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
  match_results = []  # (weight, match_quality) pairs

  for test_alt, test_az, test_mag in bright_test:
    # Weight brighter stars more heavily
    weight = max(0.1, (7.0 - test_mag) / 7.0)

    # Find nearby reference stars
    nearby = ref_index.find_nearby(test_alt, test_az, match_radius)

    if not nearby:
      # No match found - record as zero quality
      match_results.append((weight, 0.0))
      continue

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
      match_results.append((weight, match_quality))
    else:
      match_results.append((weight, 0.0))

  if not match_results:
    return 0.0

  # Apply outlier exclusion if requested
  if outlier_percentile > 0 and len(match_results) > 10:
    # Sort by match quality (ascending) so worst matches are first
    sorted_by_quality = sorted(match_results, key=lambda x: x[1])
    # Exclude bottom X% of matches
    n_exclude = int(len(sorted_by_quality) * outlier_percentile / 100.0)
    if n_exclude > 0:
      match_results = sorted_by_quality[n_exclude:]

  # Compute weighted score from remaining matches
  total_score = sum(w * q for w, q in match_results)
  total_weight = sum(w for w, q in match_results)

  if total_weight == 0:
    return 0.0

  return total_score / total_weight


def get_response(subPass: int, mode: StarIndexMode = StarIndexMode.IMAGE):
  """
  Solve celestial navigation problem for a given subpass.
  Uses beam search with multiple starting positions to avoid local maxima.
  Time is known exactly, only need to solve for location.
  
  Args:
    subPass: The subpass index
    mode: How to build the reference star index:
      - EXACT: Use exact star positions from Skyfield
      - IMAGE: Detect stars from the rendered PNG image
      - IMAGE_AND_EXACT: Compare both methods, use image for solving
  """
  cached = _load_cached_result(subPass)
  if cached is not None:
    return cached

  # Get subpass parameters from 45.py
  params = problem45.subPassToParams(subPass)
  observation_time = params['observation_time']
  location_idx = params['location_idx']
  time_idx = params['time_idx']
  temperature = params['temperature']

  stars = problem45.stars
  magnitudes = problem45.magnitudes
  earth = problem45.earth

  # ==========================================================================
  # GRID PRECOMPUTATION: Build star field grid upfront for fast interpolation
  # ==========================================================================
  GRID_SPACING = 2.0  # degrees - matches initial_positions spacing
  GRID_LAT_MIN, GRID_LAT_MAX = -62, 62
  GRID_LON_RANGE = list(range(-180, -118, int(GRID_SPACING))) + list(
    range(118, 182, int(GRID_SPACING)))

  grid_params = {'lat_min': GRID_LAT_MIN, 'lat_max': GRID_LAT_MAX, 'spacing': GRID_SPACING}
  observation_time_iso = observation_time.utc_iso()

  # Try to load from cache first
  _star_grid = _load_cached_grid(observation_time_iso, grid_params)

  if _star_grid is None:
    # Cache miss - compute the grid
    print(
      f"Precomputing star field grid ({GRID_LAT_MIN} to {GRID_LAT_MAX} lat, {len(GRID_LON_RANGE)} lon points)..."
    )
    grid_start = time.time()

    # Store raw alt/az arrays for each grid point (before visibility filtering)
    # Key: (lat, lon), Value: (alt_array, az_array) - numpy arrays for all stars
    _star_grid = {}

    grid_lats = list(range(GRID_LAT_MIN, GRID_LAT_MAX + 1, int(GRID_SPACING)))
    glatsDone = 0
    for glat in grid_lats:
      for glon in GRID_LON_RANGE:
        observer = earth + wgs84.latlon(float(glat), float(glon))
        astrometric = observer.at(observation_time).observe(stars)
        apparent = astrometric.apparent()
        alt, az, _ = apparent.altaz(temperature_C=temperature, pressure_mbar=1020)
        _star_grid[(glat, glon)] = (alt.degrees.copy(), az.degrees.copy())
      glatsDone += 1
      print(f"{glatsDone/len(grid_lats):.1%} done")

    print(f"Grid precomputation done: {len(_star_grid)} points in {time.time() - grid_start:.2f}s")

    # Save to cache for future runs
    _save_cached_grid(observation_time_iso, grid_params, _star_grid)

  # Cache for compute_test_stars - used for fine stages where grid isn't precise enough
  _star_cache = {}

  def _interpolate_star_field(lat, lon):
    """Bilinearly interpolate star positions from precomputed grid."""
    # Find the 4 surrounding grid points
    lat0 = int(np.floor(lat / GRID_SPACING) * GRID_SPACING)
    lat1 = lat0 + int(GRID_SPACING)
    lon0 = int(np.floor(lon / GRID_SPACING) * GRID_SPACING)
    lon1 = lon0 + int(GRID_SPACING)

    # Clamp to grid bounds
    lat0 = max(GRID_LAT_MIN, min(GRID_LAT_MAX - int(GRID_SPACING), lat0))
    lat1 = max(GRID_LAT_MIN + int(GRID_SPACING), min(GRID_LAT_MAX, lat1))

    # Handle longitude - find closest in GRID_LON_RANGE
    def closest_lon(target):
      return min(GRID_LON_RANGE,
                 key=lambda x: min(abs(x - target), abs(x - target + 360), abs(x - target - 360)))

    lon0 = closest_lon(lon0)
    lon1 = closest_lon(lon1)
    if lon0 == lon1:
      # Edge case: pick next grid point
      idx = GRID_LON_RANGE.index(lon0)
      if idx + 1 < len(GRID_LON_RANGE):
        lon1 = GRID_LON_RANGE[idx + 1]
      elif idx > 0:
        lon0 = GRID_LON_RANGE[idx - 1]

    # Check if all 4 corners exist
    corners = [(lat0, lon0), (lat0, lon1), (lat1, lon0), (lat1, lon1)]
    if not all(c in _star_grid for c in corners):
      return None  # Fall back to exact computation

    # Bilinear interpolation weights
    t_lat = (lat - lat0) / GRID_SPACING if lat1 != lat0 else 0.0
    t_lon = (lon - lon0) / GRID_SPACING if lon1 != lon0 else 0.0
    t_lat = max(0.0, min(1.0, t_lat))
    t_lon = max(0.0, min(1.0, t_lon))

    # Get corner data
    alt00, az00 = _star_grid[(lat0, lon0)]
    alt01, az01 = _star_grid[(lat0, lon1)]
    alt10, az10 = _star_grid[(lat1, lon0)]
    alt11, az11 = _star_grid[(lat1, lon1)]

    # Interpolate altitude (straightforward)
    alt_interp = (alt00 * (1 - t_lat) * (1 - t_lon) + alt01 * (1 - t_lat) * t_lon + alt10 * t_lat *
                  (1 - t_lon) + alt11 * t_lat * t_lon)

    # Interpolate azimuth (handle wraparound at 0/360)
    # Convert to unit vectors, interpolate, convert back
    az00_rad, az01_rad = np.radians(az00), np.radians(az01)
    az10_rad, az11_rad = np.radians(az10), np.radians(az11)

    cos_az = (np.cos(az00_rad) * (1 - t_lat) * (1 - t_lon) + np.cos(az01_rad) *
              (1 - t_lat) * t_lon + np.cos(az10_rad) * t_lat * (1 - t_lon) +
              np.cos(az11_rad) * t_lat * t_lon)
    sin_az = (np.sin(az00_rad) * (1 - t_lat) * (1 - t_lon) + np.sin(az01_rad) *
              (1 - t_lat) * t_lon + np.sin(az10_rad) * t_lat * (1 - t_lon) +
              np.sin(az11_rad) * t_lat * t_lon)
    az_interp = np.degrees(np.arctan2(sin_az, cos_az)) % 360

    return alt_interp, az_interp

  def compute_test_stars(lat, lon, cache_precision=0.01, use_grid=True):
    """Compute visible stars from a given position at the known time.
    
    Uses caching with rounded positions to avoid redundant Skyfield calls.
    For coarse stages (cache_precision >= GRID_SPACING/2), uses grid interpolation.
    """
    # Round position for cache lookup
    cache_key = (round(lat / cache_precision) * cache_precision,
                 round(lon / cache_precision) * cache_precision)

    if cache_key in _star_cache:
      return _star_cache[cache_key]

    # Try grid interpolation for coarse searches
    if use_grid and cache_precision >= 0.5:
      interp_result = _interpolate_star_field(lat, lon)
      if interp_result is not None:
        alt_deg, az_deg = interp_result
        visible_mask = alt_deg > 0
        visible_alt = alt_deg[visible_mask]
        visible_az = az_deg[visible_mask]
        visible_mag = magnitudes[visible_mask]
        test_stars = list(zip(visible_alt, visible_az, visible_mag))
        _star_cache[cache_key] = test_stars
        return test_stars

    # Fall back to exact Skyfield computation
    observer = earth + wgs84.latlon(lat, lon)
    astrometric = observer.at(observation_time).observe(stars)
    apparent = astrometric.apparent()
    alt, az, _ = apparent.altaz(temperature_C=temperature, pressure_mbar=1020)

    # Vectorized: filter visible stars using numpy boolean indexing
    alt_deg = alt.degrees
    az_deg = az.degrees
    visible_mask = alt_deg > 0

    visible_alt = alt_deg[visible_mask]
    visible_az = az_deg[visible_mask]
    visible_mag = magnitudes[visible_mask]

    # Build list of tuples (still needed for compatibility)
    test_stars = list(zip(visible_alt, visible_az, visible_mag))

    _star_cache[cache_key] = test_stars
    return test_stars

  # Build exact star index (always needed for comparison or exact mode)
  target_location = params['location']
  ref_lat, ref_lon = target_location
  observer = earth + wgs84.latlon(ref_lat, ref_lon)
  astrometric = observer.at(observation_time).observe(stars)
  apparent = astrometric.apparent()
  alt, az, _ = apparent.altaz(temperature_C=temperature, pressure_mbar=1020)
  exact_ref_stars = []
  for i in range(len(alt.degrees)):
    if alt.degrees[i] > 0:  # Above horizon
      exact_ref_stars.append((alt.degrees[i], az.degrees[i], magnitudes[i]))
  exact_index = SpatialStarIndex(exact_ref_stars, bin_size=5.0)

  # Build image-based star index if needed
  image_index = None
  if mode in (StarIndexMode.IMAGE, StarIndexMode.IMAGE_AND_EXACT):
    detectStart = time.time()
    sky_filename = problem45.getSkyMapFilename(location_idx, time_idx)
    image_stars = detect_stars_from_image(sky_filename)
    image_index = SpatialStarIndex(image_stars, bin_size=5.0)
    print(f"Finding stars in the image took {time.time() - detectStart:.3f} seconds")

  # Choose which index to use for solving
  if mode == StarIndexMode.EXACT:
    ref_index = exact_index
  else:
    ref_index = image_index

  def score_guess(lat, lon, mag_threshold, cache_precision=0.01, outlier_percentile=0.0):
    """Score a guess position against stars by looking into the bins"""
    test_stars = compute_test_stars(lat, lon, cache_precision=cache_precision)
    return match_star_fields(test_stars,
                             ref_index,
                             mag_threshold=mag_threshold,
                             outlier_percentile=outlier_percentile)

  reasoning = ""

  def addReasoning(reason):
    nonlocal reasoning
    reasoning += reason + "\n"
    print(reason)

  addReasoning(f"Exact time: {observation_time.utc_iso()}")
  addReasoning(f"Star index mode: {mode.value}")

  # Compare indices if in IMAGE_AND_EXACT mode
  if mode == StarIndexMode.IMAGE_AND_EXACT:
    addReasoning("Comparing exact and image-based star indices:")
    compare_star_indices(exact_index, image_index, addReasoning)

  # BEAM SEARCH: Keep top N candidates to avoid local maxima
  N_BEAMS = 8

  # Multi-start: Initialize beams from different starting positions
  initial_positions = []

  for lat in range(-50, 60, 2):
    for lon in list(range(-150, -180, -2)) + list(range(120, 180, 2)):
      initial_positions.append((lat, lon))

  # Each beam: (lat, lon, score)
  beams = [(lat, lon, 0.0) for lat, lon in initial_positions]

  addReasoning(f"Multi-start beam search with {len(beams)} candidates")

  # Progressive schedule: (spatial_range, mag_threshold, iterations, samples_per_beam)
  brightness_schedule = [
    (5, 1.0, 1, 20),
    (4.0, 1.5, 20, 10),
    (2.0, 1.8, 10, 10),
    (1.0, 2.0, 8, 10),
    (0.5, 2.5, 8, 10),
    (0.2, 2.8, 10, 10),
    (0.1, 3.2, 10, 100),
    (0.05, 3.5, 10, 100),
    (0.02, 3.7, 20, 100),
    (0.01, 4, 20, 100),
    (0.008, 5, 20, 10),
    (0.005, 4.5, 10, 10),
    (0.002, 5, 10, 10),
    (0.001, 5.5, 10, 10),
    (0.0005, 6.0, 10, 10),
    (0.0002, 6.0, 10, 10),
    (0.0001, 6.0, 10, 10),
  ]

  # Add fine refinement iterations
  for i in range(20):
    last = brightness_schedule[-1]
    brightness_schedule.append((last[0] * 0.85, last[1], last[2], 50))

  for hill_size, mag_threshold, max_iterations, samples_per_beam in brightness_schedule:
    if not beams:
      beams = [(0, -150, 0)]

    # Adaptive cache precision: coarser caching for coarse search, finer for fine search
    # This dramatically increases cache hits during coarse stages
    cache_precision = max(0.00001, min(hill_size / 10, 1.0))

    # Adaptive outlier exclusion: use robust scoring in fine stages
    # When hill_size < 0.1°, we're refining and ~10 bad stars out of ~2400 hurt accuracy
    # Exclude worst 1% of matches in fine stages to be robust to misidentified stars
    if hill_size < 0.05:
      outlier_pct = 5.0
    elif hill_size < 0.1:
      outlier_pct = 2.0
    elif hill_size < 1.0:
      outlier_pct = 1
    else:
      outlier_pct = 0.0  # No exclusion in coarse stages

    best_beam_score = beams[0][2] if beams else 0.0
    beam_worst_score = beams[-1][2] if beams else 0
    addReasoning(
      f"Searching: spatial={hill_size:.5f}°, mag<={mag_threshold}, beams={len(beams)}, score={best_beam_score:.5f}"
    )

    for iteration in range(max_iterations):
      # Generate all guess positions first (main thread)
      guess_positions = []
      for i, (beam_lat, beam_lon, beam_score) in enumerate(beams):
        # Sample around this beam
        for _ in range(samples_per_beam):
          guess_lat = beam_lat + random.uniform(-hill_size, hill_size)
          guess_lon = beam_lon + random.uniform(-hill_size, hill_size)
          guess_lat = max(-90, min(90, guess_lat))
          guess_lon = ((guess_lon + 180) % 360) - 180
          guess_positions.append((guess_lat, guess_lon))
        # Also include current beam position
        guess_positions.append((beam_lat, beam_lon))

      # Score all positions
      all_candidates = []
      for i, (lat, lon) in enumerate(guess_positions):
        if i > 0 and i % 100 == 0:
          addReasoning(f"Scoring position {i} of {len(guess_positions)}...")

        score = score_guess(lat,
                            lon,
                            mag_threshold,
                            cache_precision=cache_precision,
                            outlier_percentile=outlier_pct)
        all_candidates.append((lat, lon, score))

      # Sort and keep top N diverse candidates
      all_candidates.sort(key=lambda x: x[2], reverse=True)

      score = all_candidates[0][2]

      if score < 0.1:
        beamCount = 100
      elif score < 0.3:
        beamCount = 10
      elif score < 0.9:
        beamCount = 2
      else:
        beamCount = 1

      new_beams = _select_diverse_beams(all_candidates, beamCount, min_distance=hill_size)

      # Check if we've converged
      if new_beams and beams:
        if new_beams[0][2] <= beams[0][2] + 0.0005:
          break

      beams = new_beams

      if beams and beams[0][2] > 0:
        best = beams[0]
        addReasoning(
          f"  Best: ({best[0]:.4f}, {best[1]:.4f}) score={best[2]:.6f} | {len(beams)} beams")

    # Prune weak beams as we get finer
    if hill_size < 1 and len(beams) > 1:
      best_score = beams[0][2]
      beams = [b for b in beams if b[2] != beam_worst_score]

    # Merge beams that are too close together
    beams = _merge_close_beams(beams, hill_size * 2)
    for i, (beam_lat, beam_lon, beam_score) in enumerate(beams):
      addReasoning(f"  Beam {i}: ({beam_lat:.4f}, {beam_lon:.4f}) score={beam_score:.6f}")

  # Final result is the best beam
  if beams:
    lat, lon, best_score = beams[0]
  else:
    lat, lon, best_score = 0, -150, 0

  addReasoning(f"Final: ({lat:.4f}, {lon:.4f}) with score {best_score:.4f}")

  result = {"latitude": lat, "longitude": lon}, reasoning
  _save_cached_result(subPass, result)
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


def cache_solutions():
  import argparse
  parser = argparse.ArgumentParser(description="Celestial navigation solver")
  parser.add_argument("subpass",
                      nargs="?",
                      type=int,
                      default=None,
                      help="Subpass to solve (omit to run all in parallel)")
  parser.add_argument("--mode",
                      choices=["exact", "image", "compare"],
                      default="exact",
                      help="Star index mode: exact (default), image, or compare (image_and_exact)")
  args = parser.parse_args()

  # Map mode string to Enum
  mode_map = {
    "exact": StarIndexMode.EXACT,
    "image": StarIndexMode.IMAGE,
    "compare": StarIndexMode.IMAGE_AND_EXACT,
  }
  mode = mode_map[args.mode]

  if args.subpass is None:
    # Run 50 sub-tasks in parallel, solving all 50 problems in advance and cache the
    # results.
    subTasks = []
    for i in range(50):
      print(f"Spawning solver for subpass {i}")
      cmd = [sys.executable, __file__, str(i), "--mode", args.mode]
      subTasks.append(subprocess.Popen(cmd))

      if len(subTasks) > min(os.cpu_count(), 16):
        subTasks.pop(0).wait()

    # Wait for all sub-tasks to complete
    for subTask in subTasks:
      subTask.wait()
  else:
    print(f"Running subpass {args.subpass} with mode={args.mode}")
    get_response(args.subpass, mode=mode)
    print(f"Finished subpass {args.subpass}")


if __name__ == "__main__": cache_solutions()
