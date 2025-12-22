import random, os, math
import VolumeComparison as vc

title = "Can you navigate a maze from photos only?"

maze = """
################################
#A.#...   #############     ####
##...#..  ############# ###   ##
###  ##.                 #### ##
#     #. ##### ########    ## ##
# ### #...############### ### ##
# ### ## .#  ############ ### ##
# #######....#  ######### ###  #
# ##### ### ... ######### #### #
# ##### ### ##.  ######## #### #
# ##### ######.  ############# #
# ##### ######....############ #
#       #######  .#### ## # ####
###############  .#    #    ####
##               ...# ##       #
##                 .           #
## ############### .############
##  ############## .############
##    #######B.### .########## #
####  ########.### .########## #
####  ####### .###..########## #
####### ######.####.########## #
# ######### ##.####.           #
# ######### ##.####.###### #####
# ############.####.###### #####
# ############.####.###### #####
#             .####.###### #####
#### #########.####.###### #####
#### #########.####.###### #####
#### #########.####.######   ###
#### #########......###### #####
################################
""".strip()


def renderMazeAsPng():
  scad = ""
  import PIL.Image as Image
  for row, line in enumerate(maze.split("\n")):
    for col, char in enumerate(line):
      if char == "#":
        if (row + col) % 2 == 0:
          scad += f"translate([{col:.6f},{row:.6f},0]) color([0.8,0.8,0.8]) cube([1,1,1], center=true); \n"
        else:
          scad += f"translate([{col:.6f},{row:.6f},0]) color([0.5,0.5,0.5]) cube([1,1,1], center=true); \n"

      if char == "A":
        scad += f"translate([{col:.6f},{row:.6f},0]) color([1,0,0]) sphere(r=0.5, $fn=50); \n"

      if char == "B":
        scad += f"translate([{col:.6f},{row:.6f},0]) color([0,0,1]) sphere(r=0.5, $fn=50); \n"

  scad += "color([0,1,0]) translate([-2,16,0]) linear_extrude(0.01) text(\"E\", size=2, valign=\"center\", halign=\"center\"); \n"
  scad += "color([0,1,0]) translate([34,16,0]) linear_extrude(0.01) text(\"W\", size=2, valign=\"center\", halign=\"center\"); \n"
  scad += "color([0,1,0]) translate([16,-2,0]) linear_extrude(0.01) text(\"N\", size=2, valign=\"center\", halign=\"center\"); \n"
  scad += "color([0,1,0]) translate([16,34,0]) linear_extrude(0.01) text(\"S\", size=2, valign=\"center\", halign=\"center\"); \n"

  for i in range(20):
    while True:
      cameraPos = [int(random.random() * 32), int(random.random() * 32), 10]
      cameraLookat = [int(random.random() * 32), int(random.random() * 32), 0]

      while math.sqrt((cameraPos[0] - cameraLookat[0])**2 +
                      (cameraPos[1] - cameraLookat[1])**2) < 5:
        cameraLookat = [int(random.random() * 32), int(random.random() * 32), 0]

      cameraArg = \
          f"--camera={cameraPos[0]:.6f},{cameraPos[1]:.6f},{cameraPos[2]:.6f}," + \
          f"{cameraLookat[0]:.6f},{cameraLookat[1]:.6f},{cameraLookat[2]:.6f}"
      vc.render_scadText_to_png(scad,
                                f"results/42_maze_{i}.png",
                                cameraArg=cameraArg,
                                extraScadArgs=["--projection=p"])

      im = Image.open(f"results/42_maze_{i}.png")
      colours = im.getcolors()

      blueColours = 0
      redColours = 0
      greenColours = 0

      for count, (r, g, b) in colours:
        if r > g and r > b: redColours += count
        if b > g and b > r: blueColours += count
        if g > r and g > b: greenColours += count

      interestingCount = int(redColours > 0) + int(blueColours > 0) + int(greenColours > 0)

      if interestingCount == 3 and not os.path.exists("images/42.png"):
        # Pick an image with lots of info to summerise the test.
        os.rename(f"results/42_maze_{i}.png", "images/42.png")
        continue

      if interestingCount != 1:
        print(f"Redoing {i} as it contains too much or not enough info")
        continue

      break


