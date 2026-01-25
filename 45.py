title = "Can an AI navigate via the stars?"

import os
import math
import random
import csv
import datetime
from contextlib import contextmanager
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

skip = True

if not os.path.exists("hip_main.dat"):
  print("First run - downloading planet + star catalogue (~100mb), this may take some time...")

# 1. Download and load the Hipparcos catalogue
with load.open(hipparcos.URL) as f:
  df = hipparcos.load_dataframe(f)

planets = load('de421.bsp')
earth = planets['earth']

# Visible planets with their colours
planet_targets = [
  ('venus', planets['venus'], (255, 255, 200), -4),  # Very bright, yellowish
  ('mars', planets['mars'], (255, 150, 100), -2),  # Reddish
  ('jupiter', planets['jupiter barycenter'], (255, 220, 180), -2.5),  # Bright, cream
  ('saturn', planets['saturn barycenter'], (255, 230, 200), 0),  # Pale yellow
  ('moon', planets['moon'], (240, 240, 220), -12),  # Very bright!
]

# 2. Filter for visible stars (Magnitude <= 6.0)
bright_stars = df[df['magnitude'] <= 6.0]

# 3. Create Star objects (this is a single Star object that handles all stars vectorized)
stars = Star.from_dataframe(bright_stars)
magnitudes = bright_stars['magnitude'].values

ts = load.timescale()

planetDescriptions = {}

starRenders = []

_RESULTS_CSV_PATH = os.path.join("results", "45.csv")
_RESULTS_CSV_LOCK_PATH = _RESULTS_CSV_PATH + ".lock"

_RESULTS_CSV_FIELDS = [
  "timestamp_utc",
  "aiEngineName",
  "subPass",
  "location_idx",
  "time_idx",
  "time_description",
  "sky_filename",
  "utc_time",
  "target_lat",
  "target_lon",
  "guess_lat",
  "guess_lon",
  "abs_lat_error_deg",
  "abs_lon_error_deg",
  "central_angle_deg",
  "great_circle_km",
  "cartesian_km",
  "score",
  "hemisphere_correct",
  "date_line_side_correct",
  "within_10deg_lat",
  "within_10deg_lon",
  "numStarsVisible",
  "starsVisibleMagLE0",
  "starsVisibleMag0to1",
  "starsVisibleMag1to2",
  "starsVisibleMag2to3",
  "starsVisibleMag3to4",
  "starsVisibleMag4to5",
  "starsVisibleMag5to6",
  "numPlanetsVisible",
  "moonVisible",
  "visibleBodies",
]


@contextmanager
def _results_file_lock():
  os.makedirs(os.path.dirname(_RESULTS_CSV_LOCK_PATH), exist_ok=True)
  lock_file = open(_RESULTS_CSV_LOCK_PATH, "a+b")
  try:
    lock_file.seek(0, os.SEEK_END)
    if lock_file.tell() == 0:
      lock_file.write(b"0")
      lock_file.flush()
    if os.name == "nt":
      import msvcrt
      lock_file.seek(0)
      msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
    else:
      import fcntl
      fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    yield
  finally:
    try:
      if os.name == "nt":
        import msvcrt
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
      else:
        import fcntl
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    finally:
      lock_file.close()


def _append_results_csv_row(row: dict):
  os.makedirs(os.path.dirname(_RESULTS_CSV_PATH), exist_ok=True)
  with _results_file_lock():
    needs_header = (
      not os.path.exists(_RESULTS_CSV_PATH)) or os.path.getsize(_RESULTS_CSV_PATH) == 0
    with open(_RESULTS_CSV_PATH, "a", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=_RESULTS_CSV_FIELDS, extrasaction="ignore")
      if needs_header:
        writer.writeheader()
      writer.writerow(row)


_star_visibility_cache = {}
_planet_visibility_cache = {}


