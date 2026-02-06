"""
Optical Ray Tracer Test - Deduce optical device placement from resulting images.
"""

import os
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple
from LLMBenchCore.ResultPaths import result_path, report_relpath
from OpticalEngine import (Vec3, LightSource, Screen, OpticalScene, create_device,
                           get_white_light_wavelengths, wavelength_to_rgb, DEVICE_CLASSES)

title = "Optical Device Placement from Ray-Traced Images"
skip = True

prompt = """
You are presented with an image showing light hitting a screen after passing through optical devices.

**Given Information:**
- Light source(s): PARAM_LIGHTS
- Screen: PARAM_SCREEN  

**Your Task:**
Determine the position, orientation, and type of each optical device that would produce the shown pattern.

Coordinate system: +X right, +Y up, +Z toward viewer. Rotations are Euler angles (pitch, yaw, roll) in degrees.

**Device Library:**
- `prism`: Disperses light by wavelength. Params: apex_angle (default 60°), size
- `lens_convex`: Converging lens. Params: focal_length, diameter
- `lens_concave`: Diverging lens. Params: focal_length, diameter
- `mirror_flat`: Flat reflector. Params: width, height
- `mirror_concave`: Focusing mirror. Params: focal_length, diameter
- `slit`: Aperture. Params: width, height, plate_size
- `filter_bandpass`: Wavelength filter. Params: center_wavelength, bandwidth, diameter
- `beam_splitter`: 50/50 splitter. Params: size
"""

promptChangeSummary = "Increasing optical setup complexity"
earlyFail = True
subpassParamSummary = [
  "Single prism creating a spectrum",
  "Convex lens focusing with chromatic aberration",
  "Mirror redirecting a beam",
  "Prism + slit to isolate wavelengths",
  "Two-lens telescope configuration",
  "Complex: prism + lens + mirror",
]

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "devices": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": list(DEVICE_CLASSES.keys())
          },
          "position": {
            "type": "array",
            "items": {
              "type": "number"
            },
            "description": "[x,y,z] in mm"
          },
          "rotation": {
            "type": "array",
            "items": {
              "type": "number"
            },
            "description": "[pitch,yaw,roll] degrees"
          },
          "parameters": {
            "type": "string",
            "description": "Any additional parameters, url encoded. Empty if none."
          }
        },
        "required": ["type", "position", "rotation", "parameters"],
        "additionalProperties": False,
        "propertyOrdering": ["type", "position", "rotation", "parameters"]
      }
    }
  },
  "required": ["reasoning", "devices"],
  "propertyOrdering": ["reasoning", "devices"],
  "additionalProperties": False
}

# ============================================================================
# TEST SCENARIOS
# ============================================================================

