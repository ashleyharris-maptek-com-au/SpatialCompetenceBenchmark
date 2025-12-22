title = "Can an AI navigate via the stars?"

import os
import math
import random
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
import numpy as np
import PIL.Image
import PIL.ImageDraw

if not os.path.exists("hip_main.dat"):
  print("First run - downloading planet + star catalog (~100mb), this may take some time...")

# 1. Download and load the Hipparcos catalog
with load.open(hipparcos.URL) as f:
  df = hipparcos.load_dataframe(f)

planets = load('de421.bsp')
earth = planets['earth']

# Visible planets with their colors
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

#print(f"Loaded {len(bright_stars)} visible stars.")

ts = load.timescale()

planetDescriptions = {}


def render_star_field(lat, lon, time, filename, subpass, img_size=2048):
  """Render the night sky as seen from a specific location and time."""
  # Create observer position
  observer = earth + wgs84.latlon(lat, lon)

  # Observe all stars at once (vectorized)
  astrometric = observer.at(time).observe(stars)
  apparent = astrometric.apparent()

  # Get altitude and azimuth for all stars
  alt, az, _ = apparent.altaz(temperature_C=5, pressure_mbar=1020)

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

        # Planets are bigger and colored
        radius = max(4, int(6 * (7 - mag) / 10))
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)

    except Exception as e:
      pass  # Skip if planet not in ephemeris range

  # Draw cardinal directions at edges
  font_size = img_size // 30
  draw.text((center, 20), "N", fill=(100, 255, 100), anchor="mt")
  draw.text((center, img_size - 20), "S", fill=(100, 255, 100), anchor="mb")
  draw.text((img_size - 20, center), "E", fill=(100, 255, 100), anchor="rm")
  draw.text((20, center), "W", fill=(100, 255, 100), anchor="lm")

  # Draw horizon circle
  draw.ellipse([center - scale, center - scale, center + scale, center + scale],
               outline=(50, 50, 80),
               width=2)

  img.save(filename)
  return img


# Generate test scenarios - different locations, AI must identify where they are
random.seed(45)
np.random.seed(45)

test_location = \
  (35.7872, -170.7725, "North Pacific Ocean")

base_time = ts.utc(2025, 12, 25, 12, 0, 0)


def renderAllSkyMaps():
  print(f"Rendering sky from {test_location[2]}...")
  render_star_field(test_location[0], test_location[1], base_time, "results/45_sky_0.png", 0, 4096)

  if not os.path.exists("images/45.png"):
    import shutil
    shutil.copy("results/45_sky_0.png", "images/45.png")


if not os.path.exists("results/45_sky_0.png"):
  renderAllSkyMaps()

else:
  observer = earth + wgs84.latlon(test_location[0], test_location[1])

  for name, planet, color, mag in planet_targets:
    planet_astrometric = observer.at(base_time).observe(planet)
    planet_apparent = planet_astrometric.apparent()
    p_alt, p_az, _ = planet_apparent.altaz()

    if p_alt.degrees > 0:  # Above horizon
      planetDescriptions[name] = \
        f"{name} is visible and at {p_alt.degrees:.2f} degrees above the horizon. " \
          f"It is at {p_az.degrees:.2f} degrees azimuth."

# The actual test: given a star field image, identify the approximate location
# For subpasses, we'll vary the difficulty:
# - Subpass 0: Full star field with labeled constellations hints
# - Subpass 1: Just the star field, identify hemisphere
# - Subpass 2: Identify approximate latitude
# - Subpass 3: Identify city from multiple choice

# Pick a random location for the actual test
test_lat, test_lon, test_name = test_location

