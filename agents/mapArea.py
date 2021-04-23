from random import randint
class MapArea:

    def __init__(self,a,b):
        self.a = a
        self.b = b
        self.size = (b[0]-a[0] +1,b[1]-a[1] +1)
        self.heightmap = [[-1 for z in range(self.size[1])] for x in range(self.size[0])]
        self.blockMap = [[None for z in range(self.size[1])] for x in range(self.size[0])]
        self.visitMap = [[0 for z in range(self.size[1])] for x in range(self.size[0])]

        self.trees = []
        self.plots = []

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

class Plot:
    wools = [b'minecraft:white_wool',b'minecraft:orange_wool',b'minecraft:magenta_wool',
            b'minecraft:light_blue_wool',b'minecraft:yellow_wool',b'minecraft:lime_wool',
            b'minecraft:pink_wool',b'minecraft:gray_wool']
    index = 0
    def __init__(self, height):
        self.height = height
        self.cells = []
        self.colour = Plot.wools[Plot.index]
        Plot.index = (Plot.index + 1) % 8

class Palette:


    def __init__(self, plot = None):
        self.foundation = b'minecraft:stone'
        self.floor      = b'minecraft:oak_planks'
        self.wall       = b'minecraft:oak_planks'
        self.roof       = b'minecraft:cobblestone'
        self.trim       = b'minecraft:oak_log'
        self.window     = b'minecraft:glass'
        self.door       = b'minecraft:oak_door'
        self.ground     = b'minecraft:grass_block'
