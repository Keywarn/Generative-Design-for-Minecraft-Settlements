import requests

url = "http://localhost:9000"

def SetBlock(x,y,z, block):
    print(f"Setting X: {x}, Y: {y}, Z: {z} - {block}")
    r = requests.put(url+f"/blocks?x={x}&y={y}&z={z}", data = block)

def GetBlock(x,y,z):
    r = requests.get(url+f"/blocks?x={x}&y={y}&z={z}")
    print(f"Block X: {x}, Y: {y}, Z: {z} - {r.content}")