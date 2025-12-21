import sys

sys.path.insert(0, 'c:\\AshDev\\MeshBenchmark')

# Load problem 3 (angled mirror)
import importlib

test_40 = importlib.import_module('40')

prob = test_40.problems[3]
print("Problem:", prob["name"])
print("Mirror:", prob["mirrors"][0])
print("\nGenerating SCAD...")

scad = test_40.generate_room_scad(prob)
print(scad)

# Save to file
with open("test_angled_mirror.scad", "w") as f:
    f.write(scad)
print("\nSaved to test_angled_mirror.scad")
