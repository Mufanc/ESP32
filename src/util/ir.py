from math import ceil
from time import sleep_us

from machine import Pin


# https://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol
class Receiver(object):

    def __init__(self, pin: int, callback):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.callback = callback
        self.last_triggered = 0
        self.buffer = []
        self.last_received = []

    def activate(self):
        self.pin.irq(self.handler, Pin.IRQ_FALLING)

    def check_output(self):
        if len(self.buffer) < 32:
            return

        code = []
        n = 0

        for i, x in enumerate(self.buffer):
            n |= x << (i % 8)

            if (i + 1) % 8 == 0:
                code.append(n)
                n = 0

        if (code[0] ^ code[1]) != 0xFF or (code[2] ^ code[3]) != 0xFF:
            print(f'invalid code received: {code}')
            return

        self.last_received = code[::2]
        self.callback(self.last_received, False)

    def handler(self, pin: Pin):
        base = 562.5
        interval = 281

        n = ceil(4 * base / interval)

        sleep_us(13500)

        buffer = []

        while True:
            buffer.append(pin.value())

            if sum(buffer[-n:]) == n:
                break

            sleep_us(interval)

        decode = []

        for num in buffer:
            if num and len(decode):
                decode[-1] += 1
            else:
                decode.append(0)

        self.buffer = [1 if x > 2 else 0 for x in decode if x][:32]
        self.check_output()
