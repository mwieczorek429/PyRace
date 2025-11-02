import json
from pathlib import Path

class GameConfig:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 60
    TITLE = "PyRace"

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    @staticmethod
    def load_spawn_positions():
        spawn_file = Path(__file__).parent.parent / "spawn_positions.json"

        default_spawn = {"player": {"x": 2180, "y": 4700}}

        if not spawn_file.exists():
            print(f"Ostrzeżenie: Plik {spawn_file} nie znaleziony. Używam domyślnej pozycji startowej.")
            return default_spawn

        try:
            with open(spawn_file, 'r') as f:
                data = json.load(f)
                # Wczytujemy tylko dane gracza, ignorujemy resztę
                if "player" in data:
                    return {"player": data["player"]}
                else:
                    return default_spawn
        except Exception as e:
            print(f"Błąd ładowania spawn_positions.json: {e}. Używam domyślnej pozycji.")
            return default_spawn