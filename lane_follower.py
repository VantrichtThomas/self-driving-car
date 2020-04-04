import cv2
import logging
import time
import RPi.GPIO as IO
import os
from threading import Thread

from model.car import Car
from model.Led import RGBLED
from model.LaneFollower import LaneFollower
from model.tl_detector import TLDetector


def follow_lines():
    car = Car(drive_speed=70)
    lane_follower = LaneFollower(car)

    # Start reading webcam
    cap = cv2.VideoCapture(0)
    # Frame rate to analyse footage
    max_frame_rate = 10

    prev_time = 0
    try:
        # Skip first three frames of video
        for i in range(3):
            _, frame = cap.read()

        # Start the car
        car.start()
        # Start following
        while cap.isOpened():
            time_elapsed = time.time() - prev_time
            _, frame = cap.read()

            if time_elapsed > 1. / max_frame_rate:
                # Track line
                lane_follower.follow_lane(frame)
                logging.info("Lane angle=%3d" % lane_follower.curr_steering_angle)
                prev_time = time.time()

    except Exception as ex:
        logging.error('Error:', ex)
    finally:
        # Cleanup
        cap.release()
        car.stop()
        IO.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    follow_lines()
