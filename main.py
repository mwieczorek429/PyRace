import pygame
import sys
import random
import math
from pathlib import Path

from components.car import Car
from components.track import Track
from components.ai_car import AICar
from components.hud import HUD 
from components.effects import EffectManager
from components.sound import SoundManager
from components import powerup
from game.game_config import GameConfig
from game.camera_controller import CameraController
from game.race_manager import RaceManager
from game.collision_manager import CollisionManager

pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption(GameConfig.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.track = Track(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        
        self.hud = HUD(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT,
                       self.track.width, self.track.height)

        self.sound_manager = SoundManager()
        self.effect_manager = EffectManager()
        self.camera = CameraController(GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        self.race_manager = RaceManager(GameConfig.MAX_LAPS, self.sound_manager)

        self._load_spawn_positions()

        self.collision_manager = CollisionManager(
            self.track, self.effect_manager, self.sound_manager
        )

        self.hud.generate_minimap(self.track)
        self.powerups = powerup.spawn_powerups_on_track(self.track, num_hazards=8, num_boosts=5)

        self.engine_sound_timer = random.uniform(
            GameConfig.ENGINE_SOUND_MIN_INTERVAL,
            GameConfig.ENGINE_SOUND_MAX_INTERVAL
        )

        self.sound_manager.play_music()

    def _load_spawn_positions(self):
        spawn_data = GameConfig.load_spawn_positions()

        player_data = spawn_data["player"]
        self.player_car = Car(player_data["x"], player_data["y"], color=GameConfig.RED)

        finish_data = spawn_data.get("finish_line")
        if finish_data:
            finish_line = [
                (finish_data["x1"], finish_data["y1"]),
                (finish_data["x2"], finish_data["y2"])
            ]
            self.race_manager.set_finish_line(finish_line)

        racing_line = self.track.get_racing_line()
        self.ai_cars = []

        for ai_data in spawn_data.get("ai_cars", []):
            ai_car = AICar(
                ai_data["x"],
                ai_data["y"],
                racing_line,
                color=tuple(ai_data["color"]),
                ai_speed=ai_data["speed"],
                racing_line_offset=ai_data["offset"],
                sprite_name=ai_data.get("sprite", "bolid.png")
            )
            self.ai_cars.append(ai_car)

        self._set_starting_angles()
        self.race_manager.init_ai_lap_data(self.ai_cars)

    def _set_starting_angles(self):
        if not self.race_manager.finish_line:
            self.player_car.angle = 0
            for ai_car in self.ai_cars:
                ai_car.angle = 0
            return

        x1, y1 = self.race_manager.finish_line[0]
        x2, y2 = self.race_manager.finish_line[1]

        dx = x2 - x1
        dy = y2 - y1

        line_angle_rad = math.atan2(dy, dx)
        perp_angle_rad = line_angle_rad + math.pi / 2
        perp_angle_deg = math.degrees(perp_angle_rad)
        game_angle = 90 - perp_angle_deg
        game_angle = game_angle % 360

        racing_line = self.track.get_racing_line()
        if racing_line and len(racing_line) > 0:
            first_waypoint = racing_line[0]
            wx, wy = first_waypoint

            angle1 = game_angle
            angle2 = (game_angle + 180) % 360

            player_x, player_y = self.player_car.x, self.player_car.y

            dx1 = wx - player_x
            dy1 = wy - player_y
            angle1_rad = math.radians(angle1)
            forward1_x = math.sin(angle1_rad)
            forward1_y = -math.cos(angle1_rad)
            dot1 = dx1 * forward1_x + dy1 * forward1_y

            angle2_rad = math.radians(angle2)
            forward2_x = math.sin(angle2_rad)
            forward2_y = -math.cos(angle2_rad)
            dot2 = dx1 * forward2_x + dy1 * forward2_y

            if dot2 > dot1:
                game_angle = angle2

        self.player_car.angle = game_angle
        for ai_car in self.ai_cars:
            ai_car.angle = game_angle

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.race_manager.is_race_finished():
                        self.reset_race()
                    elif not self.race_manager.race_started and not self.race_manager.is_countdown_active():
                        self.race_manager.start_countdown()

    def reset_race(self):
        self.race_manager.reset()

        self.player_car.speed = 0
        self.player_car.stunned = False

        for ai_car in self.ai_cars:
            ai_car.speed = 0
            ai_car.stunned = False

        self._load_spawn_positions()
        self.powerups = powerup.spawn_powerups_on_track(self.track, num_hazards=8, num_boosts=5)

    def update(self):
        self.race_manager.update(self.dt, self.player_car, self.ai_cars)

        self.engine_sound_timer -= self.dt
        if self.engine_sound_timer <= 0:
            self.sound_manager.play_engine()
            self.engine_sound_timer = random.uniform(
                GameConfig.ENGINE_SOUND_MIN_INTERVAL,
                GameConfig.ENGINE_SOUND_MAX_INTERVAL
            )

        keys = pygame.key.get_pressed()
        if self.race_manager.is_race_active():
            self.player_car.handle_input(keys, self.dt)
        self.player_car.update(self.dt)

        for ai_car in self.ai_cars:
            if self.race_manager.is_race_active():
                ai_car.update(self.dt)

        for pu in self.powerups:
            pu.update(self.dt)

        camera_shake = self.collision_manager.update(self.player_car, self.ai_cars, self.powerups)
        if camera_shake > 0:
            self.camera.add_shake(camera_shake)

        self.effect_manager.update(self.dt)
        self.camera.update(self.player_car.x, self.player_car.y, self.dt)

    def render(self):
        camera_x, camera_y = self.camera.get_camera_offset()

        self.track.draw(self.screen, camera_x, camera_y)

        if self.race_manager.finish_line:
            self._draw_finish_line(camera_x, camera_y)

        for pu in self.powerups:
            pu.draw(self.screen, camera_x, camera_y)

        for ai_car in self.ai_cars:
            ai_car.draw(self.screen, camera_x, camera_y)

        self.player_car.draw(self.screen, camera_x, camera_y)

        self.effect_manager.draw(self.screen, camera_x, camera_y)

        self.hud.draw(
            self.screen,
            self.player_car,
            self.ai_cars,
            self.race_manager.laps,
            self.race_manager.current_lap_time,
            self.race_manager.best_lap_time
        )

        self._draw_ui_overlays()

        pygame.display.flip()

    def _draw_finish_line(self, camera_x, camera_y):
        x1, y1 = self.race_manager.finish_line[0]
        x2, y2 = self.race_manager.finish_line[1]
        screen_x1 = x1 - camera_x
        screen_y1 = y1 - camera_y
        screen_x2 = x2 - camera_x
        screen_y2 = y2 - camera_y

        margin = 50
        if (min(screen_x1, screen_x2) < GameConfig.SCREEN_WIDTH + margin and
            max(screen_x1, screen_x2) > -margin and
            min(screen_y1, screen_y2) < GameConfig.SCREEN_HEIGHT + margin and
            max(screen_y1, screen_y2) > -margin):
            pygame.draw.line(self.screen, GameConfig.WHITE,
                             (screen_x1, screen_y1), (screen_x2, screen_y2), 10)

    def _draw_ui_overlays(self):
        large_font = pygame.font.Font(None, 72)

        if self.race_manager.is_countdown_active():
            countdown_text_str = self.race_manager.get_countdown_display()
            color = GameConfig.YELLOW if countdown_text_str != "START!" else GameConfig.GREEN
            countdown_text = large_font.render(countdown_text_str, True, color)
            text_rect = countdown_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2,
                                                         GameConfig.SCREEN_HEIGHT // 2))

            shadow = large_font.render(countdown_text_str, True, GameConfig.BLACK)
            shadow_rect = shadow.get_rect(center=(GameConfig.SCREEN_WIDTH // 2 + 3,
                                                 GameConfig.SCREEN_HEIGHT // 2 + 3))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(countdown_text, text_rect)

        if (not self.race_manager.race_started and
            not self.race_manager.is_countdown_active() and
            not self.race_manager.is_race_finished()):
            start_text = large_font.render("Kliknij SPACJE aby zacząć", True, GameConfig.YELLOW)
            text_rect = start_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2,
                                                     GameConfig.SCREEN_HEIGHT // 2))

            padding = 20
            box_rect = pygame.Rect(
                text_rect.left - padding,
                text_rect.top - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            pygame.draw.rect(self.screen, GameConfig.BLACK, box_rect)
            pygame.draw.rect(self.screen, GameConfig.YELLOW, box_rect, 3)
            self.screen.blit(start_text, text_rect)

        if self.race_manager.lap_message_timer > 0 and not self.race_manager.is_race_finished():
            lap_msg = large_font.render(
                f"OKRĄŻENIE {self.race_manager.laps}/{GameConfig.MAX_LAPS}",
                True, GameConfig.WHITE
            )
            text_rect = lap_msg.get_rect(center=(GameConfig.SCREEN_WIDTH // 2,
                                                 GameConfig.SCREEN_HEIGHT // 2))

            shadow = large_font.render(
                f"OKRĄŻENIE {self.race_manager.laps}/{GameConfig.MAX_LAPS}",
                True, GameConfig.BLACK
            )
            shadow_rect = shadow.get_rect(center=(GameConfig.SCREEN_WIDTH // 2 + 3,
                                                   GameConfig.SCREEN_HEIGHT // 2 + 3))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(lap_msg, text_rect)

        if self.race_manager.is_race_finished():
            self._draw_race_results()

    def _draw_race_results(self):
        overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("KONIEC!", True, GameConfig.YELLOW)
        title_rect = title_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        medium_font = pygame.font.Font(None, 48)
        y_offset = 220

        medal_colors = {
            1: (255, 215, 0),
            2: (192, 192, 192),
            3: (205, 127, 50)
        }

        for result in self.race_manager.race_results:
            position = result['position']
            name = result['name']
            time = result['finish_time']

            if position in medal_colors:
                color = medal_colors[position]
            else:
                color = GameConfig.WHITE

            result_text = f"{position}. {name:12s} - {time:.2f}s"
            text_surface = medium_font.render(result_text, True, color)
            text_rect = text_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)

            y_offset += 70

        restart_font = pygame.font.Font(None, 42)
        restart_text = restart_font.render("Kliknij SPACJE aby zagrać jeszcze raz",
                                           True, GameConfig.GREEN)
        restart_rect = restart_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2,
                                                     GameConfig.SCREEN_HEIGHT - 80))
        self.screen.blit(restart_text, restart_rect)

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