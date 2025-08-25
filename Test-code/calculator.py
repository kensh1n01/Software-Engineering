#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSC2674/2755 (PIoT) — Task D
Sense HAT Number Calculations Pad

Controls (joystick):
- Up:    x = x + 1
- Down:  x = x - 1
- Left:  x = x * x
- Right: x = sqrt(x)
- Middle: reset x to default (4)

Always shows x on the LED matrix using a compact 3x5 font.
Flashes operation or error indicators briefly after each action.

Author: <Your Name>, <Your Student ID>
"""

from math import sqrt, isfinite
import time

# Try Sense HAT; fall back to sense_emu for off-device testing
try:
    from sense_hat import SenseHat, ACTION_PRESSED
except ImportError:
    from sense_emu import SenseHat, ACTION_PRESSED

# -----------------------------
# Small 3x5 font (fits up to 3 glyphs across 8x8 with 1px gaps)
# Each glyph: 3 columns x 5 rows, boolean matrix (1=lit)
# -----------------------------
FONT = {
    "0": ["111",
          "101",
          "101",
          "101",
          "111"],
    "1": ["010",
          "110",
          "010",
          "010",
          "111"],
    "2": ["111",
          "001",
          "111",
          "100",
          "111"],
    "3": ["111",
          "001",
          "111",
          "001",
          "111"],
    "4": ["101",
          "101",
          "111",
          "001",
          "001"],
    "5": ["111",
          "100",
          "111",
          "001",
          "111"],
    "6": ["111",
          "100",
          "111",
          "101",
          "111"],
    "7": ["111",
          "001",
          "010",
          "010",
          "010"],
    "8": ["111",
          "101",
          "111",
          "101",
          "111"],
    "9": ["111",
          "101",
          "111",
          "001",
          "111"],
    "-": ["000",
          "000",
          "111",
          "000",
          "000"],
    ".": ["000",
          "000",
          "000",
          "000",
          "010"],
    "E": ["111",
          "100",
          "111",
          "100",
          "111"],
    "R": ["110",
          "101",
          "110",
          "101",
          "101"],
    "O": ["111",
          "101",
          "101",
          "101",
          "111"],
    "F": ["111",
          "100",
          "110",
          "100",
          "100"],
}
# Colors
BLACK = [0, 0, 0]
FG = [255, 220, 0]     # default value color
OP = [0, 180, 255]     # operation flash color
ERR = [255, 40, 40]    # error flash color

def clear_buf(color=BLACK):
    return [color[:] for _ in range(64)]

def put(pixels, x, y, color):
    if 0 <= x < 8 and 0 <= y < 8:
        pixels[y*8 + x] = color[:]

def blit_glyph(pixels, glyph, x0, y0, color):
    rows = FONT.get(glyph)
    if not rows:
        return
    for y in range(5):
        for x in range(3):
            if rows[y][x] == "1":
                put(pixels, x0 + x, y0 + y, color)

def render_text_3x5(text, color=FG, y0=1, align="right"):
    """
    Render up to MAX 3 glyphs side-by-side on 8x8:
    - each glyph 3px wide + 1px gap except last
    - align right by default so numbers look natural
    """
    text = text[:3]  # cap to 3 glyphs (we preformat to fit)
    width = 3*len(text) + max(0, len(text)-1)*1
    if align == "right":
        x0 = 7 - width + 1  # right edge inclusive
    else:
        x0 = 0
    px = clear_buf()
    cursor = x0
    for i, ch in enumerate(text):
        blit_glyph(px, ch, cursor, y0, color)
        cursor += 3
        if i != len(text)-1:
            cursor += 1  # 1 px gap
    return px

def flash_message(sense, msg, color, t=0.35):
    px = render_text_3x5(msg, color=color)
    sense.set_pixels(px)
    time.sleep(t)

def format_value(x):
    """
    Produce a string that fits in ≤3 glyphs:
    Priority:
      - Integers in range -99..999 -> like "4","16","-3"
      - Otherwise one decimal if it fits: e.g., "-1.5","2.5","12." (we map trailing . to .)
      - Fallback: "OF" (overflow)
    """
    # Prefer integer if it's very close
    if abs(x - round(x)) < 1e-9:
        xi = int(round(x))
        s = str(xi)
        if len(s) <= 3:
            return s
    # try one decimal
    s = f"{x:.1f}"
    # remove leading zeros like "-0.5" stays "-0.5"
    if len(s) <= 3:
        return s
    # try no sign if small positive with two digits and dot
    if x >= 0:
        s = f"{x:.1f}".lstrip("+")
    if len(s) <= 3:
        return s
    return "OF"

class NumberPad:
    DEFAULT = 4.0

    def __init__(self):
        self.sense = SenseHat()
        self.sense.clear()
        self.sense.low_light = False
        self.x = self.DEFAULT
        # Bind joystick
        self.sense.stick.direction_up = self._on_up
        self.sense.stick.direction_down = self._on_down
        self.sense.stick.direction_left = self._on_left
        self.sense.stick.direction_right = self._on_right
        self.sense.stick.direction_middle = self._on_middle
        # Initial paint
        self._show_value()

    # ---- Rendering helpers ----
    def _show_value(self):
        s = format_value(self.x)
        color = FG if s != "OF" else ERR
        px = render_text_3x5(s, color=color)
        self.sense.set_pixels(px)

    def _flash_op(self, symbol):
        # brief blue flash to acknowledge operation
        flash_message(self.sense, symbol, OP, t=0.18)

    def _flash_err(self, code="ERR"):
        flash_message(self.sense, code, ERR, t=0.45)

    # ---- Operations ----
    def _on_up(self, e):
        if e.action != ACTION_PRESSED: return
        self.x += 1
        self._flash_op("+")
        self._show_value()

    def _on_down(self, e):
        if e.action != ACTION_PRESSED: return
        self.x -= 1
        self._flash_op("-")
        self._show_value()

    def _on_left(self, e):
        if e.action != ACTION_PRESSED: return
        # square; guard overly huge magnitudes
        nxt = self.x * self.x
        if not isfinite(nxt) or abs(nxt) > 1e9:
            self._flash_err("OF")
            return
        self.x = nxt
        self._flash_op("^")
        self._show_value()

    def _on_right(self, e):
        if e.action != ACTION_PRESSED: return
        if self.x < 0:
            self._flash_err("ERR")
            return
        self.x = sqrt(self.x)
        self._flash_op("√")
        self._show_value()

    def _on_middle(self, e):
        if e.action != ACTION_PRESSED: return
        self.x = self.DEFAULT
        self._flash_op("rst")
        self._show_value()

    # ---- Main loop ----
    def run(self):
        try:
            # Passive loop; event-driven. Keep process alive and re-draw value periodically
            # to satisfy "always show x" even after long idle (and recover from any glitches).
            while True:
                self._show_value()
                time.sleep(0.25)
        except KeyboardInterrupt:
            pass
        finally:
            self.sense.clear()

if __name__ == "__main__":
    NumberPad().run()
