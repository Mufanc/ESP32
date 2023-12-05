from time import sleep_us
from math import log2

from machine import Pin, PWM


class Beeper(object):

    A = 440
    FREQ_STEP = 2 ** (1 / 12)

    def __init__(self, pin: int):
        self.pin = PWM(Pin(pin, Pin.OUT))
        self.stopped = True
        self.mute(0)

    def note(self, freq, dur, skip):
        self.pin.freq(freq)

        if skip:
            self.pin.duty(512)
            sleep_us(int(dur))
        else:
            r, n = 0.8, 10

            self.pin.duty(512)
            sleep_us(int(dur * r))

            # for i in range(n):
            #     self.pin.duty(int(30 - 3 * i))
            #     sleep_us(int(dur * (1 - r) / n))

            self.pin.duty(0)
            sleep_us(int(dur * (1 - r)))

    def mute(self, dur):
        self.pin.duty(0)
        sleep_us(int(dur))

    def get_freqs(self, tonality: str):
        is_major = tonality[0].isupper()

        first = -9 if is_major else 0
        offset = 2 if is_major else 0

        # FREQS = [262, 294, 330, 349, 392, 440, 494]
        half_raise = int(tonality.endswith('#'))
        full_raise = 'cdefgab'.index(tonality[0].lower())

        relations = [2, 1, 2, 2, 1, 2, 2]
        base = [first]

        for i in range(6):
            base.append(base[-1] + relations[(i + offset) % 7])

        return [self.FREQ_STEP ** (half_raise + full_raise + base[i]) * self.A for i in range(7)]

    def play(self, sheet: str, bpm: int = 90, tonality: str = 'C'):
        self.stopped = False

        freqs = self.get_freqs(tonality)

        qr = 60 * 1000 * 1000 / bpm  # 1/4
        fa = 1
        da, daa = 1, 1
        skip = False

        try:
            for ch in sheet:
                if ch == '[':
                    da /= 2
                elif ch == ']':
                    da *= 2
                elif ch == '(':
                    skip = True
                elif ch == ')':
                    skip = False
                elif ch == '+':
                    fa *= 2
                elif ch == '-':
                    fa /= 2
                elif ch == '.':
                    daa = 2 - 2 ** (log2(2 - daa) - 1)
                elif ch == '~':
                    daa += 1
                elif ch == '^':
                    fa *= self.FREQ_STEP
                elif ch == '_':
                    fa /= self.FREQ_STEP
                elif ch in (' ', '\n'):
                    pass
                elif ch == '0':
                    self.mute(qr * da)
                else:
                    self.note(int(freqs[int(ch) - 1] * fa), qr * da * daa, skip)
                    daa = 1
                    fa = 1

                if self.stopped:
                    break
        finally:
            self.pin.duty(0)
            self.stopped = True

    def is_playing(self):
        return not self.stopped

    def stop(self):
        self.stopped = True
