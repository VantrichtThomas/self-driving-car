import numpy as np
import cv2
import tensorflow as tf
from keras.models import load_model


class TLClassifier:
    def __init__(self, path_cnn, path_ssd):

        self.cnn_model = path_cnn
        self.signal_classes = ['Green', 'Off', 'Red', 'Yellow']
        self.signal_status, self.tl_box = None, None

        # keras classification model
        self.cls_model = load_model(self.cnn_model)
        
        # tensorflow localization/detection model
        PATH_TO_CKPT = path_ssd

        # setup tensorflow graph
        self.detection_graph = tf.Graph()
        
        # configuration for possible GPU use
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        # load frozen tensorflow detection model and initialize the tensorflow graph
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
               serialized_graph = fid.read()
               od_graph_def.ParseFromString(serialized_graph)
               tf.import_graph_def(od_graph_def, name='')
               
            self.sess = tf.compat.v1.Session(graph=self.detection_graph, config=config)
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    # Helper function to convert image into numpy array
    def load_image_into_numpy_array(self, image):
         (im_height, im_width, channels) = image.shape
         return np.array(image).reshape((im_height, im_width, 3)).astype(np.uint8)

    # Helper function to convert normalized box coordinates to pixels
    def box_normal_to_pixel(self, box, dim):
        height, width = dim[0], dim[1]
        box_pixel = [int(box[0]*height), int(box[1]*width), int(box[2]*height), int(box[3]*width)]
        return np.array(box_pixel)       
        
    def get_localization(self, image):
        """Determines the locations of the traffic light in the image
        Args:
            image: camera image
        Returns:
            list of integers: coordinates [x_left, y_up, x_right, y_down]
        """
        with self.detection_graph.as_default():
            image_expanded = np.expand_dims(image, axis=0)
            (boxes, scores, classes, num_detections) = self.sess.run([self.boxes, self.scores, self.classes, self.num_detections], feed_dict={self.image_tensor: image_expanded})

            boxes = np.squeeze(boxes)
            classes = np.squeeze(classes)
            scores = np.squeeze(scores)

            cls = classes.tolist()

            tl_boxes = []
            for i, v in enumerate(cls):
                # 10 = TRAFFIC LIGHT
                if v == 10.:
                    if not i:
                        box = [0, 0, 0, 0]
                    elif scores[i] <= 0.3:
                        box = [0, 0, 0, 0]
                    else:
                        dim = image.shape[0:2]
                        box = self.box_normal_to_pixel(boxes[i], dim)
                        box_h = box[2] - box[0]
                        box_w = box[3] - box[1]
                        ratio = box_h/(box_w + 0.01)
                        if (box_h < 10) or (box_w < 10):
                            box = [0, 0, 0, 0]
                        elif ratio < 1.5:
                            box = [0, 0, 0, 0]
                    tl_boxes.append(box)

        # print(tl_boxes)
        return tl_boxes
        
    def get_classification(self, image):
        """Determines the color of the traffic light in the image
        Args:
            image (cv::Mat): cropped image containing the traffic light
        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)
        """
        
        # Resize cropped 
        img_resize = image
        # Color map conversion
        img_resize = cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB)
        # Convert to four-dimension input as required by Keras
        img_resize = np.expand_dims(img_resize, axis=0).astype('float32')
        # Normalization
        img_resize /= 255.
        # Prediction
        predict = self.cls_model.predict_classes(img_resize)
        predict = np.squeeze(predict, axis = 0)
        # Get color classification
        tl_color = self.signal_classes[predict]
        
        # TrafficLight message
        self.signal_status = tl_color

        return self.signal_status
