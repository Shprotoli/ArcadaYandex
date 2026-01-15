from dataclasses import dataclass
from typing import List, Tuple
import arcade
from settings import TILE, COLS, ROWS


@dataclass(frozen=True)
class LevelData:
    walls: List[Tuple[int, int]]
    coins: List[Tuple[int, int]]


def _to_world(c, r):
    return c * TILE + TILE / 2, r * TILE + TILE / 2


def _border():
    b = []
    for c in range(COLS):
        b.append((c, 0))
        b.append((c, ROWS - 1))
    for r in range(ROWS):
        b.append((0, r))
        b.append((COLS - 1, r))
    return b


def build_level(level):
    walls = _border()
    if level == 1:
        for c in range(2, COLS - 2):
            if c % 2 == 0:
                walls.append((c, ROWS // 2))
        for r in range(2, ROWS - 2):
            if r % 2 == 1:
                walls.append((COLS // 3, r))
        coins = []
        for c in range(1, COLS - 1):
            for r in range(1, ROWS - 1):
                if (c, r) not in walls and (c + r) % 5 == 0:
                    coins.append((c, r))
        return LevelData(walls, coins)

    for r in range(2, ROWS - 2):
        if r % 2 == 0:
            for c in range(2, COLS - 2):
                if c % 4 != 0:
                    walls.append((c, r))
    for c in range(4, COLS - 4, 5):
        for r in range(2, ROWS - 2, 3):
            if (c, r) in walls:
                walls.remove((c, r))

    coins = []
    for c in range(1, COLS - 1):
        for r in range(1, ROWS - 1):
            if (c, r) not in walls and (c * 3 + r) % 7 == 0:
                coins.append((c, r))
    return LevelData(walls, coins)


def make_wall_sprite(c, r):
    x, y = _to_world(c, r)
    s = arcade.SpriteSolidColor(TILE, TILE, arcade.color.DARK_SLATE_GRAY)
    s.center_x = x
    s.center_y = y
    return s


def make_coin_sprite(c, r):
    x, y = _to_world(c, r)
    size = int(TILE * 0.5)
    s = arcade.SpriteSolidColor(size, size, arcade.color.GOLD)
    s.center_x = x
    s.center_y = y
    return s
