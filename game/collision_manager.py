from components import collision

class CollisionManager:

    def __init__(self, track, effect_manager):
        self.track = track
        self.effect_manager = effect_manager

    def update(self, player_car, ai_cars, powerups):
        camera_shake_intensity = 0

        shake = self._handle_car_track_collision(player_car)
        camera_shake_intensity = max(camera_shake_intensity, shake)

        for ai_car in ai_cars:
            self._handle_car_track_collision(ai_car)


        for ai_car in ai_cars:
            if collision.check_car_collision(player_car, ai_car):
                collision.handle_car_collision(player_car, ai_car)
                collision_x = (player_car.x + ai_car.x) / 2
                collision_y = (player_car.y + ai_car.y) / 2
                self.effect_manager.add_collision_effect(collision_x, collision_y, num_particles=15)
                camera_shake_intensity = max(camera_shake_intensity, 2.0)

        for i, ai_car1 in enumerate(ai_cars):
            for ai_car2 in ai_cars[i+1:]:
                if collision.check_car_collision(ai_car1, ai_car2):
                    collision.handle_car_collision(ai_car1, ai_car2)
                    collision_x = (ai_car1.x + ai_car2.x) / 2
                    collision_y = (ai_car1.y + ai_car2.y) / 2
                    self.effect_manager.add_collision_effect(collision_x, collision_y, num_particles=15)

        return camera_shake_intensity

    def _handle_car_track_collision(self, car):
        if collision.check_collision(car, self.track):
            collision.handle_collision(car, self.track)
            self.effect_manager.add_collision_effect(car.x, car.y, num_particles=8)
            return 2.0
        
        
        return 0