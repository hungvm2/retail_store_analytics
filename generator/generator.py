from generator.person_detection.tool.utils import *
from generator.person_detection.tool.torch_utils import *
from generator.person_detection.tool.darknet2pytorch import Darknet
import torch
import argparse

import cv2
import numpy as np
from common import roi_percentage_to_px
from heatmap_server.modules.persons_tracking.person_tracker import PersonTracker
from heatmap_server._common.event import HeatmapEventKafka
import time

"""hyper parameters"""
use_cuda = True


class HeatMapGenerator:
    def __init__(self, cfgfile, weightfile):
        self.person_detector = Darknet(cfgfile)
        self.person_detector.print_network()
        self.person_detector.load_state_dict(torch.load(weightfile))
        print('Loading yolov4.pth from %s... Done!', weightfile)

        self.person_tracker = PersonTracker()

    def initialize_values(self, metadata):
        self.h, self.w = metadata.height, metadata.width
        self.roi_px, [self.x_min_in_roi, self.y_min_in_roi] = roi_percentage_to_px(self.job_cfg['roi'],
                                                                                   self.w, self.h)
        self.res = np.zeros((self.h, self.w, 3), np.uint8)
        self.loop_cycle = self.job_cfg['cycle']
        self.results = list()
        self.counting_time = int(time.time())
        self.prev_time = self.counting_time
        self.index = 0
        self.heatmap_frame = None

    def analyzing(self, frame):
        self.person_tracker.boxes = self.person_detector.detect(frame)
        self.person_tracker.update()
        if self.frame_count % self.skipped_frame_for_heat == 0:
            thres = np.zeros((self.h, self.w, 3), np.uint8)
            for person in self.person_tracker.persons:
                box = person.track_box
                w = box[2] - box[0]
                h = box[3] - box[1]
                x1, y1, x2, y2 = box[:4]
                thres = cv2.ellipse(thres, (int(self.x_min_in_roi + x1 + w / 2), int(self.y_min_in_roi + y1 + h / 2)),
                                    (int(w / 3 * 2), int(h / 3 * 2)), 0, 0,
                                    360, (1, 1, 1), -1)
            self.res = cv2.add(self.res, thres)
        self.heatmap_frame = cv2.applyColorMap(self.res, cv2.COLORMAP_JET)
        frame = cv2.addWeighted(frame, 0.7, self.heatmap_frame, 0.3, 0)
        return frame

    def make_event(self, frame, event_data=None):
        if time.time() - self.counting_time >= self.loop_cycle:
            image_name_jpg = str(uuid.uuid4()) + ".jpg"
            image_name_thumbnail_jpg = str(uuid.uuid4()) + ".jpg"
            img_url_jpg = self.capture_array(image_name_jpg, frame)
            thumbnail_frame = cv2.resize(frame, (320, 200))
            img_url_thumbnail_jpg = self.capture_array(image_name_thumbnail_jpg, thumbnail_frame)
            event = HeatmapEventKafka(self.type,
                                      self.stream_reader.metadata.stream_id,
                                      self.loop_cycle,
                                      self.counting_time,
                                      self.group,
                                      img_url_jpg,
                                      img_url_thumbnail_jpg)
            self.counting_time += self.loop_cycle
            self.res = np.zeros((self.h, self.w, 3), np.uint8)

    def process(self):
        m = Darknet(cfgfile)

        m.print_network()
        if args.torch:
            m.load_state_dict(torch.load(weightfile))
        else:
            m.load_weights(weightfile)

        if use_cuda:
            m.cuda()

        cap = cv2.VideoCapture(0)
        # cap = cv2.VideoCapture("./test.mp4")
        cap.set(3, 1280)
        cap.set(4, 720)
        print("Starting the YOLO loop...")

        num_classes = m.num_classes
        if num_classes == 20:
            namesfile = 'data/voc.names'
        elif num_classes == 80:
            namesfile = 'data/coco.names'
        else:
            namesfile = 'data/x.names'
        class_names = load_class_names(namesfile)

        while True:
            ret, img = cap.read()
            sized = cv2.resize(img, (m.width, m.height))
            sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

            start = time.time()
            boxes = do_detect(m, sized, 0.4, 0.6, use_cuda)
            finish = time.time()
            print('Predicted in %f seconds.' % (finish - start))

            result_img = plot_boxes_cv2(img, boxes[0], savename=None, class_names=class_names)

            cv2.imshow('Yolo demo', result_img)
            cv2.waitKey(1)

        cap.release()


def get_args():
    parser = argparse.ArgumentParser('Test your image or video by trained model.')
    parser.add_argument('-cfgfile', type=str, default='./cfg/yolov4.cfg',
                        help='path of cfg file', dest='cfgfile')
    parser.add_argument('-weightfile', type=str,
                        default='./checkpoints/Yolov4_epoch1.pth',
                        help='path of trained model.', dest='weightfile')
    parser.add_argument('-imgfile', type=str,
                        default='./data/mscoco2017/train2017/190109_180343_00154162.jpg',
                        help='path of your image file.', dest='imgfile')
    parser.add_argument('-torch', type=bool, default=false,
                        help='use torch yolov4.pth')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    cfgfile = "cfg/yolov4-sam-mish.cfg"
    heat_map_generator = HeatMapGenerator(cfgfile, weightfile)
    heat_map_generator.process()
