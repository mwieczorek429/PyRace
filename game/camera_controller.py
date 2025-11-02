import random

class CameraController:

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera_x = 0
        self.camera_y = 0
        self.camera_smoothness = 5.0

    def update(self, target_x, target_y, dt):
        target_camera_x = target_x - self.screen_width // 2
        target_camera_y = target_y - self.screen_height // 2

        lerp_factor = min(1.0, self.camera_smoothness * dt)
        self.camera_x += (target_camera_x - self.camera_x) * lerp_factor
        self.camera_y += (target_camera_y - self.camera_y) * lerp_factor

    def get_camera_offset(self):
        return self.camera_x, self.camera_y

    def get_camera_position(self):
        return self.camera_x, self.camera_y