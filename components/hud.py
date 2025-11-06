import pygame
import math

class HUD:
    def __init__(self, screen_width, screen_height, track_width, track_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.track_width = track_width
        self.track_height = track_height

        self.minimap_width = 200
        self.minimap_height = 300
        self.minimap_x = screen_width - self.minimap_width - 20
        self.minimap_y = 20
        self.minimap_scale = min(self.minimap_width / track_width, self.minimap_height / track_height)

        self.minimap_surface = None
        self.minimap_border_color = (255, 255, 255)
        self.minimap_bg_color = (20, 20, 20, 200)

        self.speedo_x = 120
        self.speedo_y = screen_height - 120
        self.speedo_radius = 80
        self.speedo_bg_color = (30, 30, 30, 220)
        self.speedo_border_color = (100, 100, 100)
        self.speedo_needle_color = (255, 50, 50)
        self.speedo_text_color = (255, 255, 255)

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

    def generate_minimap(self, track):
        minimap_img = pygame.transform.scale(track.map_image,
            (int(self.track_width * self.minimap_scale), int(self.track_height * self.minimap_scale)))

        self.minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height), pygame.SRCALPHA)
        self.minimap_surface.fill(self.minimap_bg_color)
        img_rect = minimap_img.get_rect(center=(self.minimap_width // 2, self.minimap_height // 2))
        self.minimap_surface.blit(minimap_img, img_rect)

    def draw_minimap(self, surface, player_car, ai_cars):
        if self.minimap_surface is None:
            return

        surface.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))
        pygame.draw.rect(surface, self.minimap_border_color,
            (self.minimap_x, self.minimap_y, self.minimap_width, self.minimap_height), 2)

        center_offset_x = (self.minimap_width - self.track_width * self.minimap_scale) / 2
        center_offset_y = (self.minimap_height - self.track_height * self.minimap_scale) / 2

        for ai_car in ai_cars:
            minimap_car_x = self.minimap_x + center_offset_x + ai_car.x * self.minimap_scale
            minimap_car_y = self.minimap_y + center_offset_y + ai_car.y * self.minimap_scale
            pygame.draw.circle(surface, ai_car.color, (int(minimap_car_x), int(minimap_car_y)), 4)

        minimap_player_x = self.minimap_x + center_offset_x + player_car.x * self.minimap_scale
        minimap_player_y = self.minimap_y + center_offset_y + player_car.y * self.minimap_scale

        angle_rad = math.radians(player_car.angle)
        triangle_size = 6

        point1_x = minimap_player_x + math.sin(angle_rad) * triangle_size
        point1_y = minimap_player_y - math.cos(angle_rad) * triangle_size
        point2_x = minimap_player_x + math.sin(angle_rad + 2.5) * triangle_size * 0.6
        point2_y = minimap_player_y - math.cos(angle_rad + 2.5) * triangle_size * 0.6
        point3_x = minimap_player_x + math.sin(angle_rad - 2.5) * triangle_size * 0.6
        point3_y = minimap_player_y - math.cos(angle_rad - 2.5) * triangle_size * 0.6

        pygame.draw.polygon(surface, (255, 255, 0), [(point1_x, point1_y), (point2_x, point2_y), (point3_x, point3_y)])
        pygame.draw.polygon(surface, (255, 255, 255), [(point1_x, point1_y), (point2_x, point2_y), (point3_x, point3_y)], 2)

    def draw_speedometer(self, surface, speed, max_speed):
        pygame.draw.circle(surface, self.speedo_bg_color, (self.speedo_x, self.speedo_y), self.speedo_radius)
        pygame.draw.circle(surface, self.speedo_border_color, (self.speedo_x, self.speedo_y), self.speedo_radius, 3)

        start_angle = 225
        end_angle = -45
        speed_percent = min(abs(speed) / max_speed, 1.0)

        pygame.draw.arc(surface, (60, 60, 60),
            (self.speedo_x - self.speedo_radius + 10, self.speedo_y - self.speedo_radius + 10,
             (self.speedo_radius - 10) * 2, (self.speedo_radius - 10) * 2),
            math.radians(end_angle), math.radians(start_angle), 8)

        if speed_percent < 0.5:
            arc_color = (0, 255, 0)
        elif speed_percent < 0.8:
            arc_color = (255, 255, 0)
        else:
            arc_color = (255, 100, 0)

        arc_span = 270
        current_arc_angle = start_angle - (arc_span * speed_percent)

        if speed_percent > 0:
            pygame.draw.arc(surface, arc_color,
                (self.speedo_x - self.speedo_radius + 10, self.speedo_y - self.speedo_radius + 10,
                 (self.speedo_radius - 10) * 2, (self.speedo_radius - 10) * 2),
                math.radians(current_arc_angle), math.radians(start_angle), 8)

        speed_text = self.font_large.render(str(int(abs(speed))), True, self.speedo_text_color)
        speed_rect = speed_text.get_rect(center=(self.speedo_x, self.speedo_y - 10))
        surface.blit(speed_text, speed_rect)

        unit_text = self.font_small.render("km/h", True, (180, 180, 180))
        unit_rect = unit_text.get_rect(center=(self.speedo_x, self.speedo_y + 20))
        surface.blit(unit_text, unit_rect)

        if speed < 0:
            reverse_text = self.font_small.render("R", True, (255, 50, 50))
            reverse_rect = reverse_text.get_rect(center=(self.speedo_x, self.speedo_y - 40))
            surface.blit(reverse_text, reverse_rect)

    def draw_lap_counter(self, surface, laps):
        x, y = 20, 20
        panel_width, panel_height = 150, 60
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((30, 30, 30, 220))
        surface.blit(panel_surface, (x, y))

        pygame.draw.rect(surface, (100, 100, 100), (x, y, panel_width, panel_height), 2)

        lap_label = self.font_small.render("Okrążenie:", True, (180, 180, 180))
        surface.blit(lap_label, (x + 10, y + 8))

        lap_number = self.font_large.render(str(laps), True, (255, 255, 255))
        surface.blit(lap_number, (x + 10, y + 25))

    def draw_lap_timer(self, surface, current_time, best_time):
        x, y = 20, 90
        panel_width, panel_height = 220, 80
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((30, 30, 30, 220))
        surface.blit(panel_surface, (x, y))

        pygame.draw.rect(surface, (100, 100, 100), (x, y, panel_width, panel_height), 2)

        current_label = self.font_small.render("Czas", True, (180, 180, 180))
        surface.blit(current_label, (x + 10, y + 8))

        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        milliseconds = int((current_time % 1) * 1000)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        current_time_text = self.font_medium.render(time_str, True, (255, 255, 255))
        surface.blit(current_time_text, (x + 10, y + 28))

        if best_time is not None:
            best_label = self.font_small.render("Best", True, (180, 180, 180))
            surface.blit(best_label, (x + 10, y + 55))

            best_minutes = int(best_time // 60)
            best_seconds = int(best_time % 60)
            best_milliseconds = int((best_time % 1) * 1000)
            best_time_str = f"{best_minutes:02d}:{best_seconds:02d}.{best_milliseconds:03d}"

            best_time_text = self.font_small.render(best_time_str, True, (255, 215, 0))
            surface.blit(best_time_text, (x + 65, y + 55))

    def draw_active_effects(self, surface, car):
        if not hasattr(car, 'active_effects') or not car.active_effects:
            return

        x = self.screen_width - 200
        y = self.screen_height - 200

        for i, effect in enumerate(car.active_effects):
            effect_y = y + i * 50

            panel_width, panel_height = 180, 45
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

            if effect['type'] == 'boost':
                panel_surface.fill((50, 100, 50, 220))
                border_color = (0, 255, 0)
                effect_name = "SPEED BOOST"
            elif effect['type'] == 'slow':
                panel_surface.fill((100, 50, 50, 220))
                border_color = (255, 100, 0)
                effect_name = "SLOWED"
            else:
                panel_surface.fill((50, 50, 50, 220))
                border_color = (150, 150, 150)
                effect_name = "EFFECT"

            surface.blit(panel_surface, (x, effect_y))
            pygame.draw.rect(surface, border_color, (x, effect_y, panel_width, panel_height), 2)

            name_text = self.font_small.render(effect_name, True, (255, 255, 255))
            surface.blit(name_text, (x + 10, effect_y + 5))

            timer_ratio = min(1.0, effect['timer'] / 5.0)
            bar_width = int((panel_width - 20) * timer_ratio)
            bar_height = 8
            bar_y = effect_y + panel_height - bar_height - 5

            pygame.draw.rect(surface, (50, 50, 50), (x + 10, bar_y, panel_width - 20, bar_height))
            pygame.draw.rect(surface, border_color, (x + 10, bar_y, bar_width, bar_height))

            time_text = self.font_small.render(f"{effect['timer']:.1f}s", True, (200, 200, 200))
            surface.blit(time_text, (x + 10, effect_y + 22))

    def draw(self, surface, player_car, ai_cars, laps, current_lap_time=0.0, best_lap_time=None):
        self.draw_speedometer(surface, player_car.speed, player_car.max_speed)
        self.draw_minimap(surface, player_car, ai_cars)
        self.draw_lap_counter(surface, laps)
        self.draw_lap_timer(surface, current_lap_time, best_lap_time)
        self.draw_active_effects(surface, player_car)