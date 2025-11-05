import math

class RaceManager:
    """Manages race state, lap tracking, and race results."""

    def __init__(self, max_laps, sound_manager): 
        self.max_laps = max_laps
        self.sound_manager = sound_manager 

        self.race_started = False
        self.countdown_active = False
        self.countdown_time = 1.0
        self.countdown_timer = 0.0
        self.race_finished = False

        self.finish_line = None

        self.laps = 0
        self.last_side = None
        self.lap_message_timer = 0
        self.lap_cooldown_timer = 0

        self.current_lap_time = 0.0
        self.best_lap_time = None
        self.lap_timer_running = False
        self.total_race_time = 0.0

        self.ai_lap_data = {}
        self.race_results = []

    def set_finish_line(self, finish_line):
        self.finish_line = finish_line

    def init_ai_lap_data(self, ai_cars):
        self.ai_lap_data = {}
        for i, ai_car in enumerate(ai_cars):
            self.ai_lap_data[ai_car] = {
                'laps': 0,
                'last_side': None,
                'cooldown_timer': 0,
                'finished': False,
                'finish_time': None,
                'name': f"AI {i+1}"
            }

    def start_countdown(self):
        self.countdown_active = True
        self.countdown_timer = self.countdown_time
        # Nowe wywołanie
        if self.sound_manager:
            self.sound_manager.play_race_counter()

    def update(self, dt, player_car, ai_cars):
        if self.countdown_active:
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self.countdown_active = False
                self.race_started = True
                self.lap_timer_running = True
                self.current_lap_time = 0.0

                if self.finish_line:
                    self._initialize_last_sides(player_car, ai_cars)

        if self.lap_timer_running:
            self.current_lap_time += dt
            self.total_race_time += dt

        if self.lap_message_timer > 0:
            self.lap_message_timer -= dt

        if self.lap_cooldown_timer > 0:
            self.lap_cooldown_timer -= dt

        if self.race_started and self.finish_line:
            self._track_player_lap(player_car, dt)

        if self.race_started and self.finish_line and not self.race_finished:
            self._track_ai_laps(ai_cars, dt)

    def _initialize_last_sides(self, player_car, ai_cars):
        if not self.finish_line:
            return

        x1, y1 = self.finish_line[0]
        x2, y2 = self.finish_line[1]
        dx = x2 - x1
        dy = y2 - y1

        cross = dx * (player_car.y - y1) - dy * (player_car.x - x1)
        self.last_side = 1 if cross > 0 else -1

        for ai_car in ai_cars:
            ai_data = self.ai_lap_data.get(ai_car)
            if ai_data:
                cross = dx * (ai_car.y - y1) - dy * (ai_car.x - x1)
                ai_data['last_side'] = 1 if cross > 0 else -1

    def _track_player_lap(self, player_car, dt):
        x1, y1 = self.finish_line[0]
        x2, y2 = self.finish_line[1]
        car_x, car_y = player_car.x, player_car.y

        dx = x2 - x1
        dy = y2 - y1
        line_length_sq = dx * dx + dy * dy

        if line_length_sq > 0:
            t = max(0, min(1, ((car_x - x1) * dx + (car_y - y1) * dy) / line_length_sq))
            nearest_x = x1 + t * dx
            nearest_y = y1 + t * dy

            dist_x = car_x - nearest_x
            dist_y = car_y - nearest_y
            distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)

            crossing_threshold = 80

            if distance < crossing_threshold:
                cross = dx * (car_y - y1) - dy * (car_x - x1)
                current_side = 1 if cross > 0 else -1

                if (self.last_side is not None and
                    self.last_side != current_side and
                    self.lap_cooldown_timer <= 0):

                    self.laps += 1
                    self.lap_message_timer = 2.0
                    self.lap_cooldown_timer = 5.0

                    if self.lap_timer_running and self.laps > 1:
                        if self.best_lap_time is None or self.current_lap_time < self.best_lap_time:
                            self.best_lap_time = self.current_lap_time

                    if self.laps > self.max_laps:
                        self.race_results.append({
                            'name': 'PLAYER',
                            'finish_time': self.total_race_time,
                            'position': None
                        })

                        self._finalize_ai_results()
                        self.finish_race()

                    self.current_lap_time = 0.0

                self.last_side = current_side

    def _track_ai_laps(self, ai_cars, dt):
        if not self.finish_line:
            return

        x1, y1 = self.finish_line[0]
        x2, y2 = self.finish_line[1]
        dx = x2 - x1
        dy = y2 - y1
        line_length_sq = dx * dx + dy * dy

        for ai_car in ai_cars:
            ai_data = self.ai_lap_data.get(ai_car)
            if not ai_data or ai_data['finished']:
                continue

            if ai_data['cooldown_timer'] > 0:
                ai_data['cooldown_timer'] -= dt

            car_x, car_y = ai_car.x, ai_car.y

            if line_length_sq > 0:
                t = max(0, min(1, ((car_x - x1) * dx + (car_y - y1) * dy) / line_length_sq))
                nearest_x = x1 + t * dx
                nearest_y = y1 + t * dy

                dist_x = car_x - nearest_x
                dist_y = car_y - nearest_y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)

                crossing_threshold = 80

                if distance < crossing_threshold:
                    cross = dx * (car_y - y1) - dy * (car_x - x1)
                    current_side = 1 if cross > 0 else -1

                    if (ai_data['last_side'] is not None and
                        ai_data['last_side'] != current_side and
                        ai_data['cooldown_timer'] <= 0):

                        ai_data['laps'] += 1
                        ai_data['cooldown_timer'] = 5.0

                        if ai_data['laps'] > self.max_laps:
                            ai_data['finished'] = True
                            ai_data['finish_time'] = self.total_race_time

                    ai_data['last_side'] = current_side

    def _finalize_ai_results(self):
        for ai_car in self.ai_lap_data:
            ai_data = self.ai_lap_data.get(ai_car)
            if not ai_data:
                continue

            if ai_data['finished'] and ai_data['finish_time'] is not None:
                finish_time = ai_data['finish_time']
            else:
                laps_completed = ai_data['laps']
                laps_behind = self.max_laps - laps_completed
                penalty_time = max(0, laps_behind) * 60.0
                finish_time = self.total_race_time + penalty_time

            self.race_results.append({
                'name': ai_data['name'],
                'finish_time': finish_time,
                'position': None
            })

    def finish_race(self):
        self.race_finished = True
        self.race_started = False
        self.lap_timer_running = False

        self.race_results.sort(key=lambda x: x['finish_time'])

        for i, result in enumerate(self.race_results):
            result['position'] = i + 1

    def reset(self):
        self.race_started = False
        self.countdown_active = False
        self.countdown_timer = 0.0
        self.race_finished = False

        self.laps = 0
        self.last_side = None
        self.lap_message_timer = 0
        self.lap_cooldown_timer = 0

        self.current_lap_time = 0.0
        self.best_lap_time = None
        self.lap_timer_running = False
        self.total_race_time = 0.0

        self.race_results = []
        self.ai_lap_data = {}

    def is_race_active(self):
        return self.race_started and not self.race_finished

    def is_countdown_active(self):
        return self.countdown_active

    def is_race_finished(self):
        return self.race_finished

    def get_countdown_display(self):
        countdown_num = int(self.countdown_timer) + 1
        if countdown_num > 0:
            return str(countdown_num)
        else:
            return "START!"