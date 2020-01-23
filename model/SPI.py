'''
MIT License

Copyright (c) 2020 Joshy Jonckheere

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys
import time
import RPi.GPIO as GPIO

class SPI:
    def __init__(self, clk, miso, mosi, cs):
        self._clk = clk
        self._miso = miso
        self._mosi = mosi
        self._cs = cs

        self._setup_pins()


    def _send_clock_pulse(self):
        GPIO.output(self._clk, 1)
        GPIO.output(self._clk, 0)


    def _send_start(self):
        GPIO.output(self._cs, 1)
        GPIO.output(self._clk, 0)
        GPIO.output(self._cs, 0)
    

    def _setup_pins(self):
        GPIO.setup([self._clk, self._mosi, self._cs], GPIO.OUT)
        GPIO.setup(self._miso, GPIO.IN)
    

    def _send_bits(self, cmd):
        bit_len = len(bin(cmd)) - 2
        cmd <<= (8 - bit_len)

        self._send_start()

        for bit in range(bit_len):
            # CHECK VALUE OF MSB AND SEND IT ON MOSI
            if cmd & 0x80:
                GPIO.output(self._mosi, 1)
            else:
                GPIO.output(self._mosi, 0)
            # SHIFT DATA TO THE LEFT
            cmd <<= 1
            # SEND CLOCK PULSE
            self._send_clock_pulse()
        

    def _rcv_bits(self, bit_len):
        val = 0
        for i in range(bit_len):
            self._send_clock_pulse()
            val <<= 1
            if GPIO.input(self._miso):
                val |= 0x1
        GPIO.output(self._cs, 1)
        val >>= 1
        # print(val) 
        return val
    

    def read(self, channel):
        if channel < 0 or channel > 7:
            return -1

        cmd = 0x18 | channel

        self._send_bits(cmd)
        val = self._rcv_bits(12)
        return val

