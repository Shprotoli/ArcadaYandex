from dataclasses import dataclass
from typing import List, Tuple
import arcade
from settings import TILE, MAP_COLS, MAP_ROWS, MAP_WIDTH, MAP_HEIGHT

@dataclass(frozen=True)
class LevelData:
    walls: List[Tuple[int, int]]
    coins: List[Tuple[int, int]]

def _grid_to_world(c, r):
    return c * TILE + TILE / 2, r * TILE + TILE / 2

def build_level(level):
    border = []
    for c in range(MAP_COLS):
        border.append((c, 0))
        border.append((c, MAP_ROWS - 1))
    for r in range(MAP_ROWS):
        border.append((0, r))
        border.append((MAP_COLS - 1, r))

    if level == 1:
        walls = border[:]
        for c in range(4, MAP_COLS - 4):
            if c % 2 == 0:
                walls.append((c, 8))
        coins = [(c, r) for c in range(3, MAP_COLS - 3, 2)
                          for r in range(3, MAP_ROWS - 3, 3)
                          if (c, r) not in walls]
        return LevelData(walls, coins)

    walls = border[:]
    coins = [(c, r) for c in range(2, MAP_COLS - 2)
                      for r in range(2, MAP_ROWS - 2)
                      if (c + r) % 7 == 0]
    return LevelData(walls, coins)

def make_wall_sprite(c, r):
    x, y = _grid_to_world(c, r)
    s = arcade.SpriteSolidColor(TILE, TILE, arcade.color.DARK_SLATE_GRAY)
    s.center_x, s.center_y = x, y
    return s

def make_coin_sprite(c, r):
    x, y = _grid_to_world(c, r)
    s = arcade.SpriteSolidColor(int(TILE * 0.45), int(TILE * 0.45), arcade.color.GOLD)
    s.center_x, s.center_y = x, y
    return s

def clamp_camera(x, y, w, h):
    return max(0, min(x - w / 2, MAP_WIDTH - w)), max(0, min(y - h / 2, MAP_HEIGHT - h))
