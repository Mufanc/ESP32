from math import log2
from time import sleep_us

from machine import Pin, PWM

from util.scheduler import Scheduler


class Beep(object):

    A = 440
    FREQ_STEP = 2 ** (1 / 12)

    def __init__(self, pin: int, screen=None):
        self.pin = PWM(Pin(pin, Pin.OUT))
        self.stopped = True
        self._mute(0)
        self.screen = screen

    def _note(self, freq, dur, skip):
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

    def _mute(self, dur):
        self.pin.duty(0)
        sleep_us(int(dur))

    def _get_freqs(self, tonality: str):
        is_major = tonality[0].isupper()

        first = -9 if is_major else 0
        offset = 2 if is_major else 0

        half_raise = int(tonality.endswith('#'))
        full_raise = 'cdefgab'.index(tonality[0].lower())

        relations = [2, 1, 2, 2, 1, 2, 2]
        base = [first]

        for i in range(6):
            base.append(base[-1] + relations[(i + offset) % 7])

        return [self.FREQ_STEP ** (half_raise + full_raise + base[i]) * self.A for i in range(7)]

    def _update_state(self, ch):
        if self.screen:
            self.screen.char_at(ch, self.screen.char_width - 2, self.screen.char_height - 2)

    def _init_timer(self):
        self.screen.char_at('0', self.screen.char_width - 7, self.screen.char_height - 2)
        self.screen.char_at('0', self.screen.char_width - 6, self.screen.char_height - 2)
        self.screen.char_at(':', self.screen.char_width - 5, self.screen.char_height - 2)
        self.screen.char_at('0', self.screen.char_width - 4, self.screen.char_height - 2)
        self.screen.char_at('0', self.screen.char_width - 3, self.screen.char_height - 2)

    def _update_timer(self, seconds):
        s1 = seconds % 10
        self.screen.char_at(str(s1), self.screen.char_width - 3, self.screen.char_height - 2)

        if s1 != 0:
            return

        s0 = seconds // 10
        self.screen.char_at(str(s0), self.screen.char_width - 4, self.screen.char_height - 2)

        if s0 != 0:
            return

        m1 = seconds // 60
        self.screen.char_at(str(m1), self.screen.char_width - 6, self.screen.char_height - 2)

    def play(self, sheet: str, bpm: int = 90, key: str = 'C', name: str = ''):
        self.screen.message(f'{name}\n1={key} {bpm}BPM')

        seconds = 0
        scheduler = Scheduler.instance()

        def refresh_timer():
            nonlocal seconds

            if self.stopped:
                return

            seconds += 1
            self._update_timer(seconds)
            scheduler.call_later(refresh_timer, 1000, True)

        self._init_timer()
        scheduler.call_later(refresh_timer, 1000, True)

        self.stopped = False

        states = ['/', '-', '\\', '|']

        freqs = self._get_freqs(key)

        qr = 60 * 1000 * 1000 / bpm  # 1/4
        fa = 1
        da, daa = 1, 1
        skip = False

        try:
            for i, ch in enumerate(sheet):
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
                elif ch in (' ', '\n', '|'):
                    pass
                elif ch == '0':
                    self._mute(qr * da)

                    self._update_state(states[i % 4])
                else:
                    self._note(int(freqs[int(ch) - 1] * fa), qr * da * daa, skip)
                    daa = 1
                    fa = 1

                    self._update_state(states[i % 4])

                if self.stopped:
                    break

        finally:
            self.pin.duty(0)
            self.stop()

    def stop(self):
        self.stopped = True
        self.screen.clear()
        self._update_state('%')

    def is_playing(self):
        return not self.stopped
