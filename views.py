import arcade
from settings import *
from levels import build_level, make_wall_sprite, make_coin_sprite, clamp_camera
from storage import load_highscore, save_highscore

class Button:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def hit(self, x, y):
        return self.x - BTN_W / 2 < x < self.x + BTN_W / 2 and self.y - BTN_H / 2 < y < self.y + BTN_H / 2

    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, BTN_W, BTN_H, arcade.color.DARK_BLUE_GRAY)
        arcade.draw_text(self.text, self.x, self.y, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.start = Button("Start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        self.exit = Button("Exit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
        self.high = load_highscore(SCORES_FILE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("COIN RACE", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120, arcade.color.GOLD, 48, anchor_x="center")
        arcade.draw_text(f"Best score: {self.high.best}", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 180, arcade.color.WHITE, 18, anchor_x="center")
        self.start.draw()
        self.exit.draw()

    def on_mouse_press(self, x, y, b, m):
        if self.start.hit(x, y):
            self.window.show_view(GameView(1, 0, 0))
        if self.exit.hit(x, y):
            arcade.close_window()

class FinalView(arcade.View):
    def __init__(self, a, b):
        super().__init__()
        save_highscore(SCORES_FILE, max(a, b))
        self.a = a
        self.b = b
        self.restart = Button("Restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120)

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120, arcade.color.WHITE, 42, anchor_x="center")
        arcade.draw_text(f"P1: {self.a}\nP2: {self.b}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 26, anchor_x="center", anchor_y="center")
        self.restart.draw()

    def on_mouse_press(self, x, y, b, m):
        if self.restart.hit(x, y):
            self.window.show_view(StartView())

class GameView(arcade.View):
    def __init__(self, level, t1, t2):
        super().__init__()
        self.level = level
        self.t1 = t1
        self.t2 = t2
        self.camera_p1 = arcade.Camera(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        self.camera_p2 = arcade.Camera(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.coins = arcade.SpriteList(use_spatial_hash=True)
        self.p1 = arcade.SpriteSolidColor(46, 46, arcade.color.CORNFLOWER_BLUE)
        self.p2 = arcade.SpriteSolidColor(46, 46, arcade.color.SALMON)
        self.score1 = 0
        self.score2 = 0
        self.time = LEVEL_TIME_SECONDS
        self.keys1 = set()
        self.keys2 = set()
        self.setup()

    def setup(self):
        d = build_level(self.level)
        for c, r in d.walls:
            self.walls.append(make_wall_sprite(c, r))
        for c, r in d.coins:
            self.coins.append(make_coin_sprite(c, r))
        self.p1.center_x, self.p1.center_y = 160, 160
        self.p2.center_x, self.p2.center_y = MAP_WIDTH - 160, MAP_HEIGHT - 160
        self.phys1 = arcade.PhysicsEngineSimple(self.p1, self.walls)
        self.phys2 = arcade.PhysicsEngineSimple(self.p2, self.walls)

    def on_draw(self):
        self.clear()

        l1, b1 = clamp_camera(self.p1.center_x, self.p1.center_y, SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        l2, b2 = clamp_camera(self.p2.center_x, self.p2.center_y, SCREEN_WIDTH // 2, SCREEN_HEIGHT)

        arcade.set_viewport(0, SCREEN_WIDTH // 2, 0, SCREEN_HEIGHT)
        self.camera_p1.move_to((l1, b1))
        self.camera_p1.use()
        self.walls.draw()
        self.coins.draw()
        self.p1.draw()
        self.p2.draw()

        arcade.set_viewport(SCREEN_WIDTH // 2, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        self.camera_p2.move_to((l2, b2))
        self.camera_p2.use()
        self.walls.draw()
        self.coins.draw()
        self.p1.draw()
        self.p2.draw()

        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        arcade.draw_line(SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT, arcade.color.WHITE, 2)
        arcade.draw_text(f"P1: {self.t1 + self.score1}", 20, SCREEN_HEIGHT - 40, arcade.color.CORNFLOWER_BLUE, 18)
        arcade.draw_text(f"P2: {self.t2 + self.score2}", SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 40, arcade.color.SALMON, 18)
        arcade.draw_text(f"Time: {int(self.time)}", SCREEN_WIDTH - 160, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)

    def on_update(self, dt):
        self.time -= dt
        self.p1.change_x = PLAYER_SPEED * ((arcade.key.RIGHT in self.keys1) - (arcade.key.LEFT in self.keys1))
        self.p1.change_y = PLAYER_SPEED * ((arcade.key.UP in self.keys1) - (arcade.key.DOWN in self.keys1))
        self.p2.change_x = PLAYER_SPEED * ((arcade.key.D in self.keys2) - (arcade.key.A in self.keys2))
        self.p2.change_y = PLAYER_SPEED * ((arcade.key.W in self.keys2) - (arcade.key.S in self.keys2))
        self.phys1.update()
        self.phys2.update()
        for c in arcade.check_for_collision_with_list(self.p1, self.coins):
            c.remove_from_sprite_lists()
            self.score1 += 1
        for c in arcade.check_for_collision_with_list(self.p2, self.coins):
            c.remove_from_sprite_lists()
            self.score2 += 1
        if not self.coins or self.time <= 0:
            if self.level == 2:
                self.window.show_view(FinalView(self.t1 + self.score1, self.t2 + self.score2))
            else:
                self.window.show_view(GameView(self.level + 1, self.t1 + self.score1, self.t2 + self.score2))

    def on_key_press(self, key, m):
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.keys1.add(key)
        if key in (arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D):
            self.keys2.add(key)

    def on_key_release(self, key, m):
        self.keys1.discard(key)
        self.keys2.discard(key)
