import pygame

class Block:
    def __init__(self, image_path, durability):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.durability = durability