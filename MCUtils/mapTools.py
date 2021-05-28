import requests
import nbt
import matplotlib.pyplot as plt

from io import BytesIO
from mcutils.bitarray import BitArray

import mcutils.blocks as blocks

url = "http://localhost:9000"

blockColours = {b"minecraft:grass_block": [94,157,52,255],b"minecraft:stone": [161,162,161,255],
                    b"minecraft:sand": [194,178,128,255],b"minecraft:water": [116,204,244,255],
                    b"minecraft:acacia_log": [110,71,11,255], b"minecraft:birch_log": [110,71,11,255],
                    b"minecraft:dark_oak_log": [110,71,11,255],b"minecraft:jungle_log": [110,71,11,255],
                    b"minecraft:oak_log": [110,71,11,255],b"minecraft:spruce_log": [110,71,11,255],
                    b"minecraft:gravel": [136,126,126,255]}

woolColours = {b'minecraft:white_wool': [233,236,236,255],b'minecraft:orange_wool': [240,118,19,255],b'minecraft:magenta_wool': [189,68,179,255],
            b'minecraft:light_blue_wool': [58,175,217,255],b'minecraft:yellow_wool': [248,198,39,255],b'minecraft:lime_wool': [112,185,25,255],
            b'minecraft:pink_wool': [237,141,172,255],b'minecraft:gray_wool':[62,68,72,255]}

def GetBuildArea():
    r = requests.get(url+'/buildarea')
    if r.ok:
        return r.json()
    else:
        return None
#Take in two chunk locations and get the chunks containing the area
def GetChunks(a, b, rtype = "text"):
    acceptType = "application/octet-stream" if rtype == "bytes" else "text/raw"
    r = requests.get(url+f"/chunks?x={a[0]}&z={a[1]}&dx={b[0]-a[0]+1}&dz={b[1]-a[1]+1}", headers={"Accept": acceptType})
    
    if rtype == "text":
        return r.text
    elif rtype == "bytes":
        return r.content

def CoordToChunks(a,b):
    #Return the chunk locations
    chunkA = (a[0]//16, a[1]//16)
    chunkB = (b[0]//16, b[1]//16)

    return chunkA, chunkB

def OrderCoords(a,b):
    aa = [min(a[0],b[0]), min(a[1],b[1])]
    bb = [max(a[0],b[0]), max(a[1],b[1])]

    return aa,bb

#Take in two locations (as tuples) and get the heightmap
def GetHeightmap(a,b):
    a,b = OrderCoords(a,b)
    chunkA, chunkB = CoordToChunks(a,b)
    data = GetChunks(chunkA,chunkB, rtype="bytes")
    file = BytesIO(data)
    
    nbtFile = nbt.nbt.NBTFile(buffer=file)

    #Create empty map:
    size = (b[0]-a[0] +1,b[1]-a[1] +1)
    heightmap = [[-1 for z in range(size[1])] for x in range(size[0])]

    #Offset into the chunk
    offsets = (a[0]%16, a[1]%16)
    #For each chunk go through co-ords
    for x in range(chunkB[0]-chunkA[0]+1):
        for z in range(chunkB[1]-chunkA[1]+1):

            # Get the chunk number in the nbt data
            chunkNum = x + z * (chunkB[0]-chunkA[0]+1)

            rawMap = nbtFile["Chunks"][chunkNum]["Level"]["Heightmaps"]["MOTION_BLOCKING_NO_LEAVES"]
            mapBitArray = BitArray(9, 16*16, rawMap)

            #Index other way round in NBT
            for cz in range(16):
                for cx in range(16):
                    xMap = x * 16 + cx - offsets[0]
                    zMap = z * 16 + cz - offsets[1]

                    #If inside the area, put it in the heightmap
                    if(xMap >= 0 and zMap >= 0 and xMap < size[0] and zMap < size[1]):
                        heightmap[xMap][zMap] = mapBitArray.getAt(cz * 16 + cx)
    
    return heightmap

#Given a heightmap and start location, get the blocks
def GetHeightmapBlocks(heightmap, start):
    #Create empty block map
    heightmapBlocks = [[b"minecraft:air" for z in range(len(heightmap[0]))] for x in range(len(heightmap))]

    #Fill the block map
    for x in range(len(heightmap)):
        for z in range(len(heightmap[0])):
            heightmapBlocks[x][z] = blocks.GetBlock([a[0] + x, heightmap[x][z]-1, a[1] + z])

    
    return heightmapBlocks


def showMap(hm, a, b, title=""):
    plt.xlabel('X World Co-Ordinate')
    plt.ylabel('Z World Co-Ordinate')
    plt.title(title)

    hmFlip = [*zip(*hm[::-1])]
    
    plt.imshow(hmFlip, origin='lower',extent=[b[0],a[0],a[1],b[1]])
    plt.show()

def convertBlockMap(blockMap):
    colourMap = [[[0,0,0,255] for z in range(len(blockMap[0]))] for x in range(len(blockMap))]
    for x in range(len(blockMap)):
        for z in range(len(blockMap[0])):
            colourMap[x][z] = blockColours.get(blockMap[x][z], [0,0,0,255])
            if(colourMap[x][z] == [0,0,0,255] and blockMap[x][z] != None):
                colourMap[x][z] = [255,192,203,255]
                #print(f"Un-Coloured block: {blockMap[x][z]}")
    
    return colourMap

def convertPlotMap(plots, size):
    colourMap = [[[0,0,0,255] for z in range(size[1])] for x in range(size[0])]

    for plot in plots:
        block = plot.colour
        for cell in plot.cells:
            colourMap[cell[0]][cell[1]] = woolColours.get(block, [0,0,0,255])
    
    return colourMap

def paintPlots(world):
    for plot in world.plots:
        for cell in plot.cells:
            blocks.SetBlock([world.a[0] + cell[0],world.heightmap[cell[0]][cell[1]] -1, world.a[1] + cell[1]], plot.colour)


def main():
    a,b = OrderCoords((-55,90),(45, 190))
    heightmap = GetHeightmap(a, b)

    heightmapBlocks = GetHeightmapBlocks(heightmap, a)

    for x in range(len(heightmapBlocks)):
            for z in range(len(heightmapBlocks[0])):
                if(heightmapBlocks[x][z] not in blockColours):
                    print(f"FOUND BLOCK NOT IN COLOUR DICT: {heightmapBlocks[x][z]}")
                heightmapBlocks[x][z] = blockColours.get(heightmapBlocks[x][z], [0,0,0,255])

    fig, axs = plt.subplots(1,2, constrained_layout=True)
    axs[0].set_xlabel('X World Co-Ordinate')
    axs[0].set_ylabel('Z World Co-Ordinate')
    axs[0].set_title('Surface Heightmap')
    img = axs[0].imshow([*zip(*heightmap)], origin='lower',extent=[a[0],b[0],a[1],b[1]])
    fig.colorbar(img, ax=axs[0], shrink=0.4)

    axs[1].imshow([*zip(*heightmapBlocks)], origin='lower',extent=[a[0],b[0],a[1],b[1]])
    axs[1].set_xlabel('X World Co-Ordinate')
    axs[1].set_ylabel('Z World Co-Ordinate')
    axs[1].set_title('Surface Block Map')

    plt.show()

