import itertools
import random
import re
import scad_format
import OpenScad as vc
from LLMBenchCore.ResultPaths import result_path, report_relpath

title = "What's the largest prime number you can 3D print without supports?"

prompt = """
2 3D shapes can be said to be stackable if there exists an orientation in which:
- they can be stacked on top of each other without any overhang
- all lowest points on the top model touch the highest points of the lower model.
- the top shapes center of gravity is within the bottom shape.
- the entire stacks center of gravity is within the footprint of the bottom shape.
- they can be 3D printed without supports - ie no cantilevers or bridges.

For example, this sequence is stackable:
- Unit cube.
- Unit cylinder (of d = 1, h = 1)
- 3 legged stool, with a seat diameter of 1.
- 3 fair dice, with a size smaller than any seat leg.

The unit cube can rest in any stable orientation. The cylinder can sit on top with a flat face down.
The stool can be flipped upsidedown and sit on top of the cylinder. The dice can sit on top
of the legs (either one per leg, or stacked on top of each other on a single leg).

Side view of a stack:

``` ascii art
      o
      o
      o   Dice

     | |     | |       | |
     | |     | |       | |
     | |     | |       | | Stool. Legs facing up, seat facing down.
     | |     | |       | |
     =====================

     X-------------------X
     |||||||||||||||||||||
     |||||||||||||||||||||
     ||||||||||||||||||||| Cylinder (flat facing up and down)
     |||||||||||||||||||||
     |||||||||||||||||||||
     X-------------------X

     =====================
     =====================
     ===================== Unit cube
     =====================
     =====================
     =====================
     =====================
     =====================
------------------------------- Build plate / ground / Z = 0
```

So now you understand the concept. Lets try something more advanced!

Using: 
- A 7 segment display font, 
- Fixed digit sizes
- Reading from the ground up,

what is the largest prime number that can be 3D printed in a stack?

2, 3, 5 and 7 can all be printed obviously.

17 can be printed. The 1 can be printed flat first, and then the 7 can be printed rotated
around the y axis so that the long bar of the 7 is resting on the 1.

331 can be printed. One 3 flat. One 3 rotated around y so it has 3 spikes sticking up, and
then a 1 (rotated in y) balanced on the tip of the spikes. 

Can we go any higher?

Clarifications:
- Only a single digit can be printed at any one z level. So you can't print "138" by printing
  the 1 and 3 concurrently and then use that to support the 8.
- You can rotate in all 3 direction, so you can print a 3 on a 7 by rotating it "spikes up", but
  you can't then print another rotated 3 on top of it, because between the points of the 3
  it would overhang.
- No duplicate triples. To ensure we don't consider infinite solutions, no triple can be repeated.
  - When written with commas every 3 digits and split, there should be no duplicates in that list.
  - So 123,321,123 is not allowed, but 123,111,231 is allowed.
  - This helps keep the problem solvable with under 1000 digits!
- The digit segments are 10x10x1mm, with their centres on [-5,0,5],[-10,0,10]. An 8 printed flat 
  has a span of -5.5 < x < 5.5 and -10.5 < y < 10.5 and -0.5 < z < 0.5, and 2 interior squares 
  each of 9x9mm.
- A 0.2mm gap in Z exists between digits in the print as sent to the the printer, the dynamics
  of molten plastic causes this gap to break thermal conductivity, to allow digits to be easily 
  separated after printing.

One of my coworkers is bragging they've solved it, and they have a stack that's 7cm high. As a 
secondary objective, can we beat that height?

"""

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "numberSequence": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "digit": {
            "type": "integer"
          },
          "orientation": {
            "type":
            "string",
            "enum": ["flat", "flippedX", "flippedY", "rotate90X", "rotate90Y", "rotate180Z"],
            "description":
            "flat = as is. Flipped X turns a 3 into an E. Flipped Y turns a 5 into a 2. Rotate 90 X makes 7 have a short spike facing up in Z. Rotate 90 Y makes 7 have a long spike facing up in Z. Rotate 180Z turns a 6 into a 9. All other rotations do not produce anything printable. "
          },
        },
        "propertyOrdering": ["digit", "orientation"],
        "required": ["digit", "orientation"],
        "additionalProperties": False
      },
    },
  },
  "required": ["numberSequence", "reasoning"],
  "propertyOrdering": ["numberSequence", "reasoning"],
  "additionalProperties": False
}


