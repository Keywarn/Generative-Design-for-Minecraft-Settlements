from agents import agent
from mcutils import mapTools
import time

a,b = mapTools.OrderCoords([-55,90],[45, 190])
heightmap = mapTools.GetHeightmap(a, b)


con = agent.Controller(heightmap, a, [6,146], 4)

tic = time.perf_counter()
blockMap = con.explore()
timeObs = time.perf_counter() - tic

print(f"Time taken: {timeObs}")

observed = 0
for row in blockMap:
    for cell in row:
        if (cell != [0,0,0,255]):
            observed += 1
print(f"Cells observed: {observed}")
print(f"Cells per second: {observed/timeObs}")

mapTools.showMap(heightmap, a, b,'Surface Heightmap')
mapTools.showMap(blockMap, a, b,'Surface Blocks')


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

print("done")