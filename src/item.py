import pygame

class Item:
    def __init__(self, image_path, action_radius, durability):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.action_radius = action_radius
        self.durability = durability
        self.strength = 3 # attack strength
        self.reach = 3 # use distance in blocks
        self.uses = 0
