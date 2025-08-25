#!/usr/bin/env python3

import time
import threading
from collections import deque

# Sense HAT import (supports emulator fallback when developing off-device)
try:
    from sense_hat import SenseHat, ACTION_PRESSED
except ImportError:  # Optional emulator support if you test on a laptop
    from sense_emu import SenseHat, ACTION_PRESSED

# Utilities
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# Basic colours (at least three per frame will be used)
BLACK = [0, 0, 0]
DIM = [5, 5, 5]
FACE = [255, 200, 0]      # yellow face
EYE = [0, 0, 0]           # black eyes
MOUTH = [200, 0, 0]       # red mouth
BLUSH = [255, 105, 97]    # coral
TEAR = [64, 180, 255]     # blue tear
ANGRY = [255, 50, 10]     # angry brow
COOL = [120, 200, 255]    # cyan sunglasses
LOVE = [255, 0, 100]      # pink heart
WOW = [255, 255, 255]     # white highlight
BKG = [10, 10, 20]        # subtle background

def blank():
    return [BLACK[:] for _ in range(64)]

def put(px, x, y, color):
    if 0 <= x < 8 and 0 <= y < 8:
        px[y*8 + x] = color[:]

def circle_face(base_color=FACE):
    p = [base_color[:] for _ in range(64)]
    # vignette border
    for x in range(8):
        for y in range(8):
            if x in (0,7) or y in (0,7):
                put(p, x, y, BKG)
    return p

def eyes(p, x1, x2, y=2, eye_color=EYE):
    put(p, x1, y, eye_color)
    put(p, x2, y, eye_color)

def mouth_line(p, y, x1=2, x2=5, color=MOUTH):
    for x in range(x1, x2+1):
        put(p, x, y, color)

def mouth_arc_smile(p, color=MOUTH):
    put(p, 2, 5, color); put(p, 5, 5, color)
    for x in range(3,5):
        put(p, x, 6, color)

def mouth_arc_sad(p, color=MOUTH):
    put(p, 2, 6, color); put(p, 5, 6, color)
    for x in range(3,5):
        put(p, x, 5, color)

def blush(p):
    put(p, 1, 3, BLUSH); put(p, 6, 3, BLUSH)

def tear(p):
    put(p, 6, 3, TEAR); put(p, 6, 4, TEAR)

def angry_brows(p):
    put(p, 1, 1, ANGRY); put(p, 2, 1, ANGRY)
    put(p, 5, 1, ANGRY); put(p, 6, 1, ANGRY)

def sunglasses(p):
    for x in range(1,3): put(p, x, 2, COOL)
    for x in range(5,7): put(p, x, 2, COOL)
    for x in range(2,5): put(p, x, 3, COOL)

def heart_eyes(p):
    # two small hearts as eyes
    for (ox) in (1,5):
        put(p, ox, 2, LOVE); put(p, ox+1, 2, LOVE)
        put(p, ox, 3, LOVE); put(p, ox+1, 3, LOVE)
        put(p, ox, 1, LOVE)

def wow_mouth(p):
    put(p, 3, 5, WOW); put(p, 4, 5, WOW)
    put(p, 3, 6, WOW); put(p, 4, 6, WOW)

# Emoji classes
class AnimatedEmoji:
    """Base class for a multi-frame emoji animation."""
    name = "Base"

    def frames(self):
        """Return list[ list[RGB]*64 ] of frames."""
        return []

    def fps(self):
        return 4  # default 4 FPS


class HappyEmoji(AnimatedEmoji):
    name = "Happy"
    def frames(self):
        F = []
        # Frame 1: smile + blush
        p1 = circle_face()
        eyes(p1, 2, 5); blush(p1); mouth_arc_smile(p1)
        F.append(p1)
        # Frame 2: wink left
        p2 = circle_face()
        put(p2, 2, 2, MOUTH)  # wink line
        put(p2, 5, 2, EYE)
        mouth_arc_smile(p2); blush(p2)
        F.append(p2)
        # Frame 3: big smile
        p3 = circle_face()
        eyes(p3, 2, 5); blush(p3)
        for y in (5,6):
            mouth_line(p3, y, 2, 5)
        F.append(p3)
        return F

class SadEmoji(AnimatedEmoji):
    name = "Sad"
    def frames(self):
        F=[]
        # Frame 1: sad arc + tear start
        p1 = circle_face()
        eyes(p1, 2, 5); mouth_arc_sad(p1); tear(p1)
        F.append(p1)
        # Frame 2: tear lower
        p2 = circle_face()
        eyes(p2, 2, 5); mouth_arc_sad(p2)
        put(p2, 6, 4, TEAR); put(p2, 6, 5, TEAR)
        F.append(p2)
        # Frame 3: double tear
        p3 = circle_face()
        eyes(p3, 2, 5); mouth_arc_sad(p3)
        put(p3, 1, 4, TEAR); put(p3, 1, 5, TEAR)
        put(p3, 6, 4, TEAR); put(p3, 6, 5, TEAR)
        F.append(p3)
        return F

class AngryEmoji(AnimatedEmoji):
    name = "Angry"
    def frames(self):
        F=[]
        # Frame 1: brows down
        p1 = circle_face()
        angry_brows(p1); eyes(p1, 2, 5); mouth_line(p1, 6, 2, 5, MOUTH)
        F.append(p1)
        # Frame 2: mouth open
        p2 = circle_face()
        angry_brows(p2); eyes(p2, 2, 5); mouth_line(p2, 5, 2, 5, ANGRY)
        F.append(p2)
        # Frame 3: red flash
        p3 = [ANGRY[:] for _ in range(64)]
        F.append(p3)
        return F
    def fps(self): return 6

