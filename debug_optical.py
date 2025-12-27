from OpticalEngine import *
import math

print("=== Tracing where light lands for each scenario ===")

# Scenario 0: Prism
print("\n--- Scenario 0: Prism ---")
prism = Prism(Vec3(0, 0, 0), (0, 0, 0), {'apex_angle': 60, 'size': 40})
for wl in [450, 550, 650]:
  ray = Ray(Vec3(-100, -50, 0), Vec3(0.866, 0.5, 0).normalized(), wl, 1.0)
  # First intersection
  r1 = prism.intersect(ray)
  if not r1: continue
  hit1 = ray.at(r1[0])
  rays1 = prism.interact(ray, hit1, r1[1])
  if not rays1: continue
  # Second intersection (exit)
  ray2 = rays1[0]
  r2 = prism.intersect(ray2)
  if not r2: continue
  hit2 = ray2.at(r2[0])
  rays2 = prism.interact(ray2, hit2, r2[1])
  if not rays2: continue
  ray3 = rays2[0]
  # Where does it hit x=150?
  if abs(ray3.direction.x) > 0.01:
    t = (150 - ray3.origin.x) / ray3.direction.x
    y = ray3.origin.y + t * ray3.direction.y
    print(f"  {wl}nm hits x=150 at y={y:.1f}")

# Scenario 1: Lens
print("\n--- Scenario 1: Lens ---")
lens = ConvexLens(Vec3(0, 0, 0), (0, 90, 0), {'focal_length': 80, 'diameter': 40})
for offset in [-10, 0, 10]:
  ray = Ray(Vec3(-150, offset, 0), Vec3(1, 0, 0), 550, 1.0)
  res = lens.intersect(ray)
  if res:
    hit = ray.at(res[0])
    new_rays = lens.interact(ray, hit, res[1])
    if new_rays:
      r2 = new_rays[0]
      t = (100 - r2.origin.x) / r2.direction.x
      y = r2.origin.y + t * r2.direction.y
      print(f"  y={offset} -> hits screen at y={y:.1f}")

# Scenario 2: Mirror - test various rotations
print("\n--- Scenario 2: Mirror ---")
for rot in [(45, 0, 0), (0, 45, 0), (0, -45, 0), (0, 45, 90), (45, 90, 0), (0, 90, 45)]:
  mirror = FlatMirror(Vec3(0, 0, 0), rot, {'width': 50, 'height': 50})
  ray = Ray(Vec3(-100, 0, 0), Vec3(1, 0, 0), 550, 1.0)
  res = mirror.intersect(ray)
  if res:
    hit = ray.at(res[0])
    new_rays = mirror.interact(ray, hit, res[1])
    if new_rays:
      r2 = new_rays[0]
      print(
        f"  rot={rot}: reflected dir=({r2.direction.x:.2f}, {r2.direction.y:.2f}, {r2.direction.z:.2f})"
      )
  else:
    print(f"  rot={rot}: missed")

print("\n=== Direct refraction test ===")
# Test refraction directly without prism geometry
# Ray at 45° to a surface

normal = Vec3(0, 1, 0)  # Surface normal pointing up
incident_dir = Vec3(0.707, -0.707, 0)  # 45° angle

for wl in [380, 550, 780]:
  n = get_refractive_index(wl, 'flint')

  cos_i = -incident_dir.dot(normal)  # Should be 0.707
  n1, n2 = 1.0, n  # Air to glass
  ratio = n1 / n2
  sin_t_sq = ratio * ratio * (1.0 - cos_i * cos_i)
  cos_t = math.sqrt(1.0 - sin_t_sq)

  rd = incident_dir * ratio + normal * (ratio * cos_i - cos_t)
  rd = rd.normalized()

  # Calculate refracted angle
  cos_r = -rd.dot(normal)
  angle_r = math.degrees(math.acos(cos_r))

  print(
    f"{wl}nm: n={n:.4f}, cos_i={cos_i:.4f}, refracted angle from normal={angle_r:.2f}°, dir=({rd.x:.4f}, {rd.y:.4f})"
  )

print("\n=== Testing prism dispersion with detailed trace ===")

# Light should enter at an angle to the face, not perpendicular
# Try: prism at origin with no rotation, but aim ray at an angle
prism = Prism(Vec3(0, 0, 0), (0, 0, 0), {'apex_angle': 60, 'size': 30})

# Aim ray slightly upward so it hits the left face at an angle
# Left face normal is (-cos30, sin30, 0) = (-0.866, 0.5, 0)
# For good dispersion, ray should hit at ~45° from normal
ray_dir = Vec3(0.866, 0.5, 0).normalized()  # Toward upper-right, hitting left face at angle

