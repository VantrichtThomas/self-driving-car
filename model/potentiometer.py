from .SPI import SPI
from numpy import interp


class PotMeter:
    POT_MIN = 0
    POT_MAX = 1023

    ANGLE_MIN = 0
    ANGLE_MAX = 180

    CENTER = (ANGLE_MAX - ANGLE_MIN) / 2

    def __init__(self):
        self.spi = SPI(23, 21, 19, 24)             # GPIO.BOARD mode!

    def read_spi(self, channel):
        spidata = self.spi.read(channel)
        return spidata

    def read_angle(self, channel=0):
        channel_value = self.read_spi(channel) # [0-1023] -> 512=center -> < 512 left -> > 512 right
        return interp(channel_value, [self.POT_MIN, self.POT_MAX], [self.ANGLE_MAX, self.ANGLE_MIN])
