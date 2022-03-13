from random import randint
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, k1, k2, oled
from europi_script import EuroPiScript


class Paddle:
    def __init__(self, knob, x_pos, height) -> None:
        self.knob = knob
        self.x_pos = x_pos
        self.height = height

    def draw(self, oled):
        y_pos = self.knob.read_position(OLED_HEIGHT - self.height)
        oled.vline(self.x_pos, y_pos, self.height, 1)


class Ball:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.x_dir = randint(-1, 1)
        self.y_dir = randint(-1, 1)

    def tick(self):
        self.x = self.x + self.x_dir
        self.y = self.y + self.y_dir

        if self.y < 0 or self.y > OLED_HEIGHT - 1:
            self.y_dir = -(self.y_dir)

        if self.x < 0 or self.x > OLED_WIDTH - 1:
            self.x_dir = -(self.x_dir)

    def draw(self, oled):
        oled.rect(self.x, self.y, 2, 2, 1)


class Pong(EuroPiScript):
    def __init__(self):
        super().__init__()

    def main(self):
        l_paddle = Paddle(k1, 0, 8)
        r_paddle = Paddle(k2, OLED_WIDTH - 1, 8)
        ball = Ball(int(OLED_WIDTH / 2), int(OLED_HEIGHT / 2))
        while True:
            oled.fill(0)
            ball.tick()
            ball.draw(oled)
            l_paddle.draw(oled)
            r_paddle.draw(oled)
            oled.show()
            sleep(0.1)


if __name__ == "__main__":
    Pong().main()
