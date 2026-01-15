import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views import StartView


def main():
    w = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    w.show_view(StartView())
    arcade.run()


if __name__ == "__main__":
    main()
