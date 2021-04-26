from threading import Event
from typing import Callable

import board
import digitalio

from adafruit_rgb_display.st7735 import ST7735R
from gpiozero import RotaryEncoder, Button

from tenacity import retry
from tenacity.stop import stop_after_delay


@retry(stop=stop_after_delay(10))
def retry_call(callable: Callable, *args, **kwargs):
    """Retry a call."""
    return callable(*args, **kwargs)


def twist_knob(knob: RotaryEncoder, label):
    # convert the knobs step counter into a 0-255 value
    val = min(knob.steps + 128, 255)
    print(f"Knob {label} steps={knob.steps} value={knob.value} val={val}")


def press_knob(label):
    print(f"Knob {label} pressed")


def hold_knob(event: Event, label):
    print(f"Knob {label} held")
    event.set()


def press_button(label):
    print(f"Button {label} pressed")


if __name__ == "__main__":
    print(f"Initializing inputs and outputs")
    event = Event()

    # knobs will track a step counter from (-128, 128)
    # twisting clockwise increments counter, counter-clockwise decrements
    knob_a = retry_call(RotaryEncoder, 5, 12, max_steps=128)   # month
    knob_b = retry_call(RotaryEncoder, 17, 13, max_steps=128)  # day
    knob_c = retry_call(RotaryEncoder, 22, 16, max_steps=128)  # year

    # buttons on the knobs
    knob_a_button = retry_call(Button, 6, hold_time=3)
    knob_b_button = retry_call(Button, 27, hold_time=3)
    knob_c_button = retry_call(Button, 23, hold_time=3)

    # pushbuttons
    button_a = retry_call(Button, 2)   # stop
    button_b = retry_call(Button, 20)  # play / pause
    button_c = retry_call(Button, 4)   # select
    button_d = retry_call(Button, 3)   # rewind
    button_e = retry_call(Button, 26)  # ffwd

    display = ST7735R(board.SPI(),
                      rotation=90,
                      width=128,
                      height=160,
                      cs=digitalio.DigitalInOut(board.CE0),
                      dc=digitalio.DigitalInOut(board.D24),
                      rst=digitalio.DigitalInOut(board.D25),
                      baudrate=40000000)

    print(f"Setting display to black")
    display.fill(0)

    # add knob callbacks
    knob_a.when_rotated = lambda x: twist_knob(knob_a, "A")
    knob_b.when_rotated = lambda x: twist_knob(knob_b, "B")
    knob_c.when_rotated = lambda x: twist_knob(knob_c, "C")

    # can implement other knob  callbacks...
    # knob_a.when_rotated_clockwise = fn()
    # knob_a.when_rotated_counter_clockwise = fn()

    knob_a_button.when_released = lambda x: press_knob("A")
    knob_b_button.when_released = lambda x: press_knob("B")
    knob_c_button.when_released = lambda x: press_knob("C")

    # can also read values off buttons instead of callbacks if
    # working in a loop
    # while True:
    #     if knob_a_button.is_pressed:
    #         print("button A is pressed")

    knob_a_button.when_held = lambda x: hold_knob(event, "A")
    knob_b_button.when_held = lambda x: hold_knob(event, "B")
    knob_c_button.when_held = lambda x: hold_knob(event, "C")

    button_a.when_released = lambda x: press_button("A")
    button_b.when_released = lambda x: press_button("B")
    button_c.when_released = lambda x: press_button("C")
    button_d.when_released = lambda x: press_button("D")
    button_e.when_released = lambda x: press_button("E")

    print("Twist and press the knobs and buttons.")
    print("Press a knob for longer than 3 seconds or Ctrl-C to exit.")

    try:
        while not event.wait(timeout=0.5):
            # would like to try updating the screen 
            pass
    except KeyboardInterrupt:
        exit(0)
