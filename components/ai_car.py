import math
from .car import Car

class AICar(Car):
    def __init__(self, x, y, waypoints, color=(0, 0, 255), ai_speed=1000, racing_line_offset=0):
        super().__init__(x, y, color)
        self.base_waypoints = waypoints
        self.racing_line_offset = racing_line_offset
        self.waypoints = self._apply_offset_to_waypoints(waypoints, racing_line_offset)
        self.current_waypoint = 0
        self.ai_base_speed = ai_speed
        self.ai_target_speed = ai_speed
        self.waypoint_threshold = 30

    def _apply_offset_to_waypoints(self, waypoints, offset):
        if offset == 0:
            return waypoints

        offset_waypoints = []
        for i, (wx, wy) in enumerate(waypoints):
            next_i = (i + 1) % len(waypoints)
            next_x, next_y = waypoints[next_i]

            dx = next_x - wx
            dy = next_y - wy
            length = math.sqrt(dx * dx + dy * dy)

            if length > 0:
                perp_x = -dy / length
                perp_y = dx / length
                new_x = wx + perp_x * offset
                new_y = wy + perp_y * offset
                offset_waypoints.append((int(new_x), int(new_y)))
            else:
                offset_waypoints.append((wx, wy))

        return offset_waypoints

    def update(self, dt):
        if self.stunned:
            self.stun_timer -= dt
            self.speed = self.stun_reverse_speed
            if self.stun_timer <= 0:
                self.stunned = False
                self.stun_timer = 0
                self.speed = 0
        else:
            self._ai_navigate(dt)

        angle_rad = math.radians(self.angle)
        self.x += math.sin(angle_rad) * self.speed * dt
        self.y -= math.cos(angle_rad) * self.speed * dt

    def _ai_navigate(self, dt):
        if not self.waypoints:
            return

        target_x, target_y = self.waypoints[self.current_waypoint]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.waypoint_threshold:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
            target_x, target_y = self.waypoints[self.current_waypoint]
            dx = target_x - self.x
            dy = target_y - self.y

        target_angle = math.degrees(math.atan2(dx, -dy))
        angle_diff = target_angle - self.angle

        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        turn_amount = self.turn_speed * dt
        if abs(angle_diff) < turn_amount:
            self.angle = target_angle
        elif angle_diff > 0:
            self.angle += turn_amount
        else:
            self.angle -= turn_amount

        if self.speed < self.ai_target_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.ai_target_speed)
        elif self.speed > self.ai_target_speed:
            self.speed = max(self.speed - self.friction * dt, self.ai_target_speed)

        if abs(angle_diff) > 45:
            target_corner_speed = self.ai_target_speed * 0.2
            if self.speed > target_corner_speed:
                self.speed = max(self.speed - self.brake_force * dt * 0.2, target_corner_speed)
        elif abs(angle_diff) > 25:
            target_corner_speed = self.ai_target_speed * 0.4
            if self.speed > target_corner_speed:
                self.speed = max(self.speed - self.friction * dt * 1.5, target_corner_speed)