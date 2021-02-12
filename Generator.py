from agents import agent
from mcutils import mapTools
import time

a,b = mapTools.OrderCoords([-55,90],[45, 190])
heightmap = mapTools.GetHeightmap(a, b)

ag = agent.Agent([6,71,146], b'minecraft:obsidian')
pf = agent.PathFinder(heightmap)

path = pf.findPath([6,146],[5,150], a)

ag.path = path

for i in range(10):
    ag.tick()

ag.kill()

print("done")