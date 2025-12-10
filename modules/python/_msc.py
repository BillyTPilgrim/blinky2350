from badgeware import screen, brushes, PixelFont, run
import blinky
import rp2
import math

display = blinky.Blinky()

rp2.enable_msc()

background = brushes.color(0, 0, 0)
white = brushes.color(35, 41, 37)


try:
        small_font = PixelFont.load("/system/assets/fonts/winds.ppf")
except OSError:
        small_font = None


class DiskMode():
    def __init__(self):
        self.transferring = False

    def draw(self):
        screen.brush = background
        screen.clear()

        if small_font:
                screen.font = small_font
                screen.brush = white
                center_text("USB", 0)

                screen.brush = white
                if self.transferring:
                        center_text("<<<", 7)
                else:
                        center_text("waiting", 7)


def center_text(text, y):
    w, h = screen.measure_text(text)
    screen.text(text, (screen.width / 2) - (w / 2), y)


def wrap_text(text, x, y):
    lines = text.splitlines()
    for line in lines:
        _, h = screen.measure_text(line)
        screen.text(line, x, y)
        y += h * 0.8


disk_mode = DiskMode()

def update():

    # set transfer state here
    disk_mode.transferring = rp2.is_msc_busy()

    # draw the ui
    disk_mode.draw()

    display.update()


run(update)
