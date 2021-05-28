from agents import agent,mapArea
from mcutils import mapTools,blocks
from utils.console_args import CONSOLE_ARGS 
import time, pickle

area = mapTools.GetBuildArea()
if area:
    a = [area['xFrom'],area['zFrom']]
    b = [area['xTo'],area['zTo']]

    if(b[0]-a[0] > 100):
        mid = (b[0] + a[0]) //2
        a[0] = mid-50
        b[0] = mid+50
    
    if(b[1]-a[1] > 100):
        mid = (b[1] + a[1]) //2
        a[1] = mid-50
        b[1] = mid+50
    a,b = mapTools.OrderCoords(a,b)
else:
    print("No Build Area, using console args")
    a,b = mapTools.OrderCoords([CONSOLE_ARGS.ax,CONSOLE_ARGS.az],[CONSOLE_ARGS.ax + CONSOLE_ARGS.dx, CONSOLE_ARGS.az + CONSOLE_ARGS.dz])
#a,b = mapTools.OrderCoords([-55,90],[45, 190])


if(CONSOLE_ARGS.worldFile):
    print("Loading World".center(30, '-'))
    with open(CONSOLE_ARGS.worldFile, 'rb') as worldFile:
        world = pickle.load(worldFile)
else:
    world = mapArea.MapArea(a,b)

    print("Getting Heightmap".center(30, '-'))
    world.heightmap = mapTools.GetHeightmap(a, b)


    print("Getting Block Data".center(30, '-'))

    con = agent.Controller(world, a, [(a[0]+b[0])//2,(a[1]+b[1])//2], 4)
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
        print(f"Total time to explore taken: {timeObs}")

print("Building".center(30, '-'))
tic = time.perf_counter()
builder = agent.Builder(world)
world.readyPlots()
world.plots.sort(key=lambda x: x.score, reverse=True)

for plot in world.plots:
    if(plot.score > 0):
        for area in plot.buildArea:
            world.addBuilding(builder.build(area[0],area[1], plot.palette,plot))
        # for area in plot.buildArea:
        #     for x in range(area[0][0],area[1][0]):
        #         for z in range(area[0][1],area[1][1]):
        #             blocks.SetBlock([x+world.a[0], world.heightmap[x][z], z+world.a[1]], b'minecraft:gold_block')

if(CONSOLE_ARGS.timing):
    print(f"Time to build: {time.perf_counter() - tic}")


if(CONSOLE_ARGS.paint):
    print("Painting World".center(30, '-'))
    input("IS WORLD BACKED UP? Enter to continue (ctrl-c to exit): ")
    mapTools.paintPlots(world)

if(CONSOLE_ARGS.output):
    print("Saving World".center(30, '-'))
    with open("world.map","wb+") as worldFile:
        pickle.dump(world, worldFile)
    print("Saved".center(30, '-'))

if(not CONSOLE_ARGS.noGraph):
    print("Converting Colour Map".center(30, '-'))
    colourMap = mapTools.convertBlockMap(world.blockMap)
    print("Converting Plot Map".center(30, '-'))
    plotMap = mapTools.convertPlotMap(world.plots, world.size)

    print("Displaying".center(30, '-'))

    mapTools.showMap(world.heightmap, a, b,'Surface Heightmap')
    mapTools.showMap(colourMap, a, b,'Surface Blocks')
    mapTools.showMap(world.visitMap, a, b,'Agent cell visit heatmap')
    mapTools.showMap(plotMap, a, b,'Building Plot Map')
    mapTools.showMap(world.pathMap, a, b,'Path Map')

    print("Finishing".center(30, '-'))