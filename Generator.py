from agents import agent,mapArea
from mcutils import mapTools
from utils.console_args import CONSOLE_ARGS 
import time, pickle

a,b = mapTools.OrderCoords([-55,90],[45, 190])

world = mapArea.MapArea(a,b)

print("Getting Heightmap".center(30, '-'))
if(CONSOLE_ARGS.hmFile):
    print(f"Reading from file {CONSOLE_ARGS.hmFile}")
    with open(CONSOLE_ARGS.hmFile, 'rb') as hmFile:
        world.heightmap = pickle.load(hmFile)
else:
    world.heightmap = mapTools.GetHeightmap(a, b)


print("Getting Block Data".center(30, '-'))

if(CONSOLE_ARGS.bmFile):
    print(f"Reading from file {CONSOLE_ARGS.bmFile}")
    with open(CONSOLE_ARGS.bmFile, 'rb') as bmFile:
        world.blockMap = pickle.load(bmFile)
else:
    con = agent.Controller(world.heightmap, a, [6,146], 4)
    tic = time.perf_counter()
    world.blockMap = con.explore()
    timeObs = time.perf_counter() - tic

    if(CONSOLE_ARGS.timing):
        print(f"Total time taken: {timeObs}")

    observed = 0
    for row in world.blockMap:
        for cell in row:
            if (cell != None):
                observed += 1
    if(CONSOLE_ARGS.timing):
        print(f"Cells observed: {observed}")
        print(f"Cells per second: {observed/timeObs}")

colourMap = mapTools.convertBlockMap(world.blockMap)

if(CONSOLE_ARGS.output):
    print("Outputting to files".center(30, '-'))
    print("Output heightmap")
    with open("height.map","wb+") as hmFile:
        pickle.dump(world.heightmap, hmFile)
    print("Output blockMap")
    with open("block.map",'wb+') as bmFile:
        pickle.dump(world.blockMap, bmFile)


mapTools.showMap(world.heightmap, a, b,'Surface Heightmap')
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