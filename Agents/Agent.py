from MCUtils import blocks

class Agent:
    def __init__(self, pos, block):

        self.pos = pos
        self.block = block

        self.prevBlock = blocks.GetBlock(self.pos)

        self.move(pos)

    def move(self, newPos):

        blocks.SetBlock(self.pos, self.prevBlock)

        self.pos = newPos

        self.prevBlock = blocks.GetBlock(self.pos)

        blocks.SetBlock(self.pos, self.block)

    def kill(self):
        blocks.SetBlock(self.pos, self.prevBlock)

