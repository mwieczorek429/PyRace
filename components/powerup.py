import pygame
import math
import random

class PowerUp:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.respawn_timer = 0.0
        self.respawn_delay = 10.0

    def check_collision(self, car):
        if not self.active:
            return False
        dx = car.x - self.x
        dy = car.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (self.radius + min(car.width, car.height) / 3)

    def apply_effect(self, car):
        pass

    def collect(self, car):
        if self.active:
            self.apply_effect(car)
            self.active = False
            self.respawn_timer = self.respawn_delay

    def update(self, dt):
        if not self.active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.active = True
                self.respawn_timer = 0.0

    def draw(self, surface, camera_x=0, camera_y=0):
        pass

class Hazard(PowerUp):
    def __init__(self, x, y, radius=25):
        super().__init__(x, y, radius)
        self.slow_factor = 0.25
        self.effect_duration = 3.0

    def apply_effect(self, car):
        if not hasattr(car, 'active_effects'):
            car.active_effects = []
        car.active_effects = [e for e in car.active_effects if e['type'] != 'slow']
        car.active_effects.append({
            'type': 'slow',
            'factor': self.slow_factor,
            'timer': self.effect_duration
        })

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.active:
            return

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if not hasattr(self, '_oil_points'):
            self._oil_points = []
            num_points = 12
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                radius_variation = random.uniform(0.7, 1.0)
                r = self.radius * radius_variation
                angle_offset = random.uniform(-0.2, 0.2)
                px = self.x + math.cos(angle + angle_offset) * r
                py = self.y + math.sin(angle + angle_offset) * r
                self._oil_points.append((px, py))

            self._oil_reflections = []
            colors = [(60, 40, 80), (40, 60, 80), (50, 70, 60), (70, 60, 90)]
            for i in range(8):
                offset_x = random.randint(-int(self.radius * 0.4), int(self.radius * 0.4))
                offset_y = random.randint(-int(self.radius * 0.4), int(self.radius * 0.4))
                color = random.choice(colors)
                size = random.randint(2, 4)
                self._oil_reflections.append({
                    'x': self.x + offset_x,
                    'y': self.y + offset_y,
                    'color': color,
                    'size': size
                })

        screen_points = [(int(px - camera_x), int(py - camera_y)) for px, py in self._oil_points]
        pygame.draw.polygon(surface, (15, 15, 20), screen_points)

        highlight_points = [
            (int(screen_x + (px - screen_x) * 0.5), int(screen_y + (py - screen_y) * 0.5))
            for px, py in screen_points
        ]
        pygame.draw.polygon(surface, (40, 30, 50), highlight_points)

        for reflection in self._oil_reflections:
            screen_refl_x = int(reflection['x'] - camera_x)
            screen_refl_y = int(reflection['y'] - camera_y)
            pygame.draw.circle(surface, reflection['color'], (screen_refl_x, screen_refl_y), reflection['size'])

class SpeedBoost(PowerUp):
    def __init__(self, x, y, radius=20):
        super().__init__(x, y, radius)
        self.boost_factor = 1.4
        self.effect_duration = 5.0
        self.respawn_delay = 15.0

    def apply_effect(self, car):
        if not hasattr(car, 'active_effects'):
            car.active_effects = []
        car.active_effects = [e for e in car.active_effects if e['type'] != 'boost']
        car.active_effects.append({
            'type': 'boost',
            'factor': self.boost_factor,
            'timer': self.effect_duration
        })

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.active:
            return

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        glow_radius = self.radius + 5 + int(math.sin(pygame.time.get_ticks() / 200) * 3)
        for i in range(3):
            alpha = 50 - i * 15
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 0, alpha), (glow_radius, glow_radius), glow_radius - i * 3)
            surface.blit(glow_surf, (int(screen_x - glow_radius), int(screen_y - glow_radius)))

        points = []
        num_points = 8
        for i in range(num_points * 2):
            angle = (i * math.pi / num_points) - math.pi / 2
            r = self.radius if i % 2 == 0 else self.radius * 0.5
            px = screen_x + math.cos(angle) * r
            py = screen_y + math.sin(angle) * r
            points.append((px, py))

        pygame.draw.polygon(surface, (255, 215, 0), points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        pygame.draw.circle(surface, (255, 165, 0), (int(screen_x), int(screen_y)), int(self.radius * 0.3))

def spawn_powerups_on_racing_line(racing_line, num_hazards=8, num_boosts=5):
    powerups = []
    if not racing_line or len(racing_line) < num_hazards + num_boosts:
        return powerups

    available_indices = list(range(len(racing_line)))
    random.shuffle(available_indices)
    used_positions = []
    min_distance = 200

    def is_position_valid(x, y):
        for px, py in used_positions:
            dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
            if dist < min_distance:
                return False
        return True

    hazards_spawned = 0
    for idx in available_indices:
        if hazards_spawned >= num_hazards:
            break
        base_x, base_y = racing_line[idx]
        offset_range = 30
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        x = base_x + offset_x
        y = base_y + offset_y
        if is_position_valid(x, y):
            powerups.append(Hazard(x, y))
            used_positions.append((x, y))
            hazards_spawned += 1

    boosts_spawned = 0
    for idx in available_indices:
        if boosts_spawned >= num_boosts:
            break
        base_x, base_y = racing_line[idx]
        offset_range = 30
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        x = base_x + offset_x
        y = base_y + offset_y
        if is_position_valid(x, y):
            powerups.append(SpeedBoost(x, y))
            used_positions.append((x, y))
            boosts_spawned += 1

    return powerups

def spawn_powerups_on_track(track, num_hazards=8, num_boosts=5):
    racing_line = track.get_racing_line()
    return spawn_powerups_on_racing_line(racing_line, num_hazards, num_boosts)