import random
import scad_format
import OpenScad as vc

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
- Fixed diget sizes
- Reading from the ground up,

what is the largest prime number that can be 3D printed in a stack?

2, 3, 5 and 7 can all be printed obviously.

17 can be printed. The 1 can be printed flat first, and then the 7 can be printed rotated
around the y axis so that the long bar of the 7 is resting on the 1.

331 can be printed. One 3 flat. One 3 rotated around y so it has 3 spikes sticking up, and
then a 1 (rotated in y) balenced on the tip of the spikes. 

Can we go any higher?

Clarifications:
- A ban on repeating any sequence of 3 more than once. 
  - So 888 and 6969 substrings are allowed, but 8888 or 69696 are not allowed.
  - The helps keep the problem solvable with under 1000 digits!
- Only a single diget can be printed at any one z level. So you can't print "138" by printing
  the 1 and 3 concurrently and then use that to support the 8.
- You can rotate in all 3 direction, so you can print a 3 on a 7 by rotating it "spikes up", but
  you can't then print another rotated 3 on top of it, becasuse between the points of the 3
  it would overhang.
- The digit segments are 10x10x1mm, with their centres on [-5,0,5],[-10,0,10]. An 8 has a span
  of -5.5 < x < 5.5 and -10.5 < y < 10.5, and 2 interior squares each of 9x9.
- A 0.5mm gap in Z exists between digits in the print as sent to the the printer, the dynamics
  of molten plastic causes this gap to appear as a fracture point, to allow digits to be easily 
  seperated after printing.

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
  if containsAny3TupleMoreThanOnce(number_str):
    return 0, str(number) + " contains a sequence of 3 digits repeated more than once"

  # Check if each individual diget can be printed on it's own.
  flatOrientations = ["flat", "flippedX", "flippedY", "rotate180Z"]
  height = 0

  for n in numberSequence:
    digit = n["digit"]
    orientation = n["orientation"]
    if orientation in flatOrientations:
      height += 1.5
    elif orientation == "rotate90X":
      height += 21.5
    elif orientation == "rotate90Y":
      if digit == 1:
        height += 1.5
      else:
        height += 11.5

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

  # The solution (AFAIK) is all of these flat, rotating the 6's to fit on the 9's, then
  # flipping the 3's to fit on the 6's, then a stack of 7's, then 2 * 1 flat, then
  # a 7 on it's side, and then 2 * 1's stacked on top of it.
  solution = 888_999_6969_666_333_777_11_7_11
  solution_len = len(str(solution))

  # I am very confident I found the best solution, however, if I'm every proven wrong,
  # this will need updating.
  if number > solution:
    return 100, "Test needs updating. Well done!"

  numberScore = len(number_str) / solution_len

  if height > 70:
    return numberScore, f"Answer given was of length {len(number_str)} while the "\
      f"largest printable prime (I know of) is of length {solution_len}. "\
      f"Height was {height}mm which was over the target height of 70mm."
  else:
    return numberScore*0.9, f"Answer given was of length {len(number_str)} while the "\
      f"largest printable prime (I know of) is of length {solution_len}. "\
      f"Height was {height}mm which was under the target height of 70mm, so "\
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

    height += 1.5

    if item["orientation"] == "rotate90X":
      if item["digit"] == 1:
        # Put the one over a corner, such that it will stand on anything.
        d = "translate([-10,10,14]) rotate([90,0,0])" + d
      else:
        # This is probably an error anyway.
        d = "rotate([90,0,0])" + d

      height += 18
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
  os.makedirs("results", exist_ok=True)
  output_path = "results/30_Visualization_" + aiEngineName + "_" + str(len(
    answer["numberSequence"])) + ".png"
  vc.render_scadText_to_png(scad, output_path, "--camera=-10,-10,10,55,0,25,100")
  print(f"Saved visualization to {output_path}")

  scadFile = "results/30_Visualization_" + aiEngineName + "_" + str(len(
    answer["numberSequence"])) + "temp.scad"

  open(scadFile, "w").write(scad_format.format(scad, vc.formatConfig))

  import zipfile
  with zipfile.ZipFile(output_path.replace(".png", ".zip"), 'w') as zipf:
    zipf.write(scadFile, os.path.basename(scadFile))

  os.unlink(scadFile)

  return f"""
<a href="{os.path.basename(output_path).replace(".png", ".zip")}" download>
<img src="{os.path.basename(output_path)}" alt="Stacked digits Visualization" style="max-width: 100%; float:left">
</a>
<p><div style="float:right">Ai suggested {number} ({len(answer["numberSequence"])} digits).<br>The correct answer is 24 digits long.</div></p>
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


def isPrime(num: int) -> bool:
  """Miller-Rabin primality test with caching. Deterministic for n < 3,317,044,064,679,887,385,961,981."""
  if num < 2:
    return False

  # Check cache first
  cache = _load_prime_cache()
  key = str(num)
  if key in cache:
    return cache[key]

  # Small primes
  small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
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

  if num >= 3_317_044_064_679_887_385_961_981:
    # fall back to a naive prime check for numbers too large for Miller-Rabin
    cache[key] = all(num % i != 0 for i in range(2, int(num**0.5) + 1))
    _save_prime_cache()
    return cache[key]

  # Miller-Rabin with deterministic witnesses for numbers up to 3,317,044,064,679,887,385,961,981
  # These witnesses are proven sufficient for this range
  witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

  result = all(_miller_rabin_test(num, a) for a in witnesses if a < num)

  cache[key] = result
  _save_prime_cache()
  return result


def containsAny3TupleMoreThanOnce(s: str) -> bool:
  for i in range(0, len(s) - 2):
    for j in range(i + 1, len(s) - 2):
      if s[i] == s[i + 1] == s[i + 2] == s[j] == s[j + 1] == s[j + 2]:
        return True
  return False


printableFlats = []


def finalAllFlatSequences(num: str):
  lastDiget = num[-1]

  suffixes = canPrintOnTop(int(lastDiget))[0]
  for suffix in suffixes:
    newNumber = num + str(suffix)

    if len(newNumber) >= 3:
      last3Digets = str(newNumber)[-3:]
      if newNumber.count(last3Digets) > 1:
        continue

    printableFlats.append(newNumber)
    finalAllFlatSequences(newNumber)


if __name__ == "__main__":
  base = 888_999_6969_666_333_777
  longestPrintablePrime = 7

  for suffix in [
      111711, 117111, 111311, 11311, 17111, 13111, 11711, 11311, 1711, 1311, 711, 311, 71, 31, 11, 1
  ]:
    num = str(base) + str(suffix)
    if int(num) < longestPrintablePrime:
      continue
    if not containsAny3TupleMoreThanOnce(num) and isPrime(int(num)):
      longestPrintablePrime = int(num)
      print(longestPrintablePrime)

if __name__ == "__main__":
  print(
    resultToNiceReport(
      {
        "numberSequence": [
          {
            "digit": 8,
            "orientation": "flat"
          },
          {
            "digit": 8,
            "orientation": "flat"
          },
          {
            "digit": 8,
            "orientation": "flat"
          },
          {
            "digit": 9,
            "orientation": "flat"
          },
          {
            "digit": 9,
            "orientation": "flat"
          },
          {
            "digit": 9,
            "orientation": "flat"
          },
          {
            "digit": 6,
            "orientation": "rotate180Z"
          },
          {
            "digit": 9,
            "orientation": "flat"
          },
          {
            "digit": 6,
            "orientation": "rotate180Z"
          },
          {
            "digit": 9,
            "orientation": "flat"
          },
          {
            "digit": 6,
            "orientation": "rotate180Z"
          },
          {
            "digit": 6,
            "orientation": "rotate180Z"
          },
          {
            "digit": 6,
            "orientation": "rotate180Z"
          },
          {
            "digit": 3,
            "orientation": "flat"
          },
          {
            "digit": 3,
            "orientation": "flat"
          },
          {
            "digit": 3,
            "orientation": "flat"
          },
          {
            "digit": 7,
            "orientation": "flat"
          },
          {
            "digit": 7,
            "orientation": "flat"
          },
          {
            "digit": 7,
            "orientation": "flat"
          },
          {
            "digit": 1,
            "orientation": "flat"
          },
          {
            "digit": 1,
            "orientation": "flat"
          },
          {
            "digit": 7,
            "orientation": "rotate90X"
          },
          {
            "digit": 1,
            "orientation": "rotate90X"
          },
          {
            "digit": 1,
            "orientation": "rotate90X"
          },
        ]
      }, 0, "Ash screwing around with Python"))

highLevelSummary = """
So this test has 2 components, a visual one and a maths one.<br><br>

