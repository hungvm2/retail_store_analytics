# Import library and package
import json
import time
from queue import Queue

import pandas as pd
import requests
import streamlit as st
from IPython.core.display import HTML
from kafka import KafkaConsumer
import av
import cv2
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

# try:
#     import streamlit.ReportThread as ReportThread
#     from streamlit.server.Server import Server
# except Exception:
    # Streamlit >= 0.65.0
import streamlit.report_thread as ReportThread
    # from streamlit.server.server import Server

from aiortc.contrib.media import MediaPlayer
from threading import Thread
from streamlit_server.streamlit_webrtc import (
    RTCConfiguration,
    VideoProcessorBase,
    WebRtcMode,
    webrtc_streamer,
)

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})


class OpenCVVideoProcessor(VideoProcessorBase):
    type: Literal["noop", "cartoon", "edges", "rotate"]

    def __init__(self) -> None:
        self.type = "noop"

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        if self.type == "noop":
            pass
        elif self.type == "cartoon":
            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)
        elif self.type == "edges":
            # perform edge detection
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)
        elif self.type == "rotate":
            # rotate image
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def select_job_name_running(api_http_job, headers):
    try:
        response = requests.get(api_http_job, headers=headers)
        if response.status_code == 200:
            dict_job = {}
            list_job_name = []
            list_job = response.json()
            for i in range(len(list_job)):
                if list_job[i]["push_enabled"] is True and list_job[i]["status"] == "running":
                    dict_job[list_job[i]["name"]] = list_job[i]["job_id"]
                    list_job_name.append(list_job[i]["name"])
            return dict_job, list_job_name
    except:
        st.write("System is failed!")

#
# def queue_to_list(q):
#     """ Dump a Queue to a list """
#     # A new list
#     l = []
#     while q.qsize() > 0:
#         l.append(q.get())
#     for i in l:
#         q.put(i)
#     l.reverse()
#     return l

def get_message_from_topic(kafka_event_col,kafka_topic,consumer):
    df = pd.DataFrame([], columns=['Time', 'Capture'])

    pd.set_option('display.max_colwidth', None)
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>

    # convert your links to html tags
    def path_to_image_html(path):
        return '<img src="' + path + '" width="210" >'

    image_cols = ['Capture']  # <- define which columns will be used to convert to html
    format_dict = {}
    for image_col in image_cols:
        format_dict[image_col] = path_to_image_html

    html_string = '''
                        {table}
                    '''
    html_string = html_string.format(
        table=df.to_html(escape=False, formatters=format_dict, index=False, border=3, ))
    with kafka_event_col:
        st.write(HTML(html_string))

    for message in consumer:
        print(message.value)
        timestamp = message.value['timestamp']
        if 'face' in kafka_topic:
            image_url = message.value['img_capture']
        elif 'traffic' in kafka_topic:
            image_url = message.value['img_capture']
        elif 'basic' in kafka_topic:
            image_url = message.value['data']['image_url']
        else:
            image_url = message.value['image_url']
        time1 = time.ctime(timestamp)
        st.write([time1, image_url])

        new_row = pd.DataFrame([time1, image_url])
        df.append(new_row)
        html_string = '''
                            {table}
                        '''
        html_string = html_string.format(
            table=df.to_html(escape=False, formatters=format_dict, index=False, border=3, ))
        with kafka_event_col:
            st.write(HTML(html_string))


