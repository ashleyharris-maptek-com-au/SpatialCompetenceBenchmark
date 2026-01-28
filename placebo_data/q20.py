import math, sys
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if True:  # Catch-all for any subpass
    import base64
    g = {}
    exec(open("20.py").read(), g)
    image = g["loadReferenceImage"]()
    sys.set_int_max_str_digits(1000000)
    gridSize = [256, 128, 64, 32, 8][subPass]
    sampleSize = image.size[0] // gridSize
    data = 0
    for y in range(gridSize):
      for x in range(gridSize):
        px = x * sampleSize + sampleSize // 2
        py = y * sampleSize + sampleSize // 2
        if image.getpixel((px, py)) == 0:
          data |= (1 << (y * gridSize + x))

    codeBook = ["0" * 16, "f" * 16, "0" * 8, "f" * 8, "0000", "ffff", "00", "ff"]

    # So I actually tried getting AI engines to write this RLE encoder and
    # they all failed in various ways... like ChatGPT5.1pro's would work
    # unless it hit a run of 256 or more, then it'd corrupt. Some made
    # encodings that needed base64ing and utf-8 encoding and stuff and
    # that added way too many characters.

    def compressor(n: int) -> str:
      n = hex(n)[2:]
      o = ""

      def realIndex(big: str, small: str) -> int:
        try:
          return big.index(small)
        except ValueError:
          return len(big) + 1  # Not found = beyond end

      while n:
        for k, v in enumerate(codeBook):
          if n.startswith(v):
            o += str(k)
            n = n[len(v):]
            break
        else:
          nextRun = min(realIndex(n, "ffff"), realIndex(n, "0000"))

          bytesToWrite = max(1, min(len(n), nextRun, 8))
          o += hex(bytesToWrite + 7)[2:]
          o += n[:bytesToWrite]
          n = n[bytesToWrite:]

      return o

    def decompressor(n: str) -> str:
      r = ""
      while n:
        o = int(n[0], 16)
        if o < 8:
          r += codeBook[o]
          n = n[1:]
        else:
          bytesToRead = o - 7
          r += n[1:bytesToRead + 1]
          n = n[bytesToRead + 1:]

      return r

    compressed = compressor(data)
    decompressCheck = decompressor(compressed)

    #print("Data going in:")
    #print(hex(data))

    #print("\n\n Compressed:")
    #print(compressed)

    #print("\n\n Decompressed:")
    #print(decompressCheck)

    #print("\n\n\n\n")

    uncompressedSize = len(str(data))
    compressedSize = len(compressed)

    print(f"Uncompressed size: {uncompressedSize}")
    print(f"Compressed size: {compressedSize} + decompressorSize")

    if uncompressedSize < compressedSize + 300:
      return {
        "minifiedCode":
        dedent(f"""
def f(x,y):
  d = {data};i = int(x * {gridSize}) + int(y * {gridSize}) * {gridSize};return (d >> i) & 1
  """.strip()).strip()
      }, ""
    else:
      code = dedent(f"""
def l(n: str) -> str:
  r = ""
  while n:
    o = int(n[0], 16)
    if o < 8:
      r += ["0"*16,"f"*16,"0"*8,"f"*8,"0000","ffff","00","ff"][o]
      n = n[1:]
    else:
      b = o - 7
      r += n[1:b + 1]
      n = n[b + 1:]
  return r
d = int(l("{compressed}"),16)
def f(x,y):
  i = int(x * {gridSize}) + int(y * {gridSize}) * {gridSize}
  return (d >> i) & 1
  """.strip()).strip()
      #print(code)
      return {"minifiedCode": code}, ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  size = rng.randint(1, 4)
  code = f"def f(x,y):\n  return (x-{rng.random():.3f})**2 + (y-{rng.random():.3f})**2 - {rng.random():.3f}"
  return {"reasoningAndDiscussion": "Random guess", "minifiedCode": code}, "Random guess"
