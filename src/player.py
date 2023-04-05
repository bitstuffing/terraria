import pygame
import math
from src.inventory import Inventory
from src.configuration import *

class Player():

    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 0  # speed in the x axis
        self.vy = 0  # speed in the y axis
        self.grounded = False
        self.facing_right = False # true if the player is facing right
        self.moving_left = False
        self.moving_right = False
        self.target_x = None
        self.inventory = Inventory(9)
        self.held_item = None


    def draw(self, screen, camera):
        if self.facing_right:
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_image, (self.rect.x - camera.rect.x, self.rect.y - camera.rect.y))
        else:
            screen.blit(self.image, (self.rect.x - camera.rect.x, self.rect.y - camera.rect.y))

        if self.held_item is not None:
            item_x = self.rect.x - camera.rect.x + self.rect.width // 2
            item_y = self.rect.y - camera.rect.y + self.rect.height // 2
            
            if self.facing_right:
                flipped_held_item = pygame.transform.flip(self.held_item.image, True, False)
                screen.blit(flipped_held_item, (item_x + self.image.get_width() / 3, item_y - self.image.get_height() / 3))
            else:
                screen.blit(self.held_item.image, (item_x - self.image.get_width(), item_y - self.image.get_height() / 3))



    def update(self):
        #self.rect.x += self.vx # uncomment this line to enable horizontal movement, commented by bug fix
        self.rect.y += self.vy
        # restrict the player to the world boundaries
        self.rect.x = max(0, min(self.rect.x, (WORLD_WIDTH * TILE_SIZE) - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, (WORLD_HEIGHT * TILE_SIZE) - self.rect.height))

    def jump(self):
        if self.grounded:
            self.vy = -15  # change this value to change the jump height
            self.grounded = False

    def move_to_x(self, target_x, speed=1):
        dx = target_x - self.rect.x

        if abs(dx) <= speed:
            self.vx = 0
            self.rect.x = target_x
        elif dx > 0:
            self.vx = speed
        else:
            self.vx = -speed

        self.rect.x += self.vx
