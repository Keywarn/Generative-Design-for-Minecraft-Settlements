from agents import agent
from mcutils import mapTools
import time

a,b = mapTools.OrderCoords([-55,90],[45, 190])
heightmap = mapTools.GetHeightmap(a, b)


con = agent.Controller(heightmap, a, [6,146], 1)

mapTools.showHeightmap(heightmap, a, b)


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