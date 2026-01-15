import arcade
from settings import *
from levels import build_level, make_wall_sprite, make_coin_sprite
from storage import load_highscore, save_highscore


class Button:
    def __init__(self, text, x, y):
        self.text = text
        self.sprite = arcade.SpriteSolidColor(260, 60, arcade.color.DARK_BLUE_GRAY)
        self.sprite.center_x = x
        self.sprite.center_y = y

    def hit(self, x, y):
        return self.sprite.left < x < self.sprite.right and self.sprite.bottom < y < self.sprite.top

    def draw(self):
        self.sprite.draw()
        arcade.draw_text(self.text, self.sprite.center_x, self.sprite.center_y, arcade.color.WHITE, 18,
                         anchor_x="center", anchor_y="center")


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.btn_start = Button("Start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        self.btn_exit = Button("Exit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
        self.high = load_highscore(SCORES_FILE).best

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("COIN RACE", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120, arcade.color.GOLD, 48, anchor_x="center")
        arcade.draw_text(f"Best score: {self.high}", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 180, arcade.color.WHITE, 18,
                         anchor_x="center")
        self.btn_start.draw()
        self.btn_exit.draw()
        arcade.draw_text("P1: Arrows    P2: W A S D", SCREEN_WIDTH / 2, 90, arcade.color.LIGHT_GRAY, 16,
                         anchor_x="center")
        arcade.draw_text("Goal: collect more coins. Level ends when all coins collected.", SCREEN_WIDTH / 2, 60,
                         arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.btn_start.hit(x, y):
            self.window.show_view(GameView(1, 0, 0))
        elif self.btn_exit.hit(x, y):
            arcade.close_window()


class FinalView(arcade.View):
    def __init__(self, p1, p2):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        best_before = load_highscore(SCORES_FILE).best
        save_highscore(SCORES_FILE, max(best_before, p1, p2))
        self.btn_restart = Button("Restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 140)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120, arcade.color.WHITE, 42, anchor_x="center")
        arcade.draw_text(f"P1: {self.p1}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30, arcade.color.CORNFLOWER_BLUE, 26,
                         anchor_x="center", anchor_y="center")
        arcade.draw_text(f"P2: {self.p2}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10, arcade.color.SALMON, 26,
                         anchor_x="center", anchor_y="center")
        if self.p1 > self.p2:
            w = "Winner: Player 1"
        elif self.p2 > self.p1:
            w = "Winner: Player 2"
        else:
            w = "Draw"
        arcade.draw_text(w, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.GOLD, 24, anchor_x="center",
                         anchor_y="center")
        self.btn_restart.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.btn_restart.hit(x, y):
            self.window.show_view(StartView())


class GameView(arcade.View):
    def __init__(self, level, total1, total2):
        super().__init__()
        self.level = level
        self.total1 = total1
        self.total2 = total2

        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.coins = arcade.SpriteList(use_spatial_hash=True)

        self.p1 = arcade.SpriteSolidColor(40, 40, arcade.color.CORNFLOWER_BLUE)
        self.p2 = arcade.SpriteSolidColor(40, 40, arcade.color.SALMON)

        self.score1 = 0
        self.score2 = 0
        self.time_left = float(LEVEL_TIME_SECONDS)

        self.keys1 = set()
        self.keys2 = set()

        self.setup()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def setup(self):
        self.walls.clear()
        self.coins.clear()

        data = build_level(self.level)
        for c, r in data.walls:
            self.walls.append(make_wall_sprite(c, r))
        for c, r in data.coins:
            self.coins.append(make_coin_sprite(c, r))

        self.p1.center_x, self.p1.center_y = TILE * 1.5, TILE * 1.5
        self.p2.center_x, self.p2.center_y = MAP_W - TILE * 1.5, MAP_H - TILE * 1.5

        self.phys1 = arcade.PhysicsEngineSimple(self.p1, self.walls)
        self.phys2 = arcade.PhysicsEngineSimple(self.p2, self.walls)

    def on_draw(self):
        self.clear()
        self.walls.draw()
        self.coins.draw()
        self.p1.draw()
        self.p2.draw()

        arcade.draw_text(f"Level {self.level}/2", 20, SCREEN_HEIGHT - 30, arcade.color.WHITE, 14)
        arcade.draw_text(f"P1: {self.total1 + self.score1}", 20, SCREEN_HEIGHT - 55, arcade.color.CORNFLOWER_BLUE, 18)
        arcade.draw_text(f"P2: {self.total2 + self.score2}", 20, SCREEN_HEIGHT - 80, arcade.color.SALMON, 18)
        arcade.draw_text(f"Time: {max(0, int(self.time_left))}", SCREEN_WIDTH - 140, SCREEN_HEIGHT - 40,
                         arcade.color.WHITE, 18)

    def _apply_input(self):
        self.p1.change_x = PLAYER_SPEED * ((arcade.key.RIGHT in self.keys1) - (arcade.key.LEFT in self.keys1))
        self.p1.change_y = PLAYER_SPEED * ((arcade.key.UP in self.keys1) - (arcade.key.DOWN in self.keys1))
        self.p2.change_x = PLAYER_SPEED * ((arcade.key.D in self.keys2) - (arcade.key.A in self.keys2))
        self.p2.change_y = PLAYER_SPEED * ((arcade.key.W in self.keys2) - (arcade.key.S in self.keys2))

    def on_update(self, dt):
        self.time_left -= dt
        self._apply_input()

        old1 = (self.p1.center_x, self.p1.center_y)
        old2 = (self.p2.center_x, self.p2.center_y)

        self.phys1.update()
        self.phys2.update()

        if arcade.check_for_collision(self.p1, self.p2):
            self.p1.center_x, self.p1.center_y = old1
            self.p2.center_x, self.p2.center_y = old2
            self.p1.change_x = self.p1.change_y = 0
            self.p2.change_x = self.p2.change_y = 0

        for coin in arcade.check_for_collision_with_list(self.p1, self.coins):
            coin.remove_from_sprite_lists()
            self.score1 += 1
        for coin in arcade.check_for_collision_with_list(self.p2, self.coins):
            coin.remove_from_sprite_lists()
            self.score2 += 1

        if len(self.coins) == 0:
            t1 = self.total1 + self.score1
            t2 = self.total2 + self.score2
            if self.level >= 2:
                self.window.show_view(FinalView(t1, t2))
            else:
                self.window.show_view(GameView(self.level + 1, t1, t2))
            return

        if self.time_left <= 0:
            self.window.show_view(FinalView(self.total1 + self.score1, self.total2 + self.score2))
            return

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.keys1.add(key)
        if key in (arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D):
            self.keys2.add(key)
        if key == arcade.key.ESCAPE:
            self.window.show_view(StartView())

    def on_key_release(self, key, modifiers):
        self.keys1.discard(key)
        self.keys2.discard(key)
