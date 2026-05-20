import pygame 
from game.game_engine import Game

def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()