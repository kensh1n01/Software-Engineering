#!/usr/bin/env python3
# Task C - tiltEmotions.py
# Author: <Your Name> (<Student ID>)
#
# Requirements covered:
# - Read pitch/roll/yaw; map orientation to mood zones.
# - Brief animation when entering a new zone (update only on change -> avoid flicker).
# - Joystick Middle toggles pause/resume.
# - Special reaction when a rapid flip (>60° within 0.5s) is detected.
# - Looks good, uses multiple colours, smooth updates.

import time, math, collections
try:
    from sense_hat import SenseHat
except Exception:
    class SenseHat:
        def __init__(self):
            class Stick: ...
            self.stick = Stick()
            self.stick.direction_middle = None
            self.low_light = False
        def set_pixels(self, px): print("[LED] frame")
        def clear(self, c=(0,0,0)): pass
        def get_orientation_degrees(self): return {"pitch":0,"roll":0,"yaw":0}
        def show_message(self, msg, **kw): print("[LED] msg:", msg)

# colours
Black  = (0,0,0)
White  = (255,255,255)
Green  = (0,255,0)
Blue   = (0,128,255)
Red    = (255,0,0)
Yellow = (255,220,0)
Orange = (255,140,0)
Purple = (200,0,255)
Cyan   = (0,230,230)

def solid(c): return [c]*64
def put(px,x,y,c):
    if 0<=x<8 and 0<=y<8: px[y*8+x]=c

def arrow(direction, fg, bg=Black):
    px = solid(bg)
    # simple 8x8 arrows
    if direction=="up":
        for i in range(8): put(px,3,7-i,fg); put(px,4,7-i,fg)
        for dx in (-2,-1,0,1,2): put(px,3+dx,0,fg)
    elif direction=="down":
        for i in range(8): put(px,3,i,fg); put(px,4,i,fg)
        for dx in (-2,-1,0,1,2): put(px,3+dx,7,fg)
    elif direction=="left":
        for i in range(8): put(px,7-i,3,fg); put(px,7-i,4,fg)
        for dy in (-2,-1,0,1,2): put(px,0,3+dy,fg)
    elif direction=="right":
        for i in range(8): put(px,i,3,fg); put(px,i,4,fg)
        for dy in (-2,-1,0,1,2): put(px,7,3+dy,fg)
    elif direction=="flat":
        for x in range(1,7): put(px,x,3,fg); put(px,x,4,fg)
    return px

def pulse(base_color, steps=5):
    frames=[]
    for t in range(steps):
        k = t/(steps-1)
        c = (int(base_color[0]*k), int(base_color[1]*k), int(base_color[2]*k))
        frames.append(solid(c))
    return frames

class TiltEmotions:
    FRAME_SEC   = 0.08
    FLIP_ANGLE  = 60.0
    FLIP_WINDOW = 0.5

    ZONES = [
        ("Forward", "up",    Green),
        ("Back",    "down",  Blue),
        ("Left",    "left",  Orange),
        ("Right",   "right", Red),
        ("Flat",    "flat",  Yellow),
        ("Diagonal","right", Purple),  # catch-all
    ]

    def __init__(self):
        self.sense = SenseHat()
        self.paused = False
        self.last_zone = None
        self.accel_hist = collections.deque(maxlen=60)  # (t, pitch)
        try:
            self.sense.stick.direction_middle = self.on_middle
        except Exception:
            pass

    def on_middle(self, event=None):
        self.paused = not self.paused
        self.sense.show_message("PAUSE" if self.paused else "PLAY", scroll_speed=0.05)

    # zone mapping from pitch/roll
    def zone_from_orientation(self, pitch, roll):
        # normalize to -180..+180
        p = ((pitch+180)%360)-180
        r = ((roll+180)%360)-180
        ap, ar = abs(p), abs(r)
        if ap > 30 and ap >= ar and p > 0:   return 0  # Forward
        if ap > 30 and ap >= ar and p < 0:   return 1  # Back
        if ar > 30 and ar >  ap and r > 0:   return 2  # Left
        if ar > 30 and ar >  ap and r < 0:   return 3  # Right
        if ap < 15 and ar < 15:              return 4  # Flat
        return 5  # Diagonal / otherwise

    def special_flip_triggered(self, pitch):
        now = time.time()
        self.accel_hist.append((now, pitch))
        earliest = now - self.FLIP_WINDOW
        recent = [p for (t,p) in self.accel_hist if t >= earliest]
        if len(recent) >= 2 and (max(recent)-min(recent)) > self.FLIP_ANGLE:
            return True
        return False

    def play_zone_animation(self, zone_idx):
        name, arrow_dir, color = self.ZONES[zone_idx]
        # brief, distinct animation: pulse + arrow
        for f in pulse(color, steps=5):
            self.sense.set_pixels(f)
            time.sleep(0.04)
        self.sense.set_pixels(arrow(arrow_dir, color))

    def special_reaction(self):
        # bright white flash x3
        for _ in range(3):
            self.sense.set_pixels(solid(White)); time.sleep(0.05)
            self.sense.clear(); time.sleep(0.03)

    def run(self):
        self.sense.show_message("Task C: tiltEmotions", scroll_speed=0.05)
        try:
            while True:
                o = self.sense.get_orientation_degrees()
                pitch = float(o.get("pitch", 0.0))
                roll  = float(o.get("roll", 0.0))

                if self.special_flip_triggered(pitch):
                    self.special_reaction()

                if not self.paused:
                    z = self.zone_from_orientation(pitch, roll)
                    if z != self.last_zone:
                        self.last_zone = z
                        self.play_zone_animation(z)

                # hold current frame (no redraws -> no flicker)
                time.sleep(self.FRAME_SEC)
        except KeyboardInterrupt:
            pass
        finally:
            self.sense.clear()

if __name__ == "__main__":
    TiltEmotions().run()
