import requests

url = "http://localhost:9000"

def SetBlock(pos, block):
    #print(f"Setting X: {pos[0]}, Y: {pos[1]}, Z: {pos[2]} - {block}")
    r = requests.put(url+f"/blocks?x={pos[0]}&y={pos[1]}&z={pos[2]}", data = block)

def GetBlock(pos):
    r = requests.get(url+f"/blocks?x={pos[0]}&y={pos[1]}&z={pos[2]}")
    #print(f"Block X: {pos[0]}, Y: {pos[1]}, Z: {pos[2]} - {r.content}")
    return(r.content)