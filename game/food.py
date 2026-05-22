import pygame
import random
from config.settings import *

class Food:
    def __init__(self, snake_body):
        self.position = self.random_position()
        self.respawn(snake_body)

    def random_position(self):
        
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)

        return (x, y)
    
    def respawn(self, snake_body):
        while True:
            new_position = self.random_position()

            if new_position not in snake_body:
                self.position = new_position
                break

    def draw(self, screen, offset_x, offset_y, tile_size):
        x = offset_x + self.position[0] * tile_size
        y = offset_y + self.position[1] * tile_size

        center = (x + tile_size // 2, y + tile_size // 2)

        pygame.draw.circle(screen, RED, center, tile_size // 2 - 2)