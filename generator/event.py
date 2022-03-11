from common.feature_classes import EventWithType

class HeatmapEventKafka(EventWithType):
    def __init__(self, event_type, stream_id, loop_cycle, counting_time, group, image_url, thumbnail_url):
        super().__init__(event_type, stream_id)
        self.count_time = counting_time
        self.cycle = loop_cycle
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.group = group

