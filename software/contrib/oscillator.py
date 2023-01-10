from europi import *
import machine
from rp2 import PIO, StateMachine, asm_pio
from europi_script import EuroPiScript

"""
Poly Square
author: Tyler Schreiber (github.com/t-schreibs)
date: 2022-05-10
labels: oscillator, poly

A poly square oscillator with detuning & several polyphony modes. The analog
input receives a V/oct and sets the root pitch of the 6 oscillators, and knob
1 sets the spread of the detuning across the oscillators. Knob 2 sets the
polyphony mode of the oscillators, which output on CVs 1-6.

digital_in: unused
analog_in: V/oct

knob_1: detune
knob_2: polyphony mode

button_1: while depressed, 'tuning mode' is turned on; this changes the knob functionality:
    knob_1: coarse tune (up to 8 octaves)
    knob_2: fine tune (up to a full octave swing)
button_2: toggles the maximum detune between a half step and a major 9th

output_1: oscillator 1
output_2: oscillator 2
output_3: oscillator 3
output_4: oscillator 4
output_5: oscillator 5
output_6: oscillator 6
"""

# Assembly code program for the PIO square oscillator
# Thanks to Ben Everard at HackSpace for the basis of this program:
# https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound
@asm_pio(sideset_init=PIO.OUT_LOW)
def square_prog():
    # Initialize x & y variables - these are used to count down the
    # loops which set the length of the square wave's cycle
    label("restart")
    pull(noblock).side(0)
    mov(x, osr)
    mov(y, isr)
    # Start loop
    # Here, the pin is low, and it will count down y
    # until y=x, then set the pin high and jump to the next section
    label("up_loop")
    jmp(x_not_y, "skip_up")
    nop().side(1)
    jmp("down")
    label("skip_up")
    jmp(y_dec, "up_loop")
    # Mirror the above loop, but with the pin high to form the second
    # half of the square wave
    label("down")
    mov(y, isr)
    label("down_loop")
    jmp(x_not_y, "skip_down")
    nop().side(0)
    jmp("restart")
    label("skip_down")
    jmp(y_dec, "down_loop")


# Class for managing a state machine running the PIO oscillator program
class SquareOscillator:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, square_prog, freq=2 * count_freq, sideset_base=Pin(pin))
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count
        self._count_freq = count_freq

    def set(self, value):
        # Minimum value is -1 (completely turn off), 0 actually still
        # produces a narrow pulse
        value = clamp(value, -1, self._max_count)
        self._sm.put(value)

    # Converts Hertz to the value the state machine running the PIO
    # program needs
    def get_pitch(self, hertz):
        return int(-1 * (((self._count_freq / hertz) - (self._max_count * 4)) / 4))


class KnobState:
    def __init__(self, k1, k2):
        self.k1 = k1
        self.k2 = k2


