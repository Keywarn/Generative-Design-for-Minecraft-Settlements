from random import randint
from collections import defaultdict
import utils.matrixSize
from utils.console_args import CONSOLE_ARGS 
from agents import agent
from mcutils import blocks

class MapArea:

    def __init__(self,a,b):
        self.a = a
        self.b = b
        self.size = (b[0]-a[0] +1,b[1]-a[1] +1)
        self.heightmap = [[-1 for z in range(self.size[1])] for x in range(self.size[0])]
        self.blockMap = [[None for z in range(self.size[1])] for x in range(self.size[0])]
        self.visitMap = [[0 for z in range(self.size[1])] for x in range(self.size[0])]
        self.pathMap = [[0 for z in range(self.size[1])] for x in range(self.size[0])]

        self.trees = []
        self.plots = []
        self.buildings = []
        

    def addTree(self, pos, type):
        self.trees.append(Tree(pos,type))

    def outputTrees(self):
        print("Trees".center(30, '-'))
        for tree in self.trees:
            print(f"{tree.type} at {tree.pos}")
        print("".center(30, '-'))

    def readyPlots(self):
        for plot in self.plots:
            if(len(plot.cells) > CONSOLE_ARGS.minBuildSize * CONSOLE_ARGS.minBuildSize):
                plot.getGround(self.blockMap)
                plot.ground = max(plot.blocks, key=plot.blocks.get)

                trees = {k: plot.blocks[k] for k in plot.blocks if (b'log' in k)}
                if(trees):
                    plot.woodType = max(trees, key=trees.get)
                    plot.woodness = trees[plot.woodType]
                plot.palette = Palette(plot)

                plot.getVisits(self.visitMap)

                plot.getBuildArea()

                if(plot.buildArea):

                    size = len(plot.cells)
                    #Change size in here for building area size
                    plot.score = plot.visits + size + plot.blocks[b'minecraft:water'] * 5 + plot.blocks[plot.woodType] * 3

                    # print("NEW SCORE: ", plot.score)
                    # print("Visits: ", plot.visits)
                    # print("Size: ", len(plot.cells))
                    # print("Water score: ", plot.blocks[b'minecraft:water'] * 5)
                    # print("Wood score", plot.blocks[plot.woodType] * 3)

        #calculate largest building area and mark

        #add palette to plot

    def addBuilding(self, new):
        #Find closest building
        paver = agent.PathFinder(self)
        closestBuild = None
        path = None
        dist = 9999
        for building in self.buildings:
            print(building.node)
            buildingNode = [building.node[0] + building.a[0], building.node[1] + building.a[1]]
            print(new.node)
            newNode = [new.node[0] + new.a[0], new.node[1] + new.a[1]]
            print(buildingNode)
            print(newNode)
            pave = paver.findPaver(newNode, buildingNode, self.a)
            if(pave):
                if len(pave) <= dist:
                    path = pave
                    closestBuild = building
        
        if(path):
            self.pave(path)

        self.buildings.append(new)
    
    def pave(self, path):
        for loc,bridge in path:
            self.pathMap[loc[0]-self.a[0]][loc[1]-self.a[1]] += 1
            #Bridges are one above the heightmap
            if(bridge):
                blocks.SetBlock([loc[0], self.heightmap, loc[1]], b'minecraft:gold_block')
            else:
                blocks.SetBlock([loc[0], self.heightmap-1, loc[1]], b'minecraft:iron_block')





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

        self.buildArea = []
    
    def getGround(self, blockMap):
        for cell in self.cells:
            if(blockMap[cell[0]][cell[1]]):
                self.blocks[blockMap[cell[0]][cell[1]]] += 1

    def getVisits(self, visitMap):
        for cell in self.cells:
            if(visitMap[cell[0]][cell[1]]):
                self.visits += visitMap[cell[0]][cell[1]]
    
    def getBuildArea(self):
        minCell = self.cells[0]
        maxCell = self.cells[1]

        for cell in self.cells:
            minCell[0] = min(minCell[0], cell[0])
            minCell[1] = min(minCell[1], cell[1])

            maxCell[0] = max(maxCell[0], cell[0])
            maxCell[1] = max(maxCell[1], cell[1])
        
        cellMap = [[0 for z in range((maxCell[1]-minCell[1]) + 1)] for x in range((maxCell[0]-minCell[0]) + 1)]
        for cell in self.cells:
            cellMap[cell[0]-minCell[0]][cell[1]-minCell[1]] = 1
        
        valid = True
        while valid:
            

            size, coords = utils.matrixSize.max_size(cellMap, 1)
            if(size[0] > CONSOLE_ARGS.minBuildSize + 2 and size[1] > CONSOLE_ARGS.minBuildSize + 2):
                self.buildArea.append([[minCell[0] + coords[1],minCell[1] + coords[0]],[minCell[0] + coords[1] + size[0]-1, minCell[1] + coords[0] + size[1] -1]])
                #Check these, size may need to be inverted
                for x in range (coords[1], coords[1]+size[0]):
                    for z in range(coords[0], coords[0] + size[1]):
                        cellMap[x][z] = 0
            else:
                valid = False


                


class Palette:


    def __init__(self, plot = None):
        if plot:
            #Plot is sand based
            if(b'sand' in plot.ground):
                self.foundation = plot.ground+ b'stone'
                self.floor      = b'minecraft:stone'
                self.wall       = plot.ground.replace(b'minecraft:', b'minecraft:cut_') + b'stone'
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
            elif(b'stone' in plot.ground):
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
                self.trim       = b'minecraft:cobblestone'
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
