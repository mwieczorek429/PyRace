import pygame
import math
from pathlib import Path

class Car:
    def __init__(self, x, y, color=(255, 0, 0), sprite_name="bolid.png"):
        self.x = x
        self.y = y
        self.color = color

        sprite_path = Path(__file__).parent.parent / "assets" / "images" / sprite_name
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

        self.stunned = False
        self.stun_timer = 0.0
        self.stun_duration = 0.1
        self.reverse_speed = -150
        self.stun_reverse_speed = 0

        self.active_effects = []

    def handle_input(self, keys, dt):
        if self.stunned:
            return

        effective_max_speed = self.get_effective_max_speed()

        if keys[pygame.K_SPACE]:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.brake_force * dt)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.brake_force * dt)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration * dt, effective_max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration * dt, -effective_max_speed / 2)
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

    def update_effects(self, dt):
        self.active_effects = [
            {**effect, 'timer': effect['timer'] - dt}
            for effect in self.active_effects
            if effect['timer'] > dt
        ]

    def get_effective_max_speed(self):
        effective_speed = self.max_speed
        for effect in self.active_effects:
            if effect['type'] == 'boost':
                effective_speed *= effect['factor']
            elif effect['type'] == 'slow':
                effective_speed *= effect['factor']
        return effective_speed

    def update(self, dt):
        self.update_effects(dt)

        if self.stunned:
            self.stun_timer -= dt
            self.speed = self.stun_reverse_speed
            if self.stun_timer <= 0:
                self.stunned = False
                self.stun_timer = 0
                self.speed = 0

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

    def apply_stun(self):
        if not self.stunned:
            self.stunned = True
            if self.speed >= 0:
                self.stun_timer = self.stun_duration
                self.stun_reverse_speed = self.reverse_speed
            else:
                self.stun_timer = self.stun_duration * 0.6
                self.stun_reverse_speed = -self.reverse_speed * 0.7