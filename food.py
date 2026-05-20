import pygame
import random
from settings import *

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
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE

        pygame.draw.rect(screen, RED, (x, y, GRID_SIZE, GRID_SIZE))