class Oscillator(EuroPiScript):
    def __init__(self):
        k1.set_samples(256)
        k2.set_samples(256)
        # PIO settings
        max_count = 1_000_000
        count_freq = 50_000_000
        self.oscillators = [
            SquareOscillator(0, 21, max_count, count_freq),
            SquareOscillator(1, 20, max_count, count_freq),
            SquareOscillator(2, 16, max_count, count_freq),
            SquareOscillator(3, 17, max_count, count_freq),
            SquareOscillator(4, 18, max_count, count_freq),
            # SquareOscillator(5, 19, max_count, count_freq),
        ]

        self.ui_update_requested = True
        self.save_state_requested = False
        self.coarse_tune = 0
        self.fine_tune = 0.5
        self.tuning_mode = False
        self.tuning_mode_compare_knob_state = KnobState(None, None)
        self.load_state()

        @b1.handler
        def tuning_mode_on():
            self.tuning_mode_compare_knob_state = KnobState(k1.percent(), k2.percent())
            self.tuning_mode = True
            self.ui_update_requested = True

        @b1.handler_falling
        def tuning_mode_off():
            self.tuning_mode = False
            self.ui_update_requested = True
            # Save the tuning settings after the button is released
            self.save_state_requested = True

    # Converts V/oct signal to Hertz, with 0V = C0
    def get_hertz(self, voltage):
        # Start with A0 because it's a nice, rational number
        a0 = 27.5
        # Subtract 3/4 from the voltage value so that 0V = C0
        return a0 * 2 ** (voltage - 3 / 4)

    # Returns the total voltage offset of the current tuning values
    def get_tuning(self):
        return self.coarse_tune * 8 + self.fine_tune - 0.5

    # Saves oscillator tuning & detuning settings
    def save_state(self):
        settings = {"c": self.coarse_tune, "f": self.fine_tune}
        self.save_state_json(settings)
        self.save_state_requested = False

    # Loads oscillator tuning & detuning settings
    def load_state(self):
        settings = self.load_state_json()
        if "c" in settings:
            self.coarse_tune = settings["c"]
        if "f" in settings:
            self.fine_tune = settings["f"]

    # Draws the UI for the "tuning" mode
    def draw_tuning_ui(self):
        oled.fill(0)
        padding = 2
        line_height = 9
        title = "Tuning"
        # Center the title at the top of the screen
        title_x = int((OLED_WIDTH - ((len(title) + 1) * 7)) / 2) - 1
        oled.text(title, title_x, padding)
        tuning_bar_x = 60
        tuning_bar_width = OLED_WIDTH - tuning_bar_x - padding
        # Coarse tuning bar
        oled.text("coarse:", padding, padding + line_height)
        oled.rect(tuning_bar_x, padding + line_height, tuning_bar_width, 8, 1)
        oled.fill_rect(
            tuning_bar_x, padding + line_height, int(self.coarse_tune * tuning_bar_width), 8, 1
        )
        # Fine tuning bar
        oled.text("fine:", padding + 16, padding + line_height * 2)
        oled.rect(tuning_bar_x, padding + line_height * 2, tuning_bar_width, 8, 1)
        if self.fine_tune < 0.5:
            filled_bar_width = int((0.5 - self.fine_tune) * tuning_bar_width)
            oled.fill_rect(
                int(tuning_bar_x + tuning_bar_width / 2 - filled_bar_width),
                padding + line_height * 2,
                filled_bar_width,
                8,
                1,
            )
        elif self.fine_tune == 0.5:
            line_x = int(tuning_bar_x + tuning_bar_width / 2)
            oled.vline(line_x, padding + line_height * 2, 8, 1)
        else:
            oled.fill_rect(
                int(tuning_bar_x + tuning_bar_width / 2 + 2),
                padding + line_height * 2,
                int((self.fine_tune - 0.5) * tuning_bar_width),
                8,
                1,
            )
        oled.show()

    # Draws the default UI
    def draw_main_ui(self):
        oled.centre_text("oscillator")

    def numbers_are_close(self, current, other, allowed_error):
        if current == None or other == None:
            return False
        return abs(current - other) <= allowed_error

    def update_ui(self):
        if self.tuning_mode:
            self.draw_tuning_ui()
        else:
            self.draw_main_ui()
        self.ui_update_requested = False

    def update_tuning_settings(self):
        new_coarse_tune = k1.percent()
        new_fine_tune = k2.percent()
        allowed_error = 0.005
        # Only update the coarse or fine tuning setting if the knob has
        # been moved since button 1 was depressed - thanks to djmjr
        # (github.com/djmjr) for the idea:
        # https://github.com/djmjr/EuroPi/blob/poly-squares-mods/software/contrib/poly_square_mods.py
        if not (
            self.numbers_are_close(
                new_coarse_tune, self.tuning_mode_compare_knob_state.k1, allowed_error
            )
            or new_coarse_tune == self.coarse_tune
        ):
            self.coarse_tune = new_coarse_tune
            self.tuning_mode_compare_knob_state.k1 = None
            self.ui_update_requested = True
        if not (
            self.numbers_are_close(
                new_fine_tune, self.tuning_mode_compare_knob_state.k2, allowed_error
            )
            or new_fine_tune == self.fine_tune
        ):
            self.fine_tune = new_fine_tune
            self.tuning_mode_compare_knob_state.k2 = None
            self.ui_update_requested = True

    # Updates oscillator settings based on the current knob positions &
    # analog input
    def update_settings(self):
        analog_input = ain.read_voltage(32)
        if self.tuning_mode:
            self.update_tuning_settings()
        else:
            self.detune_amount = k1.percent() / 12
        for oscillator in self.oscillators:
            # Add up the V/oct from the analog input, the offset from the
            # polyphony mode, the adjustment from the tuning, and the
            # adjustment from the detune amount to get the final pitch for
            # the oscillator
            oscillator_index = self.oscillators.index(oscillator)
            oscillator.set(oscillator.get_pitch(self.get_hertz(analog_input + self.get_tuning())))

    def main(self):
        while True:
            self.update_settings()
            if self.ui_update_requested:
                self.update_ui()
            if self.save_state_requested:
                self.save_state()


# Main script execution
if __name__ == "__main__":
    Oscillator().main()