def _get_star_visibility_stats(location, observation_time):
  key = (float(location[0]), float(location[1]), float(observation_time.tt))
  cached = _star_visibility_cache.get(key)
  if cached is not None:
    return cached

  observer = earth + wgs84.latlon(location[0], location[1])
  astrometric = observer.at(observation_time).observe(stars)
  apparent = astrometric.apparent()
  alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)
  visible = alt.degrees > 0
  mags = magnitudes

  num_visible = int(np.sum(visible))
  s_le0 = int(np.sum(visible & (mags <= 0)))
  s_0_1 = int(np.sum(visible & (mags > 0) & (mags <= 1)))
  s_1_2 = int(np.sum(visible & (mags > 1) & (mags <= 2)))
  s_2_3 = int(np.sum(visible & (mags > 2) & (mags <= 3)))
  s_3_4 = int(np.sum(visible & (mags > 3) & (mags <= 4)))
  s_4_5 = int(np.sum(visible & (mags > 4) & (mags <= 5)))
  s_5_6 = int(np.sum(visible & (mags > 5) & (mags <= 6)))

  stats = {
    "numStarsVisible": num_visible,
    "starsVisibleMagLE0": s_le0,
    "starsVisibleMag0to1": s_0_1,
    "starsVisibleMag1to2": s_1_2,
    "starsVisibleMag2to3": s_2_3,
    "starsVisibleMag3to4": s_3_4,
    "starsVisibleMag4to5": s_4_5,
    "starsVisibleMag5to6": s_5_6,
  }
  _star_visibility_cache[key] = stats
  return stats


def _get_planet_visibility_stats(location, observation_time):
  key = (float(location[0]), float(location[1]), float(observation_time.tt))
  cached = _planet_visibility_cache.get(key)
  if cached is not None:
    return cached

  descs = getPlanetDescriptions(location, observation_time)
  names = sorted(descs.keys())
  moon_visible = "moon" in descs
  planets_visible = [n for n in names if n != "moon"]
  stats = {
    "numPlanetsVisible": len(planets_visible),
    "moonVisible": moon_visible,
    "visibleBodies": ";".join(names),
  }
  _planet_visibility_cache[key] = stats
  return stats


