"""
Example of using a rotary encoder.

    ~/src/pinterface $ python -m pinterface.examples.rotary_encoder 16 22 23 "year"

    Awaiting input on "year". Press Ctrl-C to end.
    MyKnob <year> twisted clockwise
    MyKnob <year> pressed for 0.23075342178344727 seconds
"""

import sys
import time
from pinterface import RotaryEncoder


class MyKnob(RotaryEncoder):
    def press(self, duration):
        print(f"{self} pressed for {duration} seconds")

    def twist(self, clockwise):
        direction = "clockwise" if clockwise else "counter-clockwise"
        print(f"{self} twisted {direction}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cl, dt, sw, name = sys.argv[1:5]
    else:
        cl = 16
        dt = 22
        sw = 23
        name = "year"

    year = MyKnob(cl, dt, sw, name=name)
    print(f"Awaiting input on \"{year.name}\". Press Ctrl-C to end.")

    try:
        while True:
            time.sleep(0.001)
    except KeyboardInterrupt:
        pass
