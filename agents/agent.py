from mcutils import blocks
import time
from utils.console_args import CONSOLE_ARGS 
import time
from agents.mapArea import Plot
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

    def extractPave(self, maze, a, b, corner):
        cur = maze[b[0]][b[1]]
        moves = []
        while (cur.x != a[0] or cur.z != a[1]):
            moves.append(([cur.x + corner[0], self.world.heightmap[cur.x][cur.z], cur.z + corner[1]],cur.bridge))
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

    def findPaver(self, a,b, corner):
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
                            #Check if water or none, if it is, make the cost higher
                            if(self.world.blockMap[x][z] == b'minecraft:water' or self.world.blockMap[x][z] == None):
                                gNew = cur.gCost + 2
                                maze[x][z].bridge = True
                            else:
                                gNew = cur.gCost + 1
                                maze[x][z].bridge = False
                            
                            hNew = 0
                            #Calculate new fCost
                            fNew = gNew + hNew
                            #Reduce the cost if on a path
                            fNew -= self.world.pathMap[cur.x][cur.z] * 5
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
            return(self.extractPave(maze, a, b, corner))
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

        self.bridge = False

class Controller:
    def __init__(self, world, corner, pos, numAgents, swim = True):

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
                if(abs(a.height - b.height) <= CONSOLE_ARGS.heightDiff and len(a.cells) + len(b.cells) <= CONSOLE_ARGS.maxPlotSize):
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
                path = finder.findPath([ag.pos[0],ag.pos[2]], [cur.x + self.corner[0], cur.z + self.corner[1]], self.corner,swim=self.swim)
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
                            if(abs(self.world.heightmap[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]]-self.world.heightmap[x][z]) < 2 and not self.maze[x][z].closed and (b'water' not in self.world.blockMap[x][z] or self.swim)):
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
                                            #Add to plot if not on water
                                            if(hmDiff <= CONSOLE_ARGS.heightDiff and len(self.maze[xn][zn].plot.cells) > plotSize and len(self.maze[xn][zn].plot.cells) < CONSOLE_ARGS.maxPlotSize and b'water' not in self.world.blockMap[x][z]):
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
                            if(observedThisRound and b'water' not in self.world.blockMap[x][z]):
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

class Rect:

    def __init__(self, corner, dim):
        self.a = corner
        self.dim = dim
    
    def b(self):
        return [self.a[0] + self.dim[0] -1, self.a[1] + self.dim[1] -1]
    
    def area(self):
        return(self.dim[0] * self.dim[1])

    def pave(self, worldA, gHeight, block):
        for x in range (self.dim[0]):
            for z in range (self.dim[1]):
                blocks.SetBlock([self.a[0]+x+worldA[0], gHeight, self.a[1]+z+worldA[1]], block)

    def trim(self, rectB):
        if (self.b()[0] < rectB.a[0] or self.a[0] > rectB.b()[0] or self.b()[1] < rectB.a[1] or self.a[1] > rectB.b()[1]):
            return rectB, True

        #top left, top right, bot right, bot left
        cornerDiffs = [[],[],[],[]]

        cornerDiffs[0] = [self.a[0]-rectB.a[0],rectB.b()[1]-self.b()[1]]
        cornerDiffs[1] = [rectB.b()[0] - self.b()[0], rectB.b()[1]-self.b()[1]]
        cornerDiffs[2] = [rectB.b()[0] - self.b()[0], self.a[1]-rectB.a[1]]
        cornerDiffs[3] = [self.a[0]-rectB.a[0], self.a[1]-rectB.a[1]]

        outVerts = 0
        for i in range(4):
            if(cornerDiffs[i][0] > 0 or cornerDiffs[i][1] > 0):
                outVerts += 1
                cornerDiffs[i] = 1
            else:
                cornerDiffs[i] = 0

        if(outVerts == 0):
            return None, False
        if(outVerts == 4):
            return None, False
        if(outVerts == 3):
            #top, right, bot, left
            diffs = [max(0, rectB.b()[1] - self.b()[1]),max(0, rectB.b()[0] - self.b()[0]),max(0, self.a[1] - rectB.a[1]),max(0, self.a[0] - rectB.a[0])]

            index = -1
            diff = 9999
            for i in range(4):
                if(diffs[i] <= diff and diffs[i] != 0):
                    if(randint(0,1) == 0):
                        index = i
            #top
            if(index == 0):
                rectB.dim[1] -= diffs[0]
            #right
            elif(index == 1):
                rectB.dim[0] -= diffs[1]
            elif(index == 2):
                rectB.a[1] += diffs[2]
                rectB.dim[1] -= diffs[2]
            elif(index == 3):
                rectB.a[0] += diffs[3]
                rectB.dim[0] -= diffs[3]
            
        #Check if a corner is inside
        if(rectB.a[0] >= self.a[0] and rectB.a[1] >= self.a[1]):
            #Check if bot right is inside
            if(rectB.b()[0] <= self.b()[0] and rectB.a[1] <= self.b()[1]):
                #move it up
                dif = self.b()[1] - rectB.a[1] + 1
                rectB.a[1] += dif
                rectB.dim[1] -= dif
            else:
                #move it right
                dif = self.b()[0]-rectB.a[0] + 1
                rectB.a[0] += dif
                rectB.dim[0] -= dif
        
        #b corner is inside
        else:
            #Check if top left is inside
            if(rectB.a[0] >= self.a[0] and rectB.b()[1] >= self.a[1]):
                #move it down
                dif = rectB.b()[1] - self.a[1] + 1
                rectB.dim[1] -= dif
            else:
                #move it left
                dif = rectB.b()[0] - self.a[0] + 1
                rectB.dim[0] -= dif

        if(rectB.dim[0] < 3 and rectB.dim[1] < 3):
            return(None,False)

        return(rectB,False)

