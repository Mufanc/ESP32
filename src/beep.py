from time import sleep_us

from machine import Pin, PWM


class Beeper(object):

    FREQS = [262, 294, 330, 349, 392, 440, 494]
    FREQ_SINGLE = 2 ** (1 / 12)

    def __init__(self, pin: int):
        self.pin = PWM(Pin(pin, Pin.OUT))
        self.stopped = False
        self.mute(0)

    def play(self, freq, dur, skip):
        self.pin.freq(freq)

        if skip:
            self.pin.duty(30)
            sleep_us(int(dur))
        else:
            r, n = 0.8, 10

            self.pin.duty(30)
            sleep_us(int(dur * r))

            for i in range(n):
                self.pin.duty(int(30 - 3 * i))
                sleep_us(int(dur * (1 - r) / n))

    def mute(self, dur):
        self.pin.duty(0)
        sleep_us(int(dur))

    def music(self, sheet: str, bpm: int = 90):
        qr = 60 * 1000 * 1000 / bpm  # 1/4
        fa = 1
        da, dar = 1, 0
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
                    dar = da
                    da *= 1.5
                elif ch == '^':
                    fa *= self.FREQ_SINGLE
                elif ch == '_':
                    fa /= self.FREQ_SINGLE
                elif ch in (' ', '\n'):
                    pass
                elif ch == '0':
                    self.mute(qr * da)
                else:
                    self.play(int(self.FREQS[int(ch) - 1] * fa), qr * da, skip)

                    if dar != 0:
                        da = dar
                        dar = 0

                    fa = 1

                if self.stopped:
                    break
        finally:
            self.pin.duty(0)

    def stop(self):
        self.stopped = True
