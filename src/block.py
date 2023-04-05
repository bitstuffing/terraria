import pygame

class Block:
    
    # type: 0 = none, 1 = grass, 2 = dirt, 3 = stone
    def __init__(self, type):
        if type == 1:
            self.image = pygame.image.load("assets/grass.png").convert_alpha()
            self.hardness = 1
            self.type = 1
        elif type == 2:
            self.image = pygame.image.load("assets/dirt.png").convert_alpha()
            self.hardness = 1
            self.type = 2
        elif type == 3:
            self.image = pygame.image.load("assets/stone.png").convert_alpha()
            self.hardness = 2
            self.type = 3
        else:
            self.type = 0 # same than none
                
