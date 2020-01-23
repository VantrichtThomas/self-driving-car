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
    # lane_follower = LaneFollower(car)
    led = RGBLED(14, 15)
    path_cnn = os.path.join('assets', 'models', 'CNN_tl_model.h5')
    path_ssd = os.path.join('assets', 'models', 'ssd_frozen_inference_graph.pb')
    detector = TLDetector(path_cnn, path_ssd)

    logging.debug('Recording')
    # LINE FOLLOWER
    cap = cv2.VideoCapture(0)                                                                                           # Start reading webcam
    max_frame_rate = 10                                                                                                 # Frame rate to analyse ootage
    prev_time = 0                                                                                                       # Init start values

    try:
        _, frame = cap.read()
        cv2.imwrite("start_test.png", frame)

        # car.start()                                                                                                     # Start the car

        while cap.isOpened():                                                                                           # Start detecting
            time_elapsed = time.time() - prev_time
            _, frame = cap.read()

            if time_elapsed > 1. / max_frame_rate:
                # lane_follower.follow_lane(frame)                                                                      # Track line
                # logging.info("model=%3d" % lane_follower.curr_steering_angle)
                color = detector.detect_and_classify(frame)                                                             # ['Green', 'Off', 'Red', 'Yellow']
                if color == 'Red':
                    led.color_red()
                elif color == 'Green':
                    led.color_green()
                elif color == 'Yellow':
                    led.color_yellow()
                else:
                    logging.info('Nothing detected')
                    # led.off()

                logging.info("color=%s" % color)
                prev_time = time.time()

            if cv2.waitKey(1) & 0xFF == ord('q'):                                                                       # Quit program on 'q' keypress
                break

    except Exception as ex:
        logging.error('Error', ex)
    finally:                                                                                                            # cleanup
        cap.release()
        car.stop()
        IO.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    follow_lines_via_on_cam()
