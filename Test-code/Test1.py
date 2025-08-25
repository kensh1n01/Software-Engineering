#!/usr/bin/env python3
# Task C - Emotion Display with Joystick & Motion
# Author: <Your Name> (<Student ID>)

import time, threading, math, collections
from datetime import datetime

try:
    from sense_hat import SenseHat
except Exception:
    # Tiny dummy for local dev (does not draw LEDs)
    class SenseHat:
        def __init__(self):
            class Stick: pass
            self.stick = Stick()
            self.stick.direction_up = None
            self.stick.direction_down = None
            self.stick.direction_left = None
            self.stick.direction_right = None
            self.stick.direction_middle = None
            self.low_light = False
        def set_pixels(self, px): print("[LED] frame")
        def clear(self, c=(0,0,0)): pass
        def get_orientation_degrees(self): return {"pitch":0,"roll":0,"yaw":0}
        def get_accelerometer_raw(self): return {"x":0,"y":0,"z":1}
        def show_message(self,*args,**kwargs): print("[LED] msg:", args[0])

# ---------- helpers ----------
def clamp(v,a,b): return max(a, min(b, v))

# 8x8 helpers
def solid(color):
    return [color]*64

def blend(c1, c2, t):
    return tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))

def ring(color, bg=(0,0,0), r=3):
    """simple circle-ish ring"""
    idx = []
    for y in range(8):
        for x in range(8):
            dx, dy = x-3.5, y-3.5
            d = math.sqrt(dx*dx+dy*dy)
            idx.append(color if abs(d-r) < 0.7 else bg)
    return idx

def blink(eye_color, bg=(0,0,0)):
    """two-eye blink frames"""
    B = bg; E = eye_color
    open_eye = [B]*64
    for x in (2,5):
        for y in (2,3):
            open_eye[y*8+x] = E
    closed = [B]*64
    for x in (2,5):
        closed[3*8+x] = E
    return [open_eye, closed, open_eye]

# ---------- emotion frames (≥6 emotions, ≥3 frames each, ≥3 colours overall) ----------
Red     = (255, 0, 0)
Green   = (0, 255, 0)
Blue    = (0, 128, 255)
Yellow  = (255, 220, 0)
Purple  = (240, 0, 255)
Orange  = (255, 140, 0)
Black   = (0, 0, 0)
Cyan    = (0, 230, 230)

def mouth(smile=True, color=G, bg=BK):
    px = [bg]*64
    y = 5 if smile else 6
    xs = range(1,7)
    for x in xs: px[y*8+x] = color
    if smile:
        px[4*8+2] = color; px[4*8+5] = color
    else:
        px[6*8+1] = color; px[6*8+6] = color
    # eyes
    for x in (2,5): px[2*8+x] = Y
    return px

def angry(color=R):
    a = mouth(smile=False, color=color)
    a[1*8+2] = color; a[1*8+5] = color  # brows
    return a

def surprise():
    px = [BK]*64
    for x in (2,5): px[2*8+x] = Y
    for y in (4,5): 
        for x in (3,4): px[y*8+x] = Cyan
    return px

EMOTIONS = [
    ("Happy",    [mouth(True, Green), ring(Green, r=2), mouth(True, blend(Green, Yellow, 0.3))]),
    ("Sad",      [mouth(False, Blue), ring(Blue, r=2), mouth(False, blend(Blue, Cyan, 0.4))]),
    ("Angry",    [angry(Red), ring(Red, r=3), angry(blend(Red, Orange, 0.4))]),
    ("Calm",     [solid((5,30,5)), *blink(Yellow)]),
    ("Surprised",[surprise(), ring(Yellow, r=2), surprise()]),
    ("Confused", [ring(Purple, r=1), ring(Purple, r=2), ring(Purple, r=3)]),
]
EMO_NAMES = [n for n,_ in EMOTIONS]

