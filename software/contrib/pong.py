from random import choice
from time import sleep

from europi import MAX_OUTPUT_VOLTAGE, OLED_HEIGHT, OLED_WIDTH, cv1, cv2, cv3, cv4, cv5, cv6, k1, k2, oled
from europi_script import EuroPiScript

MAX_SCORE = int(MAX_OUTPUT_VOLTAGE)
PADDLE_HEIGHT = 8


class Paddle:
    def __init__(self, knob, x_pos, height) -> None:
        self.knob = knob
        self.x = x_pos
        self.half_height = int(height / 2)

    @property
    def y(self):
        return self.knob.read_position(OLED_HEIGHT)

    def draw(self, oled):
        oled.vline(self.x, self.y - self.half_height, self.half_height * 2, 1)

    def hit(self, ball):
        y = self.y
        return ball.y >= (y - int(self.half_height)) and ball.y <= (y + int(self.half_height))


class Ball:
    def __init__(self) -> None:
        self.start_x = int(OLED_WIDTH / 2)
        self.start_y = int(OLED_HEIGHT / 2)
        self.reset()
        self.bounce_trigger = False

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.x_dir = choice([-2, -1, 1, 2])
        self.y_dir = choice([-2, -1, 0, 1, 2])
        self.bounce_trigger = False

    def tick(self):
        self.bounce_trigger = False
        self.x = self.x + self.x_dir
        self.y = self.y + self.y_dir

        if self.y < 0 or self.y > OLED_HEIGHT - 1:
            self.y_dir = -(self.y_dir)
            self.bounce_trigger = True

        if self.x < 0 or self.x > OLED_WIDTH - 1:
            self.x_dir = -(self.x_dir)
            self.bounce_trigger = True

    def draw(self, oled):
        oled.rect(self.x, self.y, 2, 2, 1)


class Score:
    def __init__(self) -> None:
        self.l = 0
        self.r = 0
        self.x = int(OLED_WIDTH / 2) - 12
        self.score_trigger = False

    def score_l(self):
        self.l += 1
        self.score_trigger = True

    def score_r(self):
        self.r += 1
        self.score_trigger = True

    def draw(self, oled):
        oled.text(f"{self.l} {self.r}", self.x, 0, 1)

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
        l_paddle = Paddle(k1, 0, PADDLE_HEIGHT)
        r_paddle = Paddle(k2, OLED_WIDTH - 1, PADDLE_HEIGHT)
        ball = Ball()
        while True:
            # update game state
            oled.fill(0)
            ball.tick()
            ball.draw(oled)
            l_paddle.draw(oled)
            r_paddle.draw(oled)
            score.score_trigger = False
            score.draw(oled)
            self.draw_center_line(oled)

            if ball.x < 1:
                if not l_paddle.hit(ball):
                    score.score_l()
                    ball.reset()

            if ball.x > OLED_WIDTH - 1:
                if not r_paddle.hit(ball):
                    score.score_r()
                    ball.reset()

            if score.game_over():
                ball.reset()
            oled.show()

            # update CV output
            cv1.value(ball.bounce_trigger)
            cv2.voltage(ball.x)
            cv3.value(score.score_trigger)
            cv4.voltage(score.l)
            cv5.voltage(ball.y)
            cv6.voltage(score.r)

if __name__ == "__main__":
    Pong().main()
