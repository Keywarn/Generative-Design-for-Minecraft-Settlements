import requests
import nbt
import matplotlib.pyplot as plt

from io import BytesIO
from bitarray import BitArray

url = "http://localhost:9000"

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
    chunkA = (min(a[0],b[0])//16, min(a[1],b[1])//16)
    chunkB = (max(a[0],b[0])//16, max(a[1],b[1])//16)

    return chunkA, chunkB

def OrderCoords(a,b):
    aa = (min(a[0],b[0]), min(a[1],b[1]))
    bb = (max(a[0],b[0]), max(a[1],b[1]))

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
            chunkNum = x + z * (chunkB[1]-chunkA[1]+2)

            rawMap = nbtFile["Chunks"][chunkNum]["Level"]["Heightmaps"]["WORLD_SURFACE"]
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

heightmap = GetHeightmap((-55,90), (55,190))

plt.imshow(heightmap, cmap='hot', origin='lower')
plt.show()