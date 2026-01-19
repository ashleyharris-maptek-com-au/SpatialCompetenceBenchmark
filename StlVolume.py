import sys
import os
import warnings
from typing import Optional

import trimesh


def calculate_stl_volume(path: str, *, tolerance: Optional[float] = None) -> float:
  """Calculate volume of an STL file using trimesh."""
  if not os.path.exists(path):
    return 0.0

  try:
    mesh = trimesh.load(path)
  except Exception as e:
    warnings.warn(f"Failed to read STL: {e}", RuntimeWarning)
    return 0.0

  # Handle Scene objects (multiple meshes)
  if isinstance(mesh, trimesh.Scene):
    total_vol = 0.0
    for geometry in mesh.geometry.values():
      if hasattr(geometry, 'volume'):
        total_vol += abs(geometry.volume)
    return float(total_vol)

  if not hasattr(mesh, 'faces') or len(mesh.faces) == 0:
    return 0.0

  # Try to fix mesh if not watertight
  if not mesh.is_watertight:
    try:
      mesh.fill_holes()
      mesh.fix_normals()
    except Exception as e:
      warnings.warn(f"Mesh repair failed: {e}; volume may be unreliable", RuntimeWarning)

  try:
    vol = abs(mesh.volume)
  except Exception as e:
    warnings.warn(f"Volume calculation failed: {e}", RuntimeWarning)
    return 0.0

  return float(vol)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python StlVolume.py <path-to-stl> [tolerance]")
    sys.exit(1)
  p = sys.argv[1]
  tol = None
  if len(sys.argv) >= 3:
    try:
      tol = float(sys.argv[2])
    except Exception:
      tol = None
  vol = calculate_stl_volume(p, tolerance=tol)
  print(f"{vol}")
