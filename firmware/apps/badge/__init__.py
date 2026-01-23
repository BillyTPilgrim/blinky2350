import sys
import os
from badgeware import run, set_brightness, scroll_text, State, clamp

sys.path.insert(0, "/system/apps/badge")
os.chdir("/system/apps/badge")

state = {
    "text": "Hello, I'm a Blinky2350!",
    "font": "ignore",
    "brightness": 0.1
}

State.load("badge", state)

set_brightness(state["brightness"])
font_list = dir(rom_font)
font_index = font_list.index(state["font"])

scroll = scroll_text(state["text"], font_face=getattr(rom_font, state["font"]))

changed = False


def update():
    global state, scroll, changed, font_index

    if io.BUTTON_UP in io.pressed:
        state["brightness"] += 0.1

    if io.BUTTON_DOWN in io.pressed:
        state["brightness"] -= 0.1

    state["brightness"] = clamp(state["brightness"], 0.1, 1.0)

    if io.BUTTON_C in io.pressed:
        if font_index < len(font_list) - 1:
            font_index += 1
            changed = True

    if io.BUTTON_A in io.pressed:
        if font_index > 0:
            font_index -= 1
            changed = True

    if changed:
        state["font"] = font_list[font_index]
        scroll = scroll_text(state["text"], font_face=getattr(rom_font, state["font"]))
        changed = False

    set_brightness(state["brightness"])

    scroll()


def on_exit():
    State.save("badge", state)


if __name__ == "__main__":
    run(update=update, on_exit=on_exit)
