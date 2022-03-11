import requests
import streamlit as st
import yaml
import SessionState
from streamlit_server.src import api_management, output

import os
import logging

logger = logging.getLogger(__name__)

DEBUG = os.environ.get("DEBUG", "true").lower() not in ["false", "no", "0"]
logging.basicConfig(
    format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
           "%(message)s",
    force=True,
)

def main(cfg):
    session_state = SessionState.get(logged_in=False, api_http= "http://" + cfg['mgmt_server'] + "/api/v1",token="")
    ## Hide made in streamlit footer
    hide_footer = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_footer, unsafe_allow_html=True)
    _, login_screen, _ = st.columns((1,1, 1))
    login_screen = login_screen.empty()
    with login_screen.container():
        st.image("streamlit_server/logo_vivas_1.png", use_column_width="always")
        form_login = st.form(key='form_login')
        username = form_login.text_input("Username")
        password = form_login.text_input("Password", type='password')
        submit = form_login.form_submit_button('Login')
        if submit:
            api_request = session_state.api_http + "/" + "auth"
            body_json = {"username": username, "password": password}
            response = requests.post(api_request, json=body_json)
            if response.status_code == 200:
                session_state.logged_in = True
                session_state.token = response.json()["token"]
            else:
                st.error("The password you entered is incorrect")

    if session_state.logged_in:
        login_screen.empty()
        list_option = ["API Management", "Output"]
        st.sidebar.header("Select Features:")
        task = st.sidebar.selectbox(
            "List Features: ", list_option
        )
        if task == "API Management":
            api_management.write(session_state.api_http, session_state.token, cfg)
        elif task == "Output":
            output.write(session_state.api_http, session_state.token, cfg)
        else:
            st.error("Something has gone terribly wrong.")

# Start
if __name__ == "__main__":
    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)
    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)
    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)
    with open('config/streamlit_server/app.yml', 'r') as stream:
        cfg = yaml.load(stream, Loader=yaml.Loader)
    st.set_page_config(page_title="Dashboard", layout="wide")
    main(cfg)

