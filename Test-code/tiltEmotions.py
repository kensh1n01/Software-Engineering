#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSC2674/2755 - Task C (2): tiltEmotions.py
- Reads pitch/roll/yaw to classify orientation into 5 moods + special flip mood
- Displays brief animated sequence for each mood (updates only on zone change)
- Detects rapid flipping (|Δroll|>60° within 0.5s) -> special MoodEmo6
- Joystick middle: pause/resume

Author: <Your Name>, <Your Student ID>
"""

import time
from math import fabs
try:
    from sense_hat import SenseHat, ACTION_PRESSED
except ImportError:
    from sense_emu import SenseHat, ACTION_PRESSED

# Reuse simple colour palette
BLACK = [0,0,0]; FACE=[255,200,0]; EYE=[0,0,0]
MOUTH=[200,0,0]; TEAR=[64,180,255]; ANGRY=[255,50,10]
COOL=[120,200,255]; WOW=[255,255,255]; LOVE=[255,0,100]
BKG=[10,10,20]

def put(px,x,y,c):
    if 0<=x<8 and 0<=y<8: px[y*8+x]=c[:]

def face_base(col=FACE):
    p=[col[:] for _ in range(64)]
    for x in range(8):
        for y in range(8):
            if x in (0,7) or y in (0,7): put(p,x,y,BKG)
    return p

def eyes(p):
    put(p,2,2,EYE); put(p,5,2,EYE)

def smile(p):
    put(p,2,5,MOUTH); put(p,5,5,MOUTH); put(p,3,6,MOUTH); put(p,4,6,MOUTH)

def sad(p):
    put(p,2,6,MOUTH); put(p,5,6,MOUTH); put(p,3,5,MOUTH); put(p,4,5,MOUTH)

def wow(p):
    put(p,3,5,WOW); put(p,4,5,WOW); put(p,3,6,WOW); put(p,4,6,WOW)

def angry(p):
    put(p,1,1,ANGRY); put(p,2,1,ANGRY); put(p,5,1,ANGRY); put(p,6,1,ANGRY)

def sunglasses(p):
    for x in range(1,3): put(p,x,2,COOL)
    for x in range(5,7): put(p,x,2,COOL)
    for x in range(2,6): put(p,x,3,COOL)

def heart(p):
    for (ox) in (1,5):
        put(p,ox,2,LOVE); put(p,ox+1,2,LOVE); put(p,ox,3,LOVE); put(p,ox+1,3,LOVE)

def build_frames(kind):
    # five baseline moods + special:
    # forward=Happy, back=Sad, left=Angry, right=Cool, flat=Surprised, special=Love fireworks
    frames=[]
    if kind=="forward":   # Happy (subtle bounce)
        p1=face_base(); eyes(p1); smile(p1)
        p2=face_base(); put(p2,2,1,EYE); put(p2,5,1,EYE); smile(p2)
        frames=[p1,p2,p1]
    elif kind=="back":    # Sad (teardrop)
        p1=face_base(); eyes(p1); sad(p1); put(p1,6,4,TEAR)
        p2=face_base(); eyes(p2); sad(p2); put(p2,6,5,TEAR)
        p3=face_base(); eyes(p3); sad(p3)
        frames=[p1,p2,p3]
    elif kind=="left":    # Angry (flash)
        p1=face_base(); angry(p1); eyes(p1)
        p2=[ANGRY[:] for _ in range(64)]
        p3=face_base(); angry(p3); eyes(p3)
        frames=[p1,p2,p3]
    elif kind=="right":   # Cool (tilt glasses)
        p1=face_base(); sunglasses(p1)
        p2=face_base(); sunglasses(p2); put(p2,1,4,COOL)
        frames=[p1,p2,p1]
    elif kind=="flat":    # Surprised
        p1=face_base([255,230,120]); put(p1,2,2,WOW); put(p1,5,2,WOW); wow(p1)
        p2=face_base([255,220,110]); put(p2,2,2,WOW); put(p2,5,2,WOW)
        frames=[p1,p2,p1]
    elif kind=="special": # Love fireworks
        p1=face_base([255,225,150]); heart(p1); smile(p1)
        p2=face_base([255,210,140]); heart(p2); put(p2,0,0,LOVE); put(p2,7,7,LOVE)
        p3=face_base([255,200,130]); heart(p3); put(p3,7,0,LOVE); put(p3,0,7,LOVE)
        frames=[p1,p2,p3,p2]
    return frames

class TiltEmotions:
    def __init__(self):
        self.sense = SenseHat()
        self.sense.clear()
        self.paused = False
        self.zone = None
        self.last_roll = None
        self.last_roll_ts = None

        self.sense.stick.direction_middle = self._on_joy

    def _on_joy(self, event):
        if event.action == ACTION_PRESSED:
            self.paused = not self.paused

    def _read_orientation(self):
        o = self.sense.get_orientation_degrees()
        # normalize to [-180,180] for roll
        pitch = o["pitch"]
        roll = o["roll"]
        yaw = o["yaw"]
        return pitch, roll, yaw

    def _zone_from_angles(self, pitch, roll):
        # deadband ±15 for flat; threshold 20deg for tilts
        if abs(pitch) < 15 and abs((roll if roll<=180 else roll-360)) < 15:
            return "flat"
        if pitch > 20:
            return "forward"
        if pitch < -20:
            return "back"
        # Convert roll to signed
        r = roll if roll <= 180 else roll - 360
        if r > 20:
            return "right"
        if r < -20:
            return "left"
        return "flat"

    def _rapid_flip(self, roll):
        now = time.monotonic()
        r = roll if roll <= 180 else roll - 360
        if self.last_roll is None:
            self.last_roll, self.last_roll_ts = r, now
            return False
        dt = now - self.last_roll_ts
        dr = abs(r - self.last_roll)
        self.last_roll, self.last_roll_ts = r, now
        return (dr > 60.0) and (dt <= 0.5)

    def show_sequence(self, frames, fps=6):
        for f in frames:
            self.sense.set_pixels(f)
            time.sleep(1.0 / fps)

    def run(self):
        try:
            while True:
                pitch, roll, yaw = self._read_orientation()
                if self._rapid_flip(roll):
                    if not self.paused:
                        self.show_sequence(build_frames("special"))
                    continue

                z = self._zone_from_angles(pitch, roll)
                if z != self.zone:
                    self.zone = z
                    if not self.paused:
                        self.show_sequence(build_frames(z), fps=5)
                else:
                    # keep screen steady to avoid flicker
                    time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            self.sense.clear()

if __name__ == "__main__":
    TiltEmotions().run()
