import machine
import neopixel
import math
from random import randint
import utime


def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b


FPS = 45
US_PER_FRAME = 1000000 // FPS


def color_mul(color, mul):
    return (int(color[0] * mul), int(color[1] * mul), int(color[2] * mul))


class Animation:
    __slots__ = ("start", "duration", "target_colour")

    def __init__(self, current_frame):
        self.start = current_frame
        self.duration = randint(FPS * 2, FPS * 3)
        self.target_colour = hsv2rgb(randint(0, 360), 1, 1)

    def is_expired(self, current_frame):
        return self.start + self.duration * 2 <= current_frame

    def get_frame(self, current_frame):
        mul = (current_frame - self.start) / self.duration
        if mul < 0:
            return (0, 0, 0)
        if mul >= 1:
            mul = 2 - mul
        return color_mul(self.target_colour, mul)


def animation_frames():
    frame = 0
    while True:
        frame_start = utime.ticks_us()
        yield frame
        frame += 1
        next_frame_start = utime.ticks_add(frame_start, US_PER_FRAME)
        diff = utime.ticks_diff(next_frame_start, utime.ticks_us())
        if frame % 100 == 0:
            print(diff)
        if diff > 0:
            utime.sleep_us(diff)


animations = [Animation(randint(0, FPS * 3)) for _ in range(0, 50)]

for frame_num in animation_frames():
    np = neopixel.NeoPixel(machine.Pin(15), 50)
    for i, a in enumerate(animations):
        if a.is_expired(frame_num):
            a = Animation(frame_num)
            animations[i] = a
        np[i] = a.get_frame(frame_num)
    np.write()
