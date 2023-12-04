from time import ticks_us, ticks_diff

from machine import Pin


# https://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol
class Receiver(object):

    CLASSIFIER = [13500, 1125, 2250, 11250]

    TYPE_LEADING = 0
    TYPE_0 = 1
    TYPE_1 = 2
    TYPE_REPEAT = 3

    STATE_IDLE = 0
    STATE_RECEIVING = 1

    def __init__(self, pin: int, callback):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.callback = callback
        self.last_triggered = 0
        self.state = self.STATE_IDLE
        self.buffer = []
        self.last_received = []

    def activate(self):
        self.pin.irq(self.handler, Pin.IRQ_FALLING)

    def classify(self, delta: int):
        return min((abs(x - delta), i) for i, x in enumerate(self.CLASSIFIER))[1]

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

    def handler(self, pin):
        now = ticks_us()
        delta = ticks_diff(now, self.last_triggered)
        self.last_triggered = now

        klass = self.classify(delta)

        if klass == self.TYPE_LEADING:
            self.state = self.STATE_RECEIVING
            self.buffer.clear()
        elif klass == self.TYPE_0:
            self.buffer.append(0)
            self.check_output()
        elif klass == self.TYPE_1:
            self.buffer.append(1)
            self.check_output()
        elif klass == self.TYPE_REPEAT:
            self.callback(self.last_received, True)
