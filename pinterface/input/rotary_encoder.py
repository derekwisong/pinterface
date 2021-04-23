import logging
import time

import RPi.GPIO as GPIO

from pinterface.gpio import GPIODeviceMixin

logger = logging.getLogger(__name__)


class RotaryEncoder(GPIODeviceMixin):
    """A debounced and pushable rotary encoder.

    To implement a RotaryEncoder, subclass RotaryEncoder and define the methods:

    press(duration)  # called on press
    twist(clockwise) # called on twist to the next detent

    ATTRIBUTES:

    clock_pin
    dt_pin
    switch_pin
    name

    METHODS:

    press(duration)
    twist(clockwise)
    """

    def __init__(self, clock_pin: int, dt_pin: int, switch_pin: int,
                 name: str = "encoder"):
        """Create a RotaryEncoder.

        :param clock_pin: CLK pin
        :param dt_pin: DT pin
        :param switch_pin: SW pin
        :param name: The name of the rotary encoder
        """

        self.clock_pin = clock_pin
        self.dt_pin = dt_pin
        self.switch_pin = switch_pin
        self.name = name
        self._is_setup = False
        self._setup()

    def __str__(self):
        return f"{self.__class__.__name__} <{self.name}>"

    def _setup(self):
        if self._is_setup:
            raise RuntimeError(f"_setup may not be called twice")

        for pin in (self.clock_pin, self.switch_pin, self.dt_pin):
            self.setup_pin(pin, GPIO.IN, GPIO.PUD_UP)

        def twist(channel):
            cl_val = self._get_clock()
            if cl_val == 1:
                dt_val = self._get_dt()
                if cl_val == dt_val:
                    clockwise = True
                else:
                    clockwise = False

                logger.debug(f"{self} twist clockwise={clockwise}")
                self.twist(clockwise)

        def press(channel):
            val = self._get_switch()
            if val != 0:
                return
            start = time.time()
            while self._get_switch() == val:
                pass
            duration = time.time() - start

            logger.debug(f"{self} press duration={duration}")
            self.press(duration)

        self.add_event_detect(self.clock_pin, GPIO.FALLING,
                              callback=twist, bouncetime=5)
        self.add_event_detect(self.switch_pin, GPIO.FALLING,
                              callback=press, bouncetime=75)

        # mark that setup has been run so that it can't be called twice
        self._setup = True

    def _get_clock(self):
        return self.get_pin_value(self.clock_pin)

    def _get_dt(self):
        return self.get_pin_value(self.dt_pin)

    def _get_switch(self):
        return self.get_pin_value(self.switch_pin)

    def twist(self, clockwise: bool):
        raise NotImplemented("Create a subclass to implement twist()")

    def press(self, duration: float):
        raise NotImplemented("Create a subclass to implement press()")
