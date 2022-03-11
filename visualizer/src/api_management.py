# from pandas.core import api
import json

import numpy as np
import pandas as pd
import requests
import streamlit as st
from st_aggrid import AgGrid
import cv2
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# Return dataframe for list job from json list job to show table in streamlit
def show_list_jobs(response):
    name = []
    output_url = []
    push_enabled = []
    job_type = []
    status = []
    config = []
    job_id = []
    try:
        data = response.json()
        for i in range(len(data)):
            name.append(data[i]["name"])
            output_url.append(data[i]["output_url"])
            push_enabled.append(data[i]["push_enabled"])
            job_type.append(data[i]["job_type"])
            status.append(data[i]["status"])
            config.append(data[i]["config"])
            job_id.append(data[i]["job_id"])
    except:
        pass
    job_list_array = np.array([name, output_url, push_enabled, job_type,
                               status, config, job_id]).transpose()
    df = pd.DataFrame(job_list_array, columns=['name', 'output_url', 'push_enabled',
                                               'job_type', 'status', 'config', 'job_id'])
    return df


def show_list_streams(response):
    name = []
    input_url = []
    try:
        data = response.json()
        for i in range(len(data)):
            name.append(data[i]["name"])
            input_url.append(data[i]["input_url"])
    except:
        pass
    stream_list_array = np.array([name, input_url]).transpose()
    df = pd.DataFrame(stream_list_array, columns=['name', 'input_url'])
    return df

def select_job_name(api_http_job, headers, job_status=None):
    try:
        response = requests.get(api_http_job, headers=headers)
        if response.status_code == 200:
            dict_job = {}
            list_job_name = []
            list_job = response.json()
            for i in range(len(list_job)):
                if list_job[i]["status"] != job_status: continue
                name = list_job[i]["name"]
                if name == "":
                    name = list_job[i]["job_id"]
                dict_job[name] = list_job[i]["job_id"]
                list_job_name.append(name)

            return dict_job, list_job_name
    except:
        st.write("System is failed!")

# Create dict_stream {"stream name": "stream id"} to create selectbox stream in streamlit
def select_stream_name(api_http_stream, headers):
    try:
        response = requests.get(api_http_stream, headers=headers)
        if response.status_code == 200:
            dict_stream = {}
            list_stream_name = []
            list_stream = response.json()
            for i in range(len(list_stream)):
                dict_stream[list_stream[i]["name"]] = [list_stream[i]["stream_id"], list_stream[i]["input_url"]]
                list_stream_name.append(list_stream[i]["name"])
            return dict_stream, list_stream_name
    except:
        st.write("System is failed!")


