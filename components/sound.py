import pygame
from pathlib import Path

class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sounds_path = Path(__file__).parent.parent / "assets" / "sounds"
        self.sounds = {}
        self._load_sounds()

        self.sfx_volume = 0.5
        self.music_volume = 0.3
        self._apply_volumes()

    def _load_sounds(self):
        sound_files = {
            'collision': 'car_colision.mp3',
            'power_up': 'power_up.mp3',
            'power_down': 'power_down.mp3',
            'race_counter': 'race_counter.mp3',
            'engine': 'engine.mp3',
        }

        for sound_name, filename in sound_files.items():
            sound_path = self.sounds_path / filename
            if sound_path.exists():
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
                except Exception as e:
                    self.sounds[sound_name] = None
            else:
                self.sounds[sound_name] = None

    def _apply_volumes(self):
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sfx_volume)

    def play_collision(self):
        if self.sounds.get('collision'):
            self.sounds['collision'].play()

    def play_power_up(self):
        if self.sounds.get('power_up'):
            self.sounds['power_up'].play()

    def play_power_down(self):
        if self.sounds.get('power_down'):
            self.sounds['power_down'].play()

    def play_race_counter(self):
        if self.sounds.get('race_counter'):
            self.sounds['race_counter'].play()

    def play_engine(self):
        if self.sounds.get('engine'):
            self.sounds['engine'].play()

    def play_music(self, loop=True):
        music_path = self.sounds_path / "theme.mp3"
        if music_path.exists():
            try:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
            except Exception as e:
                pass

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def cleanup(self):
        self.stop_music()