wavelengths = [380, 780]  # violet and red only

exit_data = []
for wl in wavelengths:
  n_glass = get_refractive_index(wl, 'flint')
  ray = Ray(Vec3(-100, -50, 0), ray_dir, wl, 1.0)  # Start below, aim upward at prism
  print(f"\n{wl}nm (n={n_glass:.4f}):")

  # First intersection
  r1 = prism.intersect(ray)
  if not r1:
    print("  Missed prism")
    continue
  t1, normal1 = r1
  hit1 = ray.at(t1)
  cos_i1 = -ray.direction.dot(normal1)
  print(f"  Entry: cos_i={cos_i1:.4f}, angle={math.degrees(math.acos(abs(cos_i1))):.1f}°")

  rays1 = prism.interact(ray, hit1, normal1)
  if not rays1: continue
  ray2 = rays1[0]
  print(f"  After entry refraction: dir=({ray2.direction.x:.4f}, {ray2.direction.y:.4f})")

  # Second intersection (exit)
  r2 = prism.intersect(ray2)
  if not r2:
    print("  No exit intersection")
    continue
  t2, normal2 = r2
  hit2 = ray2.at(t2)
  cos_i2 = -ray2.direction.dot(normal2)
  print(f"  Exit: cos_i={cos_i2:.4f}, angle={math.degrees(math.acos(abs(cos_i2))):.1f}°")

  rays2 = prism.interact(ray2, hit2, normal2)
  if not rays2: continue
  ray3 = rays2[0]
  print(f"  After exit refraction: dir=({ray3.direction.x:.4f}, {ray3.direction.y:.4f})")

  exit_data.append((wl, ray3.origin, ray3.direction))

# Manual Snell's law test
print("\n=== Manual Snell's law test ===")

# Test Snell's law manually
# Light going into glass at 45 degrees
for wl in [380, 780]:
  n = get_refractive_index(wl, 'flint')
  # Incident angle 45 degrees from normal
  theta_i = math.radians(45)
  sin_t = math.sin(theta_i) / n
  theta_t = math.asin(sin_t)
  print(f"{wl}nm: n={n:.4f}, incident=45°, refracted={math.degrees(theta_t):.2f}°")

# Simpler test: ray perpendicular to first face should NOT refract
prism = Prism(Vec3(0, 0, 0), (0, 0, 0), {'apex_angle': 60, 'size': 30})  # No rotation

for wl in [380, 780]:
  n = get_refractive_index(wl, 'flint')
  print(f"\n{wl}nm (n={n:.4f}):")

  # Ray hitting bottom face perpendicularly
  ray = Ray(Vec3(0, -50, 0), Vec3(0, 1, 0), wl, 1.0)

  r1 = prism.intersect(ray)
  if r1:
    t, normal = r1
    hit = ray.at(t)
    print(f"  Hit bottom face at y={hit.y:.2f}, normal=({normal.x:.2f}, {normal.y:.2f})")

    # Calculate expected refraction manually
    cos_i = -ray.direction.dot(normal)
    print(f"  cos_i={cos_i:.4f} (angle={math.degrees(math.acos(cos_i)):.1f}°)")

    new_rays = prism.interact(ray, hit, normal)
    if new_rays:
      ray2 = new_rays[0]
      print(f"  After refraction: dir=({ray2.direction.x:.4f}, {ray2.direction.y:.4f})")
  else:
    print("  Missed prism")

# Calculate where rays hit a vertical screen at x=100
print("\nWhere rays hit screen at x=100:")
for wl, origin, direction in exit_data:
  if abs(direction.x) < 0.01: continue
  t = (100 - origin.x) / direction.x
  y = origin.y + t * direction.y
  print(f"  {wl}nm: y = {y:.1f}")

# Now run full simulation with properly positioned screen
print("\n=== Running full simulation ===")
scene = OpticalScene()
scene.add_light(
  LightSource(
    position=Vec3(-100, 0, 0),
    direction=Vec3(1, 0, 0),
    spread_angle=0.5,  # Narrow beam
    wavelengths=get_white_light_wavelengths(15),
    rays_per_wavelength=100))
scene.add_device(Prism(Vec3(0, 0, 0), (0, 0, 30), {'apex_angle': 60, 'size': 30}))
# Position screen below to catch the downward-deflected light
scene.set_screen(Screen(Vec3(100, -100, 0), Vec3(-1, 0, 0), 150, 150))

img = scene.run_simulation(max_rays=20000)
img.save('results/debug_prism.png')
print(f"Image saved. Max pixel: {scene.screen.image.max():.1f}")
