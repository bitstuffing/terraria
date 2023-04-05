import sys
import pygame

import sys
import pygame
import noise
import numpy as np
import random
import math

from src.configuration import *

from src.player import Player
from src.item import Item
from src.block import Block
from src.camera import Camera

class Terraria:

    # global variables
    screen = None
    clock = None

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Terraria Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.init()
        self.player_height = 32  # height of the player image, TODO change and get it from alpha of sum of player pixels and item pixels
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.selected_block = None # block selected by the player (mouse click)
        self.interaction_distance = 3 * TILE_SIZE # distance in pixels from the player to the selected block

    def get_selected_block(self, mouse_x, mouse_y, camera):
        # calculate the position of the block selected by the camera and the mouse position
        block_x = (mouse_x + camera.rect.x) // TILE_SIZE
        block_y = (mouse_y + camera.rect.y) // TILE_SIZE

        # verify that the block is inside the world
        if 0 <= block_x < WORLD_WIDTH and 0 <= block_y < WORLD_HEIGHT:
            self.selected_block = (block_x, block_y)
        else:
            self.selected_block = None
        
    def generate_terrain(self, width, height):
        
        world = np.zeros((width, height), dtype=int)

        random_offset_x = random.randint(0, 1000)
        random_offset_y = random.randint(0, 1000)

        for y in range(height):
            for x in range(width):
                nx, ny = (x + random_offset_x) / FREQUENCY, (y + random_offset_y) / FREQUENCY
                elevation = noise.pnoise2(nx, ny, octaves=OCTAVES) * AMPLITUDE

                if y > height // 2 + int(elevation):
                    if y < height // 2 + int(elevation) + 10:  # 10 blocks of grass
                        world[x, y] = 1  # grass
                    elif y < height // 2 + int(elevation) + 40:  # 30 blocks of dirt
                        world[x, y] = 2  # dirt
                    else:
                        world[x, y] = 3  # stone

        return world


    def draw_terrain(self, screen, world, camera):
        start_x = max(0, camera.rect.left // TILE_SIZE)
        end_x = min(world.shape[0], camera.rect.right // TILE_SIZE + 1)
        start_y = max(0, camera.rect.top // TILE_SIZE)
        end_y = min(world.shape[1], camera.rect.bottom // TILE_SIZE + 1)

        # draw the selected block (if any) in red
        if self.selected_block is not None:
            x, y = self.selected_block
            pygame.draw.rect(screen, RED, (x * TILE_SIZE - camera.rect.x, y * TILE_SIZE - camera.rect.y, TILE_SIZE, TILE_SIZE), 2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if world[x, y] == 1:
                    pygame.draw.rect(screen, GREEN, (x * TILE_SIZE - camera.rect.x, y * TILE_SIZE - camera.rect.y, TILE_SIZE, TILE_SIZE))
                elif world[x, y] == 2:
                    pygame.draw.rect(screen, BROWN, (x * TILE_SIZE - camera.rect.x, y * TILE_SIZE - camera.rect.y, TILE_SIZE, TILE_SIZE))
                elif world[x, y] == 3:
                    pygame.draw.rect(screen, GRAY, (x * TILE_SIZE - camera.rect.x, y * TILE_SIZE - camera.rect.y, TILE_SIZE, TILE_SIZE))

                # Dibujar un borde rojo alrededor de los bloques en la superficie o frontera con el cielo bajo el cursor del ratón
                if self.selected_block == (x, y) and (
                    (y > 0 and world[x, y - 1] == 0) or
                    (x > 0 and world[x - 1, y] == 0) or
                    (x < world.shape[0] - 1 and world[x + 1, y] == 0)
                ) and world[x, y] != 0:
                    pygame.draw.rect(screen, RED, (x * TILE_SIZE - camera.rect.x, y * TILE_SIZE - camera.rect.y, TILE_SIZE, TILE_SIZE), 2)




    def find_ground_level(self, world, x):
        for y in range(world.shape[1]):
            if world[x, y] == 1:
                return y * TILE_SIZE - self.player_height
        return 0  # case if no ground is found


    def check_collision(self, player, world):
        player.grounded = False

        # calculate blocks near of the player
        x_min = max(0, player.rect.x // TILE_SIZE - 1)
        x_max = min(world.shape[0], player.rect.right // TILE_SIZE + 1)
        y_min = max(0, player.rect.y // TILE_SIZE - 1)
        y_max = min(world.shape[1], player.rect.bottom // TILE_SIZE + 1)

        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                if world[x, y] > 0:
                    block_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    # check collision in the X axis
                    if player.rect.colliderect(block_rect) and player.rect.y < block_rect.bottom and player.rect.bottom > block_rect.y:
                        if player.vx > 0:  # collision from the left
                            player.rect.x = block_rect.x - player.rect.width
                        elif player.vx < 0:  # collision from the right
                            player.rect.x = block_rect.x + block_rect.width
                        player.vx = 0

        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                if world[x, y] > 0:
                    block_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    # colission in the Y axis
                    if player.rect.colliderect(block_rect) and player.rect.x < block_rect.right and player.rect.right > block_rect.x:
                        if player.vy > 0:  # collision from above
                            player.rect.y = block_rect.y - player.rect.height
                            player.grounded = True
                        elif player.vy < 0:  # collision from below
                            player.rect.y = block_rect.y + block_rect.height
                        player.vy = 0


    def draw_inventory(self, screen, inventory):
        self.slot_size = 40
        self.slot_gap = 5
        self.x_offset = 10
        self.y_offset = 10
        font = pygame.font.Font(None, 24)

        for i in range(inventory.slots):
            x = self.x_offset + i * (self.slot_size + self.slot_gap)
            border_width = 3 if i == inventory.selected_slot else 1
            pygame.draw.rect(screen, WHITE, (x, self.y_offset, self.slot_size, self.slot_size), border_width)

            # draw slot number
            number_surface = font.render(str(i + 1), True, WHITE)
            screen.blit(number_surface, (x + self.slot_size // 2 - number_surface.get_width() // 2, self.y_offset + self.slot_size))

            # draw item in the selected slot
            if i == inventory.selected_slot and inventory.items[i] is not None:
                item = inventory.items[i]
                item_x = x + (self.slot_size - item.image.get_width()) // 2
                item_y = self.y_offset + (self.slot_size - item.image.get_height()) // 2
                screen.blit(item.image, (item_x, item_y))

    def hitBlock(self, block_properties, world):
        target_x, target_y = self.selected_block

        # check the hardness of the selected block and the item's strength
        index = world[target_x, target_y]
        if(index > 0):
            block_hardness = block_properties[index]["hardness"]
            
            # check distance of the player to the block
            distance = math.sqrt((self.character.rect.x - target_x * TILE_SIZE) ** 2 + (self.character.rect.y - target_y * TILE_SIZE) ** 2)
            blocks = int(distance // TILE_SIZE)
            item = self.character.inventory.items[self.character.inventory.selected_slot]
            if blocks <= item.reach:

                item_strength = self.character.held_item.strength

                # increase the hit count
                self.hits += 1

                # check if the item is strong enough and the block has been hit enough times
                if self.hits >= block_hardness // item_strength:
                    world[target_x, target_y] = 0
                    self.hits = 0


    def main(self):
        # generate world (terrain)
        world = self.generate_terrain(WORLD_WIDTH, WORLD_HEIGHT)

        # build player
        start_x = 100  # coordinates of the player - starting position
        start_y = self.find_ground_level(world, start_x // TILE_SIZE)
        self.character = Player(start_x, start_y, "assets/character.png")  # player picture
        
        # fill inventory
        self.character.inventory.items[0] = Item("assets/pickaxe.png", 3 * TILE_SIZE, 3)

        # Create a dictionary to store block properties (e.g., hardness)
        block_properties = {
            1: {"hardness": 3},
            2: {"hardness": 3},
            3: {"hardness": 5}
        }

        # Add a variable to store the number of hits
        self.hits = 0

        while True:
            # events and inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.character.moving_left = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.character.moving_right = True
                    elif event.key == pygame.K_SPACE:
                        self.character.jump()
                    elif event.key in [pygame.K_1, pygame.K_KP1]:
                        self.character.inventory.selected_slot = 0
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        self.character.inventory.selected_slot = 1
                    elif event.key in [pygame.K_3, pygame.K_KP3]:
                        self.character.inventory.selected_slot = 2
                    elif event.key in [pygame.K_4, pygame.K_KP4]:
                        self.character.inventory.selected_slot = 3
                    elif event.key in [pygame.K_5, pygame.K_KP5]:
                        self.character.inventory.selected_slot = 4
                    elif event.key in [pygame.K_6, pygame.K_KP6]:
                        self.character.inventory.selected_slot = 5
                    elif event.key in [pygame.K_7, pygame.K_KP7]:
                        self.character.inventory.selected_slot = 6
                    elif event.key in [pygame.K_8, pygame.K_KP8]:
                        self.character.inventory.selected_slot = 7
                    elif event.key in [pygame.K_9, pygame.K_KP9]:
                        self.character.inventory.selected_slot = 8

                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.character.moving_left = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.character.moving_right = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left mouse button
                        mouse_x, mouse_y = event.pos
                        # Check if the mouse click is within the inventory area
                        if self.y_offset <= mouse_y <= self.y_offset + self.slot_size:
                            slot_clicked = (mouse_x - self.x_offset) // (self.slot_size + self.slot_gap)
                            if 0 <= slot_clicked < self.character.inventory.slots:
                                self.character.inventory.selected_slot = slot_clicked

                        self.hitBlock(block_properties, world)
                            
                    elif event.button == 3:  # right mouse button

                        if self.selected_block is not None:
                            target_x, target_y = self.selected_block

                            # move the self.character towards the target block (center)
                            self.character.target_x = target_x * TILE_SIZE + TILE_SIZE // 2
                            self.character.move_to_x(target_x * TILE_SIZE + TILE_SIZE // 2)

                # update the self.character's held item according to the selected slot
                self.character.held_item = self.character.inventory.items[self.character.inventory.selected_slot]

            # game updates

            # move self.character towards the target x position
            if self.character.target_x is not None:
                if self.character.moving_left or self.character.moving_right:
                    self.character.target_x = None
                else:
                    distance_to_target = self.character.target_x - self.character.rect.x
                    move_speed = min(abs(distance_to_target), 5)

                    if self.character.rect.x < self.character.target_x:
                        self.character.rect.x += move_speed
                        self.character.facing_right = True
                    elif self.character.rect.x > self.character.target_x:
                        self.character.rect.x -= move_speed
                        self.character.facing_right = False
                    else:
                        self.character.target_x = None

                self.check_collision(self.character, world)

            else: # keyboard
                if self.character.moving_left:
                    self.character.rect.x -= 5
                    self.check_collision(self.character, world)
                    self.character.facing_right = False
                if self.character.moving_right:
                    self.character.rect.x += 5
                    self.check_collision(self.character, world)
                    self.character.facing_right = True


            # gravity
            if not self.character.grounded:
                self.character.vy += 1  # gravity force, change that if you want to change the gravity strength

            # game updates
            self.character.update()
            self.check_collision(self.character, world)

            self.camera.update(self.character)
            
            # update selected block by mouse selected position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.get_selected_block(mouse_x, mouse_y, self.camera)


            # rendering part

            self.screen.fill(BLUE)
            # draw terrain
            self.draw_terrain(self.screen, world, self.camera)
            # draw player
            self.character.draw(self.screen, self.camera)
            # draw inventory
            self.draw_inventory(self.screen, self.character.inventory)    

            # flip display - frame drawing
            pygame.display.flip()
            self.clock.tick(FPS)
