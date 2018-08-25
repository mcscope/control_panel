from control_panel import init_pins, Kind, CONTROLS
from control_panel import read_controls, interpret_controls, debounce
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
    # cur_scheme = BaseScheme()
    init_pins()
    control_states = None
    while True:
        try:
            readings = read_controls()
            new_states = interpret_controls(readings)
            debounce(new_states, control_states)

        except IndexError:
            import traceback
            traceback.print_exc()
            # likely a bad serial line
            continue
        if control_states:
            for control_name in control_states.keys():
                old_state = control_states[control_name]
                new_state = new_states[control_name]
                if old_state != new_state:
                    if isinstance(old_state, float):
                        print(f"control {control_name} changed states from {old_state:0.2f} to {new_state:0.2f}")
                    else:
                        print(f"control {control_name} changed states from {old_state} to {new_state}")
        control_states = new_states
        # selected_scheme = determine_selected_scheme(control_states)
        # if selected_scheme != cur_scheme.__class__:
        # cur_scheme = selected_scheme()

        # cur_scheme.draw(control_states)
        time.sleep(0.05)


if __name__ == '__main__':
    main()
