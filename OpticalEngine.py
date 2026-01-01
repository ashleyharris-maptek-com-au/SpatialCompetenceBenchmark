"""
Optical Ray Tracer Engine - Core classes for ray tracing through optical devices.
"""

import math
import numpy as np
from PIL import Image
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

# ============================================================================
# WAVELENGTH AND COLOR UTILITIES
# ============================================================================


def wavelength_to_rgb(wavelength_nm: float) -> Tuple[int, int, int]:
  """Convert wavelength in nm to RGB color."""
  if wavelength_nm < 380:
    return (0, 0, 0)
  elif wavelength_nm < 440:
    r, g, b = -(wavelength_nm - 440) / 60, 0.0, 1.0
  elif wavelength_nm < 490:
    r, g, b = 0.0, (wavelength_nm - 440) / 50, 1.0
  elif wavelength_nm < 510:
    r, g, b = 0.0, 1.0, -(wavelength_nm - 510) / 20
  elif wavelength_nm < 580:
    r, g, b = (wavelength_nm - 510) / 70, 1.0, 0.0
  elif wavelength_nm < 645:
    r, g, b = 1.0, -(wavelength_nm - 645) / 65, 0.0
  elif wavelength_nm <= 780:
    r, g, b = 1.0, 0.0, 0.0
  else:
    return (0, 0, 0)

  factor = 0.3 + 0.7 * min(1, (wavelength_nm - 380) / 40) if wavelength_nm < 420 else \
           0.3 + 0.7 * (780 - wavelength_nm) / 80 if wavelength_nm > 700 else 1.0
  return (int(r * factor * 255), int(g * factor * 255), int(b * factor * 255))


def get_white_light_wavelengths(n: int = 15) -> List[float]:
  return [380 + i * 400 / (n - 1) for i in range(n)]


def get_refractive_index(wavelength_nm: float, material: str = "glass") -> float:
  A, B = {
    "glass": (1.5046, 4200),
    "flint": (1.62, 8000),
    "crown": (1.52, 3500)
  }.get(material, (1.5, 4000))
  return A + B / (wavelength_nm**2)


# ============================================================================
# 3D VECTOR
# ============================================================================


@dataclass
class Vec3:
  x: float = 0.0
  y: float = 0.0
  z: float = 0.0

  def __add__(self, o):
    return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

  def __sub__(self, o):
    return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

  def __mul__(self, s):
    return Vec3(self.x * s, self.y * s, self.z * s)

  def __rmul__(self, s):
    return self.__mul__(s)

  def __neg__(self):
    return Vec3(-self.x, -self.y, -self.z)

  def dot(self, o) -> float:
    return self.x * o.x + self.y * o.y + self.z * o.z

  def cross(self, o):
    return Vec3(self.y * o.z - self.z * o.y, self.z * o.x - self.x * o.z,
                self.x * o.y - self.y * o.x)

  def length(self) -> float:
    return math.sqrt(self.dot(self))

  def normalized(self):
    l = self.length()
    return Vec3(self.x / l, self.y / l, self.z / l) if l > 1e-10 else Vec3(0, 0, 1)

  def to_list(self) -> List[float]:
    return [self.x, self.y, self.z]

  @staticmethod
  def from_list(lst):
    return Vec3(lst[0], lst[1], lst[2])


def rotation_matrix(pitch_deg: float, yaw_deg: float, roll_deg: float) -> np.ndarray:
  p, y, r = math.radians(pitch_deg), math.radians(yaw_deg), math.radians(roll_deg)
  cp, sp, cy, sy, cr, sr = math.cos(p), math.sin(p), math.cos(y), math.sin(y), math.cos(
    r), math.sin(r)
  Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
  Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
  Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
  return Rz @ Ry @ Rx


def rotate_vector(v: Vec3, rot: np.ndarray) -> Vec3:
  r = rot @ np.array([v.x, v.y, v.z])
  return Vec3(r[0], r[1], r[2])


# ============================================================================
# RAY
# ============================================================================


