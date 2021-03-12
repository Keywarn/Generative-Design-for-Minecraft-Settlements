class MapArea:

    def __init__(self,a,b):
        self.a = a
        self.b = b
        self.size = (b[0]-a[0] +1,b[1]-a[1] +1)
        self.heightmap = [[-1 for z in range(self.size[1])] for x in range(self.size[0])]
        self.blockMap = [[None for z in range(self.size[1])] for x in range(self.size[0])]
        self.visitMap = [[0 for z in range(self.size[1])] for x in range(self.size[0])]

        self.trees = []

    def addTree(self, pos, type):
        self.trees.append(Tree(pos,type))

    def outputTrees(self):
        print("Trees".center(30, '-'))
        for tree in self.trees:
            print(f"{tree.type} at {tree.pos}")
        print("".center(30, '-'))

class Tree:

    def __init__(self, pos, type):
        self.pos = pos
        self.type = type