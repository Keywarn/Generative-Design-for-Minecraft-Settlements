from random import randint
from collections import defaultdict

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

    def readyPlots(self):
        for plot in self.plots:
            if(len(plot.cells) > 25):
                plot.getGround(self.blockMap)
                plot.ground = max(plot.blocks, key=plot.blocks.get)

                trees = {k: plot.blocks[k] for k in plot.blocks if (b'log' in k)}
                if(trees):
                    plot.woodType = max(trees, key=trees.get)
                    plot.woodness = trees[plot.woodType]
                plot.palette = Palette(plot)

                plot.getVisits(self.visitMap)

                #Change size in here for building area size
                plot.score = plot.visits + len(plot.cells) + plot.blocks[b'minecraft:water'] * 5 + plot.blocks[plot.woodType] * 3

                # print("NEW SCORE: ", plot.score)
                # print("Visits: ", plot.visits)
                # print("Size: ", len(plot.cells))
                # print("Water score: ", plot.blocks[b'minecraft:water'] * 5)
                # print("Wood score", plot.blocks[plot.woodType] * 3)

        #calculate largest building area and mark

        #add palette to plot

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
        self.score = 0

        self.buildAreaSize = None
        self.blocks = defaultdict(int)
        self.visits = 0
        self.buildAreaa = [[],[]]
        
        self.palette = None
        self.woodType = None
        self.woodness = None
        self.ground = None
    
    def getGround(self, blockMap):
        for cell in self.cells:
            if(blockMap[cell[0]][cell[1]]):
                self.blocks[blockMap[cell[0]][cell[1]]] += 1

    def getVisits(self, visitMap):
        for cell in self.cells:
            if(visitMap[cell[0]][cell[1]]):
                self.visits += visitMap[cell[0]][cell[1]]
                


class Palette:


    def __init__(self, plot = None):
        if plot:
            #Plot is sand based
            if(b'sand' in plot.ground):
                self.foundation = plot.ground+ b'stone'
                self.floor      = b'minecraft:stone'
                self.wall       = plot.ground.replace(b'minecraft:', b'minecraft:cut') + b'stone'
                self.roof       = b'minecraft:air'
                self.trim       = plot.ground.replace(b'minecraft:', b'minecraft:chiseled_') + b'stone'
                self.window     = b'minecraft:glass'
                self.door       = b'minecraft:air'
                self.ground     = plot.ground
                if(plot.woodType):
                    self.floor  = plot.woodType.replace(b'log', b'planks')
                    if(plot.woodness) > 3:
                        self.trim = plot.woodType
                        self.door = plot.woodType.replace(b'log', b'door')
            if(b'stone' in plot.ground):
                self.foundation = b'minecraft:stone'
                self.floor      = b'minecraft:stone'
                self.wall       = b'minecraft:stone_bricks'
                self.roof       = b'minecraft:cobblestone'
                self.trim       = b'minecrfat:chiseled_stone_bricks'
                self.window     = b'minecraft:glass'
                self.door       = b'minecraft:air'
                self.ground     = plot.ground
                if(plot.woodType):
                    self.floor  = plot.woodType.replace(b'log', b'planks')
                    self.door = plot.woodType.replace(b'log', b'door')
                    if(plot.woodness) > 3:
                        self.trim = plot.woodType
                    if(plot.woodness > 5):
                        self.wall = plot.woodType.replace(b'log', b'planks')
            else:
                self.foundation = b'minecraft:cobblestone'
                self.floor      = b'minecraft:stone'
                self.wall       = b'minecraft:stone'
                self.roof       = b'minecraft:cobblestone'
                self.trim       = b'minecrfat:cobblestone'
                self.window     = b'minecraft:glass'
                self.door       = b'minecraft:air'
                self.ground     = plot.ground
                if(plot.woodType):
                    self.floor  = plot.woodType.replace(b'log', b'planks')
                    self.door = plot.woodType.replace(b'log', b'door')
                    if(plot.woodness) > 3:
                        self.trim = plot.woodType
                    if(plot.woodness > 5):
                        self.wall = plot.woodType.replace(b'log', b'planks')


        else:
            self.foundation = b'minecraft:stone'
            self.floor      = b'minecraft:oak_planks'
            self.wall       = b'minecraft:oak_planks'
            self.roof       = b'minecraft:cobblestone'
            self.trim       = b'minecraft:oak_log'
            self.window     = b'minecraft:glass'
            self.door       = b'minecraft:oak_door'
            self.ground     = b'minecraft:grass_block'
