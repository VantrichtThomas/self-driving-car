import RPi.GPIO as GPIO


class BaseLED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.off()

    def on(self):
        GPIO.output(self.pin, 1)

    def off(self):
        GPIO.output(self.pin, 0)

    def toggle(self):
        status = GPIO.input(self.pin)
        GPIO.output(self.pin, not status)

    # def __del__(self):
    #     self.off()


class RGBLED:
    def __init__(self, red, green, blue=None):
        GPIO.setmode(GPIO.BCM)

        self.redLED = BaseLED(red)
        self.greenLED = BaseLED(green)
        if blue:
            self.blueLED = BaseLED(blue)

    def color_red(self):
        self.greenLED.off()
        self.redLED.on()

    def color_green(self):
        self.redLED.off()
        self.greenLED.on()

    def color_yellow(self):
        self.redLED.on()
        self.greenLED.on()

    def off(self):
        self.redLED.off()
        self.greenLED.off()

