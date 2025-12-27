"""Placebo responses for optical ray tracer test."""


def get_response(subPass: int):
  """Get the placebo response for this question."""

  if subPass == 0:
    # Single prism creating spectrum - light enters at angle for dispersion
    return {
      "reasoning":
      "The rainbow spectrum indicates light dispersion through a prism. "
      "Light enters the prism at an angle to one face, refracts with "
      "wavelength-dependent bending, creating a spread of colors.",
      "devices": [{
        "type": "prism",
        "position": [0, 0, 0],
        "rotation": [0, 0, 0],
        "parameters": {
          "apex_angle": 60,
          "size": 40
        }
      }]
    }, ""

  if subPass == 1:
    # Convex lens with chromatic aberration
    return {
      "reasoning":
      "The focused spot with color fringes indicates a convex lens. "
      "Blue light focuses closer than red (chromatic aberration). "
      "The lens should be between source and screen, perpendicular to beam.",
      "devices": [{
        "type": "lens_convex",
        "position": [0, 0, 0],
        "rotation": [0, 90, 0],
        "parameters": {
          "focal_length": 80,
          "diameter": 40
        }
      }]
    }, ""

  if subPass == 2:
    # Mirror redirecting beam upward
    return {
      "reasoning":
      "Light redirected 90 degrees upward indicates a 45-degree mirror. "
      "The mirror is positioned where the beam path changes direction.",
      "devices": [{
        "type": "mirror_flat",
        "position": [0, 0, 0],
        "rotation": [45, 90, 0],
        "parameters": {
          "width": 50,
          "height": 50
        }
      }]
    }, ""

  if subPass == 3:
    # Prism + slit to isolate wavelengths
    return {
      "reasoning":
      "A narrow band of color suggests prism dispersion followed by a slit "
      "that blocks most wavelengths. Prism disperses, slit selects.",
      "devices": [{
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
    }, ""

  if subPass == 4:
    # Two-lens telescope
    return {
      "reasoning":
      "Telescope configuration uses convex objective lens and concave eyepiece. "
      "The convex lens gathers and focuses light, concave lens collimates output.",
      "devices": [{
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
    }, ""

  if subPass == 5:
    # Complex: prism + lens + mirror
    return {
      "reasoning":
      "Complex setup: prism disperses light into spectrum, lens focuses it, "
      "mirror redirects upward to the screen positioned above.",
      "devices": [{
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
    }, ""

  return None
