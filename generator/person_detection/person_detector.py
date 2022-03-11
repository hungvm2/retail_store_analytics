from heatmap_server.modules.person_detection.darknet import DarkNet
import numpy as np

class PersonDetector(DarkNet):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.thresh = 0.5

    def detect(self, img, letterbox=False, thresh=0.25, hier_thresh=0.5, nms=0.3):
        c_dets, c_num, c_im = self.darknet_detections(img, letterbox, thresh, hier_thresh, nms)
        boxes, probabilities = self.convert_boxes_and_get_probabilities(c_num, c_dets)
        self.release_darknet_objects(c_dets, c_num, c_im)
        return np.array(boxes)

    def convert_boxes_and_get_probabilities(self, num, dets):
        boxes = []
        probabilities = []
        person_id = 0
        for j in range(num):
            prob = dets[j].prob[person_id]
            if prob <= self.thresh:
                continue
            b = dets[j].bbox
            x1, y1, x2, y2 = self.xy_wh_to_lt_rb(b)
            boxes.append([x1, y1, x2, y2, person_id])
            probabilities.append(dets[j].prob[person_id])
        return boxes, probabilities

    @staticmethod
    def xy_wh_to_lt_rb(b):
        top = int(b.y - b.h / 2)
        left = int(b.x - b.w / 2)
        right = int(b.x + b.w / 2)
        bottom = int(b.y + b.h / 2)
        if top < 0: top = 0
        if left < 0: left = 0
        if right < 0: right = 0
        if bottom < 0: bottom = 0
        return [left, top, right, bottom]

    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        # Rescale coords (xyxy) from img1_shape to img0_shape
        if ratio_pad is None:  # calculate from img0_shape
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]

        coords[:, [0, 2]] -= pad[0]  # x padding
        coords[:, [1, 3]] -= pad[1]  # y padding
        coords[:, :4] /= gain
        self.clip_coords(coords, img0_shape)
        return coords

    @staticmethod
    def clip_coords(boxes, img_shape):
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        boxes[:, 0].clamp_(0, img_shape[1])  # x1
        boxes[:, 1].clamp_(0, img_shape[0])  # y1
        boxes[:, 2].clamp_(0, img_shape[1])  # x2
        boxes[:, 3].clamp_(0, img_shape[0])  # y2