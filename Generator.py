from agents import agent

ag = agent.Agent([6,71,146], b'minecraft:obsidian')

for i in range(10):
    ag.move([6,71, 146+i])

ag.kill()

print("done")