prompt = f"""
You are a navigator on a ship in the middle of the pacific ocean. 

Your GPS has failed, but you can see the stars clearly. Using the attached image of the 
night sky as seen from your current location, determine your approximate position.

The image shows the sky looking straight up (zenith at center). The horizon is the outer circle.
Cardinal directions are marked: N (North) is at the top.

You have a clock that is showing time in UTC, and can confirm that this observation was made on
EXACTLY December 25th, 2025 at exactly 12pm (midday) UTC. You do not know your time zone or
local time, but it's dark outside, and has been dark for several hours, and that can narrow your
position down to a few dozen degrees.

Your ship is (obviously) at sea level, it's 5 degrees Celsius, and the barometric pressure 
is 1020 mbar. As you grab your sextant and compass, you recall that the atmosphere does
distort star positions, and this information is important.

EXTRA

Determine your longitude and lattitude to the best of your ability. Guessing is acceptable,
even getting the hemisphere right and relation to the international date line is helpful.

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
      "description": "0 is grenwich."
    }
  },
  "required": ["latitude", "longitude"],
  "additionalProperties": False,
  "propertyOrdering": ["latitude", "longitude"]
}

earlyFail = True


def prepareSubpassPrompt(index: int) -> str:
  if index == 2:
    raise StopIteration

  nicePlanetDescriptions = ""
  for k, v in planetDescriptions.items():
    nicePlanetDescriptions += f"{v}\n"

  if index == 0:
    return prompt.replace("EXTRA", nicePlanetDescriptions) + f"[[image:results/45_sky_0.png]]"
  if index == 1: return prompt.replace("EXTRA", "") + f"[[image:results/45_sky_0.png]]"


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if not isinstance(answer, dict):
    return 0, "Invalid answer format"

  target_lat, target_lon, target_name = test_location

  answer_lat = answer.get("latitude", 0)
  answer_lon = answer.get("longitude", 0)

  score = 0
  feedback = []

  if answer_lat > 0 == target_lat > 0:
    score += 0.1
  else:
    feedback.append("Wrong hemisphere.")

  if answer_lon > 0 == target_lon > 0:
    score += 0.1
  else:
    feedback.append("Wrong side of international date line.")

  if abs(answer_lat - target_lat) < 10:
    score += 0.1

  if abs(answer_lon - target_lon) < 10:
    score += 0.1

  if abs(answer_lat - target_lat) < 1:
    score += 0.1

  if abs(answer_lon - target_lon) < 1:
    score += 0.1

  if abs(answer_lat - target_lat) < .1:
    score += 0.1

  if abs(answer_lon - target_lon) < .1:
    score += 0.1

  if abs(answer_lat - target_lat) < .01:
    score += 0.1

  if abs(answer_lon - target_lon) < .01:
    score += 0.1

  return score, f"Location was {target_name}. " + "<br>\n".join(feedback)


def resultToNiceReport(answer, subPass, aiEngineName):
  if not isinstance(answer, dict):
    return "<p>Invalid answer</p>"

  target_lat, target_lon, target_name = test_location

  html = f"<p><b>Target location:</b> ({target_lat:.2f}°, {target_lon:.2f}°)</p>"
  html += f"<p><b>AI guess:</b> "
  html += f"({answer.get('latitude', '?')}°, {answer.get('longitude', '?')}°)</p>"
  html += f"<img src='45_sky_0.png' width='400'>"

  return html


highLevelSummary = """
Can an AI navigate using only the stars?<br><br>

On the easy subpass, the AI is given a 4096x4096 image of the night sky,
enough information to place their lattitude within 40 degrees (ocean name, 
exact time in london, and approx local sunset delta), and a handful of exact
sextant observations to planetary bodies.<br><br>

On level 2, it only gets the 4096x4096 photo, timing, and the ocean name.<br><br>

This requires the AI to:
<ul>
<li>Recognize star patterns and constellations</li>
<li>Understand the relationship between star positions and observer location</li>
<li>Apply astronomical navigation principles</li>
</ul><br>

A lot of progress can be made with common knowledge... eg: "Hey polaris isn't 
visible from the southern hemisphere" sorta knowledge. I actually personally
struggled with this one, being from the southern hemisphere I don't recognise
this sky at all, but humans have been doing this for millenia, so I feel 
confident declaring this solvable.

<div style="max-width:650px">
<img src="45_sky_0.png" width="300px" style="float:left; padding:4px">
</div>
"""

subpassParamSummary = [
  "Can you identify where you are from a 4096x4096 image of the night sky and a list of sextant observations?",
  "Can you identify where you are from only 4096x4096 image of the night sky?",
]
promptChangeSummary = "Less and less information"

#print(prepareSubpassPrompt(0))
