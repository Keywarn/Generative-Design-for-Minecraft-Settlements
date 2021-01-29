import requests
import nbt

from io import BytesIO

url = "http://localhost:9000"

#Take in two chunk locations and get the chunks containing the area
def GetChunks(a, b, rtype = "text"):
    acceptType = "application/octet-stream" if rtype == "bytes" else "text/raw"
    r = requests.get(url+f"/chunks?x={a[0]}&z={a[1]}&dx={b[0]-a[0]}&dz={b[1]-a[1]}", headers={"Accept": acceptType})
    
    if rtype == "text":
        return r.text
    elif rtype == "bytes":
        return r.content

def CoordToChunks(a,b):
    #Return the chunk locations
    chunkA = (min(a[0],b[0])//16, min(a[1],b[1])//16)
    chunkB = (max(a[0],b[0])//16, max(a[1],b[1])//16)

    return chunkA, chunkB

#Take in two locations (as tuples) and get the heightmap
def GetHeightmap(a,b):

    chunkA, chunkB = CoordToChunks(a,b)
    data = GetChunks(chunkA,chunkB, rtype="bytes")
    file = BytesIO(data)
    
    nbtFile = nbt.nbt.NBTFile(buffer=file)

    #Create empty map:
    heightmap = [[-1 for z in range(abs(b[1]-a[1]))] for x in range(abs(b[0]-a[0]))]

    #For each chunk go through co-ords
    for x in range(chunkB[0]-chunkA[0]):
        for z in range(chunkB[1]-chunkA[1]):

            chunkNum = x + z * (chunkB[1]-chunkA[1])

            nbtFile["Chunks"][chunkNum]["Level"]["Heightmaps"]["WORLD_SURFACE"]

GetHeightmap((0,0), (100,100))