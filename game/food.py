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

    def draw(self, screen):
        x = PLAY_OFFSET_X + self.position[0] * GRID_SIZE
        y = PLAY_OFFSET_Y + self.position[1] * GRID_SIZE

        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)

        pygame.draw.circle(screen, RED, center, GRID_SIZE // 2 - 2)