class Building:

    def __init__(self, a, b, layout, node):
        self.a = a
        self.b = b
        self.layout = layout
        self.node = node
class Builder:

    def __init__(self, world):
        self.world = world

    def clearArea(self, a,b, gHeight, ground):
        
        #ground = b'minecraft:stone'

        #First clear the plot and even out ground
        for x in range (a[0], b[0]):
            for z in range (a[1], b[1]):
                worldHeight =  self.world.heightmap[x][z] -1
            
                #Only flatten if it isn't water that we are flattening
                if(b'water' not in self.world.blockMap[x][z]):
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

    def genRect(self, a, b):
        #shrink by one each
        a = [a[0] + 1, a[1]+1]
        b = [b[0]-1, b[1]-1]
        #Set min size of area
        minEdge = max(min((b[0]-a[0])//2,(b[1]-a[1])//3),CONSOLE_ARGS.minBuildSize)
        
        #Define are to put rect in
        genEdges = [b[0]-(minEdge),b[1]-(minEdge)]

        corner = [randint(a[0],genEdges[0]),randint(a[1],genEdges[1])]
        dim = [randint(minEdge, b[0]-corner[0]), randint(minEdge, b[1]-corner[1])]

        return Rect(corner, dim)

    def getLayout(self, rectA, rectB, farm, a, b):
        layout = [[0 for z in range(b[1]-a[1])] for x in range(b[0]-a[0])]

        for x in range(rectA.dim[0]):
            for z in range(rectA.dim[1]):
                layout[(rectA.a[0]-a[0])+x][(rectA.a[1]-a[1])+z] = 1
        if(rectB and not farm):
            for x in range(rectB.dim[0]):
                for z in range(rectB.dim[1]):
                    layout[(rectB.a[0]-a[0])+x][(rectB.a[1]-a[1])+z] = 1

        neighbours = [[0,1],[1,0],[0,-1],[-1,0]]
        door = False
        node = []
        for x in range(len(layout)):
            for z in range(len(layout[0])):
                ns = 0
                lastN = []
                #If cell is in building
                if(layout[x][z] > 0):
                    #for each neighbour
                    for n in neighbours:
                        xn = x + n[0]
                        zn = z + n[1]
                        
                        #If within building area
                        if((xn >= 0 and xn < len(layout)) and (zn >= 0  and zn < len(layout[0]))):
                            #If also building, add neighbour
                            if(layout[xn][zn] > 0):
                                ns += 1
                            else:
                                lastN = [xn,zn]
                        else:
                            lastN = [xn,zn]
                #3 neighbours, wall
                if ns == 3:
                    if(randint(0,1) == 1):
                        #Make it a window
                        layout[x][z] = 4
                    else:
                        #Door
                        if(randint(0,15) == 1 and not door):
                            door = True
                            layout[x][z] = 5
                            node = lastN
                        else:
                            layout[x][z] = 2
                #2 neighbours, corner
                if ns == 2:
                    layout[x][z] = 3
        if not door:
            for x in range(len(layout)):
                for z in range(len(layout[0])):
                    if(layout[x][z] == 2 and not door):
                        for n in neighbours:
                            xn = x + n[0]
                            zn = z + n[1]
                            #If within building area
                            if(xn >= 0 and zn >= 0 and xn < len(layout) and zn < len(layout[0])):
                                #If not building, set it to be node
                                if(layout[xn][zn] == 0):
                                    node = [xn,zn]
                            else:
                                node = [xn,zn]
                        layout[x][z] = 5
                        door = True
                        break
        return layout, node

    def genShape(self,layout,floors, floorHeight,a,gHeight,palette):
        for floor in range(floors):
            for height in range(floorHeight+1):
                for x in range(len(layout)):
                    for z in range(len(layout[1])):
                        newfloor = (floor * floorHeight + height)%floorHeight == 0
                        if layout[x][z] == 1 and  newfloor:
                            blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.floor)
                        elif layout[x][z] == 2 or layout[x][z] == 4 or layout[x][z] == 5:
                            if(height == 1 and floor == 0):
                                if(layout[x][z] == 5):
                                    blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.door)
                                else:
                                    blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.foundation)

                            elif(newfloor):
                                blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.trim)
                            else:
                                if(layout[x][z] == 4):
                                    #window
                                    blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.window)
                                elif(height == 2 and floor == 0 and layout[x][z] == 5):
                                    #lay door
                                    blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.door + b'[half=upper]')
                                else:
                                    blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.wall)
                        
                        elif layout[x][z] == 3:
                            blocks.SetBlock([a[0]+x+self.world.a[0], gHeight + (floor*floorHeight) + height, a[1]+z+self.world.a[1]], palette.trim)
                        
                        if(layout[x][z] > 0):
                            self.world.heightmap[a[0] +x][a[1] + z] += 1

    def genRoof(self,rectA, rectB, farm, floors, floorHeight, a,gHeight,palette):
        roofHeight = gHeight + floors*floorHeight + 1
        
        #Longest in x
        if(rectA.dim[0] >= rectA.dim[1]):
            #Width in Z
            width = rectA.dim[1]//2
            for x in range(rectA.a[0]-1,rectA.b()[0]+2):
                for z in range(rectA.a[1]-1, rectA.b()[1]+2):
                    if(z < rectA.a[1] + width):
                        newHeight = (z-rectA.a[1])
                    else:
                        newHeight = abs((z-rectA.b()[1])) if z < rectA.b()[1] else rectA.b()[1]-z
                    blocks.SetBlock([x+self.world.a[0], roofHeight + newHeight, z+self.world.a[1]], palette.roof)
                    if(x == rectA.a[0] or x == rectA.b()[0]):
                        #At the end of the gable, fill with wall
                        if(newHeight > 0):
                            for height in range(roofHeight, roofHeight + newHeight):
                                blocks.SetBlock([x+self.world.a[0], height, z+self.world.a[1]], palette.wall)

        else:
            #Width in Z
            width = rectA.dim[0]//2
            for x in range(rectA.a[0]-1,rectA.b()[0]+2):
                for z in range(rectA.a[1]-1, rectA.b()[1]+2):
                    if(x < rectA.a[0] + width):
                        newHeight = (x-rectA.a[0])
                    else:
                        newHeight = abs((x-rectA.b()[0]))  if x < rectA.b()[0] else rectA.b()[0]-x
                    blocks.SetBlock([x+self.world.a[0], roofHeight + newHeight, z+self.world.a[1]], palette.roof)
                    if(z == rectA.a[1] or z == rectA.b()[1]):
                        #At the end of the gable, fill with wall
                        if(newHeight > 0):
                            for height in range(roofHeight, roofHeight + newHeight):
                                blocks.SetBlock([x+self.world.a[0], height, z+self.world.a[1]], palette.wall)


    def build(self,a,b, palette, plot = None):
        if plot: 
            gHeight = plot.height -1
        else:
            gHeight = self.world.heightmap[a[0]][a[1]] -1

        
        self.clearArea(a,b,gHeight,palette.ground)

        rectA = self.genRect(a,b)
        rectB = self.genRect(a,b)

        #Make sure rect A is bigger
        if(rectB.area() > rectA.area()):
            temp = rectA
            rectA = rectB
            rectB = temp
        
        #Find out if 3 vertices are outside rectA
        #If 4, two seperate buildings
        rectB,farm = rectA.trim(rectB)


        #build the house here
        layout, node = self.getLayout(rectA,rectB, farm, a, b)

        floors = randint(1,CONSOLE_ARGS.maxFloors)
        floorHeight = randint(3,CONSOLE_ARGS.moxFloorHeight)

        self.genShape(layout,floors,floorHeight,a,gHeight,palette)

        #Do the rooftops
        if(b'air' not in palette.roof):
            self.genRoof(rectA, rectB, farm, floors, floorHeight, a,gHeight,palette)
            if(rectB and not farm):
                self.genRoof(rectB, rectA, farm, floors, floorHeight, a,gHeight,palette)

        #Build farm
        if(farm):
            rectB.pave(self.world.a, gHeight, b'minecraft:farmland')
            #Create a farm
            for x in range (rectB.dim[0]):
                for z in range (rectB.dim[1]):
                    #Place water every five
                    if(x % 5 == 1 and z % 5 == 1):
                        blocks.SetBlock([rectB.a[0]+x+self.world.a[0], gHeight, rectB.a[1]+z+self.world.a[1]], b'minecraft:water')
                    else:
                        blocks.SetBlock([rectB.a[0]+x+self.world.a[0], gHeight, rectB.a[1]+z+self.world.a[1]], b'minecraft:farmland')
                        blocks.SetBlock([rectB.a[0]+x+self.world.a[0], gHeight+1, rectB.a[1]+z+self.world.a[1]], b'minecraft:wheat')
                    self.world.heightmap[rectB.a[0]+x][rectB.a[1]+z] += 5


        return(Building(a,b, layout, node))

        #Build the first main rect
        #Build second rectangle if it is there

        #Pave the two areas
        