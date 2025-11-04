import pygame
import math
import random

class Particle:
    def __init__(self, x, y, vx, vy, size, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.initial_size = size
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95
        self.vy *= 0.95
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.alive:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        life_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * life_ratio)
        current_size = int(self.initial_size * life_ratio)
        if current_size < 1:
            current_size = 1

        particle_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surf, color_with_alpha, (current_size, current_size), current_size)
        surface.blit(particle_surf, (screen_x - current_size, screen_y - current_size))

class CollisionEffect:
    def __init__(self, x, y, num_particles=15):
        self.particles = []
        self.alive = True

        for i in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 250)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(4, 10)
            color_value = random.randint(200, 255)
            color = (color_value, color_value, color_value)
            lifetime = random.uniform(0.3, 0.6)
            particle = Particle(x, y, vx, vy, size, color, lifetime)
            self.particles.append(particle)

        for i in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 100)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(12, 18)
            color_value = random.randint(150, 200)
            color = (color_value, color_value, color_value)
            lifetime = random.uniform(0.5, 0.8)
            particle = Particle(x, y, vx, vy, size, color, lifetime)
            self.particles.append(particle)

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        if len(self.particles) == 0:
            self.alive = False

    def draw(self, surface, camera_x=0, camera_y=0):
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)

class EffectManager:
    def __init__(self):
        self.effects = []

    def add_collision_effect(self, x, y, num_particles=15):
        effect = CollisionEffect(x, y, num_particles)
        self.effects.append(effect)

    def update(self, dt):
        for effect in self.effects:
            effect.update(dt)
        self.effects = [e for e in self.effects if e.alive]

    def draw(self, surface, camera_x=0, camera_y=0):
        for effect in self.effects:
            effect.draw(surface, camera_x, camera_y)

    def clear(self):
        self.effects = []