SCENARIOS = [
  # 0: Single prism spectrum - light at angle to create dispersion
  {
    "lights": [{
      "position": [-100, -50, 0],
      "direction": [0.866, 0.5, 0],  # Angled upward to hit prism face at ~60°
      "spread_angle": 0.5
    }],
    "screen": {
      "position": [150, -53, 0],  # Centered on where spectrum lands
      "normal": [-1, 0, 0],
      "width": 20,
      "height": 20
    },
    "available_devices": ["prism"],
    "actual_devices": [{
      "type": "prism",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],  # No rotation - prism apex up
      "parameters": {
        "apex_angle": 60,
        "size": 40
      }
    }]
  },
  # 1: Convex lens with chromatic aberration
  {
    "lights": [{
      "position": [-150, 0, 0],
      "direction": [1, 0, 0],
      "spread_angle": 3
    }],
    "screen": {
      "position": [100, 0, 0],
      "normal": [-1, 0, 0],
      "width": 15,
      "height": 15
    },
    "available_devices": ["lens_convex"],
    "actual_devices": [{
      "type": "lens_convex",
      "position": [0, 0, 0],
      "rotation": [0, 90, 0],
      "parameters": {
        "focal_length": 80,
        "diameter": 40
      }
    }]
  },
  # 2: Mirror redirect - 45° mirror to bounce X-traveling light upward
  {
    "lights": [{
      "position": [-100, 0, 0],
      "direction": [1, 0, 0],
      "spread_angle": 2
    }],
    "screen": {
      "position": [0, 80, 0],
      "normal": [0, -1, 0],
      "width": 30,
      "height": 30
    },
    "available_devices": ["mirror_flat"],
    "actual_devices": [{
      "type": "mirror_flat",
      "position": [0, 0, 0],
      "rotation": [45, 90, 0],
      "parameters": {
        "width": 50,
        "height": 50
      }
    }]
  },
  # 3: Prism + slit - dispersed light filtered by slit
  {
    "lights": [{
      "position": [-100, -40, 0],
      "direction": [0.866, 0.5, 0],
      "spread_angle": 0.5
    }],
    "screen": {
      "position": [150, -45, 0],
      "normal": [-1, 0, 0],
      "width": 25,
      "height": 25
    },
    "available_devices": ["prism", "slit"],
    "actual_devices": [{
      "type": "prism",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "parameters": {
        "apex_angle": 60,
        "size": 35
      }
    }, {
      "type": "slit",
      "position": [80, -40, 0],
      "rotation": [0, 0, 0],
      "parameters": {
        "width": 5,
        "height": 15,
        "plate_size": 100
      }
    }]
  },
  # 4: Two-lens telescope
  {
    "lights": [{
      "position": [-200, 0, 0],
      "direction": [1, 0, 0],
      "spread_angle": 5
    }],
    "screen": {
      "position": [150, 0, 0],
      "normal": [-1, 0, 0],
      "width": 20,
      "height": 20
    },
    "available_devices": ["lens_convex", "lens_concave"],
    "actual_devices": [{
      "type": "lens_convex",
      "position": [-50, 0, 0],
      "rotation": [0, 90, 0],
      "parameters": {
        "focal_length": 60,
        "diameter": 50
      }
    }, {
      "type": "lens_concave",
      "position": [50, 0, 0],
      "rotation": [0, 90, 0],
      "parameters": {
        "focal_length": 30,
        "diameter": 30
      }
    }]
  },
  # 5: Complex - prism disperses, lens focuses, mirror redirects
  {
    "lights": [{
      "position": [-120, -40, 0],
      "direction": [0.866, 0.5, 0],
      "spread_angle": 0.5
    }],
    "screen": {
      "position": [100, 80, 0],
      "normal": [0, -1, 0],
      "width": 40,
      "height": 40
    },
    "available_devices": ["prism", "lens_convex", "mirror_flat"],
    "actual_devices": [{
      "type": "prism",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "parameters": {
        "apex_angle": 60,
        "size": 35
      }
    }, {
      "type": "lens_convex",
      "position": [60, -30, 0],
      "rotation": [0, 90, 0],
      "parameters": {
        "focal_length": 40,
        "diameter": 50
      }
    }, {
      "type": "mirror_flat",
      "position": [100, -50, 0],
      "rotation": [-45, 0, 0],
      "parameters": {
        "width": 80,
        "height": 60
      }
    }]
  },
]


def get_scenario(subPass: int) -> Dict:
  if subPass >= len(SCENARIOS):
    raise StopIteration
  return SCENARIOS[subPass]


def build_scene(scenario: Dict, devices: List[Dict]) -> OpticalScene:
  """Build optical scene from scenario and device list."""
  scene = OpticalScene()

  for ls in scenario["lights"]:
    scene.add_light(
      LightSource(position=Vec3.from_list(ls["position"]),
                  direction=Vec3.from_list(ls["direction"]),
                  spread_angle=ls.get("spread_angle", 5),
                  wavelengths=get_white_light_wavelengths(15),
                  rays_per_wavelength=80))

  ss = scenario["screen"]
  scene.set_screen(
    Screen(position=Vec3.from_list(ss["position"]),
           normal=Vec3.from_list(ss["normal"]),
           width=ss.get("width", 100),
           height=ss.get("height", 100),
           resolution=(512, 512)))

  for dev in devices:
    scene.add_device(
      create_device(dev["type"], dev["position"], dev["rotation"], dev.get("parameters", {})))

  return scene


def generate_reference_image(subPass: int) -> Image.Image:
  scenario = get_scenario(subPass)
  scene = build_scene(scenario, scenario["actual_devices"])
  return scene.run_simulation(max_rays=400000)


