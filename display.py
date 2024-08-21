import busio
import board
from adafruit_ht16k33 import segments

# https://docs.circuitpython.org/projects/ht16k33/en/latest/api.html#adafruit_ht16k33.segments.Seg14x4.marquee

class Display:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.display = segments.Seg14x4(i2c)
        self.display.brightness = 1.0

    def print(self, message):
        self.display.fill(0)
        self.display.print(message)
