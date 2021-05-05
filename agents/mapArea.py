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
        self.upgradePathMap = [[0 for z in range(self.size[1])] for x in range(self.size[0])]

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

        for building in self.buildings:
            buildingNode = [building.node[0] + building.a[0], building.node[1] + building.a[1]]
            newNode = [new.node[0] + new.a[0], new.node[1] + new.a[1]]

            pave = paver.findPaver(newNode, buildingNode, self.a)
            if(pave):
                self.pave(pave)

        self.buildings.append(new)
    
    def pave(self, path):
        for i in range(len(path)-1):
            loc = path[i][0]
            bridge = path[i][1]

            self.pathMap[loc[0]-self.a[0]][loc[2]-self.a[1]] += 1
            height = self.heightmap[loc[0]-self.a[0]][loc[2]-self.a[1]]
            #Bridges are one above the heightmap
            if(bridge):
                blocks.SetBlock([loc[0], height, loc[2]], b'minecraft:oak_planks')
                if(i < len(path)-1):
                    #Pave sides of path tooa
                    nextLoc = path[i+1][0]
                    diff = [nextLoc[0] - loc[0],nextLoc[2]-loc[2]]
                        #Path goes up/down, pave left/right
                    if(abs(diff[0]) > 0):
                        #left
                        try:
                            blocks.SetBlock([loc[0]-1, height, loc[2]], b'minecraft:oak_planks')
                        except:
                            continue
                        #right
                        try:
                            blocks.SetBlock([loc[0]+1, height, loc[2]], b'minecraft:oak_planks')
                        except:
                            continue

                    #Path goes left/right, pave up/down
                    if(abs(diff[1]) > 0):
                        #below
                        try:
                            blocks.SetBlock([loc[0], height, loc[2]-1], b'minecraft:oak_planks')
                        except:
                            continue
                        #right
                        try:
                            blocks.SetBlock([loc[0], height, loc[2]+1], b'minecraft:oak_planks')
                        except:
                            continue
            else:
                #Randomly upgrade the path 1/3 of the time, if not already upgraded
                self.upgrade(loc, height)
                if(i < len(path)-1):
                    #Pave sides of path tooa
                    nextLoc = path[i+1][0]
                    diff = [nextLoc[0] - loc[0],nextLoc[2]-loc[2]]
                    #Path goes up/down, pave left/right
                    if(abs(diff[0]) > 0):
                        #left
                        try:
                            if(abs(height-self.heightmap[loc[0]-self.a[0]-1][loc[2]-self.a[1]]) <= 1):
                                self.upgrade([loc[0]-1,loc[1],loc[2]], height)
                        except:
                            continue
                        #right
                        try:
                            if(abs(height-self.heightmap[loc[0]-self.a[0]+1][loc[2]-self.a[1]]) <= 1):
                                self.upgrade([loc[0]+1,loc[1],loc[2]], height)
                        except:
                            continue

                    #Path goes left/right, pave up/down
                    if(abs(diff[1]) > 0):
                        #below
                        try:
                            if(abs(height-self.heightmap[loc[0]-self.a[0]][loc[2]-self.a[1]-1]) <= 1):
                                self.upgrade([loc[0],loc[1],loc[2]-1], height)
                        except:
                            continue
                        #above
                        try:    
                            if(abs(height-self.heightmap[loc[0]-self.a[0]][loc[2]-self.a[1]+1]) <= 1):
                                self.upgrade([loc[0],loc[1],loc[2]+1], height)
                        except:
                            continue
    
    def upgrade(self, loc, height):
        if(randint(0,CONSOLE_ARGS.paveFreq-1) == 0):
            self.upgradePathMap[loc[0]-self.a[0]][loc[2]-self.a[1]] += 1
            #Make it gravel path
            if(self.upgradePathMap[loc[0]-self.a[0]][loc[2]-self.a[1]] < CONSOLE_ARGS.paveFreq):
                blocks.SetBlock([loc[0], height-1, loc[2]], b'minecraft:gravel')
            #Make it dirt path
            elif(self.upgradePathMap[loc[0]-self.a[0]][loc[2]-self.a[1]] < 2*CONSOLE_ARGS.paveFreq):
                blocks.SetBlock([loc[0], height-1, loc[2]], b'minecraft:grass_path')
            #Make it stone bricks
            elif(self.upgradePathMap[loc[0]-self.a[0]][loc[2]-self.a[1]] < 4*CONSOLE_ARGS.paveFreq):
                blocks.SetBlock([loc[0], height-1, loc[2]], b'minecraft:stone_bricks')




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
                self.roof       = b'minecraft:stone'
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
            self.roof       = b'minecraft:stone'
            self.trim       = b'minecraft:oak_log'
            self.window     = b'minecraft:glass'
            self.door       = b'minecraft:oak_door'
            self.ground     = b'minecraft:grass_block'
