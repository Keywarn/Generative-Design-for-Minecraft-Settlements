import requests

url = "http://localhost:9000"

#Take in two locations (as tuples) and get the heightmaps for the chunks containing the area
def GetHeightmap(a, b):
    print(f"Getting chunks in area A: {a}, B: {b}")
    chunkA = a // 2
    chunkB = b //2
    r = requests.put(url+f"/chunks?x={x}&y={y}&dx={b[0]-a[0]}&dy={b[1]-a[1]}")