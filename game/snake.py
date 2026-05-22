import pygame
from config.settings import *

class Snake:
    def __init__(self):
        self.body = [(5, 5), (4, 5), (3, 5)]
        self.direction = "RIGHT"

        self.position = pygame.Vector2(self.body[0])
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 10
        self.smoothing = 0.15

        self.direction_queue = []
        self.grow_pending = False

    def will_collide(self, direction):
        head_x, head_y = self.body[0]

        if direction == "UP":
            new_head = (head_x, head_y - 1)
        elif direction == "DOWN":
            new_head = (head_x, head_y + 1)
        elif direction == "LEFT":
            new_head = (head_x - 1, head_y)
        elif direction == "RIGHT":
            new_head = (head_x + 1, head_y)

        new_head = (
            new_head[0] % GRID_WIDTH,
            new_head[1] % GRID_HEIGHT
        )

        if self.grow_pending:
            return new_head in self.body
        else:
            return new_head in self.body[:-1]

    def move(self):

        if self.will_collide(self.direction):
            return

        head_x, head_y = self.body[0]

        if self.direction == "UP":
            new_head = (head_x, head_y - 1)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + 1)
        elif self.direction == "LEFT":
            new_head = (head_x - 1, head_y)
        elif self.direction == "RIGHT":
            new_head = (head_x + 1, head_y)

        new_head = (
            new_head[0] % GRID_WIDTH,
            new_head[1] % GRID_HEIGHT
        )

        self.body.insert(0, new_head)

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def grow(self):
        self.grow_pending = True

    def has_valid_moves(self):
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]

        for direction in directions:
            if not self.will_collide(direction):
                return True
        
        return False

    def draw(self, screen, offset_x, offset_y, tile_size):
        for i, segment in enumerate(self.body):

            x = offset_x + segment[0] * tile_size
            y = offset_y + segment[1] * tile_size

            rect = pygame.Rect(x + 1, y + 1, tile_size - 2, tile_size - 2)

            color = GREEN if i == 0 else DARK_GREEN
            
            pygame.draw.rect(screen, color, rect)

    def update_direction(self):
        while self.direction_queue:
            new_direction = self.direction_queue[0]

            if not self.will_collide(new_direction):
                self.direction = self.direction_queue.pop(0)
                break
            else:
                self.direction_queue.pop(0)

    def update(self, delta_time):
        direction_vector = pygame.Vector2(self.direction)
        target_velocity = direction_vector * self.speed
        self.velocity += (target_velocity - self.velocity) * self.smoothing
        self.position += self.velocity * delta_time
        self.body[0] = (int(round(self.position.x)), int(round(self.position.y)))