if not os.path.exists("results/42_maze_0.png"):
  renderMazeAsPng()

prompt = """
You have to navigate a maze from the red sphere to the blue sphere. You are not given the maze, but you
are given the following aerial photographs of the maze, which gives enough information to navigate the
maze. 

Return the path from the red sphere to the blue sphere using the following notation:

w - take a step west
n - take a step north
e - take a step east
s - take a step south

So "ennne" means: go east, then turn north, north again, north for a 3rd step, then turn east.

If you are unable to solve the full maze, a partial solution is appreachiated.

Be sure to not prefix your answer with anything other than the path, 
as any character other than e, n, s, or w will be graded as incorrect.
"""

structure = None
earlyFail = True


def prepareSubpassPrompt(index: int) -> str:
  images = list(range(20))

  images = images[0:20 - index * 4]

  if index == 3: raise StopIteration

  return prompt + "".join([f"[[image:results/42_maze_{i}.png]]" for i in images])


gradedMaze = [None] * 3


def gradeAnswer(answer: str, subPass: int, aiEngineName: str) -> dict:
  global gradedMaze
  m = maze.replace(".", " ").split("\n")

  # x,y are set to the start (A) of the maze
  y = 0
  x = 0

  for r, row in enumerate(m):
    for c, char in enumerate(row):
      if char == "A":
        y = r
        x = c

  path = answer

  gradedMaze[subPass] = "\n".join(m)

  while len(path):
    step = path[0].lower()
    path = path[1:]

    currentChar = m[y][x]

    if currentChar == "#":
      m[y] = m[y][:x] + "X" + m[y][x + 1:]
      gradedMaze[subPass] = "\n".join(m)
      return 0, "You cannot move into a wall (marked with an X)"

    if currentChar == ".":
      m[y] = m[y][:x] + "!" + m[y][x + 1:]
      gradedMaze[subPass] = "\n".join(m)
      return 0, "Path forms a loop. (Marked with a !)"

    if currentChar == "B":
      return 1, "Correct"

    m[y] = m[y][:x] + "." + m[y][x + 1:]
    gradedMaze[subPass] = "\n".join(m)

    if step == "e": x += 1
    elif step == "w": x -= 1
    elif step == "n": y -= 1
    elif step == "s": y += 1
    else:
      return 0, "Path contains invalid step: " + step

  return (len(answer) / maze.count(".") /
          2), "Path does not reach the blue sphere, path length was " + str(len(answer))


def resultToNiceReport(answer, subPass, aiEngineName):
  return "<pre>" + gradedMaze[subPass] + "</pre>"


highLevelSummary = """
Can you navigate a maze from photos only?<br>

The AI is given between 20 (easy) and 8 (hard) photos of the maze, and must navigate from 
the red sphere to the blue sphere.<br>

Each photo contains ONE of (start, end, cardinal direction markers) so the solution 
requires one of two approaches:<ul>
<li>Stitch together the entire maze using feature recognition, and then solve it.
This is how I'd expect an AI to solve the problem.
</li>
<li>Navigate relative to features, not an absolute orientation. So for each image you
have one or more sequences of 'turn left, turn right, right again, walk 10, turn left, walk 2,' 
instructions as you solve the local problem, connecting features of local image together and 
then recognise the patterns in the turns allowing the images to be paths to be stitched together.
This is probably how you'd solve the problem if you were a human.
</li>
</ul>

<div style="max-width:650px">

<img src="42_maze_0.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_1.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_2.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_3.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_4.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_5.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_6.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_7.png" width="200px"  style="float:left; padding:4px">
<img src="42_maze_8.png" width="200px"  style="float:left; padding:4px">

</div>
"""

subpassParamSummary = [
  "Can you navigate with 20 photos? (Each photo shows either the start or the end)",
  "Can you navigate with 16 photos?", "Can you navigate with 12 photos?",
  "Can you navigate with 8 photos?"
]
promptChangeSummary = "Decreasing the number of photos"