def write(api_http, token, cfg):
    headers = {'Authorization': "Bearer {}".format(token)}
    apis_name = ["List job", "Add job", "Get job", "Delete job", "Start job", "Stop job",
                 "List streams", "Add stream", "Update stream", "Delete stream"]
    api_http_job = api_http + "/jobs"
    api_http_stream = api_http + "/streams"
    placeholder = st.empty()
    with placeholder.container():
        # st.markdown(
        #     f'<p style="text-align:center;background-image: linear-gradient(to right,#1aa3ff, #FF00E0);color:#ffffff;font-size:36px;border-radius:2%;">API for IVA Management Server</p>',
        #     unsafe_allow_html=True)
        option_api_http = st.selectbox(
            'Categories API',
            apis_name
        )
        result = st.empty()
        # List Job
        if option_api_http == "List job":
            api_request = api_http_job
            submit = st.button('Send request')
            if submit:
                response = requests.get(api_request, headers=headers)
                if response.status_code == 200:
                    df = show_list_jobs(response)
                    # Show table list job
                    with result.container():
                        AgGrid(df)

        # Add job
        elif option_api_http == "Add job":
            api_request = api_http_job
            roi = list()
            # form = st.form(key='my-form')
            job_types = cfg['services'] + cfg['other_job_types']
            job_types.remove('crowd')
            job_types.remove('fire')
            with result.container():
                job_name = st.text_input('Job name')
                job_type = st.selectbox(
                    'Job type', job_types
                )
                # Create request retrive all streamid - stream name
                dict_stream, list_stream_name = select_stream_name(
                    api_http_stream, headers)
                st.session_state['camera_name'] = st.selectbox(
                    'Camera name',
                    list_stream_name,
                    # on_change=get_frame,
                    # args=(dict_stream,)
                )
                cap = cv2.VideoCapture(dict_stream[st.session_state['camera_name']][1])
                _, st.session_state['frame'] = cap.read()
                if st.session_state['frame'] is None:
                    st.write("Can not read the Stream!")
                else:
                    st.write("Pick the ROI")
                    frame = st.session_state['frame']
                    scale = 1280 / frame.shape[1]
                    if scale != 1:
                        width = frame.shape[1]
                        height = frame.shape[0]
                        frame = cv2.resize(frame, (int(width * scale), int(height * scale)),
                                           interpolation=cv2.INTER_AREA)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    h, w = frame.shape[:2]
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                        stroke_width=5,
                        stroke_color="red",
                        background_color="",
                        background_image=Image.fromarray(frame.astype('uint8')),
                        update_streamlit=False,
                        height=h,
                        width=w,
                        drawing_mode="polygon",
                        display_toolbar=False
                    )
                    # config = form.text_area('Config', height=275, value={})
                    data = canvas_result.json_data
                    if data is not None and 'objects' in data and len(data['objects']) > 0:
                        for coord in data['objects'][0]['path']:
                            if len(coord) > 2: roi.append([round(coord[1] / w * 100, 2), round(coord[2] / h * 100, 2)])
                submit = st.button('Send request')
                config_job = {
                    "name": job_name,
                    "stream_id": dict_stream[st.session_state['camera_name']][0],
                    "job_type": job_type,
                    "config": {"roi": roi}
                }
                if submit:
                    response = requests.post(
                        api_request, json=config_job, headers=headers)
                    if response.status_code == 200:
                        st.write(
                            "Successfully created new job with name {}".format(job_name))
                    else:
                        st.write(response.json()['error'])

        # Get job and delete job, must add text input job name
        elif option_api_http in ["Get job", "Delete job"]:
            form = st.form(key='my-form')
            dict_job, list_job_name = select_job_name(api_http_job, headers)
            job_name = form.selectbox(
                'Job name',
                list_job_name
            )
            submit = form.form_submit_button('Send request')
            if submit:
                job_id = dict_job[job_name]
                api_request = api_http_job + "/" + job_id
                if option_api_http == "Get job":
                    response = requests.get(api_request, headers=headers)
                    if response.status_code == 200:
                        st.write(response.json())
                else:
                    requests.delete(api_request, headers=headers)
                    st.write("Deleted Job with ID: ", job_id)

        elif option_api_http == "Start job":
            form = st.form(key='start_job')
            dict_job, list_job_name = select_job_name(api_http_job, headers, "stopped")
            job_name = form.selectbox(
                'Job name',
                list_job_name
            )
            push_enabled = form.radio('Push enabled', ('True', 'False'))
            submit = form.form_submit_button('Send request')
            if submit:
                job_id = dict_job[job_name]
                # st.write("Job ID: {} starting.".format(job_id))
                api_request = api_http_job + "/" + job_id + "/" + "start"
                response = requests.get(api_request, headers=headers)
                if response.status_code == 200:
                    st.write("Started job {}!".format(job_name))
                else:
                    st.write(response.json()['error'])
                if push_enabled == "True":
                    api_request_push = api_http_job + "/" + job_id + "/" + "start_push"
                else:
                    api_request_push = api_http_job + "/" + job_id + "/" + "stop_push"
                _ = requests.get(api_request_push, headers=headers)


        elif option_api_http == "Stop job":
            form = st.form(key='stop_job')
            dict_job, list_job_name = select_job_name(api_http_job, headers, "running")
            job_name = form.selectbox(
                'Job name',
                list_job_name
            )
            submit = form.form_submit_button('Send request')
            if submit:
                job_id = dict_job[job_name]
                api_request = api_http_job + "/" + job_id + "/" + "stop"
                response = requests.get(api_request, headers=headers)
                if response.status_code == 200:
                    st.write("Stopped job {}!".format(job_name))
                else:
                    st.write("System is failed!")
        # List streams, Add streams, Update stream
        elif option_api_http in ["List streams", "Add stream", "Update stream"]:
            api_request = api_http_stream
            if option_api_http == "List streams":
                submit = st.button('Send request')
                if submit:
                    response = requests.get(api_request, headers=headers)
                    if response.status_code == 200:
                        df = show_list_streams(response)
                        AgGrid(df)

            elif option_api_http == "Add stream":  # Add, Update
                form = st.form(key='my-form')
                stream_name = form.text_input('stream name')
                input_url = form.text_input('input url')
                group = form.text_input('group')
                submit = form.form_submit_button('Send request')
                dict_stream = {"name": stream_name,
                               "input_url": input_url, 'group': group}
                # config_stream = form.text_area('Config Stream', height=275)

                if submit:
                    response = requests.post(api_request, json=dict_stream,
                                             headers=headers)
                    if response.status_code == 200:
                        st.header("Add new stream succeeded")
            elif option_api_http == "Update stream":
                form = st.form(key='my-form')
                dict_stream, list_stream_name = select_stream_name(
                    api_request, headers)
                stream_name = form.selectbox(
                    'Stream name',
                    list_stream_name
                )
                stream_id = dict_stream[stream_name]
                new_stream_name = form.text_input(
                    "New stream name", value=stream_name)
                input_url = form.text_input("Input url")
                group = form.text_input("Group")
                submit = form.form_submit_button('Send request')
                dict_stream = {"stream_id": stream_id, "name": new_stream_name,
                               "input_url": input_url, 'group': group}
                if submit:
                    response = requests.put(api_request, json=dict_stream,
                                            headers=headers)
                    if response.status_code == 200:
                        st.header("Update stream succeeded")

        # Delete stream
        elif option_api_http == "Delete stream":
            form = st.form(key='Stream ID')
            dict_stream, list_stream_name = select_stream_name(api_http_stream, headers)
            stream_name = form.selectbox(
                'Stream name',
                list_stream_name
            )
            submit = form.form_submit_button('Send request')
            if submit:
                stream_id = dict_stream[stream_name]
                api_request = api_http_stream + "/" + stream_id
                response = requests.delete(api_request, headers=headers)
                if response.status_code == 200:
                    st.header("Deleted Stream with ID: {}".format(stream_id))
