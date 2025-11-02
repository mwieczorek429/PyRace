import pygame
from pathlib import Path

class Track:
    def __init__(self, width, height):
        map_path = Path(__file__).parent.parent / "assets" / "images" / "map.png"
        original_map = pygame.image.load(str(map_path)).convert_alpha()

        self.scale_factor = 4
        scaled_width = original_map.get_width() * self.scale_factor
        scaled_height = original_map.get_height() * self.scale_factor
        self.map_image = pygame.transform.scale(original_map, (scaled_width, scaled_height))

        self.width = self.map_image.get_width()
        self.height = self.map_image.get_height()

    def draw(self, surface, camera_x=0, camera_y=0):
        surface.blit(self.map_image, (-camera_x, -camera_y))

    def is_on_track(self, x, y):
        map_x = int(x)
        map_y = int(y)

        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return False

        try:
            color = self.map_image.get_at((map_x, map_y))
            r, g, b = color[:3]

            if g > 100 and g > r + 20 and g > b + 20:
                return False
            if r < 150 and g < 150 and b < 150:
                return True
            if r > 150 and g > 100 and b < 100:
                return True
            return False
        except:
            return False