def canPrintOnTop(num):
  "Returns flat prints, and then side prints"
  if num == 0: return [0, 1, 7], [1, 3, 7]
  if num == 1: return [1], [1, 3, 7]
  if num == 2: return [2, 5], []
  if num == 3: return [1, 3, 7], [1, 3, 7]
  if num == 4: return [1, 4], [1, 3, 7]
  if num == 5: return [2, 5], []
  if num == 6: return [1, 3, 5, 6, 7, 9, 4], [1, 3, 7]
  if num == 7: return [1, 7], [1, 3, 7]
  if num == 8: return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 3, 7]
  if num == 9: return [1, 3, 5, 6, 7, 9], [1, 3, 7]


def gradeAnswer(answer: dict, subPassIndex: int, aiEngineName: str):
  numberSequence = answer["numberSequence"]

  # Build the number from the digit sequence
  number_str = ""
  for item in numberSequence:
    number_str += str(item["digit"])

  if number_str == "":
    return 0, "Empty number"

  number = int(number_str)

  # Check for repeated 3-tuples
  if t := containsAny3TupleMoreThanOnce(number_str):
    return 0, str(number) + " contains a sequence of 3 digits repeated more than once: " + str(t)

  # Check if each individual digit can be printed on its own.
  flatOrientations = ["flat", "flippedX", "flippedY", "rotate180Z"]
  height = 0

  for n in numberSequence:
    digit = n["digit"]
    orientation = n["orientation"]
    if orientation in flatOrientations:
      height += 1.2
    elif orientation == "rotate90X":
      height += 21.2
    elif orientation == "rotate90Y":
      if digit == 1:
        height += 1.2
      else:
        height += 11.2

    if orientation in flatOrientations:
      # Everything can be printed flat.
      continue
    if orientation == "rotate90X":
      if digit not in [1, 3, 7]:
        return 0, f"Digit {digit} (orientation: {orientation}) has overhangs."

    if orientation == "rotate90Y":
      if digit not in [1, 7]:
        return 0, f"Digit {digit} (orientation: {orientation}) has overhangs."

  # Check if it's prime
  if not isPrime(number):
    return 0, str(number) + " is not prime"

  i = 0
  while i < len(numberSequence) - 1:
    current_digit = numberSequence[i]["digit"]
    current_orientation = numberSequence[i]["orientation"]
    next_digit = numberSequence[i + 1]["digit"]
    next_orientation = numberSequence[i + 1]["orientation"]


    if current_orientation in flatOrientations and \
        next_orientation in flatOrientations:
      # we're staying flat!
      allowed_digits = canPrintOnTop(current_digit)[0]
      # Check if the next digit can be printed on top
      if next_digit not in allowed_digits:
        return 0, f"Digit {next_digit} (orientation: {next_orientation}) cannot be printed on top of digit {current_digit} (orientation: {current_orientation})<br>Stack is not printable."

      i += 1
      continue

    if next_orientation in flatOrientations:
      # We can only go back to flat if we're printing a 1 on top of a 1
      if current_digit != 1 or next_digit != 1 or current_orientation == "rotate90Y":
        return 0, f"Digit {next_digit} (orientation: {next_orientation}) cannot be printed on top of digit {current_digit} (orientation: {current_orientation})<br>Stack is not printable."
      i += 1
      continue

    if current_orientation == "rotate90Y":
      # After anything sticking up, we can only print 1s in rotate90X
      if next_digit != 1 or next_orientation != "rotate90X":
        return 0, f"Digit {next_digit} (orientation: {next_orientation}) cannot be printed on top of digit {current_digit} (orientation: {current_orientation})<br>Stack is not printable."
      i += 1
      continue

    if next_orientation == "rotate90X":
      assert (next_digit in [1, 3, 7])  # Should've been caught earlier.
      # This can go on top of anything.
      i += 1
      continue

    if next_orientation == "rotate90Y":
      assert (next_digit in [1, 7])
      # This can go on top of anything except a 2 and a 5
      if current_digit in [2, 5]:
        return 0, f"Digit {next_digit} (orientation: {next_orientation}) cannot be printed on top of digit {current_digit} (orientation: {current_orientation})<br>Stack is not printable."
      i += 1
      continue

    return 100, f"Digit {next_digit} (orientation: {next_orientation}) wasn't coded if it could be printed on top of digit {current_digit} (orientation: {current_orientation})<br>Grading code needs updating."

  # The solution is all of these flat, rotating the 9's to fit on the 6's, then
  # flipping the 3's to fit on the 6's, then a stack of 7's flipped in X, then 2 * 1 flat (flipped in X),
  # then a 7 on it's side, and then a 1 stacked on top of it in a giant spike.

  solution = 888999996969699696669666333377777711111171
  solution_len = len(str(solution))

  # I am very confident I found the best solution, however, if I'm every proven wrong,
  # this will need updating. A score over 100 should stand out in the report.
  if number > solution:
    return 100, "Test needs updating. Well done!"

  numberScore = len(number_str) / solution_len

  if height > 70:
    return numberScore, f"Answer given was of length {len(number_str)} while the "\
      f"largest printable prime is of length {solution_len}.<br><br> "\
      f"Height was {height:.1f}mm which was over the target height of 70mm."
  else:
    return numberScore*0.9, f"Answer given was of length {len(number_str)} while the "\
      f"largest printable prime is of length {solution_len}.<br><br> "\
      f"Height was {height:.1f}mm which was under the target height of 70mm, so "\
      "penalized by 10%."