class SurprisedEmoji(AnimatedEmoji):
    name = "Surprised"
    def frames(self):
        F=[]
        # Frame 1: wow eyes + round mouth
        p1 = circle_face()
        eyes(p1, 2, 2, 2, WOW); eyes(p1, 5, 5, 2, WOW)  # overwrite via helper misuse
        wow_mouth(p1)
        F.append(p1)
        # Frame 2: blink
        p2 = circle_face()
        put(p2, 2, 2, WOW); put(p2, 5, 2, WOW)
        put(p2, 3, 6, WOW); put(p2, 4, 6, WOW)
        F.append(p2)
        # Frame 3: glow
        p3 = circle_face([255,230,120])
        put(p3, 2, 2, WOW); put(p3, 5, 2, WOW)
        wow_mouth(p3)
        F.append(p3)
        return F

class CoolEmoji(AnimatedEmoji):
    name = "Cool"
    def frames(self):
        F=[]
        # Frame 1: sunglasses, smirk
        p1 = circle_face()
        sunglasses(p1); mouth_line(p1, 6, 3, 5, MOUTH)
        F.append(p1)
        # Frame 2: tilt shades
        p2 = circle_face()
        sunglasses(p2); put(p2, 1, 3, COOL)  # little motion
        mouth_line(p2, 6, 2, 4, MOUTH)
        F.append(p2)
        # Frame 3: sparkle
        p3 = circle_face()
        sunglasses(p3); mouth_line(p3, 6, 3, 5, [255, 80, 80])
        put(p3, 7, 0, WOW)
        F.append(p3)
        return F

class LoveEmoji(AnimatedEmoji):
    name = "Love"
    def frames(self):
        F=[]
        p1 = circle_face([255, 225, 150]); heart_eyes(p1); mouth_arc_smile(p1)
        F.append(p1)
        p2 = circle_face([255, 210, 130]); heart_eyes(p2); mouth_arc_smile(p2); put(p2, 0, 7, LOVE)
        F.append(p2)
        p3 = circle_face([255, 200, 120]); heart_eyes(p3); mouth_arc_smile(p3); put(p3, 7, 0, LOVE)
        F.append(p3)
        return F

class SleepFace(AnimatedEmoji):
    """Used for idle 'sleep mode'"""
    name = "Sleep"
    def frames(self):
        F=[]
        p = circle_face([180, 180, 190])
        # closed eyes
        put(p, 2, 2, DIM); put(p, 3, 2, DIM)
        put(p, 4, 2, DIM); put(p, 5, 2, DIM)
        mouth_line(p, 5, 3, 4, DIM)
        # tiny 'Z' in corner
        put(p, 6, 0, DIM); put(p, 7, 0, DIM); put(p, 6, 1, DIM); put(p, 7, 1, DIM)
        F += [p, p]  # two frames to satisfy multi-frame API
        return F
    def fps(self): return 2

# Animator Controller
class MoodAnimator:
    IDLE_TIMEOUT = 20.0  # seconds

    def __init__(self):
        self.sense = SenseHat()
        self.sense.clear()
        self.sense.low_light = False

        self.emojis = [
            HappyEmoji(), SadEmoji(), AngryEmoji(),
            SurprisedEmoji(), CoolEmoji(), LoveEmoji()
        ]
        self.index = 0
        self.paused = False
        self.sleeping = False
        self.last_input_ts = time.monotonic()

        # event queue for joystick
        self.events = deque()
        self._register_joystick()

        # worker thread
        self._stop = False
        self.worker = threading.Thread(target=self._run_loop, daemon=True)

    def _register_joystick(self):
        def on_event(event):
            if event.action != ACTION_PRESSED:
                return
            self.events.append(event.direction)
            self.last_input_ts = time.monotonic()

        self.sense.stick.direction_left = on_event
        self.sense.stick.direction_right = on_event
        self.sense.stick.direction_middle = on_event

    def start(self):
        self.worker.start()
        try:
            while self.worker.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        self._stop = True
        self.sense.clear()

    def _handle_events(self):
        woke = False
        while self.events:
            d = self.events.popleft()
            if self.sleeping:
                self.wake()
                woke = True
                # continue to consume but first wake; next events can act
            if d == "left":
                self.index = (self.index - 1) % len(self.emojis)
                self.paused = False
            elif d == "right":
                self.index = (self.index + 1) % len(self.emojis)
                self.paused = False
            elif d == "middle":
                self.paused = not self.paused
        return woke

    def sleep_if_idle(self):
        if self.sleeping:
            return
        if (time.monotonic() - self.last_input_ts) >= self.IDLE_TIMEOUT:
            self.sleep()

    def sleep(self):
        self.sleeping = True
        self.sense.low_light = True
        for frame in SleepFace().frames():
            self.sense.set_pixels(frame)
        # keep last sleep frame displayed

    def wake(self):
        self.sleeping = False
        self.sense.low_light = False

    def _run_loop(self):
        frame_i = 0
        while not self._stop:
            self._handle_events()
            self.sleep_if_idle()

            if not self.sleeping and not self.paused:
                emo = self.emojis[self.index]
                frames = emo.frames()
                if not frames:
                    frames = [blank()]
                frame = frames[frame_i % len(frames)]
                self.sense.set_pixels(frame)
                frame_i += 1
                time.sleep(1.0 / clamp(emo.fps(), 1, 12))
            else:
                time.sleep(0.05)

if __name__ == "__main__":
    MoodAnimator().start()
