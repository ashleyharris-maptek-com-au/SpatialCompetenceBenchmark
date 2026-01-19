import math, hashlib, os, sys
import tempfile
from textwrap import dedent

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib

problem3 = importlib.import_module("3")


def get_response(subPass: int):
  import OpenScad

  scadDescription = problem3.testParams[subPass][1]

  hash = hashlib.md5(scadDescription.encode()).hexdigest()
  scadPath = os.path.join(tempfile.gettempdir(), hash + ".scad")
  stlPath = os.path.join(tempfile.gettempdir(), hash + ".stl")

  if not os.path.exists(stlPath) or os.path.getsize(stlPath) == 0:
    with open(scadPath, "w") as f:
      f.write(scadDescription)

    OpenScad.run_openscad(scadPath, stlPath)

  stlText = open(stlPath, "r").read()

  # Parse STL and convert to JSON polyhedron format
  vertices = []
  vertex_map = {}  # (x,y,z) -> index
  faces = []

  current_face = []
  for line in stlText.split('\n'):
    line = line.strip()
    if line.startswith('vertex '):
      parts = line.split()
      x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
      key = (round(x, 6), round(y, 6), round(z, 6))
      if key not in vertex_map:
        vertex_map[key] = len(vertices)
        vertices.append([x, y, z])
      current_face.append(vertex_map[key])
    elif line == 'endloop':
      if current_face:
        faces.append(current_face)
        current_face = []

  return {
    "polyhedron": {
      "vertex": [{
        "xyz": v
      } for v in vertices],
      "faces": [{
        "vertex": f
      } for f in faces]
    }
  }, """As a 'human with tools', for this challenge I choose OpenSCAD as my tool."""


if __name__ == "__main__":
  print(get_response(0))
