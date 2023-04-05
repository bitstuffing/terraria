import pygame

class Block:
    def __init__(self, image_path, hardness):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.hardness = hardness