The maths problem is computationally extreme - finding a prime
with no 3 diget sequence repeated. The answer is around 1000
digets long. If you tackle this first, you're going to have a bad time.<br><br>

The visual problem is way simpler - each diget and orientation
choice limits the future choices, and the problem size drastically
shrinks with each step of it you solve. For example an 8:<ul>
<li>Can't be printed on it's long or short side, as that has bridge overhangs.</li>
<li>When printed flat, must not occur after any number except 8 (or the start)</li>
</ul>

So... our answer set diverges into 4 immediately:<ul>
<li>^[0123456790]+</li>
<li>^8[0123456790]+</li>
<li>^88[0123456790]+</li>
<li>^888[0123456790]+</li>
</ul>
The largest of which is the last, so the answer must start with 888, printed all flat.<br><br>

Then if we put anything other than a 6 or a 9, we'll never be able to put a 6 or 9, therefore 
the next digit must be... etc etc.<br><br>

The visual part of the problem gives the prefix of the answer and greatly limits
the search space for the suffix. If the AI is 'offering to build a program to find the
prime number' or whatever, it probably deserves its 0, as an exhaustive search for this
required only ~50 calls to "isPrime" to discover the 24 digit answer.<br><br>

As a secondary objective, we want the AI to lay it out in the tallest possible stack. The largest
possible is 86mm, but we tell it to aim for 70mm or higher. This is only 10% of the grade.
"""
