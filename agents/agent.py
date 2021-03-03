from mcutils import blocks
import time

class Agent:
    def __init__(self, pos, block):

        self.pos = pos
        self.block = block

        self.prevBlock = blocks.GetBlock(self.pos)
        self.move(pos)

        self.target = None
        self.path = None

    def move(self, newPos):
        #Prevent collisions of agents
        if(blocks.GetBlock(newPos) != self.block):
            blocks.SetBlock(self.pos, self.prevBlock)

            self.pos = newPos

            self.prevBlock = blocks.GetBlock(self.pos)

            blocks.SetBlock(self.pos, self.block)

    def __del__(self):
        blocks.SetBlock(self.pos, self.prevBlock)

    def setTarget(self, targetPos):
        self.target = targetPos

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
    
    def findPath(self, a,b, corner,swim=False, fall=False):
        a = [ai - ci for ai, ci in zip(a, corner)]
        b = [bi - ci for bi, ci in zip(b, corner)]
        neighbours = [[0,1],[1,1],[1, 0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]

        maze = [[Cell(x, z) for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]
        maze[a[0]][a[1]].open = True
        openList =[maze[a[0]][a[1]]]

        foundPath = False

        while len(openList) > 0:
            cur = openList[0]
            #Get cell with lowest f cost
            index = 0;
            for i in range(len(openList)):
                if(openList[i].fCost < cur.fCost):
                    cur = openList[i]
                    index = i
            
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

        self.parent = []

class Controller:
    def __init__(self, hm, corner, pos, numAgents):

        self.heightmap = hm
        self.corner = corner

        self.maze = [[Cell(x, z) for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]
        
        self.pos = [ai - ci for ai, ci in zip(pos, corner)]

        self.agents = [Agent([pos[0],self.heightmap[self.pos[0]][self.pos[1]+i], pos[1] + i], b'minecraft:obsidian') for i in range(numAgents)]


    def explore(self):
        
        neighbours = [[1,1],[1,-1],[-1,-1],[-1,1],[0,1],[1, 0],[0,-1],[-1,0]]
        finder = PathFinder(self.heightmap)

        blockMap = [[[0,0,0,255] for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]

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

        for step in range(500):
        #while len(openList) > 0 or workingAgents:
            while (len(freeAgents) > 0 and len(openList) > 0):
                cur = openList[0]

                #Get cell with lowest f cost
                for i in range(len(openList)):
                    if(openList[i].fCost < cur.fCost):
                        cur = openList[i]

                #Get the closest agent to the cell
                ag = freeAgents[0]
                dist = 999999999999
                path = []
                for agent in freeAgents:
                    #Find the closest available agent
                    p = finder.findPath([agent.pos[0],agent.pos[2]], [cur.x + self.corner[0], cur.z + self.corner[1]], self.corner)
                    if(len(path) < dist and p):
                        ag = agent
                        dist = len(path)
                        path = p
                
                #path = finder.findPath([ag.pos[0],ag.pos[2]], [cur.x + self.corner[0], cur.z + self.corner[1]], self.corner)

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
                ag.tick()
                #Agent arrived, observe surroundings and open frontiers
                if(not ag.path):
                    workingAgents.remove(ag)
                    freeAgents.append(ag)

                    for i in range(8):
                        x = ag.pos[0] - self.corner[0] + neighbours[i][0]
                        z = ag.pos[2] - self.corner[1] + neighbours[i][1]

                        #Check surrounding is on board
                        if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                            #TODO OBSERVE
                            blockMap[x][z] = [94,157,52,255]
                            #Now make the surroundings frontier cells if they are accessible and have unobserved neighbours
                            #TODO Water check here
                            #Check if it can even travel to newly explored cell before considering it
                            if(abs(self.heightmap[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]]-self.heightmap[x][z]) < 2 and not self.maze[x][z].closed):
                                #Check neighbouring cells for unexplored areas
                                add = False
                                for j in range(8):
                                    xn = x + neighbours[j][0]
                                    zn = z + neighbours[j][1]
                                    if((xn >= 0 and xn < len(self.maze)) and (zn >= 0 and zn < len(self.maze[0]))):
                                        if(not self.maze[xn][zn].open and not self.maze[xn][zn].closed and not self.maze[xn][zn].toBeObserved):
                                            add = True;
                                            self.maze[xn][zn].toBeObserved = True
                                #Area unexplored, add to list
                                if(add):
                                    fNew = self.maze[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]].fCost + 1
                                    if(not self.maze[x][z].open or fNew < self.maze[x][z].fCost):
                                        self.maze[x][z].fCost = fNew
                                        if(not self.maze[x][z].open):
                                            openList.append(self.maze[x][z])
                                            self.maze[x][z].open = True

        return(blockMap)
            
                





