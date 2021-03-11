from agents import agent,mapArea
from mcutils import mapTools
from utils.console_args import CONSOLE_ARGS 
import time, pickle

a,b = mapTools.OrderCoords([-55,90],[45, 190])


if(CONSOLE_ARGS.worldFile):
    print("Loading World".center(30, '-'))
    with open(CONSOLE_ARGS.worldFile, 'rb') as worldFile:
        world = pickle.load(worldFile)
else:
    world = mapArea.MapArea(a,b)

    print("Getting Heightmap".center(30, '-'))
    world.heightmap = mapTools.GetHeightmap(a, b)


    print("Getting Block Data".center(30, '-'))

    con = agent.Controller(world.heightmap, a, [6,146], 4)
    tic = time.perf_counter()
    world.blockMap = con.explore()
    timeObs = time.perf_counter() - tic

    if(CONSOLE_ARGS.timing):
        observed = 0
        for row in world.blockMap:
            for cell in row:
                if (cell != None):
                    observed += 1
        print(f"Cells observed: {observed}")
        print(f"Cells per second: {observed/timeObs}")
        print(f"Total time taken: {timeObs}")

colourMap = mapTools.convertBlockMap(world.blockMap)

if(CONSOLE_ARGS.output):
    print("Saving World".center(30, '-'))
    with open("world.map","wb+") as worldFile:
        pickle.dump(world, worldFile)

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