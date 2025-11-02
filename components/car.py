import pygame
import math
from pathlib import Path

class Car:
    def __init__(self, x, y, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.color = color

        sprite_path = Path(__file__).parent.parent / "assets" / "images" / "bolid.png"
        loaded_sprite = pygame.image.load(str(sprite_path)).convert_alpha()

        scale_factor = 0.055
        new_width = int(loaded_sprite.get_width() * scale_factor)
        new_height = int(loaded_sprite.get_height() * scale_factor)
        scaled_sprite = pygame.transform.scale(loaded_sprite, (new_width, new_height))
        self.original_sprite = pygame.transform.rotate(scaled_sprite, 180)

        self.width = self.original_sprite.get_width()
        self.height = self.original_sprite.get_height()

        self.angle = 0
        self.speed = 0
        self.max_speed = 400
        self.acceleration = 200
        self.friction = 100
        self.brake_force = 500
        self.turn_speed = 180

    def handle_input(self, keys, dt):
        if keys[pygame.K_SPACE]:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.brake_force * dt)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.brake_force * dt)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration * dt, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration * dt, -self.max_speed / 2)
        else:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.friction * dt)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.friction * dt)

        if abs(self.speed) > 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle -= self.turn_speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle += self.turn_speed * dt

    def update(self, dt):
        angle_rad = math.radians(self.angle)
        self.x += math.sin(angle_rad) * self.speed * dt
        self.y -= math.cos(angle_rad) * self.speed * dt

    def draw(self, surface, camera_x=0, camera_y=0):
        rotated_car = pygame.transform.rotate(self.original_sprite, -self.angle)
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        rotated_rect = rotated_car.get_rect(center=(screen_x, screen_y))
        surface.blit(rotated_car, rotated_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)