# PyRace

A 2D racing game built with Pygame featuring AI opponents, power-ups, and competitive lap-based racing.

## Features

- **Player vs AI Racing**: Compete against 3 AI opponents with dynamic racing lines
- **Power-up System**: Collect speed boosts (⭐) and avoid oil slicks
- **Lap Tracking**: Cross the finish line to complete laps with real-time timing
- **Dynamic Camera**: Smooth camera following with collision shake effects
- **Sound Effects**: Engine sounds, collisions, and power-up audio
- **HUD**: Real-time speedometer, minimap, lap counter, and lap times

## Controls

- **Arrow Keys / WASD**: Accelerate, brake/reverse, and steer
- **Space**: Brake (during race), Start race, Restart after finish
- **Escape**: Quit game

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PyRace.git
cd PyRace
```

2. Install dependencies:
```bash
pip install pygame
```

3. Run the game:
```bash
cd PyRace
python main.py
```

## Game Structure

```
PyRace/
   ├── main.py              # Game entry point
   ├── components/          # Game components (Car, Track, AI, PowerUps, HUD)
   ├── game/                # Game systems (RaceManager, CollisionManager, Camera)
   └── assets/              # Images and sounds
```

## Gameplay

1. Press **SPACE** to start the countdown
2. Race for **2 laps** on the track
3. Collect **yellow stars** for speed boosts
4. Avoid **dark puddles** (oil slicks) that slow you down
5. First to complete all laps wins!

## Technologies

- **Python 3.x**
- **Pygame**
