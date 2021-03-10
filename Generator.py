from agents import agent
from mcutils import mapTools
from utils.console_args import CONSOLE_ARGS 
import time
import csv
import pickle

a,b = mapTools.OrderCoords([-55,90],[45, 190])

print("Getting Heightmap".center(30, '-'))
if(CONSOLE_ARGS.hmFile):
    print(f"Reading from file {CONSOLE_ARGS.hmFile}")
    with open(CONSOLE_ARGS.hmFile, 'rb') as hmFile:
        heightmap = pickle.load(hmFile)
else:
    heightmap = mapTools.GetHeightmap(a, b)


print("Getting Block Data".center(30, '-'))

if(CONSOLE_ARGS.bmFile):
    print(f"Reading from file {CONSOLE_ARGS.bmFile}")
    with open(CONSOLE_ARGS.bmFile, 'rb') as bmFile:
        blockMap = pickle.load(bmFile)
else:
    con = agent.Controller(heightmap, a, [6,146], 4)
    tic = time.perf_counter()
    blockMap = con.explore()
    timeObs = time.perf_counter() - tic

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

colourMap = mapTools.convertBlockMap(blockMap)

if(CONSOLE_ARGS.output):
    print("Outputting to files".center(30, '-'))
    print("Output heightmap")
    with open("height.map","wb+") as hmFile:
        pickle.dump(heightmap, hmFile)
    print("Output blockMap")
    with open("block.map",'wb+') as bmFile:
        pickle.dump(blockMap, bmFile)


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