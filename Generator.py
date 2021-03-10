from agents import agent
from mcutils import mapTools
from utils.console_args import CONSOLE_ARGS 
import time
import csv

a,b = mapTools.OrderCoords([-55,90],[45, 190])

print("Getting Heightmap".center(30, '-'))
if(CONSOLE_ARGS.hmFile):
    print(f"Reading from file {CONSOLE_ARGS.hmFile}")
    #TODO read in from file
else:
    heightmap = mapTools.GetHeightmap(a, b)


print("Getting Block Data".center(30, '-'))

if(CONSOLE_ARGS.bmFile):
    print(f"Reading from file {CONSOLE_ARGS.bmFile}")
    #TODO read in from file
else:
    con = agent.Controller(heightmap, a, [6,146], 4)
    tic = time.perf_counter()
    blockMap = con.explore()
    timeObs = time.perf_counter() - tic
    colourMap = mapTools.convertBlockMap(blockMap)

    if(CONSOLE_ARGS.timing):
        print(f"Total time taken: {timeObs}")

    observed = 0
    for row in blockMap:
        for cell in row:
            if (cell != None):
                observed += 1
    if(CONSOLE_ARGS.timing):
        print(f"Cells observed: {observed}")
        print(f"Cells per second: {observed/timeObs}")

if(CONSOLE_ARGS.output):
    print("Outputting to files".center(30, '-'))
    print("Output heightmap")
    with open("height.map","w+") as hmFile:
        csvWriter = csv.writer(hmFile,delimiter=',')
        csvWriter.writerows(heightmap)
    print("Output blockMap")
    with open("block.map","w+") as bmFile:
        csvWriter = csv.writer(bmFile,delimiter=',')
        csvWriter.writerows(blockMap)


mapTools.showMap(heightmap, a, b,'Surface Heightmap')
mapTools.showMap(colourMap, a, b,'Surface Blocks')


# Agent pathfinding example
# ag = agent.Agent([6,71,146], b'minecraft:obsidian')
# pf = agent.PathFinder(heightmap)

# path = pf.findPath([6,146],[7,153], a)

# ag.path = path
# time.sleep(3)
# for i in range(len(path)):
#     ag.tick()
#     time.sleep(1)
# time.sleep(3)

print("Finishing".center(30, '-'))