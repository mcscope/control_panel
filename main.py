from control_panel import init_pins, Kind, controls, interpret_controls
from schemes import BaseScheme, SimonScheme
import time

scheme_ranges = [
    (0, BaseScheme),
    (1, SimonScheme),
]


def determine_selected_scheme(state):
    # This shall become more complicated with testing
    return BaseScheme


def main():
    cur_scheme = BaseScheme()
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

        state = interpret_controls(control_states)
        selected_scheme = determine_selected_scheme(state)
        if selected_scheme != cur_scheme.__class__:
            cur_scheme = selected_scheme()

        cur_scheme.draw(state)
        time.sleep(0.05)


if __name__ == '__main__':
    main()
