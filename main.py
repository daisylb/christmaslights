import machine
import neopixel
import math
from random import randint
import utime

# from here: https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix
gamma_lookup = [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]


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


FPS = 60
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

def gamma(color):
    return (gamma_lookup[color[0]], gamma_lookup[color[1]], gamma_lookup[color[2]])

animations = [Animation(randint(0, FPS * 3)) for _ in range(0, 50)]

for frame_num in animation_frames():
    np = neopixel.NeoPixel(machine.Pin(15), 50)
    for i, a in enumerate(animations):
        if a.is_expired(frame_num):
            a = Animation(frame_num)
            animations[i] = a
        np[i] = gamma(a.get_frame(frame_num))
    np.write()
