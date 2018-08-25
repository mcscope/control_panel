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

DEBOUNCE_DELTA = 0.05


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
    "toggle_pos",
    "range"
])

CONTROLS = [
    Control(14, "knife_up", Kind.TOGGLE, gpio.PUD_DOWN, False, None, None, None),
    Control(15, "knife_down", Kind.TOGGLE, gpio.PUD_DOWN, False, None, None, None),

    Control(18, "slide_button", Kind.MOMENTARY, gpio.PUD_DOWN, False, None, None, None),
    Control(24, "e_stop", Kind.MOMENTARY, gpio.PUD_DOWN, False, None, None, None),
    # These are parsed from the arduino
    Control(None, "hero_dial", Kind.ANALOG, gpio.PUD_DOWN, True, (3, None), None, (948, 1010)),
    Control(None, "minipot", Kind.ANALOG, gpio.PUD_DOWN, True, (5, None), None, (63, 1022)),
    Control(None, "megapot", Kind.ANALOG, gpio.PUD_DOWN, True, (6, None), None, (1, 1023)),
    Control(None, "slide", Kind.ANALOG, gpio.PUD_DOWN, True, (4, None), None, (90, 980)),

    # B - top row of toggles
    Control(16, "Toggle 0 - 0", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (0, 0), None),
    Control(20, "Toggle 0 - 1", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (0, 1), None),
    Control(21, "Toggle 0 - 2", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (0, 2), None),
    Control(12, "Toggle 0 - 3", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (0, 3), None),
    Control(7, "Toggle 0 - 4", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (0, 4), None),
    # A - 2nd row of toggles

    Control(5, "Toggle 1 - 0", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (1, 0), None),
    Control(22, "Toggle 1 - 1", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (1, 1), None),
    Control(27, "Toggle 1 - 2", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (1, 2), None),
    Control(17, "Toggle 1 - 3", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (1, 3), None),
    Control(4, "Toggle 1 - 4", Kind.TOGGLE, gpio.PUD_DOWN, False, None, (1, 4), None),

    Control(None, "Toggle 2-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 0), (2, 0), None),
    Control(None, "Toggle 2-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 1), (2, 1), None),
    Control(None, "Toggle 2-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 2), (2, 2), None),
    Control(None, "Toggle 2-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 3), (2, 3), None),
    Control(None, "Toggle 2-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (0, 4), (2, 4), None),

    Control(None, "Toggle 3-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 0), (3, 0), None),
    Control(None, "Toggle 3-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 1), (3, 1), None),
    Control(None, "Toggle 3-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 2), (3, 2), None),
    Control(None, "Toggle 3-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 3), (3, 3), None),
    Control(None, "Toggle 3-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (1, 4), (3, 4), None),

    Control(None, "Toggle 4-0", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 0), (4, 0), None),
    Control(None, "Toggle 4-1", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 1), (4, 1), None),
    Control(None, "Toggle 4-2", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 2), (4, 2), None),
    Control(None, "Toggle 4-3", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 3), (4, 3), None),
    Control(None, "Toggle 4-4", Kind.TOGGLE, gpio.PUD_DOWN, True, (2, 4), (4, 4), None),

]

ANALOG_CONTROLS = [c for c in CONTROLS if c.kind == Kind.ANALOG]


def init_pins():
    gpio.setmode(gpio.BCM)
    for control in CONTROLS:
        if not control.pin:
            continue
        print(control.pin)
        gpio.setup(control.pin, gpio.IN, pull_up_down=control.resistor)


def read_controls():
    # don't want to fall behind in the serial connection if that's possible
    ser.reset_input_buffer()
    ser.readline()
    serlin = ser.readline()
    # print(serlin)
    try:
        serlin = serlin.strip().decode()
    except UnicodeDecodeError:
        # first nonstring character os \xff for some reason sometimes
        serlin = serlin.strip()[1:].decode()

    # print(serlin)
    split_ser = serlin.split()
    states = []
    for idx, control in enumerate(CONTROLS):
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


def interpret_controls(readings):
    cs = ControlState(toggles=[[0 for _ in range(5)] for _ in range(5)])
    for control, state in zip(CONTROLS, readings):
        if control.toggle_pos:
            row, col = control.toggle_pos
            cs.toggles[row][col] = state
        else:
            if control.kind == Kind.ANALOG:
                start, end = control.range
                spectrum = end - start
                val_on_spectrum = state - start
                mapped_val = val_on_spectrum / spectrum
                mapped_val = 1.0 - max(0.0, min(1.0, mapped_val))
                cs[control.name] = mapped_val
            else:
                cs[control.name] = state

    # print(cs)

    return cs


def debounce(fresh_states, existing_states):
    """
    Reduce noise the controls!
    Right now this is just an analog correction - if you're within delta
    of the previous value, you don't get changed.
    """
    if not existing_states:
        return
    for control in ANALOG_CONTROLS:
        delta = fresh_states[control.name] - existing_states[control.name]
        if abs(delta) < DEBOUNCE_DELTA:
            fresh_states[control.name] = existing_states[control.name]


def main():
    init_pins()

    control_states = [
        0.0 if control.kind == Kind.ANALOG else False
        for control in CONTROLS]

    while True:
        new_states = read_controls()
        for control, state, new_state in zip(CONTROLS, control_states, new_states):
            if state != new_state:
                print(f"control {control.name} changed states from {oldval} to {val}")
        control_states = new_states
        time.sleep(0.05)


if __name__ == '__main__':
    main()
