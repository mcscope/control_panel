from collections import namedtuple
import RPi.GPIO as gpio
from enum import Enum
import time


# Slide needs degluing... ooof!

# Spi protocol, wifi protocol

# toggle 1-0 only toggles if  1-1 is off.

class Kind(Enum):
    MOMENTARY = 0
    TOGGLE = 1
    ANALOG = 2


Control = namedtuple("Control", [
    "pin",
    "name",
    "kind",
    "resistor"
])

controls = [
    # Joystick

    # B - top row of toggles
    Control(16, "Toggle 0 - 0", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(20, "Toggle 0 - 1", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(21, "Toggle 0 - 2", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(12, "Toggle 0 - 3", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(7, "Toggle 0 - 4", Kind.TOGGLE, gpio.PUD_DOWN),
    # A - 2nd row of toggles


    Control(5, "Toggle 1 - 0", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(22, "Toggle 1 - 1", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(27, "Toggle 1 - 2", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(17, "Toggle 1 - 3", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(4, "Toggle 1 - 4", Kind.TOGGLE, gpio.PUD_DOWN),

    Control(6, "Toggle 4-0", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(13, "Toggle 4-1", Kind.MOMENTARY, gpio.PUD_DOWN),
    Control(19, "Toggle 4-2", Kind.MOMENTARY, gpio.PUD_DOWN),
    Control(26, "Toggle 4-3", Kind.MOMENTARY, gpio.PUD_DOWN),
    Control(23, "Toggle 4-4", Kind.TOGGLE, gpio.PUD_DOWN),

    Control(14, "KNIFE-UP", Kind.TOGGLE, gpio.PUD_DOWN),
    Control(15, "KNIFE-DOWN", Kind.TOGGLE, gpio.PUD_DOWN),

    Control(18, "SLIDE-BUTTON", Kind.MOMENTARY, gpio.PUD_DOWN),
    Control(24, "E-STOP", Kind.MOMENTARY, gpio.PUD_DOWN),

]


def init_pins():
    gpio.setmode(gpio.BCM)
    for control in controls:
        print(control.pin)
        gpio.setup(control.pin, gpio.IN, pull_up_down=control.resistor)


def main():
    init_pins()

    control_states = [
        0.0 if control.kind == Kind.ANALOG else False
        for control in controls]

    while True:
        for idx, control in enumerate(controls):
            val = gpio.input(control.pin)
            if val != control_states[idx]:
                oldval = control_states[idx]
                control_states[idx] = val
                print(f"control {control.name} changed states from {oldval} to {val}")
        time.sleep(0.05)


if __name__ == '__main__':
    main()
