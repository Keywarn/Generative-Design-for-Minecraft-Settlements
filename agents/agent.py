from mcutils import blocks
import time
from utils.console_args import CONSOLE_ARGS 
import time
from agents.mapArea import Plot
from collections import defaultdict
from random import randint

class Agent:
    def __init__(self, pos, block):

        self.pos = pos
        self.block = block

        self.prevBlock = blocks.GetBlock(self.pos)
        self.move(pos)

        self.path = None

    def move(self, newPos):
        #Prevent collisions of agents (only if running in visual mode)
        if(not CONSOLE_ARGS.agentVis or blocks.GetBlock(newPos) != self.block):
            if(CONSOLE_ARGS.agentVis):
                blocks.SetBlock(self.pos, self.prevBlock)

            self.pos = newPos
            if(CONSOLE_ARGS.agentVis):
                self.prevBlock = blocks.GetBlock(self.pos)
            if(CONSOLE_ARGS.agentVis):
                blocks.SetBlock(self.pos, self.block)

    def __del__(self):
        if(CONSOLE_ARGS.agentVis):
            blocks.SetBlock(self.pos, self.prevBlock)

    def tick(self):
        if(self.path):
            #do the next sequence on the path
            self.move(self.path.pop(0))

class PathFinder:
    def __init__(self, world):
        self.world = world
    
    def distance(self,a,b):
        #return max(abs(a[0] - b[0]),abs(a[1] - b[1]))
        return((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def extractPath(self, maze, a, b, corner):
        cur = maze[b[0]][b[1]]
        moves = []
        while (cur.x != a[0] or cur.z != a[1]):
            moves.append([cur.x + corner[0], self.world.heightmap[cur.x][cur.z], cur.z + corner[1]])
            cur = cur.parent
        
        return moves[::-1]
    
    def getLowestFCost(self, openList):
        cur = openList[0]
        #Get cell with lowest f cost
        index = 0;
        for i in range(len(openList)):
            if(openList[i].fCost < cur.fCost):
                cur = openList[i]
                index = i
        return cur
    
    def findPath(self, a,b, corner,swim=False, fall=False):
        a = [ai - ci for ai, ci in zip(a, corner)]
        b = [bi - ci for bi, ci in zip(b, corner)]
        neighbours = [[0,1],[1,1],[1, 0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]

        maze = [[Cell(x, z) for z in range(len(self.world.heightmap[0]))] for x in range(len(self.world.heightmap))]
        maze[a[0]][a[1]].open = True
        openList =[maze[a[0]][a[1]]]

        foundPath = False

        while len(openList) > 0:
            cur = self.getLowestFCost(openList)
            
            openList.remove(cur)
            cur.open = False
            cur.closed = True

            #Check current isn't the final cell
            if(cur.x == b[0] and cur.z == b[1]):
                foundPath = True
                break
            else:
                #For each neighbour
                for i in range(8):
                    x = cur.x + neighbours[i][0]
                    z = cur.z + neighbours[i][1]

                    #Check neighbour is on board
                    if((x >= 0 and x < len(maze)) and (z >= 0 and z < len(maze[0]))):
                        #Check if can travel to the block

                        if(abs(self.world.heightmap[cur.x][cur.z]-self.world.heightmap[x][z]) < 2 and not maze[x][z].closed):
                            #Check if it isn't water or if we can swim
                            if((self.world.blockMap[cur.x][cur.z] != b'minecraft:water' or swim)):
                                #Calculate new fCost
                                gNew = cur.gCost + 1
                                hNew = self.distance([x,z],b)
                                fNew = gNew + hNew
                                if(not maze[x][z].open or fNew < maze[x][z].fCost):
                                    #update
                                    maze[x][z].fCost = fNew
                                    maze[x][z].gCost = gNew
                                    maze[x][z].hCost = hNew
                                    maze[x][z].parent = cur
                                    #add to open list if needed
                                    if(not maze[x][z].open):
                                        maze[x][z].open = True
                                        openList.append(maze[x][z])
        
        if(foundPath):
            return(self.extractPath(maze, a, b, corner))
        else:
            return None
class Cell:
    def __init__(self, x, z):
        #Distance from a
        self.gCost = 0
        #Distance to b
        self.hCost = 0
        #Combined
        self.fCost = 99999999

        self.open = False
        self.closed = False
        self.toBeObserved = False

        self.x = x
        self.z = z

        self.plot = None

        self.parent = []

class Controller:
    def __init__(self, world, corner, pos, numAgents, swim = False):

        self.world = world
        self.corner = corner

        self.maze = [[Cell(x, z) for z in range(len(self.world.heightmap[0]))] for x in range(len(self.world.heightmap))]
        
        self.pos = [ai - ci for ai, ci in zip(pos, corner)]

        self.agents = [Agent([pos[0],self.world.heightmap[self.pos[0]][self.pos[1]+i], pos[1] + i], b'minecraft:obsidian') for i in range(numAgents)]

        self.swim = swim

    def mergePlots(self, a,b):
        for cell in a.cells:
            if self.maze[cell[0]][cell[1]].plot != a: print("YAR THERE BE A TRAITOR BEFORE WE EVEN START")
            
        for cell in b.cells:
            #Change cells in maze to store correct plot
            self.maze[cell[0]][cell[1]].plot = a
            #Add cells in plot b to plot a
            a.cells.append(cell)

        #Remove plot b from world
        self.world.plots.remove(b)

    def handleAdjPlots(self, adjPlots):
        #Expects a sorter list adjPlots
        #Merge adjoining plots
        numPlots = len(adjPlots)
        i = 0
        while i < numPlots-1:
            a = adjPlots[i]
            j = i + 1
            while j < numPlots:
                b = adjPlots[j]
                if(a.height == b.height):
                    if(len(a.cells) >= len(b.cells)):
                        self.mergePlots(a,b)
                        adjPlots.remove(b)
                        j -= 1
                    numPlots -= 1
                j += 1
            i += 1

    def explore(self):
        
        neighbours = [[1,1],[1,-1],[-1,-1],[-1,1],[0,1],[1, 0],[0,-1],[-1,0]]
        finder = PathFinder(self.world)

        #Create a maze to hold the data

        #Keep track of frontier cells
        openList =[]

        #Add starting neighbours to be explored
        for i in range(4):
            x = self.pos[0] + neighbours[i][0]
            z = self.pos[1] + neighbours[i][1]
            if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                self.maze[x][z].open = True
                self.maze[x][z].fCost = finder.distance([x,z], self.pos)
                openList.append(self.maze[x][z])

        freeAgents = []

        for agent in self.agents:
            freeAgents.append(agent)
        workingAgents = []

        pathingTime = 0
        tickTime = 0
        observeTime = 0
        iters = 0
        while (len(openList) > 0 or workingAgents) and iters != CONSOLE_ARGS.steps:
            iters += 1
            #FREE AGENTS - ASSIGN THEM
            while (len(freeAgents) > 0 and len(openList) > 0):
                cur = finder.getLowestFCost(openList)
                ag = freeAgents[0]

                ticPathing = time.perf_counter()
                path = finder.findPath([ag.pos[0],ag.pos[2]], [cur.x + self.corner[0], cur.z + self.corner[1]], self.corner)
                pathingTime += time.perf_counter() - ticPathing

                if(path):
                    #Found a path so remove from open and assign agent
                    openList.remove(cur)
                    cur.open = False
                    cur.closed = True
                    
                    ag.path = path
                    
                    freeAgents.remove(ag)
                    workingAgents.append(ag)
            #SIMULATING THE AGENTS
            for ag in workingAgents:
                ticTick = time.perf_counter()
                ag.tick()
                self.world.visitMap[ag.pos[0]-self.corner[0]][ag.pos[2]-self.corner[1]] += 1
                tickTime += time.perf_counter() - ticTick
                #Agent arrived, observe surroundings and open frontiers
                if(not ag.path):
                    ticObserve = time.perf_counter()
                    workingAgents.remove(ag)
                    freeAgents.append(ag)

                    fModifier = 0

                    for i in range(8):
                        plotAdd = None
                        plotSize = 0
                        adjPlots = []
                        
                        observedThisRound = False
                        x = ag.pos[0] - self.corner[0] + neighbours[i][0]
                        z = ag.pos[2] - self.corner[1] + neighbours[i][1]

                        #Check surrounding is on board
                        if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                            #The fCost modifier for the cells nearby
                            #Block not currently set so observe it
                            if(not self.world.blockMap[x][z]):
                                observedThisRound = True
                                self.world.blockMap[x][z] = blocks.GetBlock([x + self.corner[0],self.world.heightmap[x][z] - 1, z + self.corner[1]])
                                if(b'water' in self.world.blockMap[x][z]): fModifier -= 1
                                if(b'log' in self.world.blockMap[x][z]):
                                    self.world.addTree([x,z], self.world.blockMap[x][z])
                                    fModifier -= 2
                            #Now make the surroundings frontier cells if they are accessible and have unobserved neighbours
                            #Check if it can even travel to newly explored cell before considering it
                            if(abs(self.world.heightmap[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]]-self.world.heightmap[x][z]) < 2 and not self.maze[x][z].closed and (self.world.blockMap[x][z] != b'minecraft:water' or self.swim)):
                                #Check neighbouring cells for unexplored areas
                                add = False
                                for j in range(8):
                                    xn = x + neighbours[j][0]
                                    zn = z + neighbours[j][1]
                                    if((xn >= 0 and xn < len(self.maze)) and (zn >= 0 and zn < len(self.maze[0]))):
                                        #Check surrounding cells for plots
                                        if(self.maze[xn][zn].plot and observedThisRound):
                                            if(self.maze[xn][zn].plot not in adjPlots): adjPlots.append(self.maze[xn][zn].plot)
                                            
                                            hmDiff = abs(self.world.heightmap[x][z] - self.maze[xn][zn].plot.height)
                                            if(hmDiff <= 1 and len(self.maze[xn][zn].plot.cells) > plotSize):
                                                plotSize = len(self.maze[xn][zn].plot.cells)
                                                plotAdd = self.maze[xn][zn].plot

                                        if(not self.maze[xn][zn].open and not self.maze[xn][zn].closed and not self.maze[xn][zn].toBeObserved):
                                            add = True;
                                            self.maze[xn][zn].toBeObserved = True
                                #Area unexplored, add to list
                                if(add):
                                    fNew = self.maze[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]].fCost + 1 + fModifier
                                    

                                    if(not self.maze[x][z].open or fNew < self.maze[x][z].fCost):
                                        self.maze[x][z].fCost = fNew
                                        if(not self.maze[x][z].open):
                                            openList.append(self.maze[x][z])
                                            self.maze[x][z].open = True
                            
                            
                            #Weren't able to assign a nearby plot, create one or just add to the one we found earlier
                            if(observedThisRound):
                                if(not plotAdd):
                                    plotAdd = Plot(ag.pos[1])
                                    self.world.plots.append(plotAdd)
                                    adjPlots.append(plotAdd)
                                
                                plotAdd.cells.append([x,z])
                                self.maze[x][z].plot = plotAdd

                            if(len(adjPlots) > 1):
                                adjPlots.sort(key=lambda x: len(x.cells), reverse=True)
                                self.handleAdjPlots(adjPlots)

                    observeTime += time.perf_counter() - ticObserve
        if(CONSOLE_ARGS.timing):
            print(f"Time spent pathfinding: {pathingTime}")
            print(f"Time spent on agent ticks: {tickTime}")
            print(f"Time spent observing: {observeTime}")

class Builder:

    def __init__(self, world):
        self.world = world

    def clearArea(self, a,b, gHeight, ground):
        
        #ground = b'minecraft:stone'

        #First clear the plot and even out ground
        for x in range (a[0], b[0]):
            for z in range (a[1], b[1]):
                worldHeight =  self.world.heightmap[x][z] -1
            
                #needs raising
                if(worldHeight < gHeight):
                    for height in range(worldHeight, gHeight):
                        blocks.SetBlock([x+self.world.a[0], height, z+self.world.a[1]], ground)

                #Needs lowering
                else:
                    for height in range (worldHeight, gHeight, -1):
                        blocks.SetBlock([x+self.world.a[0], height, z+self.world.a[1]], b'minecraft:air')
                        self.world.heightmap[x][z] -= 1

                #Ensure ground is correct
                blocks.SetBlock([x+self.world.a[0], gHeight, z+self.world.a[1]], ground)
                self.world.heightmap[x][z] = gHeight + 1
                    
                self.world.blockMap[x][z] = ground

    def getGround(self, a,b, plot):

        blocks = defaultdict(int)

        for x in range (a[0], b[0]):
            for z in range (a[1], b[1]):
                blocks[self.world.blockMap[x][z]] += 1

        return blocks


    def house(self,a,b, plot = None):
        if plot: 
            gHeight = plot.height -1
        else:
            gHeight = self.world.heightmap[a[0]][a[1]] -1

        #Get the blocks on the ground
        ground = self.getGround(a,b,plot)

        #Use the most common one to resurface
        groundBlock = max(ground, key = ground.get)
        
        self.clearArea(a,b,gHeight,groundBlock)

        #Set min size of area
        minEdge = 4
        
        #Define are to put rect in
        genEdges = [b[0]-minEdge,b[1]-minEdge]

        if(genEdges[0] < a[0] or genEdges[1] < a[1]):
            return
        
        houseCorner = [randint(a[0],genEdges[0]),randint(a[1],genEdges[1])]

        dim = [randint(4, b[0]-houseCorner[0]), randint(4, b[1]-houseCorner[1])]

        for x in range (dim[0]):
            for z in range (dim[1]):
                blocks.SetBlock([houseCorner[0]+x+self.world.a[0], gHeight, houseCorner[1]+z+self.world.a[1]], b'minecraft:stone')