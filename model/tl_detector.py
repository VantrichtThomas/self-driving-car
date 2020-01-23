import numpy as np
import cv2
import tensorflow as tf
from keras.models import load_model
from PIL import Image
import os
import time
import sys
from .tl_classifier import TLClassifier


class TLDetector:
    __IM_WIDTH = 32
    __IM_HEIGHT = 32

    def __init__(self, path_cnn, path_ssd):
        self.tl_cls = TLClassifier(path_cnn, path_ssd)

    def detect_and_classify(self, image):
        img_full = image

        img_full_np = self.tl_cls.load_image_into_numpy_array(img_full)

        start_time = time.time()

        boxes = self.tl_cls.get_localization(img_full_np)

        if len(boxes) >= 1:
            b = boxes[0]
            if np.array_equal(b, np.zeros(4)):
                color = None
            else:
                img_np = cv2.resize(img_full_np[b[0]:b[2], b[1]:b[3]], (self.__IM_WIDTH, self.__IM_HEIGHT))
                color = self.tl_cls.get_classification(img_np)
        else:
            color = None

        end_time = time.time()
        print("Detection took {} seconds".format(end_time - start_time))
        return color