def resultToNiceReport(answer: dict, subPassIndex: int, aiEngineName: str):

  scad = ""

  number = ""

  height = 0

  colors = [
    "\"White\"", "\"Red\"", "\"Blue\"", "\"Yellow\"", "\"Green\"", "[0,0,0.5]", "[0.5,0,0]",
    "\"Orange\"", "[210/255, 180/255, 140/255]", "[170/255, 140/255, 100/255]",
    "[92/255, 64/255, 51/255]", "[62/255, 38/255, 20/255]"
  ]

  random.shuffle(colors)

  for index, item in enumerate(answer["numberSequence"]):
    d = ""
    number += str(item["digit"])
    if item["digit"] in [0, 2, 3, 5, 6, 8, 9]:
      d += "translate([0,-10,0]) cube([10,1,1], center=true);"
    if item["digit"] in [2, 3, 4, 5, 6, 8, 9]:
      d += "translate([0,0,0]) cube([10,1,1], center=true);"
    if item["digit"] in [0, 2, 3, 5, 6, 7, 8, 9]:
      d += "translate([0,10,0]) cube([10,1,1], center=true);"

    if item["digit"] in [0, 2, 6, 8]:
      d += "translate([-5,-5,0]) cube([1,10,1], center=true);"

    if item["digit"] in [0, 1, 3, 4, 5, 6, 7, 8, 9]:
      d += "translate([5,-5,0]) cube([1,10,1], center=true);"

    if item["digit"] in [0, 4, 5, 6, 8, 9]:
      d += "translate([-5,5,0]) cube([1,10,1], center=true);"

    if item["digit"] in [0, 1, 2, 3, 4, 7, 8, 9]:
      d += "translate([5,5,0]) cube([1,10,1], center=true);"

    d = "// " + str(item) + "\nunion(){\n" + d + "}\n"

    scad += f"color({colors[index % len(colors)]}) translate([0,0,{height}])"

    height += 1.2

    if item["orientation"] == "rotate90X":
      if item["digit"] == 1:
        # Put the one over a corner, such that it will stand on anything.
        d = "translate([-10,10,14]) rotate([90,0,0])" + d
      else:
        # This is probably an error anyway.
        d = "rotate([90,0,0])" + d

      height += 19
    if item["orientation"] == "rotate90Y":
      if item["digit"] == 1:
        pass  # No-op
      else:
        d = "translate([-5,0,5]) rotate([0,90,0])" + d
        height += 5
    if item["orientation"] == "rotate180Z":
      d = "rotate([0,0,180])" + d
    if item["orientation"] == "flippedX":
      d = "mirror([1,0,0])" + d
    if item["orientation"] == "flippedY":
      d = "mirror([0,1,0])" + d

    scad += d
    scad += "\n\n"

  import os
  output_path = result_path("30_Visualization_" + aiEngineName + "_" + str(len(
    answer["numberSequence"])) + ".png", aiEngineName)
  vc.render_scadText_to_png(scad, output_path, "--camera=-10,-10,10,55,0,25,100")
  print(f"Saved visualization to {output_path}")

  scadFile = result_path("30_Visualization_" + aiEngineName + "_" + str(len(
    answer["numberSequence"])) + "temp.scad", aiEngineName)

  open(scadFile, "w").write(scad_format.format(scad, vc.formatConfig))

  import zipfile
  with zipfile.ZipFile(output_path.replace(".png", ".zip"), 'w') as zipf:
    zipf.write(scadFile, os.path.basename(scadFile))

  os.unlink(scadFile)

  if number == "": number = 0

  return f"""
<a href="{report_relpath(output_path.replace('.png', '.zip'), aiEngineName)}" download>
<img src="{report_relpath(output_path, aiEngineName)}" alt="Stacked digits Visualization" style="max-width: 100%; float:left">
</a>
<br><div style='clear:both;'>Ai suggested {int(number):,} ({len(answer["numberSequence"]):,} digits).<br>The correct answer is 24 digits long.</div>
"""


