import RPi.GPIO as GPIO

from tenacity import retry
from tenacity.stop import stop_after_delay

default_gpio_mode = GPIO.BCM

class GPIODeviceMixin:
    @staticmethod
    @retry(stop=stop_after_delay(10))
    def add_event_detect(*args, **kwargs):
        return GPIO.add_event_detect(*args, **kwargs)

    @staticmethod
    def get_pin_value(pin):
        return GPIO.input(pin)

    @staticmethod
    def setup_pin(pin, mode, pull=None):
        if GPIO.getmode() is None:
            # if GPIO mode hasn't been set, choose a default
            GPIO.setmode(default_gpio_mode)

        if pull is None:
            GPIO.setup(pin, mode)
        else:
            GPIO.setup(pin, mode, pull)