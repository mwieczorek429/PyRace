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

    def get_racing_line(self):
        return [
            (2093, 4787), (1121, 4791), (845, 4718), (744, 4506), (809, 4216),
            (1063, 3922), (1991, 2962), (2012, 2745), (1904, 2525), (1439, 2285),
            (1045, 2070), (936, 1780), (966, 1458), (1228, 1160), (1548, 1031),
            (2197, 1028), (2838, 1071), (3110, 1208), (3269, 1493), (3296, 1765),
            (3166, 2088), (2922, 2245), (2698, 2285), (2513, 2298), (2487, 2442),
            (2572, 2716), (2669, 3018), (2925, 3589), (3335, 3901), (3458, 4177),
            (3433, 4478), (3276, 4692), (2953, 4799), (2489, 4793), (2099, 4785)
        ]