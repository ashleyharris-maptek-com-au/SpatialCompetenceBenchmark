import random, scad_format
import subprocess
import tempfile
import StlVolume
import os
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

openScadPath = R"C:\Program Files\OpenSCAD\openscad.exe"
if not os.path.exists(openScadPath):
  openScadPath = R"C:\Program Files (x86)\OpenSCAD\openscad.exe"
if not os.path.exists(openScadPath):
  raise FileNotFoundError("OpenSCAD executable not found at expected paths")

formatConfig = scad_format.FormatConfig(
  IndentWidth=2,
  ContinuationIndentWidth=2,
  ColumnLimit=120,
  BreakBeforeBraces=scad_format.config.BraceBreakingStyle.Allman)


class TimeoutError(Exception):
  """Raised when OpenSCAD times out."""
  pass


def run_openscad(input_scad: str,
                 output_file: str,
                 timeout: Optional[float] = None) -> Optional[str]:
  """Run OpenSCAD to generate output file from SCAD input.
    
    Returns error message string if there was an error, None otherwise.
    Raises TimeoutError if timeout is specified and exceeded.
    """
  try:
    result = subprocess.run([openScadPath, "-o", output_file, input_scad],
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=timeout)
  except subprocess.TimeoutExpired:
    print(f"OpenSCAD timed out after {timeout}s for {input_scad}")
    return f"OpenSCAD render timed out after {timeout} seconds"
  if result.returncode != 0:
    print(f"Warning: OpenSCAD returned non-zero exit code for {input_scad}")
    error_msg = f"OpenSCAD error for {os.path.basename(input_scad)}:\n"
    if result.stdout:
      error_msg += f"stdout: {result.stdout}\n"
    if result.stderr:
      error_msg += f"stderr: {result.stderr}"
      print(f"Error output: {result.stderr}")
    return error_msg
  return None


def render_stl_to_png(stl_path: str, png_path: str) -> None:
  """Render an STL file to PNG using OpenSCAD with an off-axis camera."""
  # Create a temporary SCAD file that imports the STL
  temp_scad = stl_path.replace(".stl", "_render.scad")
  render_scadText_to_png(f'import("{os.path.basename(stl_path)}");', png_path)

  # Clean up the temporary SCAD file
  try:
    os.remove(temp_scad)
  except OSError:
    pass


def render_scadText_to_png(scad_content: str,
                           png_path: str,
                           cameraArg: str = "--camera=10,10,10,55,0,25,100",
                           extraScadArgs: List[str] = []) -> None:
  """Render SCAD content to PNG using OpenSCAD with an off-axis camera."""
  # Create a temporary SCAD file with the provided content
  temp_scad = png_path.replace(".png", "temp.scad")
  with open(temp_scad, "w", encoding="utf-8") as f:
    f.write(scad_content)

  # Use off-axis camera: positioned at (10, 10, 10) looking at origin
  # Format: --camera=x,y,z,rot_x,rot_y,rot_z,distance
  # We'll use auto-center and a good viewing angle
  try:
    args = [
      openScadPath, "--autocenter", "--viewall", cameraArg, "--imgsize=800,600",
      "--colorscheme=Starnight", "-o",
      os.path.basename(png_path), *extraScadArgs,
      os.path.basename(temp_scad)
    ]

    if extraScadArgs:
      args.remove("--autocenter")
      args.remove("--viewall")

    if "--no-autocenter" in args:
      args.remove("--no-autocenter")

    print(args)
    result = subprocess.run(args,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            cwd=os.path.dirname(png_path),
                            timeout=600)
  except subprocess.TimeoutExpired:
    print(f"OpenSCAD timed out after 600s for {png_path}")
    try:
      os.unlink(temp_scad)
    except:
      pass
    return
  if result.returncode != 0:
    print(f"Warning: OpenSCAD PNG rendering returned non-zero exit code")
    if result.stderr:
      print(f"Error output: {result.stderr}")

  try:
    os.unlink(temp_scad)
  except:
    pass


def hit_tests(stlFile: str, interceptStlStrings: List[str], operation="intersection") -> List[bool]:
  """
    For each interceptor (specified as an OpenSCAD string), returns true if it intercepts the STL file.
    These are calculated in parallel using concurrent calls to OpenSCAD and checking
    if the intersection volume is non-zero.

    Eg hit_tests("sphereOfRadius10.stl", [
      "translate([-50,0,0]) cube([1,1,50], center=true)",
      "translate([0,0,0]) cube([1,1,50], center=true)",
      "translate([50,0,0]) cube([1,1,50], center=true)"
     ]) will return [False, True, False]
    """
  temp_dir = tempfile.mkdtemp(prefix="hit_test_")
  stlFile = os.path.abspath(stlFile)

  def check_intersection(idx: int, interceptor: str) -> tuple:
    scad_path = os.path.join(temp_dir, f"intersect_{random.randint(0,10000)}.scad")
    stl_path = os.path.join(temp_dir, f"intersect_{random.randint(0,10000)}.stl")

    with open(scad_path, "w", encoding="utf-8") as f:
      f.write(f'{operation}() {{\n')
      f.write(f'    import("{stlFile.replace(os.sep, "/")}");\n')
      f.write(f'    {interceptor};\n')
      f.write(f'}}\n')

    err = run_openscad(scad_path, stl_path, timeout=120)
    if err:
      return idx, False

    if not os.path.exists(stl_path) or os.path.getsize(stl_path) == 0:
      return idx, False

    volume = StlVolume.calculate_stl_volume(stl_path)
    return idx, volume > 0

  results = [False] * len(interceptStlStrings)

  with ThreadPoolExecutor() as executor:
    futures = {
      executor.submit(check_intersection, i, interceptor): i
      for i, interceptor in enumerate(interceptStlStrings)
    }
    for future in as_completed(futures):
      idx, hit = future.result()
      results[idx] = hit

  return results
