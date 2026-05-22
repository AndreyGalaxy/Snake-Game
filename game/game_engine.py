import pygame
from config.settings import *
from game.snake import Snake
from game.food import Food

class Game:
    def __init__(self):

        self.width = WIDTH
        self.height = HEIGHT
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Snake Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "MENU"

        self.move_timer = 0
        self.move_delay = 200
        self.flash_timer = 0

        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0

        self.camera_strength = 0.2
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 7

        self.snake = Snake()
        self.food = Food(self.snake.body)

        self.prev_head = self.snake.body[0]
        self.velocity = pygame.Vector2(0, 0)
        self.target_velocity = pygame.Vector2(0, 0)
        
        self.play_offset_x = 0
        self.play_offset_y = 0
        self.compute_layout()
        self.update_camera(0.016)

        self.score = 0
        self.font = pygame.font.SysFont(None, 36)

    def run(self):
        while self.running:
            delta = self.clock.tick(FPS)
            dt = delta / 1000.0
            
            self.move_timer += delta

            self.handle_input()
            self.update(dt)
            self.draw()

    def compute_layout(self):
        self.tile_size = GRID_SIZE * self.zoom

        self.play_width = GRID_WIDTH * self.tile_size
        self.play_height = GRID_HEIGHT * self.tile_size
        
        self.base_offset_x = (self.width - self.play_width) // 2
        available_height = self.height - UI_HEIGHT
        self.base_offset_y = (available_height - self.play_height) // 2
    
    def update_camera(self, dt):
        centered_x, centered_y = self.snake_head_location()

        max_offset_x = self.play_width * self.camera_strength
        max_offset_y = self.play_height * self.camera_strength
        
        deadzone = 0.05

        def apply_deadzone(value):
            if abs(value) < deadzone:
                return 0
            return (value - deadzone * (1 if value > 0 else -1)) / (1 - deadzone)
        
        centered_x = apply_deadzone(centered_x)
        centered_y = apply_deadzone(centered_y)

        def smoothstep(x):
            return x * x * (3 - 2 * x)

        sx = smoothstep(abs(centered_x))
        sy = smoothstep(abs(centered_y))

        sign_x = 0 if centered_x == 0 else (1 if centered_x > 0 else -1)
        sign_y = 0 if centered_y == 0 else (1 if centered_y > 0 else -1)

        velocity = self.velocity
        if velocity.length() > 0:
            velocity = velocity.normalize()

        dx, dy = velocity

        position_weight = 0.8
        direction_weight = 0.2

        target_camera_x = -(sx * sign_x * position_weight + dx * direction_weight) * max_offset_x
        target_camera_y = -(sy * sign_y * position_weight + dy * direction_weight) * max_offset_y

        self.camera_x += (target_camera_x - self.camera_x) * self.camera_speed * dt
        self.camera_y += (target_camera_y - self.camera_y) * self.camera_speed * dt

        self.camera_x = max(-max_offset_x, min(max_offset_x, self.camera_x))
        self.camera_y = max(-max_offset_y, min(max_offset_y, self.camera_y))

        self.play_offset_x = self.base_offset_x + self.camera_x
        self.play_offset_y = self.base_offset_y + self.camera_y
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue 

            if self.game_state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.game_state = "PLAYING"

            elif self.game_state == "PAUSED":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.game_state = "PLAYING"
                    self.move_timer = 0

            elif self.game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()

            elif event.type == pygame.VIDEORESIZE:
                tile_size = GRID_SIZE * self.zoom
                MIN_WIDTH = GRID_WIDTH * tile_size
                MIN_HEIGHT = GRID_HEIGHT * tile_size + UI_HEIGHT
                self.width = max(event.w, MIN_WIDTH)
                self.height = max(event.h, MIN_HEIGHT)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

                self.compute_layout()
                self.update_camera(0.016)

            elif self.game_state == "PLAYING":        
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_p:
                        self.game_state = "PAUSED"
                        self.move_timer = 0
                        return
                    
                    new_direction = None

                    if event.key == pygame.K_UP:
                        new_direction = "UP"
                    elif event.key == pygame.K_DOWN:
                        new_direction = "DOWN"
                    elif event.key == pygame.K_LEFT:
                        new_direction = "LEFT"
                    elif event.key == pygame.K_RIGHT:
                        new_direction = "RIGHT"

                    if new_direction:
                        last_direction = (
                            self.snake.direction_queue[-1]
                            if self.snake.direction_queue 
                            else self.snake.direction
                        )

                        if not(
                            (new_direction == "UP" and last_direction == "DOWN") or
                            (new_direction == "DOWN" and last_direction == "UP") or
                            (new_direction == "LEFT" and last_direction == "RIGHT") or
                            (new_direction == "RIGHT" and last_direction == "LEFT")
                        ):
                            if len(self.snake.direction_queue) < 3:
                                self.snake.direction_queue.append(new_direction)
            
            if event.type == pygame.MOUSEWHEEL:
                self.adjust_zoom(event.y * 0.03)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self.adjust_zoom(0.05)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.adjust_zoom(-0.05)

    def update(self, dt):
        self.zoom += (self.target_zoom - self.zoom) * 8 * dt
        if abs(self.zoom - self.target_zoom) < 0.001:
            self.zoom = self.target_zoom
        self.compute_layout()
        self.update_camera(dt)
        smoothing = 3
        self.velocity += (self.target_velocity - self.velocity) * smoothing * dt
        
        if self.game_state != "PLAYING":
            return

        while self.move_timer >= self.move_delay:
            previous = self.snake.body[0]

            self.snake.update_direction()
            self.snake.move()
            
            current = self.snake.body[0]
            
            dx = current[0] - previous[0]
            dy = current[1] - previous[1]

            if dx > GRID_WIDTH // 2:
                dx -= GRID_WIDTH
            elif dx < -GRID_WIDTH // 2:
                dx += GRID_WIDTH

            if dy > GRID_HEIGHT // 2:
                dy -= GRID_HEIGHT
            elif dy < -GRID_HEIGHT // 2:
                dy += GRID_HEIGHT

            self.target_velocity = pygame.Vector2(dx, dy)
            
            self.move_timer -= self.move_delay

        if not self.snake.has_valid_moves():
            self.game_state = "GAME_OVER"

        head = self.snake.body[0]

        if head == self.food.position:
            self.flash_timer = 100
            self.snake.grow()
            self.food.respawn(self.snake.body)
            self.score += 1

    def draw(self):
        if self.game_state == "MENU":
            self.draw_menu()

        elif self.game_state == "PLAYING":
            self.draw_gameplay()

        elif self.game_state == "PAUSED":
            self.draw_gameplay()
            self.draw_pause()

        elif self.game_state == "GAME_OVER":
            self.draw_gameplay()
            self.draw_game_over()

        pygame.display.flip()
    
    def draw_gameplay(self):
        tile_size = self.tile_size
        play_width = self.play_width
        play_height = self.play_height
        
        self.screen.fill(BLACK)
        self.draw_grid()

        self.snake.draw(self.screen, self.play_offset_x, self.play_offset_y, tile_size)
        self.food.draw(self.screen, self.play_offset_x, self.play_offset_y, tile_size)

        if self.flash_timer > 0:
            flash_overlay = pygame.Surface((play_width, play_height))
            flash_overlay.set_alpha(10)
            flash_overlay.fill(WHITE)
            self.screen.blit(flash_overlay, (self.play_offset_x, self.play_offset_y))
            self.flash_timer -= self.clock.get_time()

        ui_rect = pygame.Rect(0, self.height - UI_HEIGHT, self.width, UI_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, ui_rect)
        pygame.draw.line(self.screen, GRAY, (0, self.height - UI_HEIGHT), (self.width, self.height - UI_HEIGHT), 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)

        x = self.width - score_text.get_width() - 20
        y = self.height - UI_HEIGHT + (UI_HEIGHT - score_text.get_height()) // 2

        self.screen.blit(score_text, (x, y))

    def reset_game(self):
        self.snake = Snake()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.move_timer = 0
        self.game_state = "PLAYING"

    def draw_menu(self):
        self.screen.fill(BLACK)

        title_font = pygame.font.SysFont(None, 72)
        small_font = pygame.font.SysFont(None, 36)

        title = title_font.render("Snake Game", True, GREEN)
        prompt = small_font.render("Press SPACE to Start", True, GRAY)

        self.screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 40)))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 20)))

    def draw_pause(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)

        pause_text = font_large.render("Paused", True, WHITE)
        shadow = font_large.render("Paused", True, GRAY)
        prompt_text = font_small.render("Press P to Resume", True, GRAY)

        screen_center_x = self.width // 2
        screen_center_y = self.height // 2

        pause_rect = pause_text.get_rect(center=(screen_center_x, screen_center_y - 20))
        prompt_rect = prompt_text.get_rect(center=(screen_center_x, screen_center_y + 30))

        self.screen.blit(shadow, (pause_rect.x + 2, pause_rect.y + 2))
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(prompt_text, prompt_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)

        game_over_text = font_large.render("Game Over", True, LIGHT_RED)
        shadow = font_large.render("Game Over", True, LIGHT_GRAY)
        score_text = font_small.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = font_small.render("Press R to Restart", True, GRAY)

        screen_center_x = self.width // 2
        screen_center_y = self.height // 2

        go_rect = game_over_text.get_rect(center=(screen_center_x, screen_center_y - 40))
        score_rect = score_text.get_rect(center=(screen_center_x, screen_center_y + 10))
        restart_rect = restart_text.get_rect(center=(screen_center_x, screen_center_y + 50))

        self.screen.blit(shadow, (go_rect.x + 2, go_rect.y + 2))
        self.screen.blit(game_over_text, go_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        
    def draw_grid(self):
        tile_size = self.tile_size

        play_width = self.play_width
        play_height = self.play_height

        for x in range(GRID_WIDTH + 1):
            px = self.play_offset_x + x * tile_size
            pygame.draw.line(self.screen, DARK_GRAY, (px, self.play_offset_y), (px, self.play_offset_y + play_height))

        for y in range(GRID_HEIGHT + 1):
            py = self.play_offset_y + y * tile_size
            pygame.draw.line(self.screen, DARK_GRAY, (self.play_offset_x, py), (self.play_offset_x + play_width, py))

        pygame.draw.rect(self.screen, GRAY, (self.play_offset_x, self.play_offset_y, play_width, play_height), 2)

    def adjust_zoom(self, zoom_change):
        self.target_zoom += zoom_change
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, self.target_zoom))

    def snake_head_location(self):
        head_x, head_y = self.snake.body[0]
        normalized_x = head_x / (GRID_WIDTH - 1)
        normalized_y = head_y / (GRID_HEIGHT - 1)
        centered_x = normalized_x - 0.5
        centered_y = normalized_y - 0.5
        return (centered_x, centered_y)