import time

import cv2

from person_detector.models import Yolov4
from person_detector.tool.torch_utils import *
from person_detector.tool.utils import *
from persons_tracker import Sort


class HeatMapGenerator:
    def __init__(self, weights_path, names_path):
        self.person_detector = Yolov4(yolov4conv137weight=None, n_classes=80, inference=True)
        pretrained_dict = torch.load(weights_path, map_location=torch.device('cuda'))
        self.person_detector.load_state_dict(pretrained_dict)
        self.use_cuda = True
        if self.use_cuda:
            self.person_detector.cuda()
        self.class_names = load_class_names(names_path)
        self.network_input_size = (416, 416)
        self.person_tracker = Sort()
        self.grid_nums = (160, 90)
        self.time_interval = 60
        self.heatmap_data = None

    def accumulate_heatmap_data(self, dets):
        pass

    def save_heatmap_data(self):
        pass

    def process(self, url):
        cap = cv2.VideoCapture(url)
        width = 1280
        height = 720
        cap.set(3, width)
        cap.set(4, height)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        dets = np.empty((0, 5))
        start_time = time.time()
        self.heatmap_data = np.zeros((int(1280 / self.grid_nums[0]), int(720 / self.grid_nums[1])), dtype=int)
        while True:
            ret, frame = cap.read()
            if frame_count % 2 == 0:
                sized = cv2.resize(frame, self.network_input_size)
                sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

                start = time.time()
                dets = np.array(do_detect(self.person_detector, sized, 0.3, 0.6, self.use_cuda, frame)[0])
                finish = time.time()
                print('Predicted in %f seconds.' % (finish - start))
                self.accumulate_heatmap_data(dets)
                now = time.time()
                if now - start_time > self.time_interval:
                    self.save_heatmap_data()
                    start_time = now

            persons = self.person_tracker.update(dets)
            result_img = plot_boxes_cv2(frame, persons, savename=None, class_names=self.class_names)
            cv2.imshow('Yolo demo', result_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_count += 1

        cap.release()


if __name__ == '__main__':
    weights_file = "person_detector/network_data/yolov4.pth"
    names_file = "person_detector/network_data/coco.names"
    video_url = "../temp/test_data/retail_store1.mp4"
    heat_map_generator = HeatMapGenerator(weights_file, names_file)
    heat_map_generator.process(video_url)
