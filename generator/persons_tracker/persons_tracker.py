import numpy as np

from .sort import KalmanBoxTracker, Sort, associate_detections_to_trackers


class Person(KalmanBoxTracker):
    def __init__(self, bbox):
        super().__init__(bbox)
        self.bbox = bbox
        self.centroid_coords = [((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2)]
        self.last_update_grid_pos_time = None
        self.current_grid_pos = None


class PersonsTracker(Sort):
    def __init__(self):
        super().__init__()
        self.showed_persons = list()

    def update(self, dets=np.empty((0, 5))):
        if len(dets) == 0:
            dets = np.empty((0, 5))
        self.showed_persons.clear()
        self.frame_count += 1
        # get predicted locations from existing trackers.
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        ret = []
        for t, trk in enumerate(trks):
            pos = self.trackers[t].predict()[0]
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(t)
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        for t in reversed(to_del):
            self.trackers.pop(t)
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets, trks, self.iou_threshold)
        # update matched trackers with assigned detections
        for m in matched:
            self.trackers[m[1]].update(dets[m[0], :])

        # create and initialise new trackers for unmatched detections
        for i in unmatched_dets:
            trk = Person(dets[i, :])
            self.trackers.append(trk)
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            trk.bbox = trk.get_state()[0]
            if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                # ret.append(np.concatenate((d, [trk.id + 1])).reshape(1, -1))  # +1 as MOT benchmark requires positive
                self.showed_persons.append(trk)
            i -= 1
            # remove dead tracklet
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)
        # if len(ret) > 0:
        #     return np.concatenate(ret)
        # return np.empty((0, 5))
        return self.showed_persons
