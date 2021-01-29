import requests

url = "http://localhost:9000"

#Take in two locations (as tuples) and get the heightmaps for the chunks containing the area
def GetHeightmap(a, b):
    print(f"Getting chunks in area A: {a}, B: {b}")

    #Start with the bottom left chunk
    chunkA = (min(a[0],b[0])//16, min(a[1],b[1])//16)
    chunkB = (max(a[0],b[0])//16, max(a[1],b[1])//16)
    r = requests.get(url+f"/chunks?x={chunkA[0]}&z={chunkA[1]}&dx={chunkB[0]-chunkA[0]}&dz={chunkB[1]-chunkA[1]}")
    print(r.content)