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

        self.x = x
        self.z = z

        self.parent = []

class Controller:
    def __init__(self, hm, corner, pos, numAgents):

        self.heightmap = hm
        self.corner = corner

        self.maze = [[Cell(x, z) for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]
        
        self.pos = [ai - ci for ai, ci in zip(pos, corner)]

        self.agents = [Agent([pos[0],self.heightmap[self.pos[0]][self.pos[1]], pos[1]], b'minecraft:obsidian') for i in range(numAgents)]


    def explore(self):

        neighbours = [[0,1],[1,1],[1, 0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]

        #Create a maze to hold the data

        #Set first cell to open
        self.maze[self.pos[0]][self.pos[1]].open = True

        #Keep track of frontier cells
        openList =[self.maze[self.pos[0]][self.pos[1]]]

        for i in range(8):
            x = self.pos[0] + neighbours[i][0]
            z = self.pos[1] + neighbours[i][1]
            if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                self.maze[x][z].open = True
                self.maze[x][z].gCost = 1
                self.maze[x][z].hCost = 2
                self.maze[x][z].fCost = -1
                openList.append(self.maze[x][z])

        finder = PathFinder(self.heightmap)
        count = 0
        while len(openList) > 0:
            count += 1
            time.sleep(0.5)
            print(count)
            #Simulate agents
            for ag in self.agents:
                #Agent not currently on a path, observe surroundings
                if(not ag.path):
                    for i in range(8):
                        x = ag.pos[0] - self.corner[0] + neighbours[i][0]
                        z = ag.pos[2] - self.corner[1] + neighbours[i][1]

                        #Check surrounding is on board
                        if((x >= 0 and x < len(self.maze)) and (z >= 0 and z < len(self.maze[0]))):
                            #TODO GET BLOCK DATA OF SURROUNDINGS

                            #Now make the surroundings forntier cells if they are accessible and have unobserved neighbours
                            if(abs(self.heightmap[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]]-self.heightmap[x][z]) < 2 and not self.maze[x][z].closed):
                                #Check neighbouring cells for unexplored areas
                                add = False
                                hCost = 0; #Amount of information gained
                                for i in range(8):
                                    xn = x + neighbours[i][0]
                                    zn = z + neighbours[i][1]
                                    if((xn >= 0 and xn < len(self.maze)) and (zn >= 0 and zn < len(self.maze[0]))):
                                        if(not self.maze[xn][zn].closed and not self.maze[xn][zn].open):
                                            add = True;
                                            hCost += 1;
                                #Area unexplored, add to list
                                if(add):
                                    self.maze[x][z].open = True
                                    self.maze[x][z].gCost = self.maze[ag.pos[0] - self.corner[0]][ag.pos[2] - self.corner[1]].gCost + 1
                                    self.maze[x][z].hCost = hCost
                                    self.maze[x][z].fCost = self.maze[x][z].gCost - hCost
                                    openList.append(self.maze[x][z])
                else:
                    ag.tick()

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

            agent = self.agents[0]
            dist = 999999999999
            path = []
            for ag in self.agents:
                #Find the closest available agent
                if(not ag.path):
                    p = finder.findPath([ag.pos[0],ag.pos[2]], [cur.x + self.corner[0], cur.z + self.corner[1]], self.corner)
                    if(len(path) < dist):
                        agent = ag
                        dist = len(path)
                        path = p
            agent.path = path


            
                





