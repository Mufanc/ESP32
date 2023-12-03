from machine import ADC, Pin


class RainDetector(object):

    NO_RAIN = 0
    RAINING_SMALL = 1
    RAINING_LARGE = 2

    def __init__(self, pin_no: int):
        self.pin = Pin(pin_no)
        self.adc = ADC(self.pin)
        self.adc.atten(ADC.ATTN_11DB)

    def read(self) -> int:
        return self.adc.read()

    @classmethod
    def parse_state(cls, value):
        if value > 3800:
            return cls.NO_RAIN
        elif value > 3000:
            return cls.RAINING_SMALL
        else:
            return cls.RAINING_LARGE