def render_star_field(lat, lon, time, filename, temperature, subpass, img_size=2048):
  """Render the night sky as seen from a specific location and time."""
  # Create observer position
  observer = earth + wgs84.latlon(lat, lon)

  # Observe all stars at once (vectorized)
  astrometric = observer.at(time).observe(stars)
  apparent = astrometric.apparent()

  # Get altitude and azimuth for all stars
  alt, az, _ = apparent.altaz(temperature_C=temperature, pressure_mbar=1020)

  # Convert to numpy arrays (degrees)
  alt_deg = alt.degrees
  az_deg = az.degrees

  # Create image
  img = PIL.Image.new("RGB", (img_size, img_size), (0, 0, 10))
  draw = PIL.ImageDraw.Draw(img)

  # Plot stars above horizon using stereographic projection
  center = img_size // 2
  scale = img_size / 2.2  # Leave margin

  for i in range(len(alt_deg)):
    if alt_deg[i] > 0:  # Above horizon
      # Stereographic projection (zenith at center)
      r = scale * (90 - alt_deg[i]) / 90  # Distance from center
      theta = math.radians(az_deg[i])

      # North is up, East is right
      x = center + r * math.sin(theta)
      y = center - r * math.cos(theta)

      # Star brightness based on magnitude (brighter = lower magnitude)
      mag = magnitudes[i]
      brightness = int(255 * max(0, min(1, (7 - mag) / 7)))
      radius = max(1, int(3 * (7 - mag) / 7))

      # Draw star
      color = (brightness, brightness, int(brightness * 0.9))
      draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
      starRenders.append((alt_deg[i], az_deg[i], mag))

  # Plot planets
  for name, planet, color, mag in planet_targets:
    try:
      planet_astrometric = observer.at(time).observe(planet)
      planet_apparent = planet_astrometric.apparent()
      p_alt, p_az, _ = planet_apparent.altaz()

      if p_alt.degrees > 0:  # Above horizon
        r = scale * (90 - p_alt.degrees) / 90
        theta = math.radians(p_az.degrees)
        x = center + r * math.sin(theta)
        y = center - r * math.cos(theta)

        planetDescriptions[name] = \
          f"{name} is visible and at {p_alt.degrees:.2f} degrees above the horizon. " \
          f"It is at {p_az.degrees:.2f} degrees azimuth."

        # Planets are bigger and coloured
        radius = max(4, int(6 * (7 - mag) / 10))
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)

    except Exception as e:
      pass  # Skip if planet not in ephemeris range

  # Draw cardinal directions at edges
  font_size = max(18, min(600, img_size // 30))
  margin = max(20, img_size // 100)
  stroke_width = max(2, font_size // 25)

  # Use a scalable TrueType font; fall back to default if not available.
  font = None
  for font_name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
    try:
      font = PIL.ImageFont.truetype(font_name, font_size)
      break
    except OSError:
      font = None
  if font is None:
    font = PIL.ImageFont.load_default()

  text_fill = (140, 255, 140)
  stroke_fill = (0, 0, 0)
  draw.text((center, margin),
            "N",
            fill=text_fill,
            anchor="mt",
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill)
  draw.text((center, img_size - margin),
            "S",
            fill=text_fill,
            anchor="mb",
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill)
  draw.text((img_size - margin, center),
            "E",
            fill=text_fill,
            anchor="rm",
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill)
  draw.text((margin, center),
            "W",
            fill=text_fill,
            anchor="lm",
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill)

  # Draw horizon circle
  draw.ellipse([center - scale, center - scale, center + scale, center + scale],
               outline=(50, 50, 80),
               width=2)

  img.save(filename)
  return img


random.seed(45)
np.random.seed(45)

test_locations = [
  (35.7872, -170.7725),
  (45.7750, -156.3490),
  (-11.0874, -138.853),
  (-56.6796, -129.3453),
  (20.9316, 147.1115),
  (52.6565, 162.2525),
  (14.7168, 170.0641),
]

temperatures = [19, 9, 25, 2, 25, 2, 26]

base_times = [
  ts.utc(2025, 12, 25, 12, 0, 0),
  ts.utc(2025, 12, 21, 12, 31, 11),
  ts.utc(2025, 12, 17, 14, 42, 52),
  ts.utc(2025, 12, 28, 11, 11, 41),
  ts.utc(2025, 11, 29, 10, 19, 10),
  ts.utc(2025, 11, 25, 12, 12, 42),
  ts.utc(2025, 11, 21, 13, 43, 54),
]


def format_time_exact(observation_time):
  """Format exact time for prompt."""
  tt = observation_time.utc
  return f"{tt[0]}:{tt[1]:02d}:{tt[2]:02d} {tt[3]:02d}:{tt[4]:02d}:{tt[5]:02.0f} UTC"


def subPassToParams(subPass):
  """Convert subpass index to (location_idx, time_idx) and actual values."""
  n_locations = len(test_locations)
  n_times = len(base_times)

  location_idx = subPass % n_locations
  time_idx = (subPass // n_locations) % n_times

  location = test_locations[location_idx]
  observation_time = base_times[time_idx]
  time_description = f"EXACTLY {format_time_exact(observation_time)}"

  return {
    'location': location,
    'location_idx': location_idx,
    'observation_time': observation_time,
    'time_idx': time_idx,
    'time_description': time_description,
    'temperature': temperatures[location_idx]
  }


def getTotalSubpasses():
  return len(test_locations) * len(base_times)


def getSkyMapFilename(location_idx, time_idx):
  """Get the filename for a rendered sky map."""
  return f"results/45_sky_loc{location_idx}_time{time_idx}.png"


def renderAllSkyMaps():
  """Render sky maps for all location/time combinations."""
  for loc_idx, location in enumerate(test_locations):
    for time_idx, base_time in enumerate(base_times):
      filename = getSkyMapFilename(loc_idx, time_idx)
      if not os.path.exists(filename):
        print(f"Rendering sky loc={loc_idx} time={time_idx}...")
        render_star_field(location[0], location[1], base_time, filename, temperatures[loc_idx],
                          loc_idx * 100 + time_idx, 8192)

  if not os.path.exists("images/45.png"):
    import shutil
    shutil.copy(getSkyMapFilename(0, 0), "images/45.png")


def getPlanetDescriptions(location, time):
  """Calculate planet descriptions for a specific location and time."""
  descriptions = {}
  observer = earth + wgs84.latlon(location[0], location[1])

  for name, planet, color, mag in planet_targets:
    try:
      planet_astrometric = observer.at(time).observe(planet)
      planet_apparent = planet_astrometric.apparent()
      p_alt, p_az, _ = planet_apparent.altaz()

      if p_alt.degrees > 0:  # Above horizon
        descriptions[name] = \
          f"{name} is visible and at {p_alt.degrees:.2f} degrees above the horizon. " \
          f"It is at {p_az.degrees:.2f} degrees azimuth."
    except:
      pass
  return descriptions


# Render any missing sky maps on import
renderAllSkyMaps()

prompt = f"""
You are a navigator on a ship in the middle of the pacific ocean. 

Your GPS has failed, but you can see the stars clearly. Using the attached image of the 
night sky as seen from your current location, determine your approximate position.

The image shows the sky looking straight up (zenith at center). The image was taken with a very high
resolution camera, and is ~65 megapixels. Stars of magnitudes up to 6 are visible, and there were
no clouds on the night. To help you understand the picture, I've annotated it and drawn the horizon 
as a green circle, and cardinal directions are marked: N (North) is at the top.

TIME_INFO 

You do not know your time zone or local time, but it's dark outside, dawn is far away, and has 
been dark for several hours.

Your ship is (obviously) at sea level, it's TEMP degrees Celsius outside, no wind, and the barometric 
pressure is 1020 mbar. Stars are visible all the way to the (annotated) horizon.

EXTRA

Determine your longitude and latitude to the best of your ability, up to 5 significant
figures. If you are uncertain, guessing is acceptable, even getting the hemisphere right and 
relation to the international date line is helpful.

"""

structure = {
  "type": "object",
  "properties": {
    "latitude": {
      "type": "number",
      "minimum": -90,
      "maximum": 90,
      "description": "Use negative for southern hemisphere, positive to northern. 0 is Equator."
    },
    "longitude": {
      "type": "number",
      "minimum": -180,
      "maximum": 180,
      "description": "0 is Greenwich."
    }
  },
  "required": ["latitude", "longitude"],
  "additionalProperties": False,
  "propertyOrdering": ["latitude", "longitude"]
}

# To save tokens, we instruct the test harness to run subpass 0, 1 and 2 first, and if the average
# is worse than 0.2, we stop checking it. You can get a score of 0.2 by simply getting the hemispheres
# (north vs south, east vs west) correct and placing your ship in the right quarter of the globe.
# If it gets that right, then we run the full suite. If it gets it wrong, we give it 3 attempts
# before writing it off.
earlyFail = True
earlyFailThreshold = 0.19
earlyFailSubpassSampleCount = 3
earlyFailTestsSameDifficulty = True


def prepareSubpassPrompt(index: int) -> str:
  total = getTotalSubpasses()
  if index >= total:
    raise StopIteration

  params = subPassToParams(index)
  location = params['location']
  observation_time = params['observation_time']
  time_description = params['time_description']
  location_idx = params['location_idx']
  time_idx = params['time_idx']

  # Get planet descriptions for this specific location/time
  planet_descs = getPlanetDescriptions(location, observation_time)

  planetDescriptions = ""
  if len(planet_descs) == 0:
    planetDescriptions = "No planets nor the moon are visible to the naked eye."
  elif len(planet_descs) == 1:
    planetDescriptions = "Only " + ", ".join(
      planet_descs.keys()) + " is visible to the naked eye and is in the image."
  else:
    planetDescriptions = "The planets " + ", ".join(
      planet_descs.keys()) + " are visible to the naked eye and are in the image."

  # Build time info string
  time_info = f"The time is {time_description}."

  p = prompt.replace("TIME_INFO", time_info)
  p = p.replace("EXTRA", planetDescriptions)
  p = p.replace("TEMP", str(params['temperature']))

  # Attach the appropriate sky map image
  sky_filename = getSkyMapFilename(location_idx, time_idx)
  return p + f"[[image:{sky_filename}]]"


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if not isinstance(answer, dict):
    try:
      params = subPassToParams(subPass)
      observation_time = params['observation_time']
      location_idx = params['location_idx']
      time_idx = params['time_idx']
      time_description = params['time_description']
      target_lat, target_lon = params['location']
      sky_filename = getSkyMapFilename(location_idx, time_idx)
      now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace(
        '+00:00', 'Z')
      row = {
        "timestamp_utc": now_utc,
        "aiEngineName": aiEngineName,
        "subPass": subPass,
        "location_idx": location_idx,
        "time_idx": time_idx,
        "time_description": time_description,
        "sky_filename": sky_filename,
        "utc_time": observation_time.utc_iso(),
        "target_lat": target_lat,
        "target_lon": target_lon,
        "guess_lat": "",
        "guess_lon": "",
        "score": 0,
      }
      row.update(_get_star_visibility_stats((target_lat, target_lon), observation_time))
      row.update(_get_planet_visibility_stats((target_lat, target_lon), observation_time))
      _append_results_csv_row(row)
    except Exception:
      pass
    return 0, "Invalid answer format"

  params = subPassToParams(subPass)
  target_lat, target_lon = params['location']

  try:
    answer_lat = float(answer.get("latitude", 0))
  except Exception:
    answer_lat = 0
  try:
    answer_lon = float(answer.get("longitude", 0))
  except Exception:
    answer_lon = 0

  score = 0
  feedback = []

  if (answer_lat > 0) == (target_lat > 0):
    score += 0.1
  else:
    feedback.append("Wrong hemisphere.")

  if (answer_lon > 0) == (target_lon > 0):
    score += 0.1
  else:
    feedback.append("Wrong side of international date line.")

  if abs(answer_lat - target_lat) < 10:
    score += 0.1

  if abs(answer_lon - target_lon) < 10:
    score += 0.1

  lat1 = math.radians(target_lat)
  lon1 = math.radians(target_lon)
  lat2 = math.radians(answer_lat)
  lon2 = math.radians(answer_lon)

  dlat = lat2 - lat1
  dlon = lon2 - lon1

  a = (math.sin(dlat / 2)**2) + (math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2)**2))
  central_angle_rad = 2 * math.asin(min(1.0, math.sqrt(a)))
  central_angle_deg = math.degrees(central_angle_rad)

  earth_radius_km = 6371.0088
  greatCircleDistance = earth_radius_km * central_angle_rad
  cartesianDistance = 2 * earth_radius_km * math.sin(central_angle_rad / 2)

  if score == 0.4:
    gcdlog10 = math.log10(max(greatCircleDistance, 1e-12))

    if gcdlog10 < 1:
      score = 1.0
    elif gcdlog10 < 2:
      score = 0.9
    elif gcdlog10 < 3:
      score = 0.8
    elif gcdlog10 < 4:
      score = 0.7
    elif gcdlog10 < 5:
      score = 0.6
    elif gcdlog10 < 6:
      score = 0.5
  if greatCircleDistance < 2:
    feedback.append(f"Error distance (along surface): ({greatCircleDistance * 1000:.1f} m)")
    # we don't add chord or degree measurements, because at these scales they're within a few cm of each other.
  else:

    feedback.append(
      f"Error distance (along surface): {central_angle_deg:.2f}° ({greatCircleDistance:.1f} km)")
    feedback.append(f"Error distance (through earth): {cartesianDistance:.1f} km")

  try:
    observation_time = params['observation_time']
    location_idx = params['location_idx']
    time_idx = params['time_idx']
    time_description = params['time_description']
    sky_filename = getSkyMapFilename(location_idx, time_idx)
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace(
      '+00:00', 'Z')
    row = {
      "timestamp_utc": now_utc,
      "aiEngineName": aiEngineName,
      "subPass": subPass,
      "location_idx": location_idx,
      "time_idx": time_idx,
      "time_description": time_description,
      "sky_filename": sky_filename,
      "utc_time": observation_time.utc_iso(),
      "target_lat": target_lat,
      "target_lon": target_lon,
      "guess_lat": answer_lat,
      "guess_lon": answer_lon,
      "abs_lat_error_deg": abs(answer_lat - target_lat),
      "abs_lon_error_deg": abs(answer_lon - target_lon),
      "central_angle_deg": central_angle_deg,
      "great_circle_km": greatCircleDistance,
      "cartesian_km": cartesianDistance,
      "score": score,
      "hemisphere_correct": int((answer_lat > 0) == (target_lat > 0)),
      "date_line_side_correct": int((answer_lon > 0) == (target_lon > 0)),
      "within_10deg_lat": int(abs(answer_lat - target_lat) < 10),
      "within_10deg_lon": int(abs(answer_lon - target_lon) < 10),
    }
    row.update(_get_star_visibility_stats((target_lat, target_lon), observation_time))
    row.update(_get_planet_visibility_stats((target_lat, target_lon), observation_time))
    _append_results_csv_row(row)
  except Exception:
    pass

  return score, "<br>\n".join(feedback)


def resultToNiceReport(answer, subPass, aiEngineName):
  if not isinstance(answer, dict):
    return "<p>Invalid answer</p>"

  params = subPassToParams(subPass)
  target_lat, target_lon = params['location']
  time_description = params['time_description']
  location_idx = params['location_idx']
  time_idx = params['time_idx']

  html = f"<p><b>Target location:</b> ({target_lat:.4f}°, {target_lon:.4f}°)</p>"
  html += f"<p><b>AI guess:</b> "
  html += f"({answer.get('latitude', '?'):.4f}°, {answer.get('longitude', '?'):.4f}°)</p>"
  html += f"<p><b>Time given:</b> {time_description}</p>"

  if subPass == 0:
    html += """Scoring<ul>
<li> +10% for the correct hemisphere.</li>
<li> +10% for the correct side of the international date line</li>
<li> +10% for within 10° of latitude and longitude (each. 20% total)</li>
<li> The remaining 60% is based on the great circle distance. 100m is 100%</li>
<li> So within about 10km should get the AI 100%.</li>
</ul>

"""

  sky_filename = getSkyMapFilename(location_idx, time_idx)
  html += f"<a href='{sky_filename}'><img src='{sky_filename}' style='min-width=400px'></a><br>"
  html += "(Click to zoom in - picture is huge and has ~100mb of star data)"

  return html


highLevelSummary = f"""
Can an AI navigate using only the stars?<br><br>

This pulls down ~100mb of star data, and calculates an exact night sky render,
placing all planets and stars at correct brightness, even modelling atmospheric
distortion and gravitational lensing, and then plots a high resolution image
of the sky looking up from the location of the test.

<b>Test dimensions:</b>
<ul>
<li>{len(test_locations)} different locations (pacific ocean coordinates)</li>
<li>{len(base_times)} different observation times</li>
<li>Total: {getTotalSubpasses()} subpasses</li>
</ul>

The AI is given:<ul>
<li>a 8192x8192 image of the night sky,</li>
<li>ocean name,</li>
<li>that they're far from land ('middle of the ocean')</li>
<li>exact time in UTC</li>
<li>knowledge of what planetary bodies are visible.</li>
</ul>
<br>

I actually personally struggled with this one, being from the southern hemisphere the first rendered
sky looked foreign. But with some basic googling I could recognise Orion's belt and his bow, and
the LLM needs to be able to either do this, or recognise the pattern as if it's a northern
hemisphere native. Humans have been doing this for millennia, and the AI has access to full almanacs
and can generate to-the-second accurate star maps via python, so I feel confident declaring this 
solvable.<br><br>

The 'human-with-tools' control does the following:<ul>
<li> Parses the image using scipy's image processing tools to cluster stars.</li>
<li> Converts the image into a binned index structure, 5 degree * 5 degree</li>
<li> Starts with magnitude <= 1 stars only (the top 20)</li>
<li> Starts with the area of uncertainty ~120 degree * ~140 degrees centred on the ocean centre.</li>
<li> randomly guesses, calculates where the stars would be, compares that to the given sky,</li>
<li> moves to the best guess.</li>
<li> shrinks the area of uncertainty, and adds dimmer and dimmer stars as we start getting more
  certain.</li>
<li> To speed up the early, rough, guesses, the position of every visible star from every 
 2 degree * 2 degree patch of the ground is precalculated (~350mb of data), allowing for fast linear interpolation.</li>
<li> To avoid local maxima issues, it walks multi-beams until they either converge or a clear winner emerges.
</ul>

Seems to be able to get it to within about 1.5km with only a few minutes of single threaded 
python code. Took a few hours to write the code. So 100% solvable on an $80,000 GPU.

<div style="max-width:650px">
<a href="45_sky_loc0_time0.png"><img src="45_sky_loc0_time0.png" width="300px" style="float:left; padding:4px"></a>
</div>
"""


def getSubpassParamSummary(index):
  """Generate a description for a specific subpass."""
  if index >= getTotalSubpasses():
    return None
  params = subPassToParams(index)
  loc_idx = params['location_idx']
  time_idx = params['time_idx']
  return f"Location {loc_idx}, Time {time_idx}"


subpassParamSummary = [getSubpassParamSummary(i) for i in range(min(20, getTotalSubpasses()))]
promptChangeSummary = "Varies location and observation time"

if __name__ == "__main__":
  print(prepareSubpassPrompt(0))
