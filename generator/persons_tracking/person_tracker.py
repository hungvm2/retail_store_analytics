import numpy as np

from heatmap_server.modules.persons_tracking.sort import Sort


class PersonBox:
    def __init__(self, track_id, track_box):
        self.track_id = track_id
        self.track_box = track_box
        self.is_lying = False
        self.lying_counted = 0
        self.last_event_pushing_time = None


class PersonTracker:
    def __init__(self):
        self.mot_tracker = Sort()
        self.boxes = []
        self.trackers = []
        self.persons = []

    def update(self):
        self.trackers = self.mot_tracker.update(self.boxes)
        self.sync(self.trackers)

    def sync(self, trackers):
        tracker_ids = trackers[:, 4]
        person_ids = [person.track_id for person in self.persons]

        # add new persons
        new_ids = list(set(tracker_ids) - set(person_ids))
        for id in new_ids:
            trk = trackers[np.where(trackers[:, 4] == id)][0]
            self.persons.append(PersonBox(id, trk))

        # remove lost ids
        lost_ids = list(set(person_ids) - set(tracker_ids))
        for id in lost_ids:
            for person in self.persons:
                if person.track_id == id:
                    self.persons.remove(person)
                    # person.removed = True

        # sync exist boxes
        exist_ids = list(set(tracker_ids).intersection(person_ids))

        for id in exist_ids:
            trk = trackers[np.where(trackers[:, 4] == id)][0]
            person = [x for x in self.persons if x.track_id == id][0]
            # This is object
            person.track_box = trk
