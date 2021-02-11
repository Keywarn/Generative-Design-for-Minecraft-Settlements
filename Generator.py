from agents import agent
from mcutils import mapTools

a,b = (-55,90),(45, 190)
heightmap = mapTools.GetHeightmap(a, b)

ag = agent.Agent([6,71,146], b'minecraft:obsidian')

for i in range(10):
    ag.move([6,71, 146+i])

ag.kill()

print("done")