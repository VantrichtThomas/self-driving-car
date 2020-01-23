import RPi.GPIO as gpio
import time
from numpy import interp
from .potentiometer import PotMeter


class Car:
    __MIN_STEER_DUTY = 2
    __FULL_STEER_DUTY = 10

    __ANGLE_MIN_SERVO = 0
    __ANGLE_MAX_SERVO = 180

    __ANGLE_MIN = 40
    __ANGLE_MAX = 140

    __CENTER = int((__ANGLE_MAX_SERVO - __ANGLE_MIN_SERVO) / 2)

    def __init__(self, pin_drive_1=16, pin_drive_2=20, pin_drive_pwm=12, pin_steer_pwm=13, sleep_time=1, drive_speed=100, enable_steering=False, min_steering_wheel_deviation_degrees=3, max_steering_wheel_deviation_degrees=10):
        # DC motor back/drive
        self.__pin_drive_1   = pin_drive_1
        self.__pin_drive_2   = pin_drive_2
        self.__pin_drive_pwm = pin_drive_pwm
        # Servo motor front/steer
        self.__pin_steer_pwm = pin_steer_pwm
        # Speed details
        self.sleep_time  = sleep_time
        self.drive_speed = drive_speed
        # PWM variables
        self.__drive_pwm = None
        self.__steer_pwm = None

        self.__current_angle = 0
        self.__min_steering_wheel_deviation = min_steering_wheel_deviation_degrees
        self.__max_steering_wheel_deviation = max_steering_wheel_deviation_degrees
        self.init_pins()
        # Steering wheel: SPI chip + potentiometer
        if enable_steering:
            self.__steering_wheel = PotMeter()
        else:
            self.__steering_wheel = None

    def __str__(self):
        return 'Car with DC pins ({} {}) PWM:{} and Servo PWM:{}'.format(self.__pin_drive_1, self.__pin_drive_2, self.__pin_drive_pwm, self.__pin_steer_pwm)

    def __del__(self):
        self.stop()

    def init_pins(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        # DC motor back/drive
        gpio.setup(self.__pin_drive_1, gpio.OUT)
        gpio.setup(self.__pin_drive_2, gpio.OUT)
        gpio.setup(self.__pin_drive_pwm, gpio.OUT)
        self.__drive_pwm = gpio.PWM(self.__pin_drive_pwm, 490)
        self.__drive_pwm.start(0)
        # Servo motor front/steer
        gpio.setup(self.__pin_steer_pwm, gpio.OUT)
        self.__steer_pwm = gpio.PWM(self.__pin_steer_pwm, 50)
        self.__steer_pwm.start(0)

    def stop(self):
        if self.__drive_pwm:
            self.__drive_pwm.stop()

        if self.__steer_pwm:
            self.__steer_pwm.stop()
        gpio.cleanup()

    def stand_still(self):
        print('Stand still')
        self.set_drive_pins(gpio.LOW, gpio.LOW, 0)

    def forward(self):
        print('Forward')
        self.set_drive_pins(gpio.LOW, gpio.HIGH, self.drive_speed)

    def reverse(self):
        print('Reverse')
        self.set_drive_pins(gpio.HIGH, gpio.LOW, self.drive_speed)

    def set_drive_pins(self, pin1_state: bool, pin2_state: bool, pin3_duty: int, wait=True, reset=True):
        gpio.output(self.__pin_drive_1, pin1_state)
        gpio.output(self.__pin_drive_2, pin2_state)
        self.__drive_pwm.ChangeDutyCycle(pin3_duty)

        if wait:
            time.sleep(self.sleep_time)
        if reset:
            self.set_drive_pins(gpio.LOW, gpio.LOW, 0, False, False)

    def __steer_to_new_angle(self, angle: int, sleep_time=0, reset=False):
        dc = interp(angle, [self.__ANGLE_MIN_SERVO, self.__ANGLE_MAX_SERVO], [self.__MIN_STEER_DUTY, self.__FULL_STEER_DUTY])       # 2% = 0deg, 12% = 180
        self.__steer_pwm.ChangeDutyCycle(dc)
        self.__current_angle = angle

        if sleep_time != 0:
            time.sleep(self.sleep_time)
        if reset:
            self.__steer_pwm.ChangeDutyCycle(0)

    def start(self):
        # Set front wheels straight
        if self.__steering_wheel:
            print('Setting front wheel to: ', self.steer_angle)
            self.__steer_to_new_angle(self.steer_angle)
        else:
            print('Setting front wheel to center:', self.CENTER)
            self.__steer_to_new_angle(self.CENTER)
        # pull up slowly
        print('Pull up')
        pull_up_speed = 90
        for dc in range(pull_up_speed-20, pull_up_speed):
            self.__drive_pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        time.sleep(0.5)
        print('Drive')
        for dc in range(pull_up_speed, self.drive_speed, -1):
            print(dc)
            self.__drive_pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        # time.sleep(2)

    def steer(self, angle):
        prev_angle = self.__current_angle
        if angle < (prev_angle - self.__min_steering_wheel_deviation) or (angle > prev_angle + self.__min_steering_wheel_deviation):    # If angle changed enough
            # if angle-prev_angle > self.__max_steering_wheel_deviation:                                                             # If changed too much
            #     angle = prev_angle + self.__max_steering_wheel_deviation
            # elif prev_angle-angle > (self.__max_steering_wheel_deviation):                                                            # If changed too much
            #     angle = prev_angle - self.__max_steering_wheel_deviation
            if angle < self.__ANGLE_MIN:                                                                                                # If angle is too small
                angle = self.__ANGLE_MIN
            elif angle > self.__ANGLE_MAX:                                                                                              # If angle is too large
                angle = self.__ANGLE_MAX

            self.__steer_to_new_angle(angle)

    @property
    def current_angle(self) -> int:
        return self.__current_angle

    @property
    def CENTER(self) -> int:
        return self.__CENTER

    @property
    def steer_angle(self) -> int:
        if self.__steering_wheel:
            return int(self.__steering_wheel.read_angle())
        else:
            return self.current_angle