# Prime cache stored in temp directory
import os
import tempfile
import json

_prime_cache_path = os.path.join(tempfile.gettempdir(), "prime_cache_30.json")
_prime_cache = None


def _load_prime_cache():
  global _prime_cache
  if _prime_cache is None:
    try:
      with open(_prime_cache_path, 'r') as f:
        _prime_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
      _prime_cache = {}
  return _prime_cache


def _save_prime_cache():
  if _prime_cache is not None:
    with open(_prime_cache_path, 'w') as f:
      json.dump(_prime_cache, f)


def _miller_rabin_test(n, a):
  """Single Miller-Rabin witness test."""
  # Write n-1 as 2^r * d
  d = n - 1
  r = 0
  while d % 2 == 0:
    d //= 2
    r += 1

  # Compute a^d mod n
  x = pow(a, d, n)
  if x == 1 or x == n - 1:
    return True

  for _ in range(r - 1):
    x = pow(x, 2, n)
    if x == n - 1:
      return True
  return False


def _jacobi_symbol(a, n):
  """Compute Jacobi symbol (a/n) for odd n > 0."""
  if n <= 0 or n % 2 == 0:
    raise ValueError("n must be odd and positive")
  a = a % n
  result = 1
  while a != 0:
    while a % 2 == 0:
      a //= 2
      if n % 8 in (3, 5):
        result = -result
    a, n = n, a
    if a % 4 == 3 and n % 4 == 3:
      result = -result
    a = a % n
  return result if n == 1 else 0


