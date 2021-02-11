
class Agent:
    def __init__(self, pos, block):

        self.pos = pos
        self.block = block

        #self.prevBlock = GetBlock(pos[0], pos[1])

        self.move(pos)

    def move(pos):
        #Should check if it is a valid move first

        #Set the block of current position back
        #SetBlock(self.pos, prevBlock)
        #Move to new position
        self.pos = pos
        #Set the block
        #SetBlock(pos, block)