def compare_images(img1: Image.Image, img2: Image.Image) -> float:
  """Compare images, return similarity 0-1."""
  a1 = np.array(img1.resize((128, 128)), dtype=np.float32)
  a2 = np.array(img2.resize((128, 128)), dtype=np.float32)
  if a1.max() > 0: a1 /= a1.max()
  if a2.max() > 0: a2 /= a2.max()
  mse = np.mean((a1 - a2)**2)
  return 1.0 / (1.0 + mse * 10)


# ============================================================================
# TEST FRAMEWORK
# ============================================================================

reference_images = {}
earlyFail = False


def prepareSubpassPrompt(index: int) -> str:
  scenario = get_scenario(index)
  p = prompt.replace("PARAM_LIGHTS", str(scenario["lights"]))
  p = p.replace("PARAM_SCREEN", str(scenario["screen"]))
  p = p.replace("PARAM_DEVICES", ", ".join(scenario["available_devices"]))

  if not os.path.exists(f"results/49_ref_{index}.png"):
    prepareSubpassImages(index)

  p += f"[[image:results/49_ref_{index}.png]]"

  if index == 1: raise StopIteration
  return p


def prepareSubpassImages(index: int) -> Dict:
  """Generate reference image for subpass."""
  if index not in reference_images:
    reference_images[index] = generate_reference_image(index)
  ref_path = f"results/49_ref_{index}.png"
  reference_images[index].save(ref_path)
  return {"reference_image": ref_path}


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if "devices" not in answer:
    return 0, "Answer must contain 'devices' array"

  try:
    scenario = get_scenario(subPass)
  except StopIteration:
    return 0, "Invalid subpass"

  try:
    scene = build_scene(scenario, answer["devices"])
    user_image = scene.run_simulation(max_rays=400000)
  except Exception as e:
    return 0, f"Simulation failed: {e}"

  user_path = result_path(f"49_{aiEngineName}_{subPass}.png", aiEngineName)
  user_image.save(user_path)

  if subPass not in reference_images:
    reference_images[subPass] = generate_reference_image(subPass)

  sim = compare_images(reference_images[subPass], user_image)

  if sim > 0.9: score = 1.0
  elif sim > 0.7: score = 0.7
  elif sim > 0.5: score = 0.5
  elif sim > 0.3: score = 0.3
  else: score = 0.1

  return score, f"Image similarity: {sim:.1%}"


def resultToNiceReport(answer: dict, subPass: int, aiEngineName: str) -> str:
  scenario = get_scenario(subPass)

  html = "<div style='display:flex; flex-wrap:wrap; gap:20px;'>"

  ref_path = f"results/49_ref_{subPass}.png"
  if os.path.exists(ref_path):
    html += f"<div><h4>Reference</h4><img src='{report_relpath(ref_path, aiEngineName)}' style='max-width:250px; border:1px solid #ccc'/></div>"

  user_path = result_path(f"49_{aiEngineName}_{subPass}.png", aiEngineName)
  if os.path.exists(user_path):
    html += f"<div><h4>Result</h4><img src='{report_relpath(user_path, aiEngineName)}' style='max-width:250px; border:1px solid #ccc'/></div>"

  html += "</div>"

  html += "<h4>Actual Devices:</h4><ul>"
  for dev in scenario["actual_devices"]:
    html += f"<li><b>{dev['type']}</b> at {dev['position']}, rot {dev['rotation']}</li>"
  html += "</ul>"

  if "devices" in answer:
    html += "<h4>Guessed Devices:</h4><ul>"
    for dev in answer["devices"]:
      html += f"<li><b>{dev['type']}</b> at {dev['position']}, rot {dev['rotation']}</li>"
    html += "</ul>"

  return html


highLevelSummary = """
Can an AI reason about optics from first principles? This test shows the AI an image 
produced by light passing through optical devices (prisms, lenses, mirrors, slits) and 
asks it to deduce what devices are present and where they are positioned.

<br><br>

The test uses a physically-based ray tracer that models:
<ul>
<li>Wavelength-dependent refraction (dispersion/chromatic aberration)</li>
<li>Snell's law and total internal reflection</li>
<li>Thin lens approximation with chromatic focal shift</li>
<li>Specular reflection from mirrors</li>
<li>Aperture blocking from slits</li>
</ul>

Simpler tests involve single devices (e.g., identify prism position from a spectrum).
Harder tests combine multiple devices requiring understanding of light paths.
"""
