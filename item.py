import pygame

class Item:
    def __init__(self, image_path, action_radius, durability):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.action_radius = action_radius
        self.durability = durability