def write(api_http, token, cfg):
    headers = {'Authorization': "Bearer {}".format(token)}
    api_http_job = api_http + "/jobs"
    dict_job, list_job_name = select_job_name_running(api_http_job, headers)
    placeholder = st.empty()
    with placeholder.container():
        # st.markdown(
        #     f'<p style="text-align:center;background-image: linear-gradient(to right,#1aa3ff, #FF00E0);color:#ffffff;font-size:36px;border-radius:2%;">Live View</p>',
        #     unsafe_allow_html=True)
        job_name = st.selectbox(
            'Select Running Job:',
            list_job_name
        )
        if len(list_job_name) < 1: return
        # screen_video_col, kafka_event_col = st.columns((3, 1))
        # screen_video_col = st.empty()
        job_id = dict_job[job_name]
        api_request = api_http_job + "/" + job_id
        response = requests.get(api_request, headers=headers)
        if response.status_code == 200:
            ##### Show Output Stream ######
            stream_url = response.json()["output_url"]
            url = stream_url.replace(cfg["rtsp_k8s_server"], cfg["rtsp_server"])
            # st.write(url)
            # with screen_video_col:
            def create_player():
                return MediaPlayer(url)
                # return MediaPlayer("rtsp://10.3.3.160:30554/5facf3817705d185d774ab68-")
            try:
                _ = webrtc_streamer(
                    key=f"media-streaming-{job_id}",
                    mode=WebRtcMode.RECVONLY,
                    rtc_configuration=RTC_CONFIGURATION,
                    media_stream_constraints={
                        "video": True,
                        "audio": False,
                    },
                    player_factory=create_player,
                    video_processor_factory=OpenCVVideoProcessor,
                )
            except:
                pass
            ##### Show Kafka Events ######
            # kafka_server = response.json()["kafka"]["server"]
            # kafka_topic = response.json()["kafka"]["topics"][0]["name"]
            #
            # consumer = KafkaConsumer(kafka_topic,
            #                          bootstrap_servers=[kafka_server],
            #                          value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            # kafka_thread = Thread(target=get_message_from_topic, args=(kafka_event_col, kafka_topic, consumer,))
            # ReportThread.add_report_ctx(kafka_thread)
            # kafka_thread.start()

                ##### Show Kafka Events ######
                # kafka_server = response.json()["kafka"]["server"]
                # kafka_topic = response.json()["kafka"]["topics"][0]["name"]
                # queue_event = Queue(maxsize=5)
                # temp_queue = 0
                # df = pd.DataFrame([], columns=['Time', 'Capture'])
                #
                # # convert your links to html tags
                # def path_to_image_html(path):
                #     return '<img src="' + path + '" width="210" >'
                #
                # pd.set_option('display.max_colwidth', None)
                # image_cols = ['Capture']  # <- define which columns will be used to convert to html
                # format_dict = {}
                # for image_col in image_cols:
                #     format_dict[image_col] = path_to_image_html
                # consumer = KafkaConsumer(kafka_topic,
                #                          bootstrap_servers=[kafka_server],
                #                          value_deserializer=lambda x: json.loads(x.decode('utf-8')))
                # for message in consumer:
                #     # message value and key are raw bytes -- decode if necessary!
                #     # e.g., for unicode: `message.value.decode('utf-8')`
                #     print("%s:%d:%d: key=%s value=%s" % (
                #         message.topic, message.partition, message.offset, message.key, message.value))
                #     timestamp = message.value['timestamp']
                #     if 'face' in kafka_topic:
                #         image_url = message.value['img_capture']
                #     elif 'traffic' in kafka_topic:
                #         image_url = message.value['img_capture']
                #     elif 'basic' in kafka_topic:
                #         image_url = message.value['data']['image_url']
                #     else:
                #         image_url = message.value['image_url']
                #     time1 = time.ctime(timestamp)
                #     # a = time.localtime()
                #     # time1 = time.asctime(a)
                #     while queue_event.qsize() >= 5:
                #         a = queue_event.get()
                #     queue_event.put([time1, image_url])
                #
                #     with kafka_event_col:
                #         pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
                #         html_string = '''
                #             {table}
                #         '''
                #         size_queue = queue_event.qsize()
                #         while queue_event.qsize() >= 6:
                #             a = queue_event.get()
                #         if (size_queue >= 1 and size_queue > temp_queue) or size_queue == 5:
                #             temp_queue = size_queue
                #             list_event_kafka = queue_to_list(queue_event)
                #             len_list_event = len(list_event_kafka)
                #             if len_list_event >= 5:
                #                 len_list_event = 5
                #             for i in range(len_list_event):
                #                 df.loc[i] = list_event_kafka[i]
                #             del list_event_kafka
                #         html_string = html_string.format(
                #             table=df.to_html(escape=False, formatters=format_dict, index=False, border=3, ))
                #         st.write(HTML(html_string))
