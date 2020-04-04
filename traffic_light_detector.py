import cv2
import logging
import time
import RPi.GPIO as IO
import os

from model.car import Car
from model.Led import RGBLED
# from model.LaneFollower import LaneFollower
from model.tl_detector import TLDetector


def follow_lines_via_on_cam():
    car = Car(drive_speed=100)
    # Set red and green pins for the RGB led
    led = RGBLED(14, 15)
    path_cnn = os.path.join('assets', 'models', 'CNN_tl_model.h5')
    path_ssd = os.path.join('assets', 'models', 'ssd_frozen_inference_graph.pb')
    detector = TLDetector(path_cnn, path_ssd)

    logging.debug('Webcam loaded')
    # Start reading webcam
    cap = cv2.VideoCapture(0)
    # Frame rate to analyse footage
    max_frame_rate = 10

    prev_time = 0
    try:
        # Skip first frame of video
        _, frame = cap.read()
        # Save one image to check if the field of view is okay
        cv2.imwrite("FOV_test.png", frame)

        # Start detecting
        while cap.isOpened():
            time_elapsed = time.time() - prev_time
            _, frame = cap.read()

            if time_elapsed > 1. / max_frame_rate:
                # Possible colors ['Green', 'Off', 'Red', 'Yellow']
                color = detector.detect_and_classify(frame)
                if color == 'Red':
                    led.color_red()
                elif color == 'Green':
                    led.color_green()
                elif color == 'Yellow':
                    led.color_yellow()
                else:
                    logging.info('Nothing detected')
                    # led.off()
                logging.info(f'color: {color}')
                prev_time = time.time()
    except Exception as ex:
        logging.error('Error:', ex)
    finally:
        # Cleanup
        cap.release()
        car.stop()
        IO.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    follow_lines_via_on_cam()
