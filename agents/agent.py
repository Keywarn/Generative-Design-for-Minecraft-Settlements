from mcutils import blocks
import time
from utils.console_args import CONSOLE_ARGS 
import time
from agents.mapArea import Plot

class Agent:
    def __init__(self, pos, block):

        self.pos = pos
        self.block = block

        self.prevBlock = blocks.GetBlock(self.pos)
        self.move(pos)

        self.path = None

        self.plot = None

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
    def __init__(self, hm):
        self.heightmap = hm
    
    def distance(self,a,b):
        #return max(abs(a[0] - b[0]),abs(a[1] - b[1]))
        return((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def extractPath(self, maze, a, b, corner):
        cur = maze[b[0]][b[1]]
        moves = []
        while (cur.x != a[0] or cur.z != a[1]):
            moves.append([cur.x + corner[0], self.heightmap[cur.x][cur.z], cur.z + corner[1]])
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

        maze = [[Cell(x, z) for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]
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
                        #TODO Checks for water and falling
                        if(abs(self.heightmap[cur.x][cur.z]-self.heightmap[x][z]) < 2 and not maze[x][z].closed):
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


    def explore(self):
        
        neighbours = [[1,1],[1,-1],[-1,-1],[-1,1],[0,1],[1, 0],[0,-1],[-1,0]]
        finder = PathFinder(self.world.heightmap)

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
        for step in range(500):
        #while len(openList) > 0 or workingAgents:
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
                        x = ag.pos[0] - self.corner[0] + neighbours[i][0]
                        z = ag.pos[2] - self.corner[1] + neighbours[i][1]

                        #Check surrounding is on board
                        if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                            #The fCost modifier for the cells nearby
                            #Block not currently set so observe it
                            if(not self.world.blockMap[x][z]):
                                self.world.blockMap[x][z] = blocks.GetBlock([x + self.corner[0],self.world.heightmap[x][z] - 1, z + self.corner[1]])

                                #Add the agent to a plot if it was suitable
                                if(ag.plot):
                                    hmDiff = abs(self.world.heightmap[x][z] - ag.plot.height)
                                    if(hmDiff <= 1 or b'log' in self.world.blockMap[x][z]):
                                        ag.plot.cells.append([x,z])
                                        self.maze[x][z].plot = ag.plot

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
                                        #Cell couldn't be added to current plot, add it to plot of neighbouring cell if possible
                                        #TODO check for merging of plots here
                                        if(self.maze[xn][zn].plot and not self.maze[x][z].plot):
                                            hmDiff = abs(self.world.heightmap[xn][zn] - self.maze[xn][zn].plot.height)
                                            if(hmDiff <= 1):
                                                ag.plot = self.maze[xn][zn].plot
                                                ag.plot.cells.append([x,z])
                                                self.maze[x][z].plot = ag.plot

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
                            
                            #Surroundings yielded no suitable plot so need to create a new plot
                            #TODO check nearby agents
                            if(not self.maze[x][z].plot):
                                for nearAgent in freeAgents + workingAgents:
                                    if(finder.distance([ag.pos[0],ag.pos[2]],[nearAgent.pos[0],nearAgent.pos[2]]) <= 100):
                                        if(nearAgent.plot):
                                            hmDiff = abs(self.world.heightmap[x][z] - nearAgent.plot.height)
                                            if(hmDiff <= 1):
                                                ag.plot = nearAgent.plot
                                                ag.plot.cells.append([x,z])
                                                self.maze[x][z].plot = ag.plot
                                                break
                            #Weren't able to assign a nearby plot, create one
                            if(not self.maze[x][z].plot):
                                ag.plot = Plot(ag.pos[1])
                                self.world.plots.append(ag.plot)
                                ag.plot.cells.append([x,z])
                                self.maze[x][z].plot = ag.plot

                    observeTime += time.perf_counter() - ticObserve
        if(CONSOLE_ARGS.timing):
            print(f"Time spent pathfinding: {pathingTime}")
            print(f"Time spent on agent ticks: {tickTime}")
            print(f"Time spent observing: {observeTime}")
            
                





