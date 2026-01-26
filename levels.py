from dataclasses import dataclass
from typing import Iterable, Set, Tuple
import arcade
from settings import TILE, COLS, ROWS

GridPos = Tuple[int, int]


@dataclass(frozen=True)
class LevelData:
    walls: Set[GridPos]
    coins: Set[GridPos]


def to_world(c: int, r: int) -> tuple[float, float]:
    return c * TILE + TILE / 2, r * TILE + TILE / 2


def border_walls() -> Set[GridPos]:
    walls = set()

    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))

    for r in range(ROWS):
        walls.add((0, r))
        walls.add((COLS - 1, r))

    return walls


def level1_walls() -> Set[GridPos]:
    walls = border_walls()

    mid_r = ROWS // 2
    mid_c = COLS // 3

    for c in range(2, COLS - 2):
        if c % 2 == 0:
            walls.add((c, mid_r))

    for r in range(2, ROWS - 2):
        if r % 2 == 1:
            walls.add((mid_c, r))

    return walls


def level2_walls() -> Set[GridPos]:
    walls = border_walls()

    for r in range(2, ROWS - 2):
        if r % 2 == 0:
            for c in range(2, COLS - 2):
                if c % 4 != 0:
                    walls.add((c, r))

    holes = {
        (c, r)
        for c in range(4, COLS - 4, 5)
        for r in range(2, ROWS - 2, 3)
    }

    return walls - holes


def generate_coins(walls: Set[GridPos], rule) -> Set[GridPos]:
    coins = set()

    for c in range(1, COLS - 1):
        for r in range(1, ROWS - 1):
            if (c, r) not in walls and rule(c, r):
                coins.add((c, r))

    return coins


def build_level(level: int) -> LevelData:
    if level == 1:
        walls = level1_walls()
        coins = generate_coins(walls, lambda c, r: (c + r) % 5 == 0)
    else:
        walls = level2_walls()
        coins = generate_coins(walls, lambda c, r: (c * 3 + r) % 7 == 0)

    return LevelData(walls, coins)


def make_wall_sprite(c: int, r: int) -> arcade.Sprite:
    x, y = to_world(c, r)
    sprite = arcade.SpriteSolidColor(TILE, TILE, arcade.color.DARK_SLATE_GRAY)
    sprite.center_x = x
    sprite.center_y = y
    return sprite


def make_coin_sprite(c: int, r: int) -> arcade.Sprite:
    x, y = to_world(c, r)
    size = int(TILE * 0.5)
    sprite = arcade.SpriteSolidColor(size, size, arcade.color.GOLD)
    sprite.center_x = x
    sprite.center_y = y
    return sprite
