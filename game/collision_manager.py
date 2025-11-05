from components import collision
from components import powerup 

class CollisionManager:

    def __init__(self, track, effect_manager, sound_manager): 
        self.track = track
        self.effect_manager = effect_manager
        self.sound_manager = sound_manager 

    def update(self, player_car, ai_cars, powerups):
        camera_shake_intensity = 0

        shake = self._handle_car_track_collision(player_car)
        camera_shake_intensity = max(camera_shake_intensity, shake)

        for ai_car in ai_cars:
            self._handle_car_track_collision(ai_car)

        self._handle_powerup_collisions(player_car, ai_cars, powerups)

        for ai_car in ai_cars:
            if collision.check_car_collision(player_car, ai_car):
                collision.handle_car_collision(player_car, ai_car)
                collision_x = (player_car.x + ai_car.x) / 2
                collision_y = (player_car.y + ai_car.y) / 2
                self.effect_manager.add_collision_effect(collision_x, collision_y, num_particles=15)
                self.sound_manager.play_collision() 
                camera_shake_intensity = max(camera_shake_intensity, 2.0)

        for i, ai_car1 in enumerate(ai_cars):
            for ai_car2 in ai_cars[i+1:]:
                if collision.check_car_collision(ai_car1, ai_car2):
                    collision.handle_car_collision(ai_car1, ai_car2)
                    collision_x = (ai_car1.x + ai_car2.x) / 2
                    collision_y = (ai_car1.y + ai_car2.y) / 2
                    self.effect_manager.add_collision_effect(collision_x, collision_y, num_particles=15)
                    self.sound_manager.play_collision()

        return camera_shake_intensity

    def _handle_car_track_collision(self, car):
        if collision.check_collision(car, self.track):
            collision.handle_collision(car, self.track)
            self.effect_manager.add_collision_effect(car.x, car.y, num_particles=8)
            self.sound_manager.play_collision() 
            return 2.0

        return 0

    def _handle_powerup_collisions(self, player_car, ai_cars, powerups):
        for pu in powerups:
            if pu.check_collision(player_car):
                if isinstance(pu, powerup.Hazard):
                    self.sound_manager.play_power_down()
                elif isinstance(pu, powerup.SpeedBoost):
                    self.sound_manager.play_power_up()
                pu.collect(player_car)

            for ai_car in ai_cars:
                if pu.check_collision(ai_car):
                    if isinstance(pu, powerup.Hazard):
                        self.sound_manager.play_power_down()
                    elif isinstance(pu, powerup.SpeedBoost):
                        self.sound_manager.play_power_up()
                    pu.collect(ai_car)