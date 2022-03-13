from random import choice
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, k1, k2, oled, MAX_OUTPUT_VOLTAGE
from europi_script import EuroPiScript

MAX_SCORE = int(MAX_OUTPUT_VOLTAGE)


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
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.x_dir = choice([-2, -1, 1, 2])
        self.y_dir = choice([-2, -1, 0, 1, 2])

    def tick(self):
        self.x = self.x + self.x_dir
        self.y = self.y + self.y_dir

        if self.y < 0 or self.y > OLED_HEIGHT - 1:
            self.y_dir = -(self.y_dir)

        if self.x < 0 or self.x > OLED_WIDTH - 1:
            self.x_dir = -(self.x_dir)

    def draw(self, oled):
        oled.rect(self.x, self.y, 2, 2, 1)


class Score:
    def __init__(self) -> None:
        self.l = 0
        self.r = 0

    def score_l(self):
        self.l += 1

    def score_r(self):
        self.r += 1

    def draw(self, oled):
        oled.text(f"{self.l} {self.r}", int(OLED_WIDTH / 2) - 12, 0, 1)

    def game_over(self):
        if self.l == MAX_SCORE or self.r == MAX_SCORE:
            self.l = 0
            self.r = 0
            return True
        return False


class Pong(EuroPiScript):
    def __init__(self):
        super().__init__()

    def draw_center_line(self, oled):
        x = int(OLED_WIDTH / 2)
        # oled.vline(x, 0, OLED_HEIGHT, 1)
        for y in range(0, OLED_HEIGHT, 4):
            oled.pixel(x, y, 1)

    def main(self):
        score = Score()
        l_paddle = Paddle(k1, 0, 8)
        r_paddle = Paddle(k2, OLED_WIDTH - 1, 8)
        ball = Ball(int(OLED_WIDTH / 2), int(OLED_HEIGHT / 2))
        while True:
            # update game state
            oled.fill(0)
            ball.tick()
            ball.draw(oled)
            l_paddle.draw(oled)
            r_paddle.draw(oled)
            score.draw(oled)
            self.draw_center_line(oled)

            if ball.x < 1:
                score.score_l()
                ball.reset()

            if ball.x > OLED_WIDTH - 1:
                score.score_r()
                ball.reset()

            if score.game_over():
                ball.reset()

            # update CV output

            oled.show()
            # sleep(0.1)


if __name__ == "__main__":
    Pong().main()
