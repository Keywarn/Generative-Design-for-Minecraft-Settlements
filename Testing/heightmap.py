import requests
import nbt

from io import BytesIO

url = "http://localhost:9000"

#Take in two locations (as tuples) and get the chunks containing the area
def GetChunks(a, b, rtype = 'text'):
    print(f"Getting chunks in area A: {a}, B: {b}")

    #Start with the bottom left chunk
    chunkA = (min(a[0],b[0])//16, min(a[1],b[1])//16)
    chunkB = (max(a[0],b[0])//16, max(a[1],b[1])//16)

    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/raw'
    r = requests.get(url+f"/chunks?x={chunkA[0]}&z={chunkA[1]}&dx={chunkB[0]-chunkA[0]}&dz={chunkB[1]-chunkA[1]}", headers={"Accept": acceptType})
    
    if rtype == 'text':
        return r.text
    elif rtype == 'bytes':
        return r.content

#Take in two locations (as tuples) and get the heightmap
def GetHeightmap(a,b):
    data = GetChunks(a,b, rtype='bytes')
    file = BytesIO(data)
    
    nbtFile = nbt.nbt.NBTFile(buffer=file)

    print(nbtFile)

GetHeightmap((0,0), (100,100))