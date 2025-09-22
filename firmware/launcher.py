import gc
import os
import time
import blinky2350
from picovector import HALIGN_CENTER, PicoVector, Transform
import math

import blinky_os

display = blinky2350.Blinky2350()


class App:
    ICONS = {
        "badge": "\uea67",
        "book_2": "\uf53e",
        "check_box": "\ue834",
        "cloud": "\ue2bd",
        "deployed-code": "\uf720",
        "description": "\ue873",
        "help": "\ue887",
        "water_full": "\uf6d6",
        "wifi": "\ue63e",
        "image": "\ue3f4",
        "info": "\ue88e",
        "format_list_bulleted": "\ue241",
        "joystick": "\uf5ee",
        "playing_cards": "\uf5dc"
    }
    DIRECTORY = "apps"
    DEFAULT_ICON = "description"
    ERROR_ICON = "help"  # TODO: have a reserved error icon

    def __init__(self, name):
        self._file = name
        self._meta = {
            "NAME": name,
            "ICON": App.DEFAULT_ICON,
            "DESC": ""
        }
        self.path = f"{name}/__main__"
        self._loaded = False

    def read_metadata(self):
        if self._loaded:
            return

        try:
            exec(open(f"{App.DIRECTORY}/{self._file}/__init__.py", "r").read(), self._meta)
        except SyntaxError:
            self._meta["ICON"] = App.ERROR_ICON
        self._loaded = True

    @property
    def name(self):
        self.read_metadata()
        return self._meta["NAME"]

    @property
    def icon(self):
        self.read_metadata()
        try:
            return App.ICONS[self._meta["ICON"]]
        except KeyError:
            return App.ICONS[App.ERROR_ICON]

    @property
    def desc(self):
        self.read_metadata()
        return self._meta["DESC"]

    @staticmethod
    def is_valid(file):
        try:
            open(f"{App.DIRECTORY}/{file}/__init__.py", "r")
            return True
        except OSError:
            return False


FONT_SIZE = 1

changed = False
transition = False
exited_to_launcher = False

state = {
    "selected_icon": "ebook",
    "running": "launcher",
    "selected_file": 0,
}

blinky_os.state_load("launcher", state)

if state["running"] != "launcher":
    blinky_os.launch(state["running"])

# Colours
BACKGROUND = display.create_pen(0, 0, 0)
FOREGROUND = display.create_pen(100, 100, 100)
HIGHLIGHT = display.create_pen(30, 30, 30)

# Pico Vector
vector = PicoVector(display.display)
t = Transform()
vector.set_font("Roboto-Medium-With-Material-Symbols.af", 20)
vector.set_font_align(HALIGN_CENTER)
vector.set_transform(t)

apps = [App(x) for x in os.listdir(App.DIRECTORY) if App.is_valid(x)]

MAX_PER_ROW = 1
MAX_PER_PAGE = 1
ICONS_TOTAL = len(apps)
MAX_PAGE = ICONS_TOTAL

WIDTH, HEIGHT = display.get_bounds()

LEFT_CORNER_LEDS = [(4, HEIGHT - 4)]

# Page layout
CENTRES = [20, 11]

CENTRE_X = WIDTH // 2
CENTRE_Y = HEIGHT // 2


def launch_transition():
    x, y = CENTRES
    app = apps[selected_index]

    for i in range(25):
        display.set_pen(BACKGROUND)
        display.clear()

        display.set_pen(FOREGROUND)
        vector.set_font_size(10 + i)
        vector.set_transform(t)
        vector.text(app.icon, x, y)

        t.reset()
        display.update()
        time.sleep(0.005)

    display.set_pen(BACKGROUND)
    display.clear()
    display.update()


transition_start_time = 0

def render(selected_index, previous_index, transition_start):
    global transition_start_time

    TRANSITION_TIME = 100
    TRANSITION_DISTANCE = 40
    TRANSITION_OUT_SPEED = 1.4

    display.set_pen(BACKGROUND)
    display.clear()
    display.set_pen(FOREGROUND)
    vector.set_font_size(10)
    vector.set_transform(t)

    if transition_start:
        transition_start_time = time.ticks_ms()

    # Bouncy bouncy icons
    ticks = time.ticks_ms()
    bounce = int(math.sin(ticks / 1000.0 * 12) * 2)

    # get the names of the previous and current apps
    app_current = apps[selected_index]
    app_previous = apps[previous_index]

    x, y = CENTRES
    y += bounce

    # transition from one icon to the next over a period of 100ms
    direction = selected_index > previous_index

    i = time.ticks_diff(ticks, transition_start_time)
    i = int(min(TRANSITION_TIME, i) / TRANSITION_TIME * TRANSITION_DISTANCE)

    curr_x = x - (TRANSITION_DISTANCE - i) if direction else x + (TRANSITION_DISTANCE - i)

    i *= TRANSITION_OUT_SPEED
    i = int(i)
    prev_x = x + i if direction else x - i

    vector.text(app_previous.icon, prev_x, y)
    vector.text(app_current.icon, curr_x, y)

    display.update()

    gc.collect()


def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


def launch_example(file):
    # ???
    # wait_for_user_to_release_buttons()
    launch_transition()

    time.sleep(1)

    file = f"{App.DIRECTORY}/{file}"

    for k in locals().keys():
        if k not in ("gc", "file", "blinky_os"):
            del locals()[k]

    gc.collect()

    blinky_os.launch(file)


def app_index(file):
    index = 0
    for app in apps:
        if app.path == file:
            return index
        index += 1
    return 0


selected_index = app_index(state["selected_file"])
previous_index = 0


while True:

    if display.pressed(blinky2350.BUTTON_B):
        launch_example(state["selected_file"])

    if display.pressed(blinky2350.BUTTON_C) and selected_index > 0:
        previous_index = selected_index
        selected_index -= 1
        changed = True
        print(apps[selected_index].name)

    if display.pressed(blinky2350.BUTTON_A) and selected_index < ICONS_TOTAL - 1:
        previous_index = selected_index
        selected_index += 1
        changed = True
        print(apps[selected_index].name)

    if changed:
        state["selected_file"] = apps[selected_index].path
        blinky_os.state_save("launcher", state)

    render(selected_index, previous_index, changed)
    changed = False
