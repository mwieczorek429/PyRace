import pygame
import sys
import random
import math
from pathlib import Path

# Importy dla Etapu 1
from components.car import Car
from components.track import Track
from game.game_config import GameConfig
from game.camera_controller import CameraController

pygame.init()

class Game:
    def __init__(self):
        # Inicjalizacja ekranu
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption(GameConfig.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        # Inicjalizacja toru
        self.track = Track(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)

        # Inicjalizacja kamery
        self.camera = CameraController(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)

        # Ładowanie gracza
        spawn_data = GameConfig.load_spawn_positions()
        player_data = spawn_data["player"]
        self.player_car = Car(player_data["x"], player_data["y"], color=GameConfig.RED)
        self.player_car.angle = 90 # Domyślny kąt startowy

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.player_car.handle_input(keys, self.dt)
        self.player_car.update(self.dt)
        self.camera.update(self.player_car.x, self.player_car.y, self.dt)

    def render(self):
        camera_x, camera_y = self.camera.get_camera_offset()

        self.track.draw(self.screen, camera_x, camera_y)
        self.player_car.draw(self.screen, camera_x, camera_y)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.dt = self.clock.tick(GameConfig.FPS) / 1000.0

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()