def _lucas_sequence(n, D, P, Q, k):
  """Compute U_k and V_k of Lucas sequence mod n using binary method."""
  if k == 0:
    return 0, 2

  # Start with U_1 = 1, V_1 = P
  U, V = 1, P
  Qk = Q  # Tracks Q^m where m is current index

  # Process remaining bits after the leading 1
  bits = bin(k)[3:]  # Skip '0b1'

  for bit in bits:
    # Double: U_{2m} = U_m * V_m, V_{2m} = V_m^2 - 2*Q^m
    U = (U * V) % n
    V = (V * V - 2 * Qk) % n
    Qk = (Qk * Qk) % n

    if bit == '1':
      # Add 1: U_{m+1} = (P*U + V)/2, V_{m+1} = (D*U + P*V)/2
      U_new = P * U + V
      V_new = D * U + P * V
      if U_new % 2: U_new += n
      if V_new % 2: V_new += n
      U = (U_new // 2) % n
      V = (V_new // 2) % n
      Qk = (Qk * Q) % n

  return U, V


def _strong_lucas_test(n):
  """Strong Lucas primality test using Selfridge's Method A for D selection."""
  if n < 2:
    return False
  if n == 2:
    return True
  if n % 2 == 0:
    return False

  # Check for perfect square (Lucas test requires n not be a perfect square)
  sqrt_n = int(n**0.5)
  if sqrt_n * sqrt_n == n:
    return False

  # Selfridge's Method A: find D where Jacobi(D, n) = -1
  D = 5
  while True:
    g = _jacobi_symbol(D, n)
    if g == 0:
      return abs(D) != n  # n divides D, so n is composite unless n == |D|
    if g == -1:
      break
    D = -D - 2 if D > 0 else -D + 2
    if D == -15:  # Safety check for perfect squares we might have missed
      sqrt_n = int(n**0.5)
      if sqrt_n * sqrt_n == n:
        return False

  P, Q = 1, (1 - D) // 4

  # Write n+1 = 2^s * d where d is odd
  d = n + 1
  s = 0
  while d % 2 == 0:
    d //= 2
    s += 1

  U, V = _lucas_sequence(n, D, P, Q, d)
  Qd = pow(Q, d, n)  # Compute Q^d once

  # Strong Lucas: n is probably prime if U_d ≡ 0 (mod n) or V_{d*2^r} ≡ 0 (mod n) for some 0 ≤ r < s
  if U == 0 or V == 0:
    return True

  for _ in range(s - 1):
    V = (V * V - 2 * Qd) % n
    Qd = (Qd * Qd) % n  # Q^{2d}, Q^{4d}, etc.
    if V == 0:
      return True

  return False


def isPrime(num: int) -> bool:
  """BPSW primality test with caching. No known counterexamples exist."""
  if num < 2:
    return False

  # Check cache first
  cache = _load_prime_cache()
  key = str(num)
  if key in cache:
    return cache[key]

  # Small primes
  small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
  if num in small_primes:
    cache[key] = True
    _save_prime_cache()
    return True

  # Quick divisibility check
  for p in small_primes:
    if num % p == 0:
      cache[key] = False
      _save_prime_cache()
      return False

  # BPSW test: Miller-Rabin base 2 + Strong Lucas test
  # No known counterexamples exist for any n (verified computationally to 2^64 and beyond)

  # Step 1: Miller-Rabin with base 2
  if not _miller_rabin_test(num, 2):
    cache[key] = False
    _save_prime_cache()
    return False

  # Step 2: Strong Lucas test
  result = _strong_lucas_test(num)

  cache[key] = result
  _save_prime_cache()
  return result


def containsAny3TupleMoreThanOnce(s: str) -> bool:
  s = s[::-1]

  tuples = list(itertools.batched(s, 3))
  sets = set(tuples)
  if len(tuples) != len(sets):
    for s in sets:
      if tuples.count(s) > 1:
        return s

  return None


printableFlats = []


def finalAllFlatSequences(num: str):
  lastDigit = num[-1]

  suffixes = canPrintOnTop(int(lastDigit))[0]
  for suffix in suffixes:
    newNumber = num + str(suffix)

    if len(newNumber) >= 3:
      last3Digits = str(newNumber)[-3:]
      if newNumber.count(last3Digits) > 1:
        continue

    printableFlats.append(newNumber)
    finalAllFlatSequences(newNumber)


if __name__ == "__main__":

  # Depending on where the boundary splitting into groups of 3 goes, we might be able
  # to get up to 5 repeated digits.
  # ie 888,889  888,899   888,999 so we have to build our bases algorithmically.

  bases = []

  for i8 in range(3, 6):
    for i3 in range(3, 6):
      for i7 in range(3, 6):
        bases.append(
          int("8" * i8 + ("999"
                          "996"
                          "969"
                          "699"
                          "696"
                          "669"
                          "666") + "3" * i3 + "7" * i7))

  bases2 = bases
  bases = []
  for b in bases2:
    if containsAny3TupleMoreThanOnce(str(b)) and containsAny3TupleMoreThanOnce(
        str(b) + "0") and containsAny3TupleMoreThanOnce(str(b) + "00"):
      continue
    bases.append(b)

  print("Found " + str(len(bases)) + " bases:")
  print("\n".join(map(str, bases)))

  longestPrintablePrime = 7

  tried = 0

  suffixes = []

  for suffix in itertools.product(["", "3", "1", "7"], repeat=10):
    suffix = "".join(suffix)

    # Suffix starts printing on a flat 7.

    topBarAllowed = True
    longSideAllowed = True

    invalid = False
    for s in suffix:
      if topBarAllowed and longSideAllowed:
        if s == "7": continue
        if s == "3":
          # We have to rotate the 3
          topBarAllowed = False
          longSideAllowed = False
        if s == "1":
          # We loose the ability to print the top bar.
          topBarAllowed = False
      elif longSideAllowed:
        if s == "1": continue
        if s in ["3", "7"]:
          # We have to rotate the 3 or 7 leaving spikes up
          topBarAllowed = False
          longSideAllowed = False
      else:
        if s == "1": continue
        invalid = True

    if invalid:
      continue

    suffixes.append(suffix)

  print("Found " + str(len(suffixes)) + " suffixes:")
  print("\n".join(suffixes))

  print("\n")

  for base in bases:
    for suffix in suffixes:
      num = str(base) + suffix

      if int(num) <= longestPrintablePrime:
        continue
      if containsAny3TupleMoreThanOnce(num):
        continue

      tried += 1
      if tried % 10000 == 0:
        print("Tried " + str(tried) + " candidates. Trying " + num + " next.")
      if isPrime(int(num)):
        longestPrintablePrime = int(num)
        print(longestPrintablePrime)
        print(str(base) + " lying flat with suffix " + suffix)

  for base in bases:
    num = str(base) + "3111"
    if isPrime(int(num)):
      print("The tallest prime is " + num)

  print("The longest printable prime is " + str(longestPrintablePrime))

highLevelSummary = """
So this test has 2 components, a visual one and a maths one.<br><br>

The maths problem is computationally extreme - finding a prime
with no 3 digit sequence repeated. The answer is around 1000
digits long. If you tackle this first, you're going to have a bad time.<br><br>

The visual problem is way simpler - each digit and orientation
choice limits the future choices, and the problem size drastically
shrinks with each step of it you solve. For example an 8:<ul>
<li>Can't be printed on it's long or short side, as that has bridge overhangs.</li>
<li>When printed flat, must not occur after any number except 8 (or the start)</li>
</ul>

So... our answer set diverges into 4 immediately:<ul>
<li>^[0123456789]+</li>
<li>^8[0123456789]+</li>
<li>^88[0123456789]+</li>
<li>^888[0123456789]+</li>
</ul>
The largest of which is the last, so the answer must start with 888, printed all flat.<br><br>

Then if we put anything other than a 6 or a 9, we'll never be able to put a 6 or 9, therefore 
the next digit must be... etc etc.<br><br>

The visual part of the problem gives the prefix of the answer and greatly limits
the search space for the suffix. If the AI is 'offering to build a program to find the
prime number' or whatever, it probably deserves its 0, as an exhaustive search for this
required only ~50 calls to "isPrime" to discover the 24 digit answer.<br><br>

As a secondary objective, we want the AI to lay it out in the tallest possible stack. The largest and
tallest possible prime numbers are different:<br>
Tallest: 88888999996969699696669666333337773111 (The last 3 1's are a spire).<br>
Largest: 888999996969699696669666333377777711111171<br>
But we instruct the AI this is a secondary priority. This complicaiton was
added as both gemini-3-pro and gpt-5.2-pro both figured out the '9 can be printed on 8 but not 8 on 9'
part of the problem and I foresaw it being solved by the next version.
"""
