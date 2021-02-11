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
    
    def findPath(a,b,swim=False, fall=False):
        print("Finding path")




