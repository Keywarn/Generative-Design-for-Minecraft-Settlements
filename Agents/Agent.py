from mcutils import blocks

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

    def kill(self):
        blocks.SetBlock(self.pos, self.prevBlock)

    def setTarget(self, targetPos):
        self.target = targetPos

    def tick(self):
        if(path):
            #do the next sequence on the path
            print("moving")
        else:
            #Get a path
            print("PathFinding")

class PathFinder:
    def __init__(self, hm):
        self.heightmap = hm
    
    def distance(self,a,b):
        #return max(abs(a[0] - b[0]),abs(a[1] - b[1]))
        return round(((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5)*10

    def extractPath(self, maze, a, b):
        cur = maze[b[0]][b[1]]
        print(a)
        print(b)
        moves = []
        while (cur.x != a[0] or cur.z != a[1]):
            moves.append([cur.x - cur.parent.x, cur.z - cur.parent.z])
            cur = cur.parent
        moves.reverse()
        return moves
    
    def findPath(self, a,b, corner,swim=False, fall=False):
        a = [ai - ci for ai, ci in zip(a, corner)]
        b = [bi - ci for bi, ci in zip(b, corner)]
        neighbours = [[0,1],[1,1],[1, 0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]

        maze = [[Cell(x, z) for z in range(len(self.heightmap[0]))] for x in range(len(self.heightmap))]
        maze[a[0]][a[1]].open = True
        openList =[maze[a[0]][a[1]]]

        foundPath = False

        while len(openList) != 0:
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
                        if(abs(self.heightmap[cur.x][cur.z]-self.heightmap[x][z]) < 2):

                            #Calculate new fCost
                            if(i % 2 ==0 ):
                                #Straight move
                                gNew = cur.gCost + 10
                            else:
                                gNew = cur.gCost + 14
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
            return(self.extractPath(maze, a, b))
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



