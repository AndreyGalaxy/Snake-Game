import pygame
from config.settings import *
from game.snake import Snake
from game.food import Food

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Snake Game")
        self.update_layout()

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "MENU"

        self.move_timer = 0
        self.move_delay = 100
        self.flash_timer = 0

        self.snake = Snake()
        self.food = Food(self.snake.body)

        self.score = 0
        self.font = pygame.font.SysFont(None, 36)

    def run(self):
        while self.running:
            delta = self.clock.tick(FPS)
            self.move_timer += delta

            self.handle_input()
            self.update()
            self.draw()

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
                MIN_WIDTH = PLAY_WIDTH
                MIN_HEIGHT = PLAY_HEIGHT + UI_HEIGHT
                WIDTH = max(event.w, MIN_WIDTH)
                HEIGHT = max(event.h, MIN_HEIGHT)
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

                self.update_layout()

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

    def update(self):
        if self.game_state != "PLAYING":
            return
        
        self.snake.update_direction()

        if self.move_timer >= self.move_delay:
            self.snake.move()
            self.move_timer = 0

        if not self.snake.has_valid_moves():
            self.game_state = "GAME_OVER"

        head = self.snake.body[0]

        if head == self.food.position:
            self.flash_timer = 3
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
        self.screen.fill(BLACK)
        self.draw_grid()

        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        if self.flash_timer > 0:
            flash_overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT))
            flash_overlay.set_alpha(10)
            flash_overlay.fill(WHITE)
            self.screen.blit(flash_overlay, (0, 0))
            self.flash_timer -= self.clock.get_time()

        ui_rect = pygame.Rect(0, HEIGHT - UI_HEIGHT, WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, ui_rect)
        pygame.draw.line(self.screen, GRAY, (0, HEIGHT - UI_HEIGHT), (WIDTH, HEIGHT - UI_HEIGHT), 2)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)

        x = WIDTH - score_text.get_width() - 20
        y = HEIGHT - UI_HEIGHT + (UI_HEIGHT - score_text.get_height()) // 2

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

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)

        pause_text = font_large.render("Paused", True, WHITE)
        shadow = font_large.render("Paused", True, GRAY)
        prompt_text = font_small.render("Press P to Resume", True, GRAY)

        screen_center_x = WIDTH // 2
        screen_center_y = HEIGHT // 2

        pause_rect = pause_text.get_rect(center=(screen_center_x, screen_center_y - 20))
        prompt_rect = prompt_text.get_rect(center=(screen_center_x, screen_center_y + 30))

        self.screen.blit(shadow, (pause_rect.x + 2, pause_rect.y + 2))
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(prompt_text, prompt_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)

        game_over_text = font_large.render("Game Over", True, LIGHT_RED)
        shadow = font_large.render("Game Over", True, LIGHT_GRAY)
        score_text = font_small.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = font_small.render("Press R to Restart", True, GRAY)

        screen_center_x = WIDTH // 2
        screen_center_y = HEIGHT // 2

        go_rect = game_over_text.get_rect(center=(screen_center_x, screen_center_y - 40))
        score_rect = score_text.get_rect(center=(screen_center_x, screen_center_y + 10))
        restart_rect = restart_text.get_rect(center=(screen_center_x, screen_center_y + 50))

        self.screen.blit(shadow, (go_rect.x + 2, go_rect.y + 2))
        self.screen.blit(game_over_text, go_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        
    def draw_grid(self):
        for x in range(0, PLAY_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x + PLAY_OFFSET_X, PLAY_OFFSET_Y), (x + PLAY_OFFSET_X, PLAY_OFFSET_Y + PLAY_HEIGHT))

        for y in range(0, PLAY_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (PLAY_OFFSET_X, y + PLAY_OFFSET_Y), (PLAY_OFFSET_X + PLAY_WIDTH, y + PLAY_OFFSET_Y))

        pygame.draw.rect(self.screen, GRAY, (PLAY_OFFSET_X, PLAY_OFFSET_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)

    def update_layout(self):
        global PLAY_OFFSET_X, PLAY_OFFSET_Y
        PLAY_OFFSET_X = (WIDTH - PLAY_WIDTH) // 2
        PLAY_OFFSET_Y = (HEIGHT - UI_HEIGHT - PLAY_HEIGHT) // 2