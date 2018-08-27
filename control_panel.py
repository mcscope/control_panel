from collections import namedtuple
try:
    import RPi.GPIO as gpio
    import serial
except ImportError:
    print("Mocking out raspberry pi libraries")
    import unittest.mock
    gpio = unittest.mock.Mock()
    serial = unittest.mock.Mock()
from enum import Enum
import time
from utils import dictobj
ser = serial.Serial('/dev/ttyUSB0', 9600)

# Slide needs degluing... ooof!

# Spi protocol, wifi protocol

# toggle 1-0 only toggles if  1-1 is off.
# TODO bracket hero dial to 11 choices
# TODO make sure analog assignments are correct
#todo actually turn on leds


class Kind(Enum):
    MOMENTARY = 0
    TOGGLE = 1
    ANALOG = 2


class ControlState(dictobj):
    pass

Control = namedtuple("Control", [
    "pin",
    "name",
    "kind",
    "resistor",
    "ardunio",
    "serial_split_pos",
    "toggle_pos"
], defaults=[False, None, None])

controls = [
    Control(14, "knife_up", Kind.TOGGLE, gpio.PUD_DOWN,),
    Control(15, "knife_down", Kind.TOGGLE, gpio.PUD_DOWN,),

    Control(18, "slide_button", Kind.MOMENTARY, gpio.PUD_DOWN,),
    Control(24, "e_stop", Kind.MOMENTARY, gpio.PUD_DOWN,),
    # These are parsed from the arduino
    Control(None, "hero_dial", Kind.ANALOG, gpio.PUD_DOWN, True, (3, None),),
    Control(None, "minipot", Kind.ANALOG, gpio.PUD_DOWN, True, (4, None),),
    Control(None, "megapot", Kind.ANALOG, gpio.PUD_DOWN, True, (5, None),),
    Control(None, "slide", Kind.ANALOG, gpio.PUD_DOWN, True, (6, None),),

    # B - top row of toggles
    Control(16, "Toggle 0 - 0", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(0, 0)),
    Control(20, "Toggle 0 - 1", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(0, 1)),
    Control(21, "Toggle 0 - 2", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(0, 2)),
    Control(12, "Toggle 0 - 3", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(0, 3)),
    Control(7, "Toggle 0 - 4", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(0, 4)),
    # A - 2nd row of toggles

    Control(5, "Toggle 1 - 0", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(1, 0)),
    Control(22, "Toggle 1 - 1", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(1, 1)),
    Control(27, "Toggle 1 - 2", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(1, 2)),
    Control(17, "Toggle 1 - 3", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(1, 3)),
    Control(4, "Toggle 1 - 4", Kind.TOGGLE, gpio.PUD_DOWN, toggle_pos=(1, 4)),

    Control(None, "Toggle 2-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 0), toggle_pos=(2, 0)),
    Control(None, "Toggle 2-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 1), toggle_pos=(2, 1)),
    Control(None, "Toggle 2-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 2), toggle_pos=(2, 2)),
    Control(None, "Toggle 2-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 3), toggle_pos=(2, 3)),
    Control(None, "Toggle 2-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 4), toggle_pos=(2, 4)),

    Control(None, "Toggle 3-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 0), toggle_pos=(3, 0)),
    Control(None, "Toggle 3-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 1), toggle_pos=(3, 1)),
    Control(None, "Toggle 3-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 2), toggle_pos=(3, 2)),
    Control(None, "Toggle 3-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 3), toggle_pos=(3, 3)),
    Control(None, "Toggle 3-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 4), toggle_pos=(3, 4)),

    Control(None, "Toggle 4-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 0), toggle_pos=(4, 0)),
    Control(None, "Toggle 4-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 1), toggle_pos=(4, 1)),
    Control(None, "Toggle 4-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 2), toggle_pos=(4, 2)),
    Control(None, "Toggle 4-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 3), toggle_pos=(4, 3)),
    Control(None, "Toggle 4-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 4), toggle_pos=(4, 4)),

]


def init_pins():
    gpio.setmode(gpio.BCM)
    for control in controls:
        print(control.pin)
        gpio.setup(control.pin, gpio.IN, pull_up_down=control.resistor)


def read_controls():
    serlin = ser.read_line()
    split_ser = serlin.split()
    # don't want to fall behind in the serial connection if that's possible
    trash = ser.read()
    states = []
    for idx, control in enumerate(controls):
        if control.ardunio:
            first_split, second_split = control.serial_split_pos
            split_seg = split_ser[first_split]
            if second_split is not None:
                split_seg = split_seg[second_split]
            val = int(split_seg)
        elif control.pin is not None:
            val = gpio.input(control.pin)
        states.append(val)
    return states


def interpret_controls(control_states):
    cs = ControlState(toggles=[[] for _ in range(5)])
    for control, state in zip(controls, control_states):
        if control.toggle_pos:
            row, col = control.toggle_pos
            cs.toggles[row][col] = state
        else:
            if control.analog:
                cs[control.name] = state / 1000

            cs[control.name] = state
            #TODO analog corrections


def main():
    init_pins()

    control_states = [
        0.0 if control.kind == Kind.ANALOG else False
        for control in controls]

    while True:
        new_states = read_controls()
        for control, state, new_state in zip(controls, control_states, new_states):
            if state != new_state:
                print(f"control {control.name} changed states from {oldval} to {val}")
        control_states = new_states
        time.sleep(0.05)


if __name__ == '__main__':
    main()