@dataclass
class Ray:
  origin: Vec3
  direction: Vec3
  wavelength: float
  intensity: float = 1.0
  bounces: int = 0
  max_bounces: int = 50
  path: List[Vec3] = field(default_factory=list)

  def __post_init__(self):
    self.direction = self.direction.normalized()
    if not self.path: self.path = [self.origin]

  def at(self, t: float) -> Vec3:
    return self.origin + self.direction * t

  def add_path_point(self, pt: Vec3):
    self.path.append(pt)


# ============================================================================
# OPTICAL DEVICE BASE
# ============================================================================


class OpticalDevice:

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    self.position = position
    self.rotation = rotation
    self.rot_matrix = rotation_matrix(*rotation)
    self.inv_rot_matrix = np.linalg.inv(self.rot_matrix)
    self.params = params or {}

  def to_local(self, pt: Vec3) -> Vec3:
    return rotate_vector(pt - self.position, self.inv_rot_matrix)

  def to_world(self, pt: Vec3) -> Vec3:
    return rotate_vector(pt, self.rot_matrix) + self.position

  def dir_to_local(self, d: Vec3) -> Vec3:
    return rotate_vector(d, self.inv_rot_matrix)

  def dir_to_world(self, d: Vec3) -> Vec3:
    return rotate_vector(d, self.rot_matrix)

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    raise NotImplementedError

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    raise NotImplementedError

  def get_type(self) -> str:
    raise NotImplementedError


# ============================================================================
# PRISM - Triangular prism with proper dispersion
# ============================================================================


class Prism(OpticalDevice):
  """
  Triangular prism oriented with apex at top.
  In local coordinates:
  - Base is at y = -h/3 (horizontal face pointing down)
  - Left face tilts from bottom-left to apex
  - Right face tilts from bottom-right to apex
  - Prism extends in Z direction (depth)
  """

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.apex_angle = math.radians(params.get("apex_angle", 60))
    self.size = params.get("size", 30)  # edge length of equilateral triangle
    self.depth = params.get("depth", self.size)  # depth in Z
    self.material = params.get("material", "flint")  # flint glass has more dispersion

    # For equilateral triangle with edge length s:
    # height h = s * sqrt(3) / 2
    # centroid is at h/3 from base
    self.h = self.size * math.sqrt(3) / 2

    # Define the 3 face normals (pointing outward) and a point on each face
    # Face 1: Left face - normal points upper-left
    # Face 2: Right face - normal points upper-right
    # Face 3: Bottom face - normal points down
    half_apex = self.apex_angle / 2  # 30 degrees for 60 degree apex

    self.faces = [
      # (normal, point_on_face)
      # Left face: normal = (-cos(30), sin(30), 0) = (-sqrt(3)/2, 0.5, 0)
      (Vec3(-math.cos(half_apex), math.sin(half_apex), 0), Vec3(-self.size / 4, self.h / 6, 0)),
      # Right face: normal = (cos(30), sin(30), 0) = (sqrt(3)/2, 0.5, 0)
      (Vec3(math.cos(half_apex), math.sin(half_apex), 0), Vec3(self.size / 4, self.h / 6, 0)),
      # Bottom face: normal = (0, -1, 0)
      (Vec3(0, -1, 0), Vec3(0, -self.h / 3, 0)),
    ]

  def get_type(self):
    return "prism"

  def _point_in_prism_2d(self, x: float, y: float) -> bool:
    """Check if point is inside the triangular cross-section."""
    # Triangle vertices (equilateral, centered at origin):
    # apex at (0, 2h/3), bottom-left at (-s/2, -h/3), bottom-right at (s/2, -h/3)
    # Check using barycentric or half-plane tests
    s, h = self.size, self.h

    # Must be above bottom edge
    if y < -h / 3 - 0.01:
      return False
    # Must be below both slanted edges
    # Left edge: from (-s/2, -h/3) to (0, 2h/3)
    # Right edge: from (s/2, -h/3) to (0, 2h/3)

    # Left edge equation: y <= (h/3 + 2h/3) / (s/2) * (x + s/2) - h/3
    # Simplified: y <= 2*h/s * (x + s/2) - h/3 = 2h*x/s + h - h/3 = 2h*x/s + 2h/3
    if y > 2 * h / s * x + 2 * h / 3 + 0.01:
      return False
    # Right edge: y <= -2h/s * x + 2h/3
    if y > -2 * h / s * x + 2 * h / 3 + 0.01:
      return False
    return True

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    """Find intersection with prism faces."""
    lo = self.to_local(ray.origin)
    ld = self.dir_to_local(ray.direction)

    best_t = float('inf')
    best_normal = None

    for normal, point in self.faces:
      denom = ld.dot(normal)
      if abs(denom) < 1e-10:
        continue

      # t = (point - origin) . normal / (direction . normal)
      t = (point - lo).dot(normal) / denom

      if t < 0.001 or t >= best_t:
        continue

      hit = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, lo.z + t * ld.z)

      # Check Z bounds (prism depth)
      if abs(hit.z) > self.depth / 2:
        continue

      # Check if hit point is within the triangular face
      if self._point_in_prism_2d(hit.x, hit.y):
        best_t = t
        best_normal = normal

    if best_normal is None:
      return None

    return (best_t, self.dir_to_world(best_normal))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    """Apply Snell's law for refraction through the prism."""
    n_glass = get_refractive_index(ray.wavelength, self.material)

    # Determine if entering or exiting the prism
    cos_i = -ray.direction.dot(normal)

    if cos_i > 0:
      # Entering prism (ray coming from outside, hitting outer surface)
      n1, n2 = 1.0, n_glass
    else:
      # Exiting prism (ray inside, hitting inner surface)
      n1, n2 = n_glass, 1.0
      normal = -normal
      cos_i = -cos_i

    ratio = n1 / n2
    sin_t_sq = ratio * ratio * (1.0 - cos_i * cos_i)

    if sin_t_sq > 1.0:
      # Total internal reflection
      rd = ray.direction + normal * (2 * cos_i)
    else:
      # Refraction (Snell's law)
      cos_t = math.sqrt(1.0 - sin_t_sq)
      rd = ray.direction * ratio + normal * (ratio * cos_i - cos_t)

    rd = rd.normalized()
    new_ray = Ray(
      hit + rd * 0.02,  # Step slightly away from surface
      rd,
      ray.wavelength,
      ray.intensity * 0.98,
      ray.bounces + 1,
      ray.max_bounces)
    new_ray.path = ray.path.copy()
    new_ray.add_path_point(hit)
    return [new_ray]


