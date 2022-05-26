#! /usr/bin/env python3
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms

from person_detector_YOLOv3.models import load_model
from person_detector_YOLOv3.utils.transforms import Resize, DEFAULT_TRANSFORMS
from person_detector_YOLOv3.utils.utils import load_classes, rescale_boxes, non_max_suppression


class PersonDetector:
    def __init__(self, weights_path, cfg_path, class_names_path, input_size):
        self.model = load_model(cfg_path, weights_path)
        self.model.eval()  # Set model to evaluation mode
        self.class_name = load_classes(class_names_path)
        self.input_size = input_size

    def detect_image(self, image, conf_thres=0.6, nms_thres=0.5):
        # Configure input
        input_img = transforms.Compose([
            DEFAULT_TRANSFORMS,
            Resize(self.input_size)])(
            (image, np.zeros((1, 5))))[0].unsqueeze(0)

        if torch.cuda.is_available():
            input_img = input_img.to("cuda")

        # Get detections
        with torch.no_grad():
            detections = self.model(input_img)
            detections = non_max_suppression(detections, conf_thres, nms_thres)
            detections = rescale_boxes(detections[0], self.input_size, image.shape[:2])
        return detections.numpy()

    @staticmethod
    def plot_boxes_cv2(img, person, bbox_thick):
        x1, y1, x2, y2 = person.bbox[:4]
        rgb = (255, 0, 0)
        img = cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), rgb, bbox_thick)
        return img
