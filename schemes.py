import time
import random
import light_control
from colorsys import hsv_to_rgb
from utils import flatten


class BaseScheme(object):

    def __init__(self):
        self.memory = [[255, 255, 255]
                       for _ in range(light_control.number_of_lights)]

    def set_light_pattern_from_knife(self, state):
        if state.knife_up:
            if not light_control.strobe_state:
                light_control.strobe_state = True
                light_control.jump_state = False
                light_control.force = True
        elif state.knife_down:
            if not light_control.jump_state:
                light_control.strobe_state = False
                light_control.jump_state = True
                light_control.force = True
        else:
            if light_control.jump_state or light_control.strobe_state:
                light_control.strobe_state = False
                light_control.jump_state = False
                light_control.force = True
        light_control.delay = state.slide / 500

    def emergency_stop_animation(self):
        """
        for the case of the emergency stop,
         I think it would be cool to make the whole thing 'spaz out' for a while
        this would be a first attempt at that.
        It's supposed to do a rainbow random spaz-out for a while,
        and then do slowing white/black strobe
        until it goes completely off
        """

        for x in range(100):
            self.memory = [
                hsv_to_rgb(random.randint(x) / 100,
                           random.randint(x) / 100,
                           random.randint(x) / 100)
                for x in range(light_control.number_of_lights)]

            light_control.set_colors(self.memory)
        for x in range(50):
            color = [0, 0, 0] if x % 2 == 0 else [255, 255, 255]
            self.memory = [color for x in range(light_control.number_of_lights)]
            light_control.set_colors(self.memory)
            time.sleep(x / 10.0)

        time.sleep(90)

    def celebrate_animation(self):
        """
        An animation to celebrate something.
        It's a slow fade through the rainbow on the whole sculpture
        """

        for x in range(100):
            color = hsv_to_rgb(x / 100)
            self.memory = [color
                           for x in range(light_control.number_of_lights)]
            light_control.set_colors(self.memory)

        time.sleep(5)

    def draw(self, state):
        if state.e_stop:
            self.emergency_stop_animation()

        self.set_light_pattern_from_knife(state)

        self._draw(state)

    def _draw(self, state):
        h, s, v = state.slide, state.minipot, state.megapot
        rgb = hsv_to_rgb(h, s, v)
        flat_toggles = flatten(state.toggles)[:light_control.number_of_lights]
        for idx, tog in enumerate(flat_toggles):
            if tog:
                self.memory[idx] = rgb

        light_control.set_colors(self.memory)


class SimonScheme(object):
    """
    Only correctly illuminate the toggles that are in the state that the
    computer has decided it wants. The others will be red
    """

    def randomize_wanted_toggles(self):
        self.wanted_toggles = [random.choice(1, 0) for _ in range(25)]

    def __init__(self):
        self.memory = [[255, 0, 0]
                       for _ in range(light_control.number_of_lights)]
        self.randomize_wanted_toggles()

    def _draw(self, state):
        h, s, v = state.slide, state.minipot, state.megapot
        rgb = hsv_to_rgb(h, s, v)
        flat_toggles = flatten(state.toggles)[:light_control.number_of_lights]
        perfect = True
        for idx, tog in enumerate(flat_toggles):
            if tog == self.wanted_toggles[idx]:
                self.memory[idx] = rgb
            else:
                self.memory[idx] = [255, 0, 0]
                perfect = False

        light_control.set_colors(self.memory)

        if perfect:
            self.celebrate_animation()
            self.randomize_wanted_toggles()