# ============================================================================
# LENSES
# ============================================================================


class ConvexLens(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.focal_length = params.get("focal_length", 50)
    self.diameter = params.get("diameter", 25)
    self.material = params.get("material", "glass")

  def get_type(self):
    return "lens_convex"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if math.sqrt(h.x**2 + h.y**2) > self.diameter / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    lh, ld = self.to_local(hit), self.dir_to_local(ray.direction)
    n = get_refractive_index(ray.wavelength, self.material)
    f = self.focal_length * (get_refractive_index(550, self.material) - 1) / (n - 1)
    h = math.sqrt(lh.x**2 + lh.y**2)
    if h < 0.001: nd = ld
    else:
      fp = Vec3(0, 0, f if ld.z > 0 else -f)
      tf = (fp - lh).normalized()
      nd = Vec3(ld.x * 0.2 + tf.x * 0.8, ld.y * 0.2 + tf.y * 0.8,
                ld.z * 0.2 + tf.z * 0.8).normalized()
    wd = self.dir_to_world(nd)
    nr = Ray(hit + wd * 0.01, wd, ray.wavelength, ray.intensity * 0.95, ray.bounces + 1,
             ray.max_bounces)
    nr.path = ray.path.copy()
    nr.add_path_point(hit)
    return [nr]


class ConcaveLens(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.focal_length = params.get("focal_length", 50)
    self.diameter = params.get("diameter", 25)
    self.material = params.get("material", "glass")

  def get_type(self):
    return "lens_concave"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if math.sqrt(h.x**2 + h.y**2) > self.diameter / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    lh, ld = self.to_local(hit), self.dir_to_local(ray.direction)
    h = math.sqrt(lh.x**2 + lh.y**2)
    if h < 0.001: nd = ld
    else:
      rad = Vec3(lh.x, lh.y, 0).normalized()
      da = h / self.focal_length * 0.3
      nd = Vec3(ld.x + rad.x * da, ld.y + rad.y * da, ld.z).normalized()
    wd = self.dir_to_world(nd)
    nr = Ray(hit + wd * 0.01, wd, ray.wavelength, ray.intensity * 0.95, ray.bounces + 1,
             ray.max_bounces)
    nr.path = ray.path.copy()
    nr.add_path_point(hit)
    return [nr]


# ============================================================================
# MIRRORS
# ============================================================================


class FlatMirror(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.width = params.get("width", 50)
    self.height = params.get("height", 50)

  def get_type(self):
    return "mirror_flat"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if abs(h.x) > self.width / 2 or abs(h.y) > self.height / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    cos_i = -ray.direction.dot(normal)
    rd = ray.direction + normal * (2 * cos_i)
    nr = Ray(hit + rd * 0.01, rd.normalized(), ray.wavelength, ray.intensity * 0.98,
             ray.bounces + 1, ray.max_bounces)
    nr.path = ray.path.copy()
    nr.add_path_point(hit)
    return [nr]


class ConcaveMirror(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.focal_length = params.get("focal_length", 50)
    self.diameter = params.get("diameter", 50)
    self.radius = 2 * self.focal_length

  def get_type(self):
    return "mirror_concave"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    c = Vec3(0, 0, self.radius)
    oc = lo - c
    a, b, cc = ld.dot(ld), 2 * oc.dot(ld), oc.dot(oc) - self.radius**2
    disc = b * b - 4 * a * cc
    if disc < 0: return None
    t1, t2 = (-b - math.sqrt(disc)) / (2 * a), (-b + math.sqrt(disc)) / (2 * a)
    t = t1 if t1 > 0.001 else t2
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, lo.z + t * ld.z)
    if math.sqrt(h.x**2 + h.y**2) > self.diameter / 2 or h.z > 0.1: return None
    return (t, self.dir_to_world((h - c).normalized()))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    cos_i = -ray.direction.dot(normal)
    rd = ray.direction + normal * (2 * cos_i)
    nr = Ray(hit + rd * 0.01, rd.normalized(), ray.wavelength, ray.intensity * 0.98,
             ray.bounces + 1, ray.max_bounces)
    nr.path = ray.path.copy()
    nr.add_path_point(hit)
    return [nr]


# ============================================================================
# SLITS AND FILTERS
# ============================================================================


class Slit(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.slit_width = params.get("width", 1)
    self.slit_height = params.get("height", 20)
    self.plate_size = params.get("plate_size", 50)

  def get_type(self):
    return "slit"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if abs(h.x) > self.plate_size / 2 or abs(h.y) > self.plate_size / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    lh = self.to_local(hit)
    if abs(lh.x) < self.slit_width / 2 and abs(lh.y) < self.slit_height / 2:
      nr = Ray(hit + ray.direction * 0.01, ray.direction, ray.wavelength, ray.intensity,
               ray.bounces + 1, ray.max_bounces)
      nr.path = ray.path.copy()
      nr.add_path_point(hit)
      return [nr]
    return []


class BandpassFilter(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.center_wavelength = params.get("center_wavelength", 550)
    self.bandwidth = params.get("bandwidth", 50)
    self.diameter = params.get("diameter", 25)

  def get_type(self):
    return "filter_bandpass"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if math.sqrt(h.x**2 + h.y**2) > self.diameter / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    diff = ray.wavelength - self.center_wavelength
    trans = math.exp(-(diff**2) / (2 * (self.bandwidth / 2.355)**2))
    if trans > 0.01:
      nr = Ray(hit + ray.direction * 0.01, ray.direction, ray.wavelength, ray.intensity * trans,
               ray.bounces + 1, ray.max_bounces)
      nr.path = ray.path.copy()
      nr.add_path_point(hit)
      return [nr]
    return []


class BeamSplitter(OpticalDevice):

  def __init__(self, position: Vec3, rotation: Tuple[float, float, float], params: Dict = None):
    super().__init__(position, rotation, params)
    self.size = params.get("size", 25)

  def get_type(self):
    return "beam_splitter"

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Vec3]]:
    lo, ld = self.to_local(ray.origin), self.dir_to_local(ray.direction)
    if abs(ld.z) < 1e-10: return None
    t = -lo.z / ld.z
    if t < 0.001: return None
    h = Vec3(lo.x + t * ld.x, lo.y + t * ld.y, 0)
    if abs(h.x) > self.size / 2 or abs(h.y) > self.size / 2: return None
    return (t, self.dir_to_world(Vec3(0, 0, 1 if ld.z < 0 else -1)))

  def interact(self, ray: Ray, hit: Vec3, normal: Vec3) -> List[Ray]:
    rays = []
    tr = Ray(hit + ray.direction * 0.01, ray.direction, ray.wavelength, ray.intensity * 0.5,
             ray.bounces + 1, ray.max_bounces)
    tr.path = ray.path.copy()
    tr.add_path_point(hit)
    rays.append(tr)
    cos_i = -ray.direction.dot(normal)
    rd = ray.direction + normal * (2 * cos_i)
    rr = Ray(hit + rd * 0.01, rd.normalized(), ray.wavelength, ray.intensity * 0.5, ray.bounces + 1,
             ray.max_bounces)
    rr.path = ray.path.copy()
    rr.add_path_point(hit)
    rays.append(rr)
    return rays


# ============================================================================
# LIGHT SOURCE AND SCREEN
# ============================================================================


@dataclass
class LightSource:
  position: Vec3
  direction: Vec3
  spread_angle: float = 5.0
  wavelengths: List[float] = field(default_factory=lambda: get_white_light_wavelengths(300))
  intensity: float = 1.0
  rays_per_wavelength: int = 50

  def generate_rays(self) -> List[Ray]:
    rays = []
    spread_rad = math.radians(self.spread_angle)
    for wl in self.wavelengths:
      for _ in range(self.rays_per_wavelength):
        theta, phi = random.uniform(0, 2 * math.pi), random.uniform(0, spread_rad)
        up = Vec3(0, 1, 0) if abs(self.direction.y) < 0.9 else Vec3(1, 0, 0)
        right = self.direction.cross(up).normalized()
        actual_up = right.cross(self.direction).normalized()
        sd = self.direction + right * (math.sin(phi) * math.cos(theta)) + actual_up * (
          math.sin(phi) * math.sin(theta))
        rays.append(Ray(self.position, sd.normalized(), wl, self.intensity / len(self.wavelengths)))
    return rays


@dataclass
class Screen:
  position: Vec3
  normal: Vec3
  width: float = 100
  height: float = 100
  resolution: Tuple[int, int] = (256, 256)
  photon_packet_size: int = 1000  # Each ray represents this many photons

  def __post_init__(self):
    self.normal = self.normal.normalized()
    up = Vec3(0, 1, 0) if abs(self.normal.y) < 0.9 else Vec3(1, 0, 0)
    self.right = self.normal.cross(up).normalized()
    self.up = self.right.cross(self.normal).normalized()
    self.image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.float32)

  def intersect(self, ray: Ray) -> Optional[Tuple[float, Tuple[int, int]]]:
    denom = ray.direction.dot(self.normal)
    if abs(denom) < 1e-10: return None
    t = (self.position.dot(self.normal) - ray.origin.dot(self.normal)) / denom
    if t < 0.001: return None
    hit = ray.at(t)
    off = hit - self.position
    u, v = off.dot(self.right), off.dot(self.up)
    if abs(u) > self.width / 2 or abs(v) > self.height / 2: return None
    px = max(0, min(self.resolution[0] - 1, int((u / self.width + 0.5) * self.resolution[0])))
    py = max(0, min(self.resolution[1] - 1, int((0.5 - v / self.height) * self.resolution[1])))
    return (t, (px, py))

  def record_hit(self, ray: Ray, px: Tuple[int, int]):
    rgb = wavelength_to_rgb(ray.wavelength)
    scale = ray.intensity * self.photon_packet_size

    for offsetX in range(-2, 3):
      for offsetY in range(-2, 3):
        try:
          self.image[px[1] + offsetY, px[0] + offsetX, 0] += rgb[0] * scale / 4
          self.image[px[1] + offsetY, px[0] + offsetX, 1] += rgb[1] * scale / 4
          self.image[px[1] + offsetY, px[0] + offsetX, 2] += rgb[2] * scale / 4
        except IndexError:
          pass

  def get_image(self, blur_sigma: float = 6.0, glow_sigma: float = 12.0) -> Image.Image:
    """Convert accumulated photon hits to a smooth image.
    
    Uses multi-pass Gaussian convolution to spread light naturally:
    1. A tighter blur preserves color detail
    2. A wider "glow" pass fills in gaps and creates smooth gradients
    
    This simulates the continuous nature of real light rather than discrete photon hits.
    """
    from scipy.ndimage import gaussian_filter

    img = self.image.copy()

    # Pass 1: Tighter blur to smooth immediate neighbours
    detail = np.zeros_like(img)
    if blur_sigma > 0:
      for c in range(3):
        detail[:, :, c] = gaussian_filter(img[:, :, c], sigma=blur_sigma)

    # Pass 2: Wider glow to fill gaps and create smooth color gradients
    glow = np.zeros_like(img)
    if glow_sigma > 0:
      for c in range(3):
        glow[:, :, c] = gaussian_filter(img[:, :, c], sigma=glow_sigma)

    # Combine: detail layer + glow layer (glow helps fill sparse areas)
    combined = detail * 0.7 + glow * 0.5

    # Normalize and convert to 8-bit
    if combined.max() > 0:
      combined = combined / combined.max() * 255

    return Image.fromarray(np.clip(combined, 0, 255).astype(np.uint8))

  def is_saturated(self) -> bool:
    return self.image.max() >= 255


# ============================================================================
# SCENE
# ============================================================================


class OpticalScene:

  def __init__(self):
    self.devices: List[OpticalDevice] = []
    self.lights: List[LightSource] = []
    self.screen: Optional[Screen] = None

  def add_device(self, dev: OpticalDevice):
    self.devices.append(dev)

  def add_light(self, light: LightSource):
    self.lights.append(light)

  def set_screen(self, screen: Screen):
    self.screen = screen

  def trace_ray(self, ray: Ray) -> Optional[Tuple[int, int]]:
    while ray.bounces < ray.max_bounces and ray.intensity > 0.01:
      closest_t, closest_dev, closest_n = float('inf'), None, None
      for dev in self.devices:
        res = dev.intersect(ray)
        if res and res[0] < closest_t:
          closest_t, closest_n = res[0], res[1]
          closest_dev = dev
      if self.screen:
        sr = self.screen.intersect(ray)
        if sr and sr[0] < closest_t:
          ray.add_path_point(ray.at(sr[0]))
          return sr[1]
      if not closest_dev: return None
      hit = ray.at(closest_t)
      new_rays = closest_dev.interact(ray, hit, closest_n)
      if not new_rays: return None
      ray = new_rays[0]
    return None

  def run_simulation(self, max_rays: int = 50000) -> Image.Image:
    if not self.screen: raise ValueError("No screen")
    rc = 0
    for light in self.lights:
      while rc < max_rays and not self.screen.is_saturated():
        for ray in light.generate_rays():
          px = self.trace_ray(ray)
          if px: self.screen.record_hit(ray, px)
          rc += 1
          if rc >= max_rays: break
    return self.screen.get_image()


# ============================================================================
# DEVICE FACTORY
# ============================================================================

DEVICE_CLASSES = {
  "prism": Prism,
  "lens_convex": ConvexLens,
  "lens_concave": ConcaveLens,
  "mirror_flat": FlatMirror,
  "mirror_concave": ConcaveMirror,
  "slit": Slit,
  "filter_bandpass": BandpassFilter,
  "beam_splitter": BeamSplitter,
}


def create_device(dtype: str,
                  pos: List[float],
                  rot: List[float],
                  params: Dict = None) -> OpticalDevice:
  if dtype not in DEVICE_CLASSES: raise ValueError(f"Unknown device: {dtype}")
  return DEVICE_CLASSES[dtype](Vec3.from_list(pos), tuple(rot), params or {})
