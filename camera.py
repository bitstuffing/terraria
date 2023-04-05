import pygame
from configuration import *

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)

    def update(self, target):
        self.rect.center = target.rect.center
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH * TILE_SIZE, WORLD_HEIGHT * TILE_SIZE))
