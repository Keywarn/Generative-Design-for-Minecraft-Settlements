# Feel free to modify and use this filter however you wish. If you do,
# please give credit to SethBling.
# http://youtube.com/SethBling

from pymclevel import TAG_Compound
from pymclevel import TAG_Int
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
from pymclevel import TAG_Float
from pymclevel import TAG_Double
from pymclevel import TAG_List
from pymclevel import TileEntity
from copy import deepcopy

displayName = "Create Spawners"

inputs = (
("Include position data", False),
)


def perform(level, box, options):
    includePos = options["Include position data"]
    entitiesToRemove = []

    for (chunk, slices, point) in level.getChunkSlices(box):

        for _entity in chunk.Entities:
            entity = deepcopy(_entity)
            x = int(entity["Pos"][0].value)
            y = int(entity["Pos"][1].value)
            z = int(entity["Pos"][2].value)

            if box.minx <= x < box.maxx and box.miny <= y < box.maxy and box.minz <= z < box.maxz:
                entitiesToRemove.append((chunk, _entity))

                level.setBlockAt(x, y, z, 52)
                level.setBlockDataAt(x, y, z, 0)

                spawner = TileEntity.Create("MobSpawner", entity=entity)
                TileEntity.setpos(spawner, (x, y, z))
                spawner["Delay"] = TAG_Short(120)
                if not includePos:
                    del spawner["SpawnData"]["Pos"]
                spawner["EntityId"] = entity["id"]

                chunk.TileEntities.append(spawner)

    for (chunk, entity) in entitiesToRemove:
        chunk.Entities.remove(entity)
