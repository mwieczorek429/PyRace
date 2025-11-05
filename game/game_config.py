import json
from pathlib import Path

class GameConfig:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 60
    TITLE = "PyRace"

    MAX_LAPS = 2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    ENGINE_SOUND_MIN_INTERVAL = 5.0
    ENGINE_SOUND_MAX_INTERVAL = 15.0

    @staticmethod
    def load_spawn_positions():
        spawn_file = Path(__file__).parent.parent / "spawn_positions.json"

        default_spawn = {
            "player": {"x": 2180, "y": 4700},
            "ai_cars": [],
            "finish_line": None
        }

        if not spawn_file.exists():
            print(f"Ostrzeżenie: Plik {spawn_file} nie znaleziony. Używam domyślnej pozycji startowej.")
            return default_spawn

        try:
            with open(spawn_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Błąd ładowania spawn_positions.json: {e}. Używam domyślnej pozycji.")
            return default_spawn