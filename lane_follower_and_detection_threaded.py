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


def detect():
    led = RGBLED(14, 15)
    path_cnn = os.path.join('assets', 'models', 'CNN_tl_model.h5')
    path_ssd = os.path.join('assets', 'models', 'ssd_frozen_inference_graph.pb')
    detector = TLDetector(path_cnn, path_ssd)
    # Start reading webcam
    cap = cv2.VideoCapture(0)
    # Start detecting
    while cap.isOpened():
        _, frame = cap.read()
        # Possible colors ['Green', 'Off', 'Red', 'Yellow']
        color = detector.detect_and_classify(frame)
        if color == 'Red':
            # ToDo Stop the car when close enough
            led.color_red()
        elif color == 'Green':
            # ToDo Continue driving when the light was red
            led.color_green()
        elif color == 'Yellow':
            # ToDo Slow down the car
            led.color_yellow()
        else:
            logging.info('Nothing detected')
            # led.off()

        logging.info("color=%s" % color)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit program on 'q' keypress
            break


def follow_lines_detect_lights():
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
        # Start the traffic lights detection on separate thread
        Thread(target=detect)
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
        logging.error('Error', ex)
    finally:
        # Cleanup
        cap.release()
        car.stop()
        IO.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    follow_lines_detect_lights()
