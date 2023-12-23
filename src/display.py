from machine import Pin, SoftI2C

from external.oled.ssd1306 import SSD1306_I2C


class Screen(object):
    def __init__(self, scl: int, sda: int):
        self.char_size = 8
        self.i2c = SoftI2C(Pin(scl), Pin(sda))
        self.oled = SSD1306_I2C(128, 64, self.i2c)
        self.char_width = self.oled.width // self.char_size
        self.char_height = self.oled.height // self.char_size

    def clear(self):
        self.oled.fill(0)
        self.oled.show()

    def char_at(self, ch: str, x: int, y: int):
        self.oled.fill_rect(
            x * self.char_size,
            y * self.char_size,
            (x + 1) * self.char_size,
            (y + 1) * self.char_size,
            0
        )
        self.oled.text(ch, x * self.char_size, y * self.char_size)
        self.oled.show()

    def message(self, string: str):
        self.oled.fill(0)

        x, y = 0, 0
        x_max, y_max = self.char_width, self.char_height

        for ch in string:
            if ch == '\n':
                x, y = 0, y + 1
                continue

            self.oled.text(ch, x * self.char_size, y * self.char_size)
            x += 1

            if x >= x_max:
                x = 0
                y += 1

        self.oled.show()

    def image(self, path: str):
        with open(path, 'rb') as fp:
            image = fp.read()

        self.oled.fill(0)

        x, y = 0, 0
        x_max, y_max = self.oled.width, self.oled.height

        for ch in image:
            for i in range(8)[::-1]:
                if ch & (1 << i):
                    self.oled.pixel(x, y, 1)
                x += 1

                if x >= x_max:
                    x = 0
                    y += 1

        self.oled.show()