# ---------- controller ----------
class EmotionApp:
    ROTATE_SEC = 0.25              # frame duration within an emotion
    SLEEP_AFTER = 20.0             # idle -> display sleep (dims)
    FLIP_ANGLE = 60.0              # special reaction threshold
    FLIP_WINDOW = 0.5              # seconds

    def __init__(self):
        self.s = SenseHat()
        self.s.low_light = False
        self._stop = threading.Event()
        self._paused = False
        self._idx = 0               # current emotion
        self._frame_i = 0
        self._last_input = time.time()
        self._sleeping = False
        self._last_zone = None
        self._accel_hist = collections.deque(maxlen=50)  # (t, pitch)

        # joystick
        try:
            self.s.stick.direction_up = self._on_up
            self.s.stick.direction_down = self._on_down
            self.s.stick.direction_left = self._on_left
            self.s.stick.direction_right = self._on_right
            self.s.stick.direction_middle = self._on_middle
        except Exception:
            pass

    # ----- joystick -----
    def _touch(self):
        self._last_input = time.time()
        if self._sleeping:
            self._sleeping = False
            self.s.low_light = False
            self.s.show_message("WAKE", scroll_speed=0.05)

    def _on_up(self, event=None):
        self._touch()
        self._idx = (self._idx + 1) % len(EMOTIONS)
        self._frame_i = 0

    def _on_down(self, event=None):
        self._touch()
        self._idx = (self._idx - 1) % len(EMOTIONS)
        self._frame_i = 0

    def _on_left(self, event=None):
        self._touch()
        self._paused = not self._paused
        self.s.show_message("PAUSE" if self._paused else "PLAY", scroll_speed=0.05)

    def _on_right(self, event=None):
        self._touch()
        # quick flash to indicate next-speed (just a UX nicety)
        self.s.set_pixels(solid((20,20,20)))

    def _on_middle(self, event=None):
        self._touch()
        # jump to Happy
        self._idx = 0
        self._frame_i = 0
        self.s.show_message(EMO_NAMES[self._idx], scroll_speed=0.05)

    # ----- mapping tilt -> emotion zone -----
    def _zone_from_tilt(self, pitch, roll):
        """
        Map device tilt to emotion indices. Smooth zones so it feels stable.
        pitch: nose up/down, roll: left/right
        """
        # zones: 6 slices in 360° plane of (pitch, roll) magnitude/angle
        angle = (math.degrees(math.atan2(roll, pitch)) + 360.0) % 360.0
        sector = int(angle // 60)  # 0..5
        return sector

    def _special_flip_triggered(self):
        """Detect rapid pitch change > 60° within FLIP_WINDOW seconds."""
        now = time.time()
        # record latest pitch
        o = self.s.get_orientation_degrees()
        pitch = float(o.get("pitch", 0.0))
        self._accel_hist.append((now, pitch))

        # check window
        earliest = now - self.FLIP_WINDOW
        recent = [p for (t,p) in self._accel_hist if t >= earliest]
        if len(recent) >= 2:
            if max(recent) - min(recent) > self.FLIP_ANGLE:
                return True
        return False

    def _change_animation(self):
        """Unique animation when emotion changes (no flicker)."""
        # simple pulse: blend from black -> current color ring
        _, frames = EMOTIONS[self._idx]
        base = frames[self._frame_i % len(frames)]
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            eased = [blend((0,0,0), px, t) for px in base]
            self.s.set_pixels(eased)
            time.sleep(0.05)

    def _special_reaction(self):
        """Triggered by fast flip."""
        for i in range(3):
            self.s.set_pixels(solid((255,255,255)))
            time.sleep(0.05)
            self.s.clear()

    def run(self):
        self.s.show_message("TASK C", scroll_speed=0.05)
        try:
            while not self._stop.is_set():
                now = time.time()

                # Sleep/dim after inactivity
                if (now - self._last_input) > self.SLEEP_AFTER:
                    if not self._sleeping:
                        self._sleeping = True
                        self.s.low_light = True
                        self.s.clear()
                    # stay dim until user input or movement special
                else:
                    self.s.low_light = False

                # Read orientation for tilt mapping & flip detection
                orient = self.s.get_orientation_degrees()
                pitch = float(orient.get("pitch", 0.0))
                roll  = float(orient.get("roll", 0.0))

                if self._special_flip_triggered():
                    self._touch()
                    self._special_reaction()

                # Update emotion from tilt zones (only if not paused)
                if not self._paused:
                    zone = self._zone_from_tilt(pitch, roll)
                    if zone != self._last_zone:
                        self._last_zone = zone
                        self._idx = zone % len(EMOTIONS)
                        self._frame_i = 0
                        self._change_animation()

                # Draw current frame (no flicker: set_pixels once)
                name, frames = EMOTIONS[self._idx]
                frame = frames[self._frame_i % len(frames)]
                self.s.set_pixels(frame)

                # Next frame (if not paused)
                if not self._paused:
                    self._frame_i += 1

                # small, stable cadence
                time.sleep(self.ROTATE_SEC)
        except KeyboardInterrupt:
            pass
        finally:
            self.s.clear()

if __name__ == "__main__":
    EmotionApp().run()
