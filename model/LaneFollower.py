import logging
import cv2
import numpy as np
from keras.models import load_model


class LaneFollower(object):

    def __init__(self,
                 car=None,
                 model_path='assets/models/lane_navigation_checkpoint_yuv_3.h5'):
        logging.info('Creating a EndToEndLaneFollower...')

        self.car = car
        if self.car is not None:
            self.curr_steering_angle = self.car.current_angle
        else:
            self.curr_steering_angle = 90
        self.model = load_model(model_path)

    def follow_lane(self, frame):
        self.curr_steering_angle = self.compute_steering_angle(frame)
        logging.debug("curr_steering_angle = %d" % self.curr_steering_angle)

        if self.car is not None:
            self.car.steer(self.curr_steering_angle)

        return frame

    def compute_steering_angle(self, frame):
        """ Find the steering angle directly based on video frame
            We assume that camera is calibrated to point to dead center
        """
        preprocessed = self.img_preprocess(frame)
        X = np.asarray([preprocessed])
        steering_angle = self.model.predict(X)[0]

        logging.debug('new steering angle: %s' % steering_angle)
        return int(steering_angle + 0.5)                                                                                # round the nearest integer

    def img_preprocess(self, image):
        height, _, _ = image.shape
        image = image[int(height*2/3):, :, :]                      # 1. remove top 2/3 of the image, as it is not relavant for lane following
        image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)             # 2. Nvidia model said it is best to use YUV color space
        image = cv2.GaussianBlur(image, (3, 3), 0)                 # Add blur
        image = cv2.resize(image, (200, 66))                       # input image size (200,66) Nvidia model
        return image
