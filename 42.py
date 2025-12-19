import random, os, math
import VolumeComparison as vc

maze = """
################################
#A.#...   ######################
##...#..  ######################
###  ##.                 #######
#######. ##### ########    #####
##### #...############### ######
##### ## .#  ###################
#########....#  ################
########### ... ################
########### ##.  ###############
##############.  ###############
##############....##############
###############  .#### ## # ####
###############  .#    #    ####
##               ...# ##       #
##                 .           #
## ############### .############
##  ############## .############
##    #######B.### .############
####  ########.### .############
####  ####### .###..############
####### ######.####.############
########### ##.####.############
########### ##.####.############
##############.####.############
##############.####.############
##############.####.############
##############.####.############
##############.####.############
##############.####.############
##############......############
################################
""".strip()


def renderMazeAsPng():
    scad = ""
    for row, line in enumerate(maze.split("\n")):
        for col, char in enumerate(line):
            if char == "#":
                scad += f"translate([{col:.6f},{row:.6f},0]) cube([1,1,1], center=true); \n"

            if char == "A":
                scad += f"translate([{col:.6f},{row:.6f},0]) color([1,0,0]) sphere(r=0.5); \n"

            if char == "B":
                scad += f"translate([{col:.6f},{row:.6f},0]) color([0,0,1]) sphere(r=0.5); \n"

    scad += "translate([-2,16,0]) linear_extrude(0.01) text(\"E\", size=2, valign=\"center\", halign=\"center\"); \n"
    scad += "translate([34,16,0]) linear_extrude(0.01) text(\"W\", size=2, valign=\"center\", halign=\"center\"); \n"
    scad += "translate([16,-2,0]) linear_extrude(0.01) text(\"N\", size=2, valign=\"center\", halign=\"center\"); \n"
    scad += "translate([16,34,0]) linear_extrude(0.01) text(\"S\", size=2, valign=\"center\", halign=\"center\"); \n"

    for i in range(50):
        cameraPos = [int(random.random() * 32), int(random.random() * 32), 10]
        cameraLookat = [
            int(random.random() * 32),
            int(random.random() * 32), 0
        ]

        while math.sqrt((cameraPos[0] - cameraLookat[0])**2 +
                        (cameraPos[1] - cameraLookat[1])**2) < 5:
            cameraLookat = [
                int(random.random() * 32),
                int(random.random() * 32), 0
            ]

        cameraArg = \
            f"--camera={cameraPos[0]:.6f},{cameraPos[1]:.6f},{cameraPos[2]:.6f}," + \
            f"{cameraLookat[0]:.6f},{cameraLookat[1]:.6f},{cameraLookat[2]:.6f}"
        vc.render_scadText_to_png(scad,
                                  f"results/42_maze_{i}.png",
                                  cameraArg=cameraArg,
                                  extraScadArgs=["--projection=p"])


if not os.path.exists("results/42_maze_0.png"):
    renderMazeAsPng()

prompt = """
You have to navigate a maze from the red sphere to the blue sphere. You are not give the maze, but you
are given the following aerial photographs of the maze, which may give enough information to navigate the
maze.

Return the path from the red sphere to the blue sphere using the following notation:

w - take a step west
n - take a step north
e - take a step east
s - take a step south

So "ennne" means: go east, then turn north, north again, north for a 3rd step, then turn east.

"""


def prepareSubpassPrompt(index: int) -> str:
    images = list(range(50))

    images = images[0:50 - index * 10]

    return prompt + "\n\n" + "A maze with a red sphere at A and a blue sphere at B" + "\n\n" + "Here are some other images of the maze: " + ", ".join(
        [f"results/42_maze_{i}.png" for i in images])
