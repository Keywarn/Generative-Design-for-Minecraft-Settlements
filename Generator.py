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

    con = agent.Controller(world, a, [6,146], 4)
    tic = time.perf_counter()
    con.explore()
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

print("Converting Colour Map".center(30, '-'))
colourMap = mapTools.convertBlockMap(world.blockMap)
print("Converting Plot Map".center(30, '-'))
plotMap = mapTools.convertPlotMap(world.plots, world.size)


if(CONSOLE_ARGS.output):
    print("Saving World".center(30, '-'))
    with open("world.map","wb+") as worldFile:
        pickle.dump(world, worldFile)

mapTools.showMap(world.heightmap, a, b,'Surface Heightmap')
mapTools.showMap(colourMap, a, b,'Surface Blocks')
mapTools.showMap(world.visitMap, a, b,'Agent cell visit heatmap')
mapTools.showMap(plotMap, a, b,'Building Plot Map')

print("Finishing